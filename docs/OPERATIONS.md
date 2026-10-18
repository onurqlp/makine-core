# İşletim ve güncelleme

Üretim: https://onurqlp.github.io/makine-core/ · `onurqlp/makine-core`

1. `.github/workflows/support.yml` GitHub cron `17,47 * * * *` ile çalışmayı dener; gecikmeler mümkündür. Commit ve manuel çalıştırma otomatik cron kanıtı değildir.
2. `python -m makine.bridge`: altı girdiyi salt-okunur doğrula, `site/data/support.json` ve `site/data/coinlive-support.json` üret, kendi `data/support-history.json` günlüğüne kaydet.
3. `python -m makine.tasks`: `site/data/tasks.json` güncelle; yalnız durum değişiminde MAKİNE issue #1'e sınırlı bildirim yap.
4. Python birim testleri, node JS sözdizimi ve emir/çapraz yazım yasağı testini geçir.
5. Yalnız MAKİNE'nin dört çıktı JSON'unu commit et; Pages'e `site/` paketini dağıt. Diğer depolara yazma.
6. Arıza halinde GitHub Actions logu, `support.json` kaynak zamanı ve `tasks.json` kayıtlarına bak. Asla veri eksikliğinde kâr veya al/sat sinyali gösterme.

Kullanıcı onayı olmadan COIN.LIVE motoru veya ALTI stratejisi değiştirilmez. Yeni AI hesabı/token/ücretli agent gerekmiyor; salt-okunur motor bağımsızdır. Eski modüller git geçmişinde kalabilir ama güncel `main` ağacından kaldırılmıştır.
