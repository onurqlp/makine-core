# MAKİNE — Otomatik Koordinasyon ve AI Araştırma Çalıştırıcısı

**Kurulum:** 18 Ekim 2026 · kaynak repo `onurqlp/makine-core` · ilk başarılı koordinatör çalışması: https://github.com/onurqlp/makine-core/actions/runs/39108496959

## 1. Kullanıcı komut vermeden ne çalışıyor?

`.github/workflows/coordination.yml` içinde:
- Her saat 17. dakika (UTC): COIN.LIVE ve ALTI'nın `main` commit SHA'sı sabitlenip izin verilen kamuya açık JSON'lar salt-okunur indirilir. Doğrulama, tazelik, strateji eşleştirme ve kaynak sağlık durumu `site/data/coordination.json` dosyasına yazılır.
- Her gün 04:41 UTC (Türkiye 07:41): aynı kontrol + `python -m makine refresh` ile COIN.LIVE'ın 57 fikrinin kaynak ve veri bütünlüğü daha geniş kapsamda doğrulanır.
- Günlük ve saatlik kayıtlar: `data/coordination-history.json` son 336 saatlik kayıt (maksimum 14 gün); tarih, gerçek source SHA, scan ID ve durum.
- GitHub Actions saatleri **best effort**; gerçek schedule başarısı yalnız Actions `event=schedule` ile kanıtlanır. Anahtarların hiçbiri algoritmik veya finansal emir yetkisi taşımaz.

Yayımlanan dosyalar:
- [Koordinasyon raporu](../site/data/coordination.json)
- [14 günlük log](../data/coordination-history.json)
- [57 fikir raporu](../site/data/report.json)
- [Salt-okunur COIN.LIVE handoff](../site/data/coinlive-handoff.json)
- [Üretim test ve workflow geçmişi](https://github.com/onurqlp/makine-core/actions/workflows/coordination.yml)

## 2. Sağlık kanıtı ve ayırıcı durumlar

COIN.LIVE kontrolü: `v4-manifest.json`, `health.json`, `v4-radar.json`, `v4-paper.json`; kapanış/gözlem zamanı, iki veri SHA-256 hash'i, scan ID, no-orders deklarasyonu, kaynak sağlık durumu. Bu test **tüm dosyaların** hash doğrulaması değildir; geniş çaplı kaynak yenilemesi ayrı kontrol eder.

ALTI kontrolü: `site/report.json`; A1, A2, A3, B1, B2, T0 durumları, kaynak scan zamanı, provider erişimi, 90 dakikalık kaynak tazeliği. Coin için tazelik sınırı 30 dakikadır. `FRESH`, `PARTIAL`, `STALE`, `UNAVAILABLE`, `INVALID`, `INVALID_TIME` durumları açık etiketlenir. İş akışının çalışmış olması, verinin canlı/işlem yapılabilir olduğu anlamına gelmez.

MAKİNE ↔ ALTI eşleştirmeleri: fikir ID 31→B1, 36→B2, 43→A1, 45→A2, 54→A3, 55→T0. Hepsi `RESEARCH_ONLY` ve öneri düzeyindedir.

## 3. Yapay zekâ katmanı: bilinçli şekilde kapalı

`makine/agent.py` yalnız **opsiyonel günlük** model değerlendirmesi yapar; API bağlı değilse *hiçbir model çağrısı yapmaz* ve gerçek ajan çalışıyor iddiasında bulunmaz.

Bağlamak için GitHub deposunda:
1. `Settings → Secrets and variables → Actions → Secrets → New repository secret`: adı **OPENAI_API_KEY** olan anahtarı GitHub'ın gizli alanına yapıştır. Sohbete veya kod dosyasına yazma.
2. Aynı ekrandaki `Variables` bölümünde **MAKINE_AI_ENABLED** değerini **true** olarak belirle. Bu olmadan secret tek başına model çağrısı tetiklemez.
3. İstersen **MAKINE_AI_MODEL** = **gpt-5.4-mini**; izinli alternatifler: `gpt-5.4-nano`, `gpt-4.1-mini`. Kurum/model erişimi ve ücretler platform hesabına bağlıdır. Fiyat, limit ve API bütçesini ayrıca kontrol et.
4. İlk denemeyi `Actions → MAKİNE — Autonomous Read-Only Coordination → Run workflow → full_refresh=true` ile yap; sonuç `site/data/agent-analysis.json` olur. Otomatik AI çağrısı yalnız günlük çalışma veya tam yenileme isteğinde tetiklenir, saatlik kontrollerde tetiklenmez.

Yapay zekâ API çağrısı: resmi `POST /v1/responses`, `store:false`, `max_output_tokens:900`, JSON şemalı en fazla 3 araştırma görevi. Model hiçbir GitHub/borsa araç yetkisine sahip değildir. Secret yalnız GitHub Actions görevinde kullanılır; repo, commit, statik sayfa veya rapora yazılmaz. OpenAI kullanım ücretleri API hesabına yansıyabilir.

Modelden dönen görevler **yalnız öneridir**: `PROPOSED_NOT_APPROVED`. Yeni issue/PR/commit/işlem açılmaz. Farklı sohbetlerdeki ChatGPT/Codex ajanlarına doğrudan mesaj iletilmez; GitHub issue'ları okuyup karşılık verme işi ayrı ajan yürütücüsü gerektirir.

## 4. Değiştirilmeyen sistemler ve eksik bağlantı

- COIN.LIVE'ın kaynak kodu, strateji ve 10.000 USDT sanal kasa kayıtlarına yazılmaz.
- ALTI'nın kaynak kodu, stratejileri ve 150.000 TL referansı değiştirilmez.
- MAKİNE'nin sürüm numarası kullanıcı onayı olmadan artırılmaz.
- Mevcut **Vercel** üretim sitesi GitHub'a otomatik bağlı değildir. Koordinatör çalışması GitHub JSON'larını günceller, Vercel üretim sitesini **kendiliğinden yenilemez**. Vercel proje yönetimi yetkisi erişim hatası verirse ayrıca yeniden yetkilendirme gerekir.
- Gerçek ödeme, alım-satım, cüzdan, AI ajanlar arası sohbet yürütücüsü ve üçüncü taraf veri dağıtım lisansı kurulu değildir.

## 5. Yerel ve otomatik test

```bash
python -m unittest discover -s tests -q
python -m makine.coordinator
# Yalnız gerekli GitHub Actions secret + opt-in olduğunda:
MAKINE_AI_ENABLED=true python -m makine.agent
```

Local AI denemesine anahtarı terminal geçmişine veya örnek komut içine gömme. Testlerden biri başarısız olursa workflow kayıtlarına bak; eski kayıtları yeni sayma.
