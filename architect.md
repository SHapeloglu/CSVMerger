# architect.md — CSV Merger Mimarisi

## Veri Akışı

```
source/*.csv ──merge.py──► birlesik_cikti.csv ──csv_to_mysql.py──► MySQL email_db.email_sonuclari
     │            │                                   │
     │            ├─ natural_sort_key (1,2,10,11)     ├─ detect_encoding (ops.)
     │            ├─ ilk dosyanın başlığı referans    ├─ COLUMN_MAP / normalize_value
     │            ├─ farklı başlıklı dosya → atla+log ├─ ensure_table (yoksa CREATE)
     │            └─ tamamen boş satır → yazma        └─ batch executemany: INSERT IGNORE | UPSERT
     └─ çıktı dosyası girdi listesinden hariç tutulur (find_csv_files)
```

## Modüller

| Dosya | Önemli fonksiyonlar | Not |
|---|---|---|
| `merge.py` | `natural_sort_key`, `find_csv_files`, `merge`, `main` | Argümanlar: `-i/--input` (source), `-o/--output`, `-p/--pattern`, `-e/--encoding`, `--auto-encoding`, `--log` |
| `csv_to_mysql.py` | `get_password`, `connect`, `ensure_table`, `build_insert_sql`, `build_upsert_sql`, `normalize_value`, `import_csv` | Argümanlar: `--csv --host --port --user --password --db --table --batch --encoding --auto-encoding --truncate --upsert --log` |
| `utils.py` | `ProgressBar`, `detect_encoding`, `_file_size` | İki script ortak kullanır |
| `help.py` | bölüm fonksiyonları | Sadece dokümantasyon çıktısı |

## Hedef Tablo (varsayılan `email_sonuclari`)

| CSV başlığı | Kolon | Tip |
|---|---|---|
| — | `id` | INT AUTO_INCREMENT PK |
| email | `email` | VARCHAR(255), UNIQUE `uq_email` |
| validity | `validity` | ENUM('valid','invalid','unknown') NULL |
| validSMTP | `valid_smtp` | TINYINT(1) |
| validIdentity | `valid_identity` | TINYINT(1) |
| customData | `custom_data` | VARCHAR(255) |
| jobId | `job_id` | VARCHAR(100) |
| reason | `reason` | VARCHAR(255) |
| mxDomain | `mx_domain` | VARCHAR(255) |
| reasonCode | `reason_code` | VARCHAR(100) |

## Testler

`test/test_merge.py` (13 test): normal birleştirme, boş dosya, sadece boş satırlar, yanlış başlık, doğal sıralama, encoding tespiti. `csv_to_mysql.py` için test yok.

## Mimari Kararlar

- **İki ayrı script**: birleştirme veritabanı olmadan da kullanılabilsin diye.
- **Şifre ortam değişkeninden**: `ps`/shell geçmişinde görünmesin.
- **`INSERT IGNORE` varsayılan**: tekrar çalıştırmak güvenli (idempotent); güncelleme isteniyorsa açıkça `--upsert`.
- **Encoding fallback zinciri CP1254 içeriyor**: Türkçe Windows Excel çıktıları için.
