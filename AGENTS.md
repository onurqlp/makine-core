# MAKİNE — Altı Modül Yardım Motoru

Bu repo artık yalnız **COIN.LIVE bağımsız altı strateji destek servisidir**. Başka iş modeli veya genel araştırma kataloğu ekleme. Kullanıcının yönlendirmesiyle bunlar kaldırıldı.

Kaynak depolar **salt-okunur**:
- ALTI: https://github.com/onurqlp/alti-quant-lab
- COIN.LIVE: https://github.com/onurqlp/coin-live-pro

Görev kimlikleri: **A1 / A2 / A3 / B1 / B2 / T0**. Bu kimlikleri veya ALTI'nın strateji anlamlarını değiştirme.
Sahibi MAKİNE olan ve yalnız bu depoda çalışan dosyalar `makine/bridge.py`, `makine/tasks.py`, `site/`, `.github/workflows/support.yml`, `data/support-history.json`.

Sert güvenlik:
- Sinyal, entry/exit, paper fill, gerçek alım-satım, API key sızıntısı, çapraz depoya kod yazma, kasaları birleştirme **yasak**.
- Her kaynak immutable 40 karakter SHA ile sabitlenmeli; hash, scan ID ve gerçek UTC kaynak zamanı gerekir. Stale veya yarım kaynak eyleme yükseltilemez.
- B1'de yalnız **gerçekleşmiş** funding oranı bağlam olabilir, tek borsa farkı arbitraj kanıtı sayılamaz. Finansal kazanç iddiası yok.
- Altı modülün veri sağlamadığını saklama; ALTI'nın gerçek statüsüne sadık kal.
- MAKiNE'nin üretimi COIN.LIVE'ı otomatik değiştirmez. COIN.LIVE tarafındaki tüketici değişiklikleri o projenin yetkili ajanının ayrı çalışmasıdır.
- Görev kayıtları yalnız MAKİNE issue #1'e durum değişiminde yazılabilir; başka repo/issue otomatik değiştirilmez.

Test: `python -m unittest discover -s tests -q`. Yayın GitHub Actions ve GitHub Pages ile. Tüm finansal/strateji taslakları eski yapıya ait ve bu depoda tekrar yer almamalıdır.
