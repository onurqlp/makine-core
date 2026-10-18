# MAKİNE CORE — Dağıtım durumu (17 Ekim 2026)

## Tamamlanan

- Vercel projesi: `makine-core-lab`; proje kimliği `prj_dIuEzbbt7AGstS18apThTEqLVqZe`.
- Üretim dağıtımı: `dpl_7pZhtXePtNe6yqJtngW9sqxXcfyn`, Vercel durum `READY`.
- Üretim alan adı: `https://makine-core-lab.vercel.app/`.
- Public erişim için Vercel Auth koruması kapatıldı. Dış ağda web tarayıcısı yoluyla ayrıca uçtan uca doğrulama yapılmadı.
- 57 katalog modeli + 5 motor, mobil statik UI, gelir senaryosu hesaplayıcısı, güncelleme ve ürün sürümü kayıtları, COIN.LIVE'a okunur ama sinyal olmayan aktarım paketi.
- Python ve JavaScript sözleşme/sözdizimi doğrulaması: 7 Python birim testi başarılı, Node sözdizimi başarılı.

## GitHub kurulumu / güncel durum

- `onurqlp/makine-core` deposu **17 Ekim 2026 tarihinde kullanıcı tarafından oluşturuldu**; kaynak kodun bu depoya aktarılması yetkilendirildi.
- GitHub Actions üzerinde `Research & Optional Pages` iş akışı, kaynak araştırmasını yalnız `workflow_dispatch` veya açık `[refresh-source]` commit isteğiyle yapar.
- GitHub Pages ayarı etkin değilse site dağıtımı atlanır; mevcut Vercel yayını etkilenmez.
- Vercel henüz GitHub'a bağlı değildir; yeni GitHub commit'leri Vercel'i kendiliğinden güncellemez.
- İlk kaynak senkronizasyonunun doğrulanması, Github çalışma kayıtlarının tamamlanması ve tarihli `site/data/report.json` kaydı görülmesiyle gerçekleşir; yapılmadan `VERIFIED` denmez.
- Gerçek ödeme, müşteri ve işlem hesapları halen bağlı değildir.

## Yönetim sınırları

Yalnız `onurqlp/makine-core` üzerinde değişiklik ve manuel salt-okunur kaynak araştırması yapılır. `onurqlp/coin-live-pro` ve `onurqlp/alti-quant-lab` için hiçbir kaynak güncellemesi, workflow eylemi veya dosya yazımı yapılmaz.

## İlk canlı kaynak aktarımı — doğrulandı

- **İlk başarılı COIN.LIVE kaynak sabitlemesi:** 17 Ekim 2026, 14:35:03 UTC (Türkiye 17:35).
- **Kaynaktaki commit:** `2ba2dd85e2bd6219aa6dae2873ee0a0bf3b31883`.
- **Kaynak scan ID:** `bc2691aff50c54a02cac84bf`.
- **Kaynak katalog:** 57/57 kimlik ve ad eşleşti; `MATCHES_REMOTE_PINNED_COMMIT`.
- **Kaynak bütünlüğü:** `VERIFIED`, aktarım sırasında `fresh_at_import: true`.
- **Kaynak işletim uyarısı:** `DEGRADED_SCHEDULE_GAP`; kaynak taramalarının kesintisiz gerçekleştiği garanti edilmez.
- **İlk doğrulama GitHub Actions:** https://github.com/onurqlp/makine-core/actions/runs/39041358006 — başarıyla tamamlandı, testler geçti.
- **Güncellenen Vercel dağıtımı:** `dpl_F4b67GgbYyvhDbSc8pdNV1WQNyqT`, durum `READY`, adres https://makine-core-lab.vercel.app/.
- **Ürün sürümü:** `UNASSIGNED`; kullanıcı onayı olmadan değiştirilmedi.
- **GitHub Pages:** İlk doğrulamada henüz etkin değildi; bu yüzden opsiyonel yayın adımı atlandı. Vercel yayını aktif.

Bu tarihli kaydın `fresh_at_import` durumu, ilerleyen günlerde de verinin hâlâ güncel olduğunu **göstermez**; kaynak zamanları her yeni araştırmada tekrar kontrol edilir. Vercel, GitHub'a otomatik bağlı değildir. COIN.LIVE veya ALTI deposuna hiçbir yazma yapılmadı.


## MAKİNE son ürünleştirme denetimi — 18 Ekim 2026

**Kaynak gerçekliği:** Depo kodu ve Actions raporları başarılı, ancak bu durumun otomatik olarak Vercel üretim alanına dağıtıldığını gösteren kanıt **yok**. Vercel'in daha eski `READY` dağıtım kaydı, yeni kodun o adreste çalıştığı anlamına gelmez.

