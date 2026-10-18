# MAKİNE — Altı Modül Üretim Sınırları

Bu depo, COIN.LIVE için ayrı ve salt-okunur destek hizmetidir; genel gelir fikri laboratuvarı değildir.

Tek izinli çalışma kümesi **A1, A2, A3, B1, B2, T0**. `makine/bridge.py` her birini kontrol eder, `site/data/support.json` üretir ve destek paketini `site/data/coinlive-support.json` olarak yayımlar.

- ALTI ve COIN.LIVE kaynak depolarına **yazma**; yalnız izinli kamuya açık JSON GET.
- Sinyal, trade, real/paper order, para transferi, sanal pozisyon, PnL, otomatik model terfisi, strateji policy veya kasa birleştirme **yasak**.
- Kontroller veri yoksa BLOCKED_SOURCE üretir, uydurma olumlu gözlem yapmaz.
- Yardım dosyasının yayımlanması COIN.LIVE'ın onu kendiliğinden kullandığı anlamına gelmez; tüketici adaptörünü yalnız ayrı proje onayıyla ekle.
- GitHub Actions gerçek schedule çalışmasının kanıtı `event=schedule` olmalıdır; push tetikleri bu değildir.
- Ürün/strateji sürümleri onaysız değiştirilemez. Gizli anahtarlar asla GitHub Pages'e çıkmaz.
