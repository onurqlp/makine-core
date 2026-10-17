# Önceden onaylı pilot ve değişmez kayıt politikası

MAKİNE temel ürün olarak 57 araştırma fikrini gösterir; herhangi bir ticari modelde müşteri, maliyet, ödeme ve talep doğrulanmadan **gelir kaydı açmaz**.

## Deney statüleri

`CATALOG_ONLY` → `RESEARCH_PLANNED` → `APPROVED_PILOT` → `RUNNING` → `OBSERVED` → `ACCEPTED/REJECTED`.

Geçmişe dönük başarılı olayları seçerek geçmiş kararı değiştirmek yasaktır. `approved_at_utc` ve tüm kararlar kullanıcı onayından sonraki zamanı göstermelidir. Ürün sürümü yalnız kullanıcı tarafından artırılır. Geriye dönük çalışma `BACKTEST` / `RETROSPECTIVE` olarak işaretlenmeli; `FORWARD` olarak sunulmamalıdır.

## Gelir matematiği

Brüt faturalandırılan (örnekte müşteri sayısı × fiyat) − altyapı sabit gideri − müşteri başına değişken gider = **varsayımsal katkı**. Vergi, pazarlama, ücret iadesi, tahsil edilememe, müşteri edinme maliyeti ve diğer giderleri içermez. Gerçek net kâr değildir. Verilen varsayımsal birim ekonomi gerçek satış veya gerçek müşteri yaratmaz.

## Piyasa araştırması

COIN.LIVE açık sanal pozisyonları, geçmiş forward kayıtları ve gerçek para iddiaları MAKİNE'nin ticari geliri olarak kopyalanamaz. Mevcut Coin.Live kağıt hesap ile MAKİNE/ALTI referans bütçesi asla toplanamaz. Her strateji kendi yeni örneklemini ve örneklem yetersizliğini gösterir; manipülasyon iddiası veya garantili gelir yoktur.
