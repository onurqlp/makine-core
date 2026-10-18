# MAKİNE · COIN.LIVE Bağımsız Yardım Motoru

**Tek görev:** ALTI Quant'ın **A1, A2, A3, B1, B2, T0** modüllerini her çevrimde bağımsız kontrol etmek ve güvenli bağlam çıktısını COIN.LIVE'a sunmak.

Üretim arayüzü: https://onurqlp.github.io/makine-core/

- Altı modül her 30 dakikalık hedef çevrimde **ayrı kaynak uygunluk denetimi** çalıştırır. GitHub Actions gecikebilir.
- Geçerli ve güncel ALTI funding olayları, COIN.LIVE'ın mevcut watch sembolleriyle eşleştirilir.
- Fiyat/strateji uygulama emirleri **üretilmez**. Kaynak depo ALTI ve COIN.LIVE kodlarına **yazılmaz**.
- Kaynaklar: `onurqlp/alti-quant-lab` ve `onurqlp/coin-live-pro`. İkisi ayrı sistemlerdir.
- Şu an yalnız B1 salt-okunur funding verisi sağlayabiliyor; diğer beş modül eksik veriyi açıkça gösterir. Altı modülün **denetimi** çalışıyor olması altısının **piyasa sinyali** ürettiği anlamına gelmez.
- MAKİNE'nin dışa aktarımı: [coinlive-support.json](site/data/coinlive-support.json). Bu, COIN.LIVE'ın kendiliğinden okuduğu/uyguladığı anlamına gelmez. COIN.LIVE tarafında salt-okunur tüketici bağlantısı ayrı bir değişiklik ve onay gerektirir.
- Güncel kaynak/hata raporu: [support.json](site/data/support.json).
- Engellerin takip kaydı: [tasks.json](site/data/tasks.json) ve [GitHub Issue #1](https://github.com/onurqlp/makine-core/issues/1).
- Otomasyon: [MAKİNE Six Support](.github/workflows/support.yml). CLI: `python -m makine`.

**Sınır:** Sinyal, işlem, gerçek/paper PnL, sanal kasa transferi, sürüm terfisi ve yeni strateji uygulaması yoktur. Destek modülü doğrulanmadığında `BLOCKED_SOURCE` olur; varsayımsal değer gösterilmez.

Kapsam ve testler: [docs/CONTRACT.md](docs/CONTRACT.md), [docs/OPERATIONS.md](docs/OPERATIONS.md).
