"""
CSV → MySQL Aktarıcı
----------------------
birlesik_cikti.csv dosyasını MySQL veritabanına aktarır.

Sütunlar:
  email, validity, validSMTP, validIdentity,
  customData, jobId, reason, mxDomain, reasonCode

Kullanım:
  python csv_to_mysql.py                          # varsayılan ayarlarla
  python csv_to_mysql.py --host 127.0.0.1 --db emailler --table sonuclar
  python csv_to_mysql.py --csv baska_dosya.csv --batch 500

Kurulum:
  pip install mysql-connector-python
"""

import argparse
import csv
import sys
import time
from pathlib import Path


# ── Varsayılan ayarlar ────────────────────────────────────────────────────────
DEFAULT_CSV     = Path(__file__).parent / "birlesik_cikti.csv"
DEFAULT_HOST    = "localhost"
DEFAULT_PORT    = 3306
DEFAULT_USER    = "root"
DEFAULT_PASS    = "102030"
DEFAULT_DB      = "aws_mail_sender_pro_v3"
DEFAULT_TABLE   = "trykitty_email_sonuclari"
DEFAULT_BATCH   = 500      # Her seferinde kaç satır insert edilsin
DEFAULT_ENC     = "utf-8"
# ─────────────────────────────────────────────────────────────────────────────

# CSV'deki başlık → MySQL sütun adı eşlemesi (gerekirse buradan değiştir)
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

# MySQL sütun tipleri (tablo otomatik oluşturulurken kullanılır)
COLUMN_TYPES = {
    "email":          "VARCHAR(255)",
    "validity":       "VARCHAR(50)",
    "valid_smtp":     "VARCHAR(50)",
    "valid_identity": "VARCHAR(50)",
    "custom_data":    "VARCHAR(255)",
    "job_id":         "VARCHAR(100)",
    "reason":         "VARCHAR(255)",
    "mx_domain":      "VARCHAR(255)",
    "reason_code":    "VARCHAR(100)",
}


class ProgressBar:
    def __init__(self, total: int, label: str = ""):
        self.total = total
        self.done  = 0
        self.label = label
        self.start = time.time()
        self.width = 35

    def update(self, n: int = 1):
        self.done += n
        pct     = self.done / self.total if self.total else 1
        filled  = int(self.width * pct)
        bar     = "█" * filled + "░" * (self.width - filled)
        elapsed = time.time() - self.start
        eta     = (elapsed / pct - elapsed) if pct > 0 else 0
        sys.stdout.write(
            f"\r{self.label} [{bar}] "
            f"{self.done:,}/{self.total:,} ({pct*100:.1f}%)  ETA: {eta:.0f}s  "
        )
        sys.stdout.flush()
        if self.done >= self.total:
            sys.stdout.write("\n"); sys.stdout.flush()


def connect(host, port, user, password, database):
    try:
        import mysql.connector
    except ImportError:
        print("❌ mysql-connector-python kurulu değil.")
        print("   Kurmak için: pip install mysql-connector-python")
        sys.exit(1)

    try:
        conn = mysql.connector.connect(
            host=host, port=port,
            user=user, password=password,
            database=database,
            charset="utf8mb4",
            autocommit=False,
        )
        return conn
    except mysql.connector.Error as e:
        print(f"❌ MySQL bağlantı hatası: {e}")
        sys.exit(1)


