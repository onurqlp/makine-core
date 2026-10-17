# MAKİNE CORE — Bağımsız araştırma işletim sistemi

**17 Ekim 2026** · Mimari belge · İlk yapı `BUILD-20261017-01`

## Sorumlulukların ayrılması

- `onurqlp/coin-live-pro`: bağımsız çalışan, OKX verileri, kendi radar/sanal portföyleri ve GitHub Actions akışı olan sistem. Bu proje dışarıdan Coin.Live kodu çalıştırmaz, değiştirmez veya emir iletmez.
- `onurqlp/makine-core` (planlanan): fikir kataloğu, veri kaynağı doğrulama, ürün araştırması, maliyet senaryoları, geçmiş araştırma kararları ve entegrasyon raporu. Özel kullanıcı API key'i, gerçek banka hareketi veya emir yok.
- `onurqlp/alti-quant-lab`: altı farklı finansal araştırma stratejisi ve bağımsız referans sanal kasa. Herhangi bir PnL veya talep otomatik MAKİNE gelirine bağlanmaz.

## Beş motor

1. **MARKET_INTEL**: Kripto piyasa geçmişi, kaynak sağlığı, OHLC/OI/funding, çapraz piyasa araştırma fikri. Yalnızca doğrulanmış gözlem ve karşılaştırma.
2. **STRATEGY_DISCOVERY**: Diğer finansal modeller, araştırma tasarımı, ileri dönem veri ve yanlış sinyallerin tespiti. Fikir laboratuvarı; kârlılık ispatı değildir.
3. **PERFORMANCE_RISK**: Bütün modellere uygulanan veri kökeni, maliyet, gerçekleşme ve performans metodolojisi. Ayrı bir gelir fikri üretmediğinden kataloğa yedinci ya da 58. model eklemez.
4. **DATA_API**: Veri API, otomasyon, WordPress ve dijital hizmet fikirleri; gerçek ödeme kanıtı gelince hizmet kârlılığı incelenebilir.
5. **REVENUE_VENTURE**: B2B abonelik, alarm, fiyat takibi, sektör raporları gibi ticari ürün fikirlerinin pilot ve müşteri doğrulaması.

## İlk gerçek veri bağlayıcısı

`makine/source.py` GitHub API üzerinden COIN.LIVE `main` commit SHA'sını alır. `raw.githubusercontent.com` üzerinden **yalnız bu immutable commit** altındaki sabit dosyaları okur: 2 katalog dosyası ve 6 veri çıktısı. Her dosyanın hash'i hesaplanır. Manifest'in içerdiği data dosyaları hash ile karşılaştırılır. Aynı taramanın `scan_id` eşleşmesi ve kaynak zamanı denetlenir. Market snapshot 45 dakikadan eskiyse sistem bunu ayrıca belirtir.

İndirilen JS dosyaları **kesinlikle çalıştırılmaz**: model kimlikleri ve katalogdaki açıklamalar yalnız kaynak metni olarak ayrıştırılır. Beklenen 57 ID'den biri eksikse kaynak işlemi reddedilir. COIN.LIVE'ın sonuçları MAKİNE'nin veya ALTI'nın yeni sanal işlemi değildir.

## Manuel güncelleme

- GitHub Actions → MAKİNE CORE — Research & Publish → Run workflow → `refresh_source: true`.
- Kaynak sabitlenir, 57 fikir yeniden değerlendirilir ve yalnız MAKİNE raporları arşivlenir.
- `site/data/report.json`: site görünümü, 57 katalog kaydı, motorlar, kaynak/kanıt statüsü.
- `site/data/coinlive-handoff.json`: kullanıcının **ayrı COIN.LIVE geliştirme sürecinde** değerlendirmesi için okuma paketi; `can_promote_to_live_signal=false`, `can_execute_orders=false`.
- `data/update-history.json`: her manuel çevrim tarih, kaynak SHA ve ürün sürümüyle kaydedilir. Sürüm kendiliğinden değişmez.
- Ağ erişimi kesilirse canlı veriyi güncelmiş gibi göstermeyiz; rapora `REFRESH_FAILED` yazılır ve gelir/sinyal uydurulmaz.

## Sürüm ve para muhasebesi

- Ürün sürümü: `UNASSIGNED` (yeni platform için kullanıcının onayı beklenecek). **Öneri:** `1.0.0`.
- Yapı kaydı: `BUILD-20261017-01`, ayrı tarih alanları; araştırma zamanıyla karıştırılmaz.
- 150.000 TL: Kullanıcının iş modelleri için varsayımsal referans pilot bütçesi, yatırılmış para veya sanal borsa bakiyesi **değil**.
- `actual_verified_revenue_try=null`: ödeme sistemi bağlı değil. Bir fikrin 85/100 olması kâr olasılığı veya önerilen alım emri değildir.
- Müşteri kanıtı, ödeme makbuzu, vergiler, veri lisansı veya gerçek giderlerle desteklenmeyen hesaplar `SCENARIO_ONLY` kalır.

## Gelecek fazlar (otomatik tamamlanmış sayılmaz)

1. Gerçek müşteri görüşmeleri, fiyat pilotu, sağlayıcı kullanım koşulları.
2. P0 altı iş fikri için önceden onaylanmış deney kaydı ve vaka geçmişi.
3. Müşteri/ödeme sistemlerinden **izinli** doğrulanmış ticari gelir modülü.
4. Sonuçları `coinlive-handoff.json` ile **manuel kabul koşulu olan** bir COIN.LIVE geliştirme turuna taşımak.
5. Haklı çıkma değil ileriye dönük doğrulama: bağımsız veri dönemi, istatistiksel örnek sayısı, hata maliyetleri, veri boşlukları.

## Yayın ve güvenlik

Site GitHub Pages üzerinde statiktir. Hiçbir özel API anahtarı veya müşteri kaydı site JSON'larına yazılmamalıdır. Ücretli abonelik ve özel veri erişimi için ayrı sunucu gerekir. Piyasa verilerinin kamuya yeniden yayım lisansları kontrol edilmeden ham veri yayınlanmamalıdır. Bu nedenle site yalnız kaynak sağlığı ve agregat araştırma bilgisi gösterir.
