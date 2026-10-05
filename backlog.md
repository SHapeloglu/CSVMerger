# backlog.md — CSV Merger Fikir Havuzu

- `ensure_table` için şema farkı tespiti: eksik kolonları `ALTER TABLE ADD COLUMN` ile ekle (onaylı).
- Birleştirmede e-posta bazlı tekilleştirme seçeneği (`--dedupe email`).
- `COLUMN_MAP`'i harici YAML/JSON'dan okuma — farklı doğrulama sağlayıcılarının CSV formatları için.
- `--dry-run`: MySQL'e yazmadan kaç satır ekleneceğini / atlanacağını raporla.
- PostgreSQL / SQLite hedefi.
- Paketleme: `pyproject.toml` + `csvmerge` / `csv2mysql` konsol komutları.

## Ekleme Şablonu

```markdown
### Başlık
- **Kategori:** yeni özellik / iyileştirme / teknik borç / araştırma
- **Neden:** kısa gerekçe
- **Notlar:** büyüklük, bağımlılıklar, riskler
```
