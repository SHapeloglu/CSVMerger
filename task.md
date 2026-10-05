# task.md — CSV Merger Görevleri

## 🔜 Sıradaki

- [ ] `csv_to_mysql.py` için birim testleri: `normalize_value`, `build_insert_sql`, `build_upsert_sql`, `get_password` önceliği (MySQL gerektirmeden)
- [ ] Repo temizliği: `birlesik_cikti.csv` `.gitignore`'da ama izleniyor → `git rm --cached`; kökteki `3150-...csv` ile `source/` altındaki kopya tekrarlı — örnek veri tek yerde dursun
- [ ] `--table` / `--db` adlarını `^[A-Za-z0-9_]+$` ile doğrula (backtick içine gömülüyor)
- [ ] README'deki test sayısı rozetini test sayısıyla senkron tut (şu an 13, doğru)

## 🚧 Devam Eden

_(şu anda boş)_

## ✅ Tamamlanan

- [x] 2026-10-05 — Çalışma dosyaları kod okunarak yeniden yazıldı; `pytest -q test` → 13 passed
- [x] 2026-05-17 — Son yükleme (README, help.py, testler)
