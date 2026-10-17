# MAKİNE CORE — Ajanlar Arası Koordinasyon (AGENTS.md)

Bu dosya yalnız bu repoda göreve başlayan kod/araştırma ajanları için kalıcı çalışma kılavuzudur. **Canlı çalışan başka ChatGPT/Codex ajanına doğrudan mesaj göndermez ve hiçbir ajanı otomatik başlatmaz.**

## Koordinasyon merkezleri

- MAKİNE master issue: https://github.com/onurqlp/makine-core/issues/1
- ALTI araştırma/devralma issue: https://github.com/onurqlp/alti-quant-lab/issues/1
- COIN.LIVE dış kaynak/read-only issue: https://github.com/onurqlp/coin-live-pro/issues/28

İlk adımda bu üç görevin güncel içeriğini ve kendi reponun README, docs/ARCHITECTURE.md, config/settings.json, docs/EXPERIMENT_POLICY.md dosyalarını oku. Güncel görev bilgisini tarihli issue mesajlarında tut. Issue yorumları mekanik olarak senkronize edilmez.

## Yetki sınırları

- MAKİNE = 57 fikir / 5 motor / araştırma düzlemi; bu repoda kal. `config/settings.json` içindeki `allow_cross_repo_writes=false`, `manual_research_only=true`, `live_orders_enabled=false` korunur.
- COIN.LIVE = kendi piyasa ve sanal kasa sisteminin tek sahibi. Başka ajan onun stratejisini, emir/sinyalini, ledger'ını, sürümünü değiştiremez.
- ALTI = A1/A2/A3/B1/B2/T0 altı stratejinin tek sahibi. 150.000 TRY varsayımsal referansı COIN.LIVE'ın 10.000 USDT sanal kasasıyla birleştirme.
- **Hiçbir sonuç otomatik canlı sinyal/gerçek işlem/paper fill veya para kazancı olamaz**. Ajan kendiliğinden başka depoya kod push etmez; ayrı kullanıcı onayı gerekir.
- Ürün sürümü ve release alanları ancak kullanıcının açık onayıyla güncellenir. Gizli anahtar, müşteri/ödeme verisi ve erişim token'ı public repo/site JSON'una konulmaz.

## Mevcut sözleşme

MAKİNE → COIN.LIVE geri bildirim dosyası: `site/data/coinlive-handoff.json` / `makine-coinlive-research-handoff-v1`. Bu **bir araştırma aktarımıdır**, COIN.LIVE'a sinyal vermez. `can_promote_to_live_signal=false`, `can_modify_live_policy=false`, `can_execute_orders=false`, `can_modify_coins_live_ledger=false` değişmeden kalır.

Fikir eşleştirmeleri: MAKİNE 31 → ALTI B1; 36 → B2; 43 → A1; 45 → A2; 54 → A3; 55 → T0. Eşleşme strateji doğrulaması değil, araştırma sınıflamasıdır.

Kaynak okuma sadece belge ve JSON GET yöntemiyle; her veri parçası `source_repo`, immutable `source_commit_sha`, `scan_id`, gerçek gözlem zamanı (UTC), import/generation zamanı (UTC), hash/doğrulama sonucu, tazelik ve kaynak lisansı/kalite uyarısını taşımalı. Zaman damgası yoksa güncel iddiası yok; boşluk varsa `UNKNOWN` veya `NOT_CONNECTED`. Repo commit zamanı market event zamanı değildir.

## İş akışı

1. Başlamadan önce issue'daki son görev/yanıt durumuna bak; önceki ajanın açık işini tekrar etme.
2. Gerekli girdileri salt-okunur doğrula, kaynak SHA ve gerçek UTC zamanlarını sabitle.
3. En az maliyetli değişikliği öner; bağımsız strateji/piyasa motorlarına dokunma. Aynı model için yinelenen iş açma.
4. Güncelleme raporunu ilgili issue'da paylaş: amaç; kullanılan kaynak SHA/scan ID; `PROPOSED|REVIEWED|USER_APPROVED|IMPLEMENTED|VERIFIED` statüsü; veri kalitesi; değiştirilen dosyalar; test kanıtı; açık risk; diğer ajandan istenen somut teslim.
5. Kullanıcı onayı veya gerçek veri kanıtı yoksa sonucu `RESEARCH_ONLY` tut, PnL veya gelir uydurma.
6. Bir sonraki ajan teslimi kabul etmeden önce `source_commit_sha`, şema, sayısal birimler, UTC ve bozulmama testini doğrular. Başarısızsa nedenini issue'ya yaz ve mevcut çalışan sistemi koru.

## İlk ortak araştırma kabul kriterleri

- MAKİNE katalog: 57/57 sabit model kimliği korunur.
- ALTI: altı modülün durumu ve `NOT_CONNECTED|WATCH_ONLY|SCREEN_ONLY|SOURCE_ERROR` gerekçesi ayrı kaydedilir.
- COIN.LIVE: manifest hash, source scan ve quality kontrol edilmeden `VERIFIED` denmez.
- Gerçek piyasa gözlemi, sentetik demo, ileri paper muhasebe ve ticari gelir birbirine karışmaz.
- Yeni bir entegrasyon, yalnız dokümantasyon ve issues ile *başlatılmış* sayılır; otomatik ajanlar arası mesajlaşma veya canlı cross-repo pipeline olarak sunulamaz.
