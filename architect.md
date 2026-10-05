# architect.md — 📊 CSV Merger & MySQL Aktarıcı Mimari Referansı

Bu dosya projenin yapısının hızlı-referans özetidir. Kod değiştikçe güncel tutun.

## Genel Bakış

**Çok parçalı CSV dosyalarını tek dosyada birleştir, MySQL'e güvenli şekilde aktar.**

## Teknoloji Yığını

- pytest
- Python

## Dizin Yapısı

```
.env.example
.gitignore
3150-2026-04-23-81972135.csv
README.md
birlesik_cikti.csv
csv_to_mysql.py
help.py
merge.py
requirements.txt
source/
  3150-2026-04-23-81972135.csv
  birlesik_cikti.csv
  ornek.csv
test/
  test_merge.py
utils.py
```

## Modüller / Kaynak Dosyalar

- `csv_to_mysql.py` — CSV → MySQL Aktarıcı
- `help.py` — CSV Merger & MySQL Aktarıcı — Yardım Sayfası
- `merge.py` — CSV Birleştirici
- `utils.py` — Ortak yardımcı modül

## Giriş Noktaları ve Yapılandırma

- `requirements.txt`

## Dağıtım / Çalışma Ortamı

- GitHub: https://github.com/SHapeloglu/CSVMerger

## Diğer Dokümanlar

- `README.md`

## Mimari Kararlar

_Önemli tasarım kararlarını ve gerekçelerini buraya ekleyin (ör. "X yerine Y seçildi çünkü ...")._
