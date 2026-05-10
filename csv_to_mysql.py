"""
CSV → MySQL Aktarıcı
----------------------
birlesik_cikti.csv dosyasını MySQL veritabanına aktarır.

Sütunlar:
  email, validity, validSMTP, validIdentity,
  customData, jobId, reason, mxDomain, reasonCode

Kullanım:
  python csv_to_mysql.py                           # .env veya ortam değişkenleri
  python csv_to_mysql.py --host 127.0.0.1 --db emailler --table sonuclar
  python csv_to_mysql.py --csv baska_dosya.csv --batch 500
  python csv_to_mysql.py --truncate                # önce tabloyu temizle
  python csv_to_mysql.py --upsert                  # duplicate email güncelle

Güvenlik:
  Şifreyi komut satırında VERME. Bunun yerine:
    1) DB_PASSWORD ortam değişkeni:  export DB_PASSWORD=sifre
    2) .env dosyası (python-dotenv):  DB_PASSWORD=sifre

Kurulum:
  pip install mysql-connector-python python-dotenv chardet

Değişiklikler (v2):
  - Şifre artık env değişkeninden / .env'den okunuyor (güvenlik)
  - Duplicate email koruması: --upsert ile ON DUPLICATE KEY UPDATE
  - email sütununa UNIQUE INDEX otomatik ekleniyor
  - ProgressBar utils.py'ye taşındı (DRY)
  - Log dosyası desteği eklendi
  - Encoding otomatik tespiti eklendi
  - count_csv_rows kaldırıldı; çift tarama ortadan kalktı
"""

import argparse
import csv
import logging
import os
import sys
import time
from pathlib import Path

from utils import ProgressBar, detect_encoding

# .env desteği: python-dotenv kuruluysa proje kökündeki .env dosyasını yükler.
# Kurulu değilse ImportError sessizce geçilir; ortam değişkenleri yine de çalışır.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ── Varsayılan ayarlar ────────────────────────────────────────────────────────
DEFAULT_CSV   = Path(__file__).parent / "birlesik_cikti.csv"  # merge.py çıktısı
DEFAULT_HOST  = "localhost"   # MySQL sunucu adresi
DEFAULT_PORT  = 3306          # MySQL varsayılan port
DEFAULT_USER  = "root"        # MySQL kullanıcı adı
DEFAULT_DB    = "email_db"    # Hedef veritabanı adı
DEFAULT_TABLE = "email_sonuclari"  # Hedef tablo adı
DEFAULT_BATCH = 500           # Tek seferde insert edilecek satır sayısı
DEFAULT_ENC   = "utf-8"       # Sabit encoding (--auto-encoding yoksa kullanılır)
LOG_FILE      = "import.log"  # Varsayılan log dosyası
# ─────────────────────────────────────────────────────────────────────────────

# Geçerli validity değerleri; bunların dışındakiler NULL'a dönüştürülür
VALID_VALIDITY = {"valid", "invalid", "unknown", ""}

# CSV başlık adı → MySQL sütun adı eşlemesi.
# CSV'deki camelCase isimler snake_case'e çevrilir (SQL konvansiyonu).
COLUMN_MAP = {
    "email":         "email",
    "validity":      "validity",
    "validSMTP":     "valid_smtp",
    "validIdentity": "valid_identity",
    "customData":    "custom_data",
    "jobId":         "job_id",
    "reason":        "reason",
    "mxDomain":      "mx_domain",
    "reasonCode":    "reason_code",
}

# Her MySQL sütunu için DDL tipi tanımı.
# ensure_table() tablo yokken bu tipleri kullanarak CREATE TABLE çalıştırır.
COLUMN_TYPES = {
    "email":          "VARCHAR(255)",
    "validity":       "ENUM('valid','invalid','unknown') DEFAULT NULL",
    "valid_smtp":     "TINYINT(1) DEFAULT NULL",    # 0/1 boolean
    "valid_identity": "TINYINT(1) DEFAULT NULL",    # 0/1 boolean
    "custom_data":    "VARCHAR(255)",
    "job_id":         "VARCHAR(100)",
    "reason":         "VARCHAR(255)",
    "mx_domain":      "VARCHAR(255)",
    "reason_code":    "VARCHAR(100)",
}


