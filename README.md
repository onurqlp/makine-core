# MAKİNE CORE — 57 fikirden kanıta dayalı araştırma platformuna

**Bağımsız GitHub deposuna yayınlanan ilk yapı** · `BUILD-20261017-01` · 17 Ekim 2026.

MAKİNE, COIN.LIVE PRO'nun yerine geçmez, kodunu değiştirmez, otomatik emir/sinyal oluşturmaz. `onurqlp/coin-live-pro` üzerinden **yalnız salt-okunur** kaynak verilerini inceleyen, 57 gelir fikrini beş motor altında yöneten, mobil uyumlu bir araştırma kontrol düzlemidir. Kaynak depo: `https://github.com/onurqlp/makine-core`. Bağımsız Vercel arayüzü: `https://makine-core-lab.vercel.app/`.

## İçerik

- **57 modelin tamamı:** Kaynak katalogdaki sabit ID/ad, piyasa ve ticari ürün ayrımı; 30 ana + 27 finansal/arbitraj fikir.
- **5 motor:** Market Intel, Strategy Discovery, Performance & Risk, Data/API, Revenue Venture.
- **İlk 6 öncelikli ürün:** #21 Veri API, #17 Form/ödeme izleme, #16 Webhook altyapısı, #14 Dosya işlem API, #13 AI API gateway, #19 WordPress eklentisi. Bunlar kanıtlanmış kazançlar değildir.
- **Orijinal kaynak detayları:** Manuel araştırma çalışınca kaynak `models.js` ve `arbitraj-models.js` dosyalarından kim, nasıl, neden, pilot, engel ve vazgeçme koşulları script ÇALIŞTIRILMADAN okunur.
- **Kaynak sabitleme:** Public GitHub source commit SHA, SHA-256 ve scan manifest doğrulaması, tarih, 45 dakika tazelik eşiği.
- **Gelir matematiği:** Müşteri, aylık ücret, değişken ve sabit gider senaryoları; gerçek gelir NULL.
- **Çıkış raporu:** `site/data/coinlive-handoff.json` — hiçbir strateji otomatik terfi etmez, sinyal göndermez, emir yetkisi yok.
- **Otomatik GitHub Actions:** Saatlik read-only ALTI + COIN.LIVE koordinasyonu ve günlük tam 57 fikir araştırması planlıdır. GitHub cron best-effort, asla canlı emir yok.
- **Version governance:** `config/release.json` ürün sürümü `UNASSIGNED`, öneri `1.0.0`; sadece kullanıcı onayıyla değişebilir; build ID tarihli.

## Çalıştırma

Python 3.10+; çalışma modülleri sadece standard library ile çalışır:

```bash
python -m makine refresh --offline       # 57 fikir, canlı veri yok; ilk site
python -m makine refresh                 # İSTEĞE BAĞLI, kaynaklardan manuel salt-okunur araştırma
python -m http.server 8080 --directory site
```

Siteyi `http://localhost:8080` adresinden açın. Offline modda gerçek kaynak doğrulanmış gibi görünmez. `python -m unittest discover -s tests -q` temel sözleşme ve güvenlik testlerini çalıştırır.

## GitHub, manuel araştırma ve web yayını

