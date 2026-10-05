# CLAUDE.md

Bu dosya, bu proje üzerinde çalışırken Claude'un (Claude Code dahil) izlemesi gereken bağlamı ve kuralları içerir.

## Proje

**📊 CSV Merger & MySQL Aktarıcı** — **Çok parçalı CSV dosyalarını tek dosyada birleştir, MySQL'e güvenli şekilde aktar.**

- GitHub: https://github.com/SHapeloglu/CSVMerger

## Teknoloji Yığını

- pytest
- Python

## Önemli Dosyalar

- `requirements.txt`

Mimari ayrıntılar için bkz. `architect.md`.

## Sık Kullanılan Komutlar

```bash
python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
pytest
```

## Kurallar

- `.env`, parola, token ve API anahtarlarını asla commit etme.
- Her çalışma oturumunun sonunda `session.md`ye kısa kayıt düş; görev durumunu `task.md`de güncelle.
- Önceliklendirilmemiş fikirleri `backlog.md`ye yaz; somutlaşınca `task.md`ye taşı.

## Çalışma Dosyaları

| Dosya | Amaç |
|---|---|
| `architect.md` | Mimari ve dizin yapısı referansı |
| `task.md` | Aktif / devam eden / tamamlanan görevler |
| `backlog.md` | Önceliklendirilmemiş fikir ve teknik borç havuzu |
| `session.md` | Oturum günlüğü — her oturum sonunda güncellenir |
