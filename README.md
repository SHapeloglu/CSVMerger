<div align="center">

# 📊 CSV Merger & MySQL Aktarıcı

**Çok parçalı CSV dosyalarını tek dosyada birleştir, MySQL'e güvenli şekilde aktar.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/Lisans-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/Testler-13%20geçti-brightgreen)](#-testler)

</div>

---

## 📌 İçindekiler

- [Nedir?](#-nedir)
- [Özellikler](#-özellikler)
- [Proje Yapısı](#-proje-yapısı)
- [Gereksinimler](#-gereksinimler)
- [Kurulum](#️-kurulum)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [merge.py — CSV Birleştirici](#-mergepy--csv-birleştirici)
- [csv_to_mysql.py — MySQL Aktarıcı](#️-csv_to_mysqlpy--mysql-aktarıcı)
- [Güvenlik](#-güvenlik)
- [Sütun Eşlemesi](#-sütun-eşlemesi)
- [Encoding Desteği](#-encoding-desteği)
- [Hata Yönetimi](#-hata-yönetimi)
- [Testler](#-testler)
- [Sık Sorulan Sorular](#-sık-sorulan-sorular)
- [Katkı](#-katkı)

---

## 🔍 Nedir?

**CSV Merger**, e-posta doğrulama servislerinden (veya başka sistemlerden) gelen yüzlerce parça CSV dosyasını tek seferde birleştirip MySQL veritabanına aktarmanızı sağlayan, sade ve güvenilir bir Python araç setidir.

```
source/
├── 1-sonuc.csv     ┐
├── 2-sonuc.csv     ├──▶  merge.py  ──▶  birlesik_cikti.csv  ──▶  csv_to_mysql.py  ──▶  MySQL
├── 3-sonuc.csv     ┘
└── ...
```

---

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| 🔀 **Akıllı birleştirme** | Yüzlerce CSV'yi tek geçişte birleştirir; başlık uyuşmazlıklarını otomatik atlar |
| 🔢 **Doğal sıralama** | Dosyaları 1, 2, 10, 11 sırasıyla işler (leksikografik değil) |
| 🌐 **Encoding tespiti** | `chardet` ile otomatik; yoksa UTF-8 → CP1254 → Latin-1 fallback zinciri |
| 🔐 **Güvenli şifre** | Şifre ortam değişkeni / `.env` üzerinden alınır, komut satırına yazılmaz |
| 🔄 **Duplicate koruması** | Aynı e-posta tekrar geldiğinde `INSERT IGNORE` (atla) veya `UPSERT` (güncelle) |
| 📦 **Toplu insert** | Ayarlanabilir batch boyutuyla yüksek performanslı veritabanı yazımı |
| 🚫 **Boş satır filtresi** | Tamamen boş satırları çıktıya yazmaz |
| 📋 **Kalıcı log** | Her işlem hem terminale hem `.log` dosyasına yazılır |
| ✅ **13 unit test** | `pytest` ile tam kapsam; MySQL gerekmez |

---

## 📁 Proje Yapısı

```
csv_merger/
│
├── merge.py              # 🔀 CSV birleştirici — ana script
├── csv_to_mysql.py       # 🗄️ MySQL aktarıcı — ana script
├── utils.py              # 🔧 Ortak araçlar: ProgressBar, encoding tespiti
│
├── requirements.txt      # Python bağımlılıkları
├── .env.example          # Ortam değişkeni şablonu (.env bu dosyadan kopyalanır)
├── .gitignore            # .env, *.log, birlesik_cikti.csv git'e girmez
│
├── source/               # 📂 Kaynak CSV dosyaları buraya atılır
│   └── *.csv
│
├── birlesik_cikti.csv    # merge.py çıktısı (otomatik oluşturulur)
│
└── tests/
    ├── test_merge.py     # 🧪 Unit testler (13 test)
    └── data/             # Sabit örnek CSV'ler (test fixture'ları)
        ├── normal_a.csv
        ├── normal_b.csv
        ├── wrong_header.csv
        ├── blank_rows.csv
        └── empty.csv
```

---

## 📋 Gereksinimler

| Bağımlılık | Sürüm | Zorunlu mu? |
|---|---|---|
| Python | ≥ 3.8 | ✅ Evet |
| `mysql-connector-python` | ≥ 8.0 | ✅ MySQL aktarımı için |
| `python-dotenv` | ≥ 1.0 | ⚡ Önerilen (`.env` desteği) |
| `chardet` | ≥ 5.0 | ⚡ Önerilen (encoding tespiti) |
| `pytest` | ≥ 7.0 | 🧪 Testler için |

> `chardet` veya `python-dotenv` kurulu değilse araç çalışmaya devam eder; ilgili özellikler devre dışı kalır.

---

## ⚙️ Kurulum

### 1. Repoyu klonla

```bash
git clone https://github.com/kullanici/csv-merger.git
cd csv-merger
```

### 2. Sanal ortam oluştur (önerilen)

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
```

### 3. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarla

```bash
cp .env.example .env
```

`.env` dosyasını bir metin editörüyle açıp MySQL şifrenizi girin:

```dotenv
DB_PASSWORD=buraya_gercek_sifrenizi_yazin
```

> ⚠️ `.env` dosyasını asla Git'e commit etmeyin. `.gitignore` zaten bu dosyayı dışlamaktadır.

---

## 🚀 Hızlı Başlangıç

```bash
# 1. CSV dosyalarınızı source/ klasörüne koyun
cp /veri/parca*.csv source/

# 2. Tüm CSV'leri birleştirin
python merge.py

# 3. MySQL'e aktarın
python csv_to_mysql.py --db hedef_db --table email_sonuclari
```

Hepsi bu kadar. `birlesik_cikti.csv` ve `merge.log` / `import.log` dosyaları otomatik oluşturulur.

---

## 🔀 merge.py — CSV Birleştirici

`source/` klasöründeki `.csv` dosyalarını okur; ortak başlığı bir kez yazar ve tüm veri satırlarını tek bir çıktı dosyasında birleştirir.

### Kullanım

```bash
python merge.py [seçenekler]
```

### Argümanlar

| Argüman | Kısa | Varsayılan | Açıklama |
|---|---|---|---|
| `--input DIR` | `-i` | `source` | Kaynak CSV dosyalarının bulunduğu klasör |
| `--output FILE` | `-o` | `birlesik_cikti.csv` | Birleşik çıktı dosyasının adı |
| `--pattern DESEN` | `-p` | `*.csv` | Hangi dosyaların alınacağını belirleyen glob deseni |
| `--encoding ENC` | `-e` | `utf-8` | Tüm dosyalar için sabit encoding |
| `--auto-encoding` | — | kapalı | Her dosya için encoding'i otomatik tespit et |
| `--log FILE` | — | `merge.log` | Log dosyasının yolu |

### Örnekler

```bash
# Varsayılan ayarlarla çalıştır
python merge.py

# Farklı bir klasörden al
python merge.py -i ./ham_veri

# Çıktı adını değiştir
python merge.py -o temmuz_2024.csv

# Yalnızca "11-" ile başlayan dosyaları al
python merge.py -p "11-*.csv"

# Encoding otomatik tespit (Türkçe / karma kaynaklı dosyalar için)
python merge.py --auto-encoding

# Özel log dosyası
python merge.py --log logs/birlesim_$(date +%F).log

# Hepsini bir arada kullan
python merge.py -i ./ham -o temiz.csv -p "*.csv" --auto-encoding --log temiz.log
```

### Çıktı Örneği

```
2024-07-15 10:23:01 [INFO] Giriş    : source
2024-07-15 10:23:01 [INFO] Bulunan  : 47 CSV dosyası
2024-07-15 10:23:01 [INFO] Çıktı    : birlesik_cikti.csv
Birleştiriliyor [███████████████████░░░░░░░░░░░░░░░] 28/47 (59.6%)  ETA: 3s
...
2024-07-15 10:23:05 [INFO] Tamamlandı!
2024-07-15 10:23:05 [INFO]   Birleştirilen : 46 dosya
2024-07-15 10:23:05 [INFO]   Toplam satır  : 142,381
2024-07-15 10:23:05 [INFO]   Boş satır     : 12 (atlandı)
2024-07-15 10:23:05 [INFO]   Çıktı boyutu  : 18,421.7 KB
2024-07-15 10:23:05 [INFO]   Süre          : 4.1s
2024-07-15 10:23:05 [WARNING] Atlanan dosyalar (1):
2024-07-15 10:23:05 [WARNING]   - 23-ozet.csv: farklı başlık: ['tarih', 'adet']

🎉 Tamamlandı! 142,381 satır → birlesik_cikti.csv
```

### Davranış Kuralları

```
Dosya açılabildi mi?  ──No──▶  Logla, atla, devam et
        │ Yes
        ▼
Dosya boş mu?  ──Yes──▶  Logla, atla, devam et
        │ No
        ▼
Başlık referansla eşleşiyor mu?  ──No──▶  Logla, atla, devam et
        │ Yes
        ▼
Satır tamamen boş mu?  ──Yes──▶  Boş satır sayacını artır, atla
        │ No
        ▼
Çıktıya yaz ✓
```

---

## 🗄️ csv_to_mysql.py — MySQL Aktarıcı

`birlesik_cikti.csv` (veya belirtilen başka bir CSV) dosyasını MySQL veritabanına toplu şekilde aktarır.

### Kullanım

```bash
python csv_to_mysql.py [seçenekler]
```

### Argümanlar

| Argüman | Varsayılan | Açıklama |
|---|---|---|
| `--csv FILE` | `birlesik_cikti.csv` | Okunacak CSV dosyası |
| `--host ADRES` | `localhost` | MySQL sunucu adresi |
| `--port PORT` | `3306` | MySQL port numarası |
| `--user KULLANICI` | `root` | MySQL kullanıcı adı |
| `--password SIFRE` | *(boş)* | ⚠️ Güvensiz — `.env` kullanın |
| `--db VERITABANI` | `email_db` | Hedef veritabanı adı |
| `--table TABLO` | `email_sonuclari` | Hedef tablo adı |
| `--batch N` | `500` | Tek seferde insert edilecek satır sayısı |
| `--encoding ENC` | `utf-8` | Sabit encoding |
| `--auto-encoding` | kapalı | Encoding otomatik tespit et |
| `--truncate` | kapalı | Insert öncesi tabloyu temizle (TRUNCATE) |
| `--upsert` | kapalı | Duplicate e-posta varsa güncelle (varsayılan: atla) |
| `--log FILE` | `import.log` | Log dosyasının yolu |

### Örnekler

```bash
# Varsayılan ayarlarla (DB_PASSWORD env değişkeni gerekli)
python csv_to_mysql.py

# Uzak sunucuya bağlan
python csv_to_mysql.py --host 192.168.1.50 --port 3306 --user admin --db prod_db

# Farklı bir CSV dosyasını aktar
python csv_to_mysql.py --csv arsiv/haziran.csv

# Büyük dosya için batch boyutunu artır (bellek ile hız dengesi)
python csv_to_mysql.py --batch 2000

# Tabloyu önce temizleyip yeniden doldur
python csv_to_mysql.py --truncate

# Duplicate e-postayı silmek yerine güncelle
python csv_to_mysql.py --upsert

# Encoding otomatik tespit + özel log
python csv_to_mysql.py --auto-encoding --log logs/import_$(date +%F).log

# Tüm seçeneklerle tam örnek
python csv_to_mysql.py \
  --csv birlesik_cikti.csv \
  --host db.sirket.com \
  --user etl_user \
  --db email_db \
  --table sonuclar_2024 \
  --batch 1000 \
  --upsert \
  --auto-encoding
```

### Duplicate Yönetimi

```
Yeni kayıt geldi
       │
email sütununda UNIQUE INDEX var mı?
       │ Evet
       ▼
Bu e-posta zaten tabloda mı?
   │           │
  Evet         Hayır
   │           │
   ▼           ▼
--upsert?    Ekle ✓
 Evet │ Hayır
  │   │
  ▼   ▼
Güncelle  Atla (INSERT IGNORE)
   ✓
```

---

## 🔐 Güvenlik

### Neden `--password` kullanmamalısınız?

```bash
# ❌ Kötü — şifre terminal geçmişine kaydolur
python csv_to_mysql.py --password gizlisifre123

# ✅ İyi — ortam değişkeni
export DB_PASSWORD=gizlisifre123
python csv_to_mysql.py

# ✅ İyi — .env dosyası
echo "DB_PASSWORD=gizlisifre123" >> .env
python csv_to_mysql.py
```

### `.env` Dosyası

```dotenv
# .env (bu dosyayı asla Git'e commit etme!)
DB_PASSWORD=gizlisifre123
```

`.gitignore` zaten `.env`'i dışlamaktadır. Takım çalışması için `.env.example` dosyasını şablonu olarak paylaşın:

```bash
cp .env.example .env
# .env'i düzenle, ardından
git add .env.example   # ✅ şablon paylaşılabilir
git add .env           # ❌ asla!
```

---

## 🗂️ Sütun Eşlemesi

CSV başlıkları otomatik olarak MySQL sütun adlarına ve tiplerine dönüştürülür.

| CSV Başlığı | MySQL Sütunu | Tip | Not |
|---|---|---|---|
| `email` | `email` | `VARCHAR(255)` | `UNIQUE INDEX` — tekrar eklenmez |
| `validity` | `validity` | `ENUM('valid','invalid','unknown')` | Geçersiz değer → NULL |
| `validSMTP` | `valid_smtp` | `TINYINT(1)` | Yalnızca 0/1; diğerleri → NULL |
| `validIdentity` | `valid_identity` | `TINYINT(1)` | Yalnızca 0/1; diğerleri → NULL |
| `customData` | `custom_data` | `VARCHAR(255)` | |
| `jobId` | `job_id` | `VARCHAR(100)` | |
| `reason` | `reason` | `VARCHAR(255)` | Boş hücre → NULL |
| `mxDomain` | `mx_domain` | `VARCHAR(255)` | |
| `reasonCode` | `reason_code` | `VARCHAR(100)` | |
| *(otomatik)* | `yukleme_tarihi` | `TIMESTAMP` | Insert zamanı otomatik kaydedilir |

> Tablo yoksa `CREATE TABLE IF NOT EXISTS` ile otomatik oluşturulur.

---

## 🌐 Encoding Desteği

Araç, karma encoding'li kaynaklarla çalışmak için çok katmanlı bir tespit mekanizması kullanır.

```
--auto-encoding aktif mi?
       │ Evet
       ▼
chardet kurulu mu?
   Evet │ Hayır
    │   │
    ▼   ▼
 chardet  Sırayla dene:
 analizi  1. utf-8-sig
    │     2. utf-8
    │     3. cp1254 (Türkçe Windows)
    │     4. latin-1
    │
    ▼
Güven ≥ %50?
  Evet │ Hayır
   │   │
   ▼   ▼
 Kullan  utf-8 (fallback)
```

**Öneri:** Türkçe veya karma kaynaklı dosyalar için her zaman `--auto-encoding` kullanın:

```bash
python merge.py --auto-encoding
python csv_to_mysql.py --auto-encoding
```

---

## ⚠️ Hata Yönetimi

| Durum | Davranış |
|---|---|
| Kaynak klasör bulunamadı | Hata logu + çıkış |
| CSV dosyası boş | Uyarı logu + atla + devam |
| Başlık uyuşmazlığı | Uyarı logu + atla + devam |
| Tamamen boş satır | Sessizce atla, sayacı artır |
| Batch insert hatası | Rollback + hata logu + sonraki batch'e devam |
| MySQL bağlantı hatası | Hata logu + çıkış |
| Geçersiz validity değeri | NULL'a çevir + uyarı logu |
| Geçersiz boolean değeri | NULL'a çevir (sessiz) |

Tüm hatalar hem terminale hem `*.log` dosyasına yazılır.

---

## 🧪 Testler

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Yalnızca belirli bir test
pytest tests/test_merge.py::test_merge_basic -v

# Kısa çıktı
pytest tests/ -q
```

### Test Kapsamı

| Test | Açıklama |
|---|---|
| `test_natural_sort_order` | 1 < 2 < 10 doğal sıralama |
| `test_find_csv_files_excludes_output` | Çıktı dosyası kaynak listesine girmiyor |
| `test_find_csv_files_pattern` | Glob deseni yalnızca CSV seçiyor |
| `test_merge_basic` | İki dosya doğru birleştiriliyor |
| `test_merge_skips_wrong_header` | Farklı başlıklı dosya atlanıyor |
| `test_merge_skips_empty_file` | Boş dosya hata vermeden atlanıyor |
| `test_merge_skips_blank_rows` | Boş satırlar filtreleniyor |
| `test_merge_output_not_included_as_source` | Çıktı/kaynak çakışma koruması |
| `test_detect_encoding_utf8` | UTF-8 tespiti |
| `test_detect_encoding_latin1` | Latin-1 tespiti |
| `test_progress_bar_completes` | ProgressBar tamamlanma durumu |
| `test_data_files_exist` | Örnek veri dosyaları yerinde |
| `test_normal_data_files_have_correct_header` | Başlık doğrulama |

> MySQL bağlantısı gerekmez; tüm testler yerel dosya sistemi üzerinde çalışır.

---

## ❓ Sık Sorulan Sorular

**S: Kaç dosyayı birleştirebilirim?**
Dosya sayısında bir üst sınır yoktur. Sistem belleği ve disk alanı yeterli olduğu sürece yüzlerce, binlerce dosya işlenebilir.

**S: CSV dosyalarının sırası önemli mi?**
Evet. Dosyalar doğal sayı sıralamasıyla (`1-`, `2-`, `10-`, `11-`…) işlenir. Sıralama dosya adına göre yapılır; oluşturulma tarihine değil.

**S: Tablo zaten varsa ne olur?**
`CREATE TABLE IF NOT EXISTS` kullanıldığı için mevcut tablo ve veriler dokunulmaz. Yalnızca yeni satırlar eklenir. Sıfırdan başlamak için `--truncate` kullanın.

**S: Aynı script iki kez çalıştırılırsa ne olur?**
Varsayılan davranış `INSERT IGNORE`'dur: aynı e-posta adresi tekrar geldiğinde satır sessizce atlanır, mevcut veri değişmez. Güncel veriyle üzerine yazmak için `--upsert` kullanın.

**S: `chardet` kurulu değilse ne olur?**
Araç çalışmaya devam eder. Encoding tespiti `utf-8-sig → utf-8 → cp1254 → latin-1` zinciriyle yapılır. Ancak karmaşık encoding'ler için `chardet` önerilir.

**S: MySQL dışında başka veritabanı destekleniyor mu?**
Şu an için yalnızca MySQL desteklenmektedir. PostgreSQL veya SQLite desteği için `csv_to_mysql.py`'deki bağlantı ve SQL katmanları adapte edilebilir.

---

## 🤝 Katkı

1. Repoyu fork'layın
2. Özellik dalı oluşturun: `git checkout -b ozellik/yeni-eklenti`
3. Değişikliklerinizi test edin: `pytest tests/ -v`
4. Commit atın: `git commit -m "feat: yeni özellik açıklaması"`
5. Push yapın: `git push origin ozellik/yeni-eklenti`
6. Pull Request açın

### Kod Standartları

- Her yeni fonksiyon için docstring yazın
- Yeni davranışlar için test ekleyin
- `--password` argümanı gibi güvenlik kurallarını koruyun

---

<div align="center">

MIT Lisansı © 2024

</div>