- **Kaynak kod:** [onurqlp/makine-core](https://github.com/onurqlp/makine-core), `main` dalı.
- **İlk mobil web sitesi:** [makine-core-lab.vercel.app](https://makine-core-lab.vercel.app/). Bu Vercel dağıtımı kaynak depoya otomatik bağlı değildir; sonraki GitHub commit'i kendiliğinden Vercel'i güncellemez.
- **Ek manuel tam veri araştırması:** `Actions → MAKİNE CORE — Research & Optional Pages → Run workflow → refresh_source=true`. Alternatif olarak GitHub üzerinde `main` dalına yalnız isteğe bağlı `[refresh-source]` işaretli commit yapılması da aynı görevi başlatır.
- **Tam 57 fikir veri yenilemesi** günlük planlı iş veya açık manuel istekle çalışır. Koordinasyon kodunun ilk push'u ayrıca ilk kontrolü başlatır.
- **Opsiyonel GitHub Pages:** `Settings → Pages → Build and deployment → Source: GitHub Actions` seçilirse dağıtım işi `https://onurqlp.github.io/makine-core/` adresini yayınlamayı dener. Bu ayar yapılmadıysa Pages adımı güvenli şekilde atlanır; `research` çalışmaya devam eder. Pages başarısı doğrulanmadan bu URL'nin aktif olduğu varsayılmaz.
- **Veri gecikmesi:** Kaynağın 45 dakika üzerindeki anlık verisi eski olarak işaretlenir. Kaynak taraması başarısızsa geçmiş veriler yeni gibi gösterilmez.

## Yönetim sınırı

COIN.LIVE için planlanan değişiklikleri sadece [`docs/COINLIVE_GUNCELLEME_PROMPTU.md`](docs/COINLIVE_GUNCELLEME_PROMPTU.md) içinde metin olarak hazırladık. COIN.LIVE'a ayrı kullanıcı onayı olmadan hiçbir commit, PR, Pages, Actions veya sanal kayıt değişikliği yapılmaz.

## Dosyalar

- `makine/catalog.py`: 57 model, grup, başlangıç sıralaması, kaynak metni ayrıştırma.
- `makine/source.py`: allowlist GitHub GET ve hash + tarih kontrolü.
- `makine/engine.py`: araştırma sonucu, beş motor, kanıt durumu, kontrollü handoff.
- `makine/cli.py`: manuel yenileme, tarihli audit, statik JSON.
- `config/pilot_approvals.json`: kullanıcı tarafından tarihli, onaylı deney kayıtları. İlk kurulumda boş.
- `site/`: yalın, mobil, etkileşimli araştırma masası.
- `docs/`: mimari, ayrı COIN.LIVE promptu, deney ve gelir doğrulama politikası.

**Güvenlik:** Piyasa ve kripto gözlemleri gerçek işlem veya kâr garantisi değildir. Public kaynaklara erişim, üçüncü taraf verinin ticari dağıtım lisansı değildir. API/hesap/ödeme anahtarlarını GitHub Pages üzerinde bulundurmayın. Ücretli servis için ayrıca güvenli sunucu ve mevzuat incelemesi gerekir.


## Otomatik MAKİNE koordinatörü — 18 Ekim 2026

- **Saatlik:** `17 * * * *` UTC (GitHub cron best-effort) ile `python -m makine.coordinator` COIN.LIVE manifest/health + radar/paper SHA doğrulaması ve ALTI altı strateji durumunu immutable commit'lerden salt-okunur alır.
- **Günlük:** `41 4 * * *` UTC ile ayrıca `python -m makine refresh` ve 57 model kataloğunun kaynak bütünlüğü yenilenir. Araştırma otomatik; ticaret ve model/sürüm değişiklikleri otomatik değildir.
- **Durum:** [koordinasyon raporu](site/data/coordination.json) ve [14 günlük kayıt](data/coordination-history.json). Eski, kısmi, erişilemez veya geçersiz kaynaklar açık durum bayrağıyla saklanır.
- **Test:** `python -m unittest discover -s tests -q`; ilk canlı GitHub çalışması [39108496959](https://github.com/onurqlp/makine-core/actions/runs/39108496959) başarılıdır.
- **Ajan sınırı:** GitHub saatlik iş akışı kural tabanlı koordinatördür; kendiliğinden diğer ChatGPT/Codex sohbetlerini açmaz, ayrı bir LLM çalışma servisi henüz bağlı değildir.
- **Yayın sınırı:** Vercel mevcut GitHub'a otomatik bağlanmış değildir; GitHub JSON'larının yenilenmesi tek başına `makine-core-lab.vercel.app` adresini güncellemez.
- **Güvenlik:** Kaynak depolara yazma / işlem / sanal pozisyon / sürüm terfisi yok; yalnız MAKİNE çıktıları commit edilir. GitHub Actions schedule kesin SLA değildir.

## İleri koordinasyon — görev kuyruğu

`makine/taskboard.py` raporlardan yalnız kurala dayalı görev çıkarır ve aynı sorun için GitHub'a tekrar tekrar yorum göndermemeye çalışır. İlk doğrulanan otomatik yorum: https://github.com/onurqlp/makine-core/issues/1#issuecomment-6247388866. [Canlı görev raporu](site/data/task-board.json); [ayrıntılı otomasyon kılavuzu](docs/AUTOMATED_COORDINATION.md). Sadece MAKİNE issue #1'e yorum yazılır, ALTI/COIN.LIVE depolarına değişiklik yapılmaz. API modeli yoksa veya kullanıcı etkinleştirme yapmadıysa yapay zekâ agent'i bağlı değildir.

### Mobil durum ekranı

`site/status.html` telefon öncelikli koordinasyon panelidir; kamuya açık GitHub main JSON kaynaklarını no-cache okuyarak kaynak zamanı, açık görev ve AI durumunu gösterir. URL yalnız site GitHub Pages ya da Vercel'e yayımlandıktan sonra kullanılabilir. GitHub Pages ayarı varsa `https://onurqlp.github.io/makine-core/status.html` adresine dağıtılır. Eski Vercel projesi henüz GitHub'a bağlı değildir.
