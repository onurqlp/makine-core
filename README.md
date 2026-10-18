# MAKİNE — Bağımsız COIN.LIVE Destek Motoru

MAKİNE yalnız **ALTI A1, A2, A3, B1, B2, T0** modüllerini ve COIN.LIVE'a salt-okunur destek veri paketini yönetir. Eski 57 gelir fikri, beş genel araştırma motoru, gelir hesaplayıcısı, AI deneyleri ve genel amaçlı iş laboratuvarı kaldırılmıştır.

**Site:** https://onurqlp.github.io/makine-core/

**Canlı olmayan kaynaklar çalışma sonucu gibi gösterilmez.** Modüller çalıştırılır; veri yeterliyse gözlem, yoksa BLOCKED_SOURCE üretir. B1, OKX doğrulanmış geçmiş funding gözlemlerini çevrimiçi kaynak uygun olduğunda aktarabilir. Kârlılık, sinyal, emir, spread avantajı veya hedge güvenliği asla varsayılmaz.

## İşletim
- Saatlik: `.github/workflows/support.yml` GitHub Actions; cron best-effort.
- Kaynaklar: `onurqlp/alti-quant-lab/site/report.json` ve `onurqlp/coin-live-pro/web/data/{v4-manifest,v4-radar,health}.json` — immutable commit ve SHA doğrulaması.
- Ekran: `site/index.html`.
- Durum: `site/data/support.json`.
- COIN.LIVE'ın **ayrıca okuyup bağlaması gereken** aktarım: `site/data/coinlive-support.json`. Bu çıktının varlığı COIN.LIVE'ın onu tükettiğini kanıtlamaz.
- Tarihli son 672 saatlik (maksimum) çalışma kaydı: `data/support-history.json`.
- Yerel test: `python -m unittest discover -s tests -q`.
- Gerçek emir, sanal emir, kaynak repo güncellemesi, farklı kasa birleştirme, otomatik işlem sinyali ve otomatik kod ajanı yok.

Değişiklikler yalnız MAKİNE deposunda gerçekleştirilir. ALTI ve COIN.LIVE strateji/sinyal/ledger/sürüm kodları değişmez. Kaynak erişim hatası `UNAVAILABLE` olarak korunur. Çıktı istatistiksel strateji doğrulaması veya finansal tavsiye değildir.