**Otomatik motor (doğrulandı):**
- 57 fikir + 5 motor ve salt-okunur COIN.LIVE → MAKİNE köprüsü muhafaza edildi.
- ALTI altı modülün kimlik/status eşleşmesi korunuyor; makine paper/live işlem üretmez.
- Saatlik rapor + günlük daha geniş katalog okuması `.github/workflows/coordination.yml` içinde tanımlı; GitHub cron kesin zamanda çalışmayabilir.
- Otomatik durum değişikliği GitHub issue #1 yorumlarıyla test edildi; aynı durum değişmeden gereksiz bildirim yapmaz.
- Mobil `site/status.html`: mevcut kaynak yaşını tarayıcıda hesaplar, açık görevleri, 6 eşleşmeyi, geçmiş kaydı ve AI durumunu gösterir.
- Ana sayfa `site/index.html`: canlı kaynak ve görev özet paneli eklendi.
- Kaynaklar eskiyse panel `FRESH` göstermemeli; boş veya erişilemeyen kaynaklar hiçbir zaman kâr veya işlem doğruluğu olarak yorumlanmamalı.
- Javascript ve Python testleri GitHub üzerinde geçti.

**Yayın (eksik kullanıcı hesabı ayarı):**
- `onurqlp/makine-core` GitHub repo API `has_pages=false` gösteriyor. GitHub Actions sayfa işinin `configure/upload/deploy` adımları **bilerek atlandı**. Siteye açık/dogrulanmış yeni URL ilan edilmedi.
- Kullanıcı GitHub'da **Settings → Pages → Build and deployment → Source = GitHub Actions** seçtiğinde, kaynak değişikliklerinde `publish.yml`, saatlik güncellemelerde `coordination.yml` Pages'e güncel `site/` içeriğini yayınlayacak. Yayın ancak `deploy-pages` adımı başarılı ve sayfa erişilebilir olduğunda onaylanabilir.
- Vercel bağlantısı erişim yetkisi yüzünden burada yapılandırılamadı; daha önce bildirilen `https://makine-core-lab.vercel.app/` yeni sürüm için doğrulanmış URL değildir.

**Ücretli AI araştırma:** `makine/agent.py` kodu + sınırlandırılmış çıktı şeması hazır fakat `MAKINE_AI_ENABLED=true` Actions variable ve `OPENAI_API_KEY` Actions secret olmadan açılmaz. Gizli değeri sohbet, dosya veya siteyle paylaşma. AI açık olsa da diğer ChatGPT/Codex oturumları başlatılmaz ve kaynak repo değişikliği, sinyal veya emir üretilmez.

**GitHub kanıtlar:**
- Koordinatör kodu, testler, site ve Pages tespit işi başarılı: https://github.com/onurqlp/makine-core/actions/runs/39110910481
- Saatlik botun ilk gerçek görev yorumu: https://github.com/onurqlp/makine-core/issues/1#issuecomment-6247388866
- Değişen duruma göre takip yorumu: https://github.com/onurqlp/makine-core/issues/1#issuecomment-6247441307


## GitHub Pages ilk gerçek yayın — 18 Ekim 2026

**Kullanıcı GitHub Pages'i etkinleştirdi; başarı doğrulandı.**

- Repo `has_pages=true` (GitHub public repository API).
- Kullanıcı onayı sonrası ilk dağıtımı tetiklemek için `site/.nojekyll` dosyası eklendi.
- Yayın workflow run: https://github.com/onurqlp/makine-core/actions/runs/39111561162
- Commit: `fc9908e18674cff6221461d7b6d7856cbb13c109`
- `research` işi **success**, sözleşme testleri **success**; `pages` işi **success** ve `Deploy Pages` adımı **success**.
- Deploy logu doğrudan `Reported success!` kaydetti; GitHub tarafından atanan üretim URL'si: **https://onurqlp.github.io/makine-core/**. Mobil panel: **https://onurqlp.github.io/makine-core/status.html**.
- Repo `site/` klasörü Pages artifact olarak yüklenir; GitHub Actions koordinasyon workflow'u her başarılı saatlik/günlük çalışmadan sonra yeniden Pages deploy etmeyi dener.
- Dış HTTP/telefon tarayıcısıyla bağımsız uçtan uca açılış testi bu oturumda tamamlanmadı; Pages API ve yayın logları ile doğrulanan nokta **dağıtım başarılı** durumudur.
- **AI araştırma modülü hâlen varsayılan kapalıdır**. GitHub Pages etkinleştirmek OpenAI API anahtarını, diğer sohbetlerdeki ajanları veya piyasa işlemlerini etkinleştirmez.
- Eski Vercel URL'si otomatik GitHub entegre değildir; güncel site adresi olarak Pages kullanılmalıdır.

> Önceki bölümlerdeki GitHub Pages kapalı/etkin değil ifadeleri, bu tarihli başarıdan **önceki** durumu anlatır.
