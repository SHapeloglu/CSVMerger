# session.md — CSV Merger Oturum Günlüğü

Her oturum sonunda en üste yeni kayıt ekle.

---

## 2026-10-05

**Yapılanlar:**
- Şablondan üretilmiş çalışma dosyaları kod okunarak yeniden yazıldı.
- `pytest -q test` → 13 passed.

**Tespitler:**
- `csv_to_mysql.py` test edilmiyor.
- `birlesik_cikti.csv` ignore edilmiş olmasına rağmen izleniyor; örnek CSV'ler kökte ve `source/`'ta tekrarlı.

**Sıradaki adım:** `task.md` → "Sıradaki".

---

## 2026-05-03 → 2026-05-17

- GitHub web arayüzünden yüklemeler: ilk sürüm (05-03), test altyapısı ve test verileri (05-10), son güncelleme (05-17). Ayrıntılı oturum kaydı yok.

---

### Kayıt Şablonu

```markdown
## YYYY-AA-GG
**Yapılanlar:** ...
**Kararlar / neden:** ...
**Açık sorunlar:** ...
**Sıradaki adım:** ...
```
