# COIN.LIVE PRO — MAKİNE CORE entegrasyonu için ayrı uygulama promptu

> **BU BİR TALİMAT TASLAĞIDIR.** MAKİNE CORE kurulumu COIN.LIVE PRO'yu değiştirmez. Bu metin yalnız kullanıcı ayrı COIN.LIVE güncellemesi başlatıp açıkça onay verince uygulanır.

## Kullanıma hazır prompt

Sen COIN.LIVE PRO'nun GitHub deposundan (`onurqlp/coin-live-pro`) sorumlu uzman full-stack/quant mühendissin. COIN.LIVE'ın mevcut ana sürümünü, canlı çalışan OKX kolektörünü, V4 radarını, 7 araştırma dedektörünü, ayrı strict/early sanal hesaplarını, geri dönük gözlem arşivlerini ve 6 kullanıcı ekranını EKSİLTMEDEN koru. Sürüm numarasını asla otomatik artırma; yalnız kullanıcı açıkça onay verirse değiştir. Her değişikliği benzersiz build kimliği ve tarihle kaydet.

MAKİNE CORE bağımsız repodan gelecek araştırma dışa aktarımı `site/data/coinlive-handoff.json` (MAKİNE deposu) veya yayınlanan read-only site `/data/coinlive-handoff.json` üzerinden okunabilecek; bağlayıcı yalnızca **GET** yapabilir. Önce MAKİNE'nin GitHub deposunun gerçekten var olduğunu, public ham veri veya yayın URL'sinin doğru olduğunu doğrula; isim veya URL tahmin edip canlı sisteme bağlama.

Entegrasyon SÖZLEŞMESİ:

1. `schema=makine-coinlive-research-handoff-v1` bekle. Bilinmeyen `schema` durumunda REDDET.
2. `source_commit_sha`, `source_scan_id`, `generated_at_utc`, `source_integrity`, `source_fresh_at_import` kontrol et. Yanlış/eksik/eskimiş veri REDDET; eski raporu yeni diye gösterme.
3. `can_promote_to_live_signal=false`, `can_modify_live_policy=false`, `can_execute_orders=false`, `can_modify_coins_live_ledger=false`, `new_trade_candidates=[]` sözleşmeleri değiştirilemez. Bu alanlardan herhangi biri diğer değerdeyse entegrasyonu REDDET.
4. COIN.LIVE kendi verisinin MAKİNE'den geri dönen kopyasını ikincil bilgi olarak görür; döngüsel sinyal onay mekanizması KURMA. MAKİNE'nin öncelik puanı (`research_priority_score`) olasılık ya da işlem kalitesi ölçüsü değildir.
5. Yalnız `MAKİNE Araştırması` başlıklı, basit/ayrıntılı geçişli yeni read-only bir sekme ekle. COIN.LIVE'ın 7 mevcut strateji motoru, pozisyon açma kuralları, sanal bakiyeleri, işlem maliyetleri veya bildirim tetikleri otomatik değişmesin.
6. Aynı raporun eski tarihli kopyası tekrar görünürse deduplikasyon yap. Geçmiş arşiv verilerini silme; `main` üzerine force-push yapma.
7. Kullanıcı açıkça ayrı bir yükseltmeyi onaylamadıkça MAKİNE raporundan COIN.LIVE işlem stratejisi, giriş filtresi veya paper-fill üretme.
8. Yeni bölüm telefon ekranında yatay taşmayacak; son kaynak zamanı, MAKİNE yayın zamanı, güncellik, kaynak SHA kısa gösterimi ve risk uyaranı gözle görünür olacak.
9. Projeye test ekleme/değiştirme gerekiyor ise yalnız COIN.LIVE güncellemesi için uygun CI ve gerçek site doğrulamasını çalıştır. Kapanmış mum, kaynak `scan_id`, veri kalitesi, işlem sırası ve eş zamanlılık ilkelerini koru.
10. **Gerçek parasal emir, exchange API key, cüzdan, transfer, kullanıcı ödeme veya otomatik işlem bağlantısı ekleme.**

Önce mevcut COIN.LIVE `main` ve MAKİNE çıktısı üzerinde değişiklik etkisi raporu ver. Kullanıcı ayrı bir COIN.LIVE GO komutu verdiğinde sürümü yükseltmeden entegrasyon kodunu yayınla. Başarılı canlı yayın URL'sini, kullanılan commit'i, son kaynak tarihini ve eklenen tek ekranı raporla.

## Önerilen ekran metni

`MAKİNE Araştırması` → `İlk bakışta: bize ne öneriyor?` → `Kanıt nedir?` → `Bu işlem sinyali mi? HAYIR` → `Geliştiricinin inceleyeceği öneriler` → `Kaynak ve tarih`.
