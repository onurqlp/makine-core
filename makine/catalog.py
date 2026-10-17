"""57 model registry. Names/IDs preserve the Coin.Live research catalogue.

Seed metadata is internal research classification, not validated project income.
The remote catalogue is read-only and used to verify exact names/source lineage.
"""
import re

CORE = [
"Funding farkı & delta-nötr taşıma",
"Spot–vadeli cash & carry",
"Borsalar arası spot arbitrajı",
"Üçgen kur arbitrajı",
"Piyasa yapıcılığı / spread stratejisi",
"DeFi oran farkı tarayıcısı",
"Likid staking / stake havuzu",
"Doğrulayıcı (validator) işletme servisi",
"Blockchain RPC / indeksleme API'si",
"DePIN / bant genişliği paylaşım düğümü",
"Bulut kapasite arbitrajı",
"CPU batch işleme pazarı",
"AI API geçidi / inference broker",
"Otomatik PDF / dosya işlem API'si",
"Belge okuma / sınıflandırma motoru",
"Webhook yeniden deneme altyapısı",
"Site formu / ödeme kontrol robotu",
"API kota / maliyet koruma yazılımı",
"Küçük WordPress eklenti fabrikası",
"Chrome eklenti / mikro otomasyon",
"Ücretli niş veri API'si",
"İhale / uyum değişikliği alarmı",
"Fiyat trendi ve rakip izleme servisi",
"Sektörel gösterge / endeks API'si",
"Otomatik hesaplayıcı / mikro ürün ağı",
"Gelirli dijital varlık satın alma",
"Niş B2B benchmark rapor aboneliği",
"Ücretli alarm / olay motoru",
"Sistematik kupon / promosyon fark analizörü",
"Arama trafikli otomatik karşılaştırma ağı",
]
FINANCIAL = [
"Perpetual funding farkı — iki borsa",
"Spot A / perpetual B çapraz basis",
"CEX–DEX fiyat arbitrajı",
"DEX–DEX aynı zincir arbitrajı",
"Zincirler arası köprü fiyat farkı",
"Stablecoin fiyat sapması arbitrajı",
"Perpetual funding vadesi/interval farkı",
"Kripto ödünç alma–verme spreadi",
"Likid staking token indirimi",
"Kripto opsiyon put–call parity",
"Kripto opsiyon volatilite farkı",
"Borsa endeksi–vadeli sözleşme basis",
"Borsa hisseleri pairs trading",
"ETF–NAV primi/iskontosu",
"ETF–ETF göreli değer farkı",
"Opsiyon put–call parity — pay piyasası",
"ADR / çift borsada işlem gören hisse",
"Takvim spreadi — farklı vadeli futures",
"Temettü / birleşme özel durum stratejisi",
"Döviz üçgen çapraz kur karşılaştırması",
"Döviz forward / faiz paritesi farkı",
"Altın fiyat paritesi ve yerel prim",
"Emtia ETF / vadeli / spot fiyat ilişkisi",
"İstatistiksel sepet / cointegration stratejisi",
"Tahvil–repo finansman farkı",
"Opsiyon sentetik forward / conversion reversal",
"Kapalı uçlu fon iskontosu takibi",
]
assert len(CORE) == 30 and len(FINANCIAL) == 27

# Engine ownership is the primary view. Exactly one owner per model.
API_IDS = {9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 24, 25}
VENTURE_IDS = {8, 10, 11, 12, 22, 23, 26, 27, 28, 29, 30}
STRATEGY_IDS = {1, 2, 3, 4, 5, 6, 7, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57}
assert len(API_IDS | VENTURE_IDS | STRATEGY_IDS) == 57
assert not(API_IDS & VENTURE_IDS or API_IDS & STRATEGY_IDS or VENTURE_IDS & STRATEGY_IDS)

