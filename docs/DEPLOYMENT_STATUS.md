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