def ensure_table(cursor, table: str, db_columns: list):
    """Tablo yoksa oluştur; varsa atla."""
    col_defs = ",\n  ".join(
        f"`{col}` {COLUMN_TYPES.get(col, 'TEXT')}"
        for col in db_columns
    )
    sql = f"""
    CREATE TABLE IF NOT EXISTS `{table}` (
      `id` INT AUTO_INCREMENT PRIMARY KEY,
      {col_defs},
      `yukleme_tarihi` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cursor.execute(sql)


def count_csv_rows(csv_path: Path, encoding: str) -> int:
    with open(csv_path, "r", encoding=encoding, errors="replace") as f:
        return sum(1 for _ in f) - 1  # başlık hariç


def import_csv(
    csv_path: str, host: str, port: int, user: str,
    password: str, database: str, table: str,
    batch_size: int, encoding: str, truncate: bool,
):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"❌ CSV dosyası bulunamadı: {csv_path}")
        sys.exit(1)

    print(f"\n📄 CSV       : {csv_path.name}")
    print(f"🔌 Sunucu   : {host}:{port}  /  Veritabanı: {database}  /  Tablo: {table}")
    print(f"📦 Batch     : {batch_size} satır\n")

    # Bağlan
    conn   = connect(host, port, user, password, database)
    cursor = conn.cursor()

    with open(csv_path, "r", encoding=encoding, errors="replace", newline="") as f:
        reader      = csv.DictReader(f)
        csv_headers = reader.fieldnames or []

        # CSV başlıklarını DB sütun adlarına çevir
        db_columns = [COLUMN_MAP.get(h, h.lower()) for h in csv_headers]

        print(f"  Sütunlar   : {' | '.join(db_columns)}")

        # Tablo oluştur
        ensure_table(cursor, table, db_columns)
        conn.commit()

        if truncate:
            cursor.execute(f"TRUNCATE TABLE `{table}`")
            conn.commit()
            print(f"  ⚠️  Tablo temizlendi (TRUNCATE)\n")

        # Satır sayısını say (ilerleme için)
        total = count_csv_rows(csv_path, encoding)
        print(f"  Toplam     : {total:,} satır aktarılacak\n")
        progress = ProgressBar(total=total, label="Aktarılıyor")

        # INSERT şablonu
        placeholders = ", ".join(["%s"] * len(db_columns))
        col_names    = ", ".join(f"`{c}`" for c in db_columns)
        insert_sql   = f"INSERT INTO `{table}` ({col_names}) VALUES ({placeholders})"

        batch      = []
        total_done = 0
        errors     = 0

        for row in reader:
            values = []
            for h in csv_headers:
                val = row.get(h, "").strip()
                values.append(val if val != "" else None)
            batch.append(values)

            if len(batch) >= batch_size:
                try:
                    cursor.executemany(insert_sql, batch)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    errors += len(batch)
                    print(f"\n  ⚠️  Batch hatası (atlandı): {e}")
                total_done += len(batch)
                progress.update(len(batch))
                batch = []

        # Son batch
        if batch:
            try:
                cursor.executemany(insert_sql, batch)
                conn.commit()
            except Exception as e:
                conn.rollback()
                errors += len(batch)
                print(f"\n  ⚠️  Son batch hatası (atlandı): {e}")
            total_done += len(batch)
            progress.update(len(batch))

    elapsed = time.time() - progress.start
    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
    db_count = cursor.fetchone()[0]

    print(f"\n🎉 Tamamlandı!")
    print(f"   Aktarılan satır : {total_done - errors:,}")
    print(f"   Hatalı satır    : {errors:,}")
    print(f"   Tablodaki toplam: {db_count:,}")
    print(f"   Süre            : {elapsed:.1f}s\n")

    cursor.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="birlesik_cikti.csv → MySQL aktarıcı"
    )
    parser.add_argument("--csv",      default=str(DEFAULT_CSV),   help="CSV dosyası yolu")
    parser.add_argument("--host",     default=DEFAULT_HOST,        help="MySQL sunucu adresi")
    parser.add_argument("--port",     default=DEFAULT_PORT, type=int)
    parser.add_argument("--user",     default=DEFAULT_USER,        help="MySQL kullanıcı adı")
    parser.add_argument("--password", default=DEFAULT_PASS,        help="MySQL şifresi")
    parser.add_argument("--db",       default=DEFAULT_DB,          help="Veritabanı adı")
    parser.add_argument("--table",    default=DEFAULT_TABLE,       help="Tablo adı")
    parser.add_argument("--batch",    default=DEFAULT_BATCH, type=int, help="Batch boyutu")
    parser.add_argument("--encoding", default=DEFAULT_ENC,         help="Dosya encoding")
    parser.add_argument("--truncate", action="store_true",
                        help="Aktarmadan önce tabloyu temizle")
    args = parser.parse_args()

    import_csv(
        csv_path=args.csv, host=args.host, port=args.port,
        user=args.user, password=args.password,
        database=args.db, table=args.table,
        batch_size=args.batch, encoding=args.encoding,
        truncate=args.truncate,
    )


if __name__ == "__main__":
    main()