# These are prioritization hypotheses, not proven winners or revenue claims.
PILOT = {21:('A',85, 'Önce veri ürününün lisans ve müşteri talebini doğrula.'),
         17:('A',81,'Form/ödeme izleme için hedef müşteriyle pilot yap.'),
         16:('A',79,'Yüksek değerli webhook hatalarında ücretli müşteri ihtiyacını sınama.'),
         14:('A',77,'Tekrarlanan dosya işlemini API hizmetine dönüştürme talebini ölç.'),
         13:('A',74,'AI API aracı olarak maliyet avantajı ve talebi doğrula.'),
         19:('A',72,'Bakımı düşük tek WordPress eklentisiyle pilot yap.'),
         27:('B',68,'B2B rapor müşterileriyle ücretli talebi doğrula.'),
         28:('B',67,'Alarm kullanımını değil, ödeme istekliliğini ölç.'),
         24:('B',66,'Veri yeniden dağıtım lisansını incele.'),
         31:('B',64,'Net funding ve çift bacak maliyetleri doğrulanmadan işlem yok.'),
         36:('B',60,'Eşzamanlı derinlik ve transfer maliyeti gerekir.'),
         37:('B',59,'Settlement interval ve gerçek fonlama farkını doğrula.'),
         43:('B',57,'Hisse veri lisansı ve borrow maliyeti gerekir.'),
         45:('B',57,'NAV, temettü ve short erişimini doğrula.'),
         54:('B',56,'Out-of-sample model ve çoklu bacak gerekir.'),
         55:('B',54,'Repo dealer fiyatı ve teminat şartları gerekir.')}

ALI_ID={31:'B1',36:'B2',43:'A1',45:'A2',54:'A3',55:'T0'}

def engine_for(i):
    if i in API_IDS:return 'DATA_API'
    if i in VENTURE_IDS:return 'REVENUE_VENTURE'
    if i in {1,2,3,4,5,6,7,31,32,33,34,35,36,37,38,39}:return 'MARKET_INTEL'
    return 'STRATEGY_DISCOVERY'

def registry():
    entries=[]
    for i,name in enumerate(CORE+FINANCIAL,1):
        tier,score,next_step=PILOT.get(i,('C' if i>=31 else 'B',42 if i>=31 else 53,'Araştırma, maliyet ve erişim koşulları doğrulanmalı.'))
        group='PİYASA FIRSATI' if i in STRATEGY_IDS else ('VERİ & YAZILIM' if i in API_IDS else 'TİCARİ MODEL')
        entries.append({'id':i,'code':f'M-{i:02d}','name':name,'engine':engine_for(i),'category':group,
             'tier':tier,'research_priority_score':score,'priority_is_profit_probability':False,
             'status':'CATALOG_ONLY','validated_revenue_try':None,'estimated_revenue_try':None,
             'verified_customers':0,'decision':'RESEARCH','next_step':next_step,
             'related_alti':ALI_ID.get(i), 'origin':'COINLIVE_57_ID_SEED'})
    return entries

# Strict ID+name parse, no evaluation of remote JavaScript and no script execution.
PAIR_PATTERN = re.compile(r'''(?:\{|,)\s*["']?id["']?\s*:\s*(\d+)\s*,\s*["']?name["']?\s*:\s*(["'])(.*?)\2''',re.DOTALL)
def parse_source_names(js):
    return {int(m.group(1)):m.group(3) for m in PAIR_PATTERN.finditer(js)}


def parse_source_details(js):
    """Extract non-executable descriptive fields from the source JS catalogue.

    This deliberately does not call eval, node, or execute remote JavaScript.
    A field that cannot be parsed stays absent, never guessed.
    """
    import json
    matches=list(PAIR_PATTERN.finditer(js))
    text_keys=('simple','buyer','money','build','obstacle','pilot','kill','example','tag','cat','tier')
    numeric_keys=('capital','ops','risk','auto')
    out={}
    for ix,match in enumerate(matches):
        block=js[match.end():matches[ix+1].start() if ix+1<len(matches) else len(js)]
        doc={'id':int(match.group(1)),'name':match.group(3)}
        for key in text_keys:
            pattern=re.compile(r'(?:^|,)\s*["\']?'+key+r'["\']?\s*:\s*"((?:\\.|[^"\\])*)"',re.DOTALL)
            found=pattern.search(block)
            if found:
                try:doc[key]=json.loads('"'+found.group(1)+'"')
                except ValueError:pass
        for key in numeric_keys:
            found=re.search(r'(?:^|,)\s*["\']?'+key+r'["\']?\s*:\s*(\d+(?:\.\d+)?)',block)
            if found:doc[key]=float(found.group(1))
        out[doc['id']]=doc
    return out