def setup_logging(log_file: str):
    """
    Logging'i hem dosyaya hem de stdout'a yazacak şekilde yapılandırır.
    Tüm INFO ve üstü mesajlar her iki hedefe de iletilir.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),  # Kalıcı log dosyası
            logging.StreamHandler(sys.stdout),                 # Anlık terminal çıktısı
        ],
    )


def get_password(cli_value: str) -> str:
    """
    Şifreyi güvenli şekilde alır; öncelik sırası:
      1. DB_PASSWORD ortam değişkeni (.env dahil)  ← önerilen yöntem
      2. CLI'dan --password argümanı               ← güvensiz, terminal geçmişine kaydolur
    İkisi de tanımlı değilse boş string döner.

    Neden ortam değişkeni öncelikli?
      `ps aux` veya shell history ile CLI argümanları görülebilir;
      ortam değişkenleri bu riskten büyük ölçüde muaftır.
    """
    return os.environ.get("DB_PASSWORD", cli_value or "")


def connect(host, port, user, password, database):
    """
    MySQL veritabanına bağlantı kurar ve bağlantı nesnesini döner.

    mysql-connector-python kurulu değilse kurulum talimatını yazdırıp çıkar.
    Bağlantı hatası alınırsa hata mesajını loglar ve çıkar.

    autocommit=False: Her batch sonunda manuel conn.commit() yapılır;
    böylece batch başarısız olursa rollback ile geri alınabilir.
    """
    try:
        import mysql.connector
    except ImportError:
        logging.error("mysql-connector-python kurulu değil.")
        logging.error("Kurmak için: pip install mysql-connector-python")
        sys.exit(1)

    try:
        conn = mysql.connector.connect(
            host=host, port=port,
            user=user, password=password,
            database=database,
            charset="utf8mb4",   # Türkçe ve emoji gibi geniş Unicode karakterleri destekler
            autocommit=False,    # Manuel transaction kontrolü için
        )
        logging.info(f"MySQL bağlantısı kuruldu: {host}:{port}/{database}")
        return conn
    except mysql.connector.Error as e:
        logging.error(f"MySQL bağlantı hatası: {e}")
        sys.exit(1)


def ensure_table(cursor, table: str, db_columns: list):
    """
    Hedef tablo yoksa oluşturur; varsa dokunmaz (IF NOT EXISTS).

    Tablo yapısı:
      - id: otomatik artan birincil anahtar
      - CSV'den gelen sütunlar (COLUMN_TYPES'tan tip alınır; bilinmeyene TEXT verilir)
      - yukleme_tarihi: kaydın ne zaman eklendiğini gösteren timestamp
      - uq_email: email sütununa UNIQUE kısıt — aynı adres iki kez insert edilemez

    Args:
        cursor:     Aktif MySQL cursor nesnesi.
        table:      Oluşturulacak / kontrol edilecek tablo adı.
        db_columns: CSV başlıklarından dönüştürülmüş MySQL sütun adları listesi.
    """
    col_defs = ",\n  ".join(
        f"`{col}` {COLUMN_TYPES.get(col, 'TEXT')}"
        for col in db_columns
    )
    sql = f"""
    CREATE TABLE IF NOT EXISTS `{table}` (
      `id` INT AUTO_INCREMENT PRIMARY KEY,
      {col_defs},
      `yukleme_tarihi` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      UNIQUE KEY `uq_email` (`email`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cursor.execute(sql)
    logging.info(f"Tablo hazır: {table}")


def build_upsert_sql(table: str, db_columns: list) -> str:
    """
    ON DUPLICATE KEY UPDATE içeren INSERT SQL cümlesi üretir.

    Aynı email tekrar geldiğinde satırı SİLMEZ, diğer sütunları günceller.
    --upsert bayrağı verildiğinde bu fonksiyon kullanılır.

    Örnek çıktı:
        INSERT INTO `tablo` (`email`, `validity`, ...)
        VALUES (%s, %s, ...)
        ON DUPLICATE KEY UPDATE `validity` = VALUES(`validity`), ...
    """
    placeholders = ", ".join(["%s"] * len(db_columns))
    col_names    = ", ".join(f"`{c}`" for c in db_columns)
    # email birincil anahtar olduğu için güncelleme listesinden çıkar
    update_parts = ", ".join(
        f"`{c}` = VALUES(`{c}`)"
        for c in db_columns
        if c != "email"
    )
    return (
        f"INSERT INTO `{table}` ({col_names}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {update_parts}"
    )


def build_insert_sql(table: str, db_columns: list) -> str:
    """
    INSERT IGNORE içeren SQL cümlesi üretir.

    Aynı email tekrar geldiğinde satırı sessizce atlar (hata vermez).
    --upsert verilmediğinde (varsayılan davranış) bu fonksiyon kullanılır.
    """
    placeholders = ", ".join(["%s"] * len(db_columns))
    col_names    = ", ".join(f"`{c}`" for c in db_columns)
    return f"INSERT IGNORE INTO `{table}` ({col_names}) VALUES ({placeholders})"


def normalize_value(col: str, val: str):
    """
    Ham CSV değerini MySQL sütun tipine uygun Python değerine dönüştürür.

    Kurallar:
      - Boş string → None (SQL NULL)
      - valid_smtp / valid_identity → int (0 veya 1); geçersiz değer → None
      - validity → ENUM kontrolü; geçersiz değer → None + uyarı logu
      - Diğer sütunlar → string olarak bırak

    Args:
        col: MySQL sütun adı (snake_case).
        val: CSV'den okunan ham değer (strip edilmiş).

    Returns:
        None, int veya str.
    """
    # Boş hücre her zaman NULL olarak saklanır
    if val == "":
        return None

    # Boolean sütunlar: yalnızca "0" veya "1" kabul edilir
    if col in ("valid_smtp", "valid_identity"):
        return int(val) if val in ("0", "1") else None

    # ENUM sütunu: tanımsız değer gelirse uyar ve NULL kullan
    if col == "validity" and val not in VALID_VALIDITY:
        logging.warning(f"Geçersiz validity değeri: '{val}' → NULL")
        return None

    return val


def import_csv(
    csv_path: str, host: str, port: int, user: str,
    password: str, database: str, table: str,
    batch_size: int, encoding: str, auto_encoding: bool,
    truncate: bool, upsert: bool,
):
    """
    CSV dosyasını okuyarak MySQL'e toplu (batch) insert yapar.

    Akış:
      1. CSV varlık kontrolü
      2. Encoding tespiti
      3. MySQL bağlantısı
      4. Tablo oluşturma / doğrulama
      5. İsteğe bağlı TRUNCATE
      6. SQL türü seçimi (upsert veya insert ignore)
      7. Satırları batch'ler halinde insert et; hata olursa o batch'i rollback yap
      8. Özet istatistik logu

    Args:
        csv_path:     Okunacak CSV dosyasının yolu.
        host:         MySQL sunucu adresi.
        port:         MySQL port numarası.
        user:         MySQL kullanıcı adı.
        password:     MySQL şifresi.
        database:     Hedef veritabanı adı.
        table:        Hedef tablo adı.
        batch_size:   Tek seferde insert edilecek satır sayısı.
        encoding:     auto_encoding=False ise kullanılacak sabit encoding.
        auto_encoding:True ise CSV encoding'i otomatik tespit edilir.
        truncate:     True ise insert öncesi tablo temizlenir.
        upsert:       True ise duplicate email güncellenir; False ise atlanır.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        logging.error(f"CSV dosyası bulunamadı: {csv_path}")
        sys.exit(1)

    # Encoding belirle
    file_enc = detect_encoding(str(csv_path)) if auto_encoding else encoding
    logging.info(f"CSV       : {csv_path.name}  (encoding: {file_enc})")
    logging.info(f"Sunucu    : {host}:{port} / {database} / {table}")
    logging.info(f"Batch     : {batch_size} satır")

    conn   = connect(host, port, user, password, database)
    cursor = conn.cursor()

    with open(csv_path, "r", encoding=file_enc, errors="replace", newline="") as f:
        reader      = csv.DictReader(f)
        csv_headers = reader.fieldnames or []

        # CSV başlık adlarını MySQL sütun adlarına çevir
        db_columns  = [COLUMN_MAP.get(h, h.lower()) for h in csv_headers]

        logging.info(f"Sütunlar  : {' | '.join(db_columns)}")

        # Tablo yoksa oluştur
        ensure_table(cursor, table, db_columns)
        conn.commit()

        # --truncate: Mevcut verileri sil, tabloyu temiz başlat
        if truncate:
            cursor.execute(f"TRUNCATE TABLE `{table}`")
            conn.commit()
            logging.warning("Tablo temizlendi (TRUNCATE)")

        # Kullanılacak SQL'i bir kez belirle (döngüde tekrar üretme)
        sql = build_upsert_sql(table, db_columns) if upsert else build_insert_sql(table, db_columns)

        batch      = []    # Biriktirilmiş satırların geçici listesi
        total_done = 0     # O ana kadar işlenen toplam satır sayısı
        errors     = 0     # Hata nedeniyle insert edilemeyen satır sayısı
        start_time = time.time()

        # Satır sayısı önceden bilinmediği için dosyayı streaming olarak oku.
        # Her 10.000 satırda ilerleme bilgisi loglanır.
        for row in reader:
            values = []
            for h, col in zip(csv_headers, db_columns):
                raw = row.get(h, "").strip()  # Baştaki/sondaki boşlukları temizle
                values.append(normalize_value(col, raw))
            batch.append(values)

            # Batch dolunca veritabanına gönder
            if len(batch) >= batch_size:
                try:
                    cursor.executemany(sql, batch)
                    conn.commit()
                except Exception as e:
                    # Batch hatalıysa tümünü geri al; kısmi yazma engellenir
                    conn.rollback()
                    errors += len(batch)
                    logging.error(f"Batch hatası (atlandı): {e}")
                total_done += len(batch)
                if total_done % 10_000 == 0:
                    logging.info(f"  {total_done:,} satır işlendi…")
                batch = []  # Batch'i sıfırla

        # Döngü bittikten sonra kalan son batch'i gönder
        if batch:
            try:
                cursor.executemany(sql, batch)
                conn.commit()
            except Exception as e:
                conn.rollback()
                errors += len(batch)
                logging.error(f"Son batch hatası (atlandı): {e}")
            total_done += len(batch)

    # Gerçek tablodaki satır sayısını sorgula (duplicate'ler sayılmaz)
    elapsed = time.time() - start_time
    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
    db_count = cursor.fetchone()[0]

    logging.info("Tamamlandı!")
    logging.info(f"  Aktarılan satır : {total_done - errors:,}")
    logging.info(f"  Hatalı satır    : {errors:,}")
    logging.info(f"  Tablodaki toplam: {db_count:,}")
    logging.info(f"  Süre            : {elapsed:.1f}s")

    print(f"\n🎉 Tamamlandı! {total_done - errors:,} satır aktarıldı → {table}")

    # Kaynakları serbest bırak
    cursor.close()
    conn.close()


def main():
    """CLI argümanlarını ayrıştırır ve import_csv() işlevini çağırır."""
    parser = argparse.ArgumentParser(
        description="birlesik_cikti.csv → MySQL aktarıcı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Güvenlik notu:
  Şifreyi --password ile VERME. Bunun yerine:
    export DB_PASSWORD=sifre          # ortam değişkeni
    echo 'DB_PASSWORD=sifre' > .env   # .env dosyası (python-dotenv)
        """,
    )
    parser.add_argument("--csv",      default=str(DEFAULT_CSV),   help="CSV dosyası yolu")
    parser.add_argument("--host",     default=DEFAULT_HOST,        help="MySQL sunucu adresi")
    parser.add_argument("--port",     default=DEFAULT_PORT, type=int, help="MySQL port")
    parser.add_argument("--user",     default=DEFAULT_USER,        help="MySQL kullanıcı adı")
    parser.add_argument(
        "--password", default="",
        help="⚠️  Güvensiz! DB_PASSWORD ortam değişkenini tercih et.",
    )
    parser.add_argument("--db",       default=DEFAULT_DB,          help="Veritabanı adı")
    parser.add_argument("--table",    default=DEFAULT_TABLE,        help="Tablo adı")
    parser.add_argument("--batch",    default=DEFAULT_BATCH, type=int, help="Batch boyutu")
    parser.add_argument("--encoding", default=DEFAULT_ENC,          help="Sabit encoding")
    parser.add_argument("--auto-encoding", action="store_true",
                        help="Encoding otomatik tespit et")
    parser.add_argument("--truncate", action="store_true",
                        help="Aktarmadan önce tabloyu temizle")
    parser.add_argument("--upsert",   action="store_true",
                        help="Duplicate email'i atlamak yerine güncelle")
    parser.add_argument("--log",      default=LOG_FILE,             help="Log dosyası yolu")
    args = parser.parse_args()

    setup_logging(args.log)

    # Şifreyi güvenli kanaldan al (env > CLI)
    password = get_password(args.password)

    import_csv(
        csv_path=args.csv, host=args.host, port=args.port,
        user=args.user, password=password,
        database=args.db, table=args.table,
        batch_size=args.batch, encoding=args.encoding,
        auto_encoding=args.auto_encoding,
        truncate=args.truncate, upsert=args.upsert,
    )


if __name__ == "__main__":
    main()
