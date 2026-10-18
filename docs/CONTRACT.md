# MAKİNE ↔ ALTI ↔ COIN.LIVE — Altı modül sözleşmesi

## Üretim kimlikleri
- A1: hisse pairs; henüz lisanslı düzeltilmiş fiyat/borrow doğrulanmadı → sadece bağlantı sağlığı.
- A2: ETF–ETF; NAV/endeks/kur doğrulanmadı → sadece bağlantı sağlığı.
- A3: istatistiksel sepet/cointegration; formation/out-of-sample doğrulaması yok → sadece bağlantı sağlığı.
- B1: perpetual funding; OKX gerçekleşmiş olayları bulunabiliyor → yalnız doğrulanmış olay bağlamı. İki borsa farkı veya trade edge doğrulanmadı.
- B2: stablecoin sapması; doğrulanmış iki borsa kotasyonu yok → veri engeli.
- T0: tahvil–repo; ISIN/dirty price/repo teminat verisi yok → veri engeli.

Bütün modüller **kontrol çevriminde çalışır**, ancak mevcut upstream eksikleri nedeniyle modüllerin hepsinin sonuç üretmesi mümkün değildir.

## İthalat
`ALTI/site/report.json` ve `COIN.LIVE/web/data/v4-manifest.json`, `v4-radar.json`, `health.json`; her depodan immutable commit SHA. V4 manifest'teki radar/health SHA-256 ve scan ID kontrolü uygulanır. Her bağlam gerçek gözlem UTC anına göre yaşlanır. COIN.LIVE 45 dk, ALTI 120 dk; GitHub Actions best-effort.

## Çıktı
`site/data/coinlive-support.json` şema `coinlive-external-context-v1`: kaynak SHA/scan ID, `funding_event_context`, `matching_watch_symbols`, `status`, `trade_candidates=[]` ve tüm izin alanları `false`. Görüntüleme ve araştırma **değil**, salt-okunur veri kalitesi/yardım bağlamı.

COIN.LIVE'ın mevcut pipeline'ı bu paketi henüz otomatik tüketmez. Kontrol merkezi tarafından dışa aktarılması bir **veri köprüsü sunma** işlemidir, kaynak depoya entegrasyon yapıldığı iddiası değildir.

Risk kapıları: kaynak taze + manifest doğrulama + kaynak güvenliği. Piyasa girdi eksikken ilkeli `BLOCKED_SOURCE` kullanılır. Gerçekleşmiş funding yüzdesi getiri tahmini değildir.
