# CLAUDE.md — CSV Merger & MySQL Aktarıcı

E-posta doğrulama servislerinden gelen parça parça CSV sonuçlarını tek dosyada birleştiren (`merge.py`) ve bu dosyayı MySQL'e toplu aktaran (`csv_to_mysql.py`) iki CLI aracı. Standart kütüphane + `mysql-connector-python` + `chardet`.

- GitHub: https://github.com/SHapeloglu/CSVMerger (2026-05-03 → 05-17, tarayıcıdan yüklemeler)
- Mimari: `architect.md` · Görevler: `task.md` · Fikirler: `backlog.md` · Günlük: `session.md`

## Komutlar

```bash
python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
cp .env.example .env                  # DB_PASSWORD

python merge.py                       # source/*.csv → birlesik_cikti.csv
python merge.py -i source -p '11-*.csv' -o cikti.csv --auto-encoding
python csv_to_mysql.py                # birlesik_cikti.csv → email_db.email_sonuclari
python csv_to_mysql.py --upsert --batch 1000 --auto-encoding
python help.py [merge|mysql|akis|encoding|guvenlik|hata]   # renkli yardım

pytest -q test                        # 13 test, MySQL gerektirmez
```

## Dosyalar

- `merge.py` — birleştirme: doğal sıralama, başlık uyuşmayan dosyayı atlama, boş satır filtresi, `merge.log`.
- `csv_to_mysql.py` — aktarma: `COLUMN_MAP` (camelCase → snake_case), `COLUMN_TYPES` (DDL), `ensure_table`, `INSERT IGNORE` veya `--upsert`, `import.log`.
- `utils.py` — `ProgressBar`, `detect_encoding` (chardet → UTF-8 → CP1254 → Latin-1).
- `help.py` — kullanıcı yardım ekranı (ANSI renkli). CLI seçeneği değişirse bunu da güncelle.
- `test/test_merge.py` + `test/data/*.csv` — sadece `merge.py` ve `utils.py`'yi test ediyor.

## Kurallar ve Tuzaklar

- Şifre önceliği: `DB_PASSWORD` ortam değişkeni > `--password` (`get_password`). Yeni kimlik bilgisi eklersen aynı deseni izle; komut satırına şifre yazmayı önerme.
- CSV kolonu eklemek = `COLUMN_MAP` + `COLUMN_TYPES` + (gerekirse) `normalize_value` üçünü birlikte güncelle. `ensure_table` var olan tabloyu değiştirmez; yeni kolon için elle `ALTER TABLE` gerekir.
- `validity` sadece `valid/invalid/unknown` kabul eder; diğer değerler NULL'a döner. `email` üzerinde `UNIQUE (uq_email)` var — tekrar eden adres ya atlanır ya da (`--upsert`) güncellenir.
- Tablo/sütun adları SQL'e backtick ile gömülüyor (parametre olamaz); `--table` girdisini doğrulamadan genişletme.
- Kökte ve `source/` altında örnek/gerçek çıktı CSV'leri commit'li (`birlesik_cikti.csv` `.gitignore`'da olsa da izleniyor). Yeni gerçek e-posta verisi commit etme.
- Değişiklikten sonra `pytest -q test` çalıştır.
- Oturum sonunda `session.md`'ye kayıt düş, `task.md`'yi güncelle.
