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
- **Manuel GitHub Actions:** Kullanıcı tetiklemedikçe araştırma yenilenmez; kod güncellemesi veri taraması yapmaz. Pages mobil site yayınlar.
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
- **Manuel gerçek veri araştırması:** `Actions → MAKİNE CORE — Research & Optional Pages → Run workflow → refresh_source=true`. Alternatif olarak GitHub üzerinde `main` dalına yalnız isteğe bağlı `[refresh-source]` işaretli commit yapılması da aynı görevi başlatır.
- **Kod push'u kendi başına piyasa taraması başlatmaz.** Yeni kaynak verisi yalnız yukarıdaki açık talep üzerine okunur.
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
