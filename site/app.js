'use strict';
(function(){
  const $=id=>document.getElementById(id);
  const nf=new Intl.NumberFormat('tr-TR',{maximumFractionDigits:0});
  const time=v=>{if(!v)return 'Henüz kayıt yok';const d=new Date(v);return Number.isFinite(+d)?d.toLocaleString('tr-TR',{timeZone:'Europe/Istanbul',year:'numeric',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}):'Tarih bilinmiyor'};
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const engineNames={MARKET_INTEL:'Piyasa',STRATEGY_DISCOVERY:'Strateji',PERFORMANCE_RISK:'Performans',DATA_API:'Veri/API',REVENUE_VENTURE:'Gelir modeli'};
  const engineIcons={MARKET_INTEL:'⌁',STRATEGY_DISCOVERY:'◇',PERFORMANCE_RISK:'◈',DATA_API:'▣',REVENUE_VENTURE:'↗'};
  const tierNames={A:'İLK ARAŞTIR',B:'SIRADAKİ',C:'UZUN VADE'};
  let models=[],topIds=[],listLimit=12,release={};
  const sourceRepo='https://github.com/onurqlp/coin-live-pro';
  function drawEngines(engines){
    const ownCount=id=>models.filter(m=>m.engine===id).length;
    $('engineGrid').innerHTML=engines.map((e,i)=>`<article class="engine-card"><div class="engine-head"><span class="engine-n">MOTOR ${String(i+1).padStart(2,'0')} / ${e.id==='PERFORMANCE_RISK'?'ORTAK DENETİM':ownCount(e.id)+' MODEL'}</span><span class="engine-icon" aria-hidden="true">${engineIcons[e.id]||'◇'}</span></div><h3>${esc(e.name)}</h3><p>${esc(e.plain)}</p><div class="engine-foot">${e.id==='PERFORMANCE_RISK'?'TÜM MODELLERE UYGULANIR':e.handoff==='NOT_APPLICABLE'?'BAĞIMSIZ TİCARİ ARAŞTIRMA':'ARAŞTIRMA ÇIKTISI ÜRETİR'}</div></article>`).join('');
  }
  function filtered(){const q=$('searchInput').value.trim().toLocaleLowerCase('tr-TR'),eng=$('engineSelect').value,tier=$('tierSelect').value;
    return models.filter(m=>(!q||[m.name,m.code,m.category,m.next_step,m.engine,m.related_alti,...Object.values(m.original_catalogue||{})].some(x=>String(x||'').toLocaleLowerCase('tr-TR').includes(q)))&&(eng==='ALL'||m.engine===eng)&&(tier==='ALL'||m.tier===tier))
      .sort((a,b)=>b.research_priority_score-a.research_priority_score||a.id-b.id);
  }
  function renderModels(){const rows=filtered(),shown=rows.slice(0,listLimit);$('matchCount').textContent=`${rows.length} MODEL`;
    $('modelGrid').innerHTML=shown.map(m=>`<article class="model-card"><div class="model-head"><span class="model-code">${esc(m.code)} / ${esc(engineNames[m.engine]||m.engine)}</span><span class="tier tier-${m.tier}">${tierNames[m.tier]}</span></div><h3>${esc(m.name)}</h3><p>${esc(m.next_step)}</p><div class="model-foot"><small>ÖNCELİK: ${m.research_priority_score}/100*</small><button type="button" data-model="${m.id}" aria-label="${esc(m.name)} detayını aç">Detayları gör ↗</button></div></article>`).join('')||'<div class="empty">Bu aramada eşleşen fikir yok. Arama veya filtreyi temizle.</div>';
    $('showMore').hidden=rows.length<=12;
    $('showMore').textContent=listLimit>=rows.length?'İlk 12 modeli göster ↑':`Diğer ${rows.length-shown.length} modeli göster ↓`;
    $('showMore').setAttribute('aria-expanded',String(listLimit>=rows.length));
  }
  function detail(id){const m=models.find(x=>x.id===id);if(!m)return;const cat=m.original_catalogue||{};
    const sector=m.engine==='DATA_API'?'Bir hizmet veya API müşterisi ücret öderse gelir oluşabilir.':m.engine==='REVENUE_VENTURE'?'Gerçek müşteri veya hizmet satışına ihtiyaç vardır.':'Fiyat farkı veya piyasa getiri hipotezidir; risksiz ve kesin kazanç değildir.';
    const block=(title,txt)=>`<div class="detail-block"><b>${esc(title)}</b><p>${esc(txt||'Kaynak kataloğundan ayrıntılı açıklama henüz içe aktarılmadı. Bu model için doğrulanmış kanıt bulunmuyor.')}</p></div>`;
    $('modelDetail').innerHTML=`<div class="dialog-main"><span class="model-code">${esc(m.code)} · ${esc(engineNames[m.engine])}</span><h2>${esc(m.name)}</h2><span class="tier tier-${m.tier}">${tierNames[m.tier]}</span><p class="dialog-intro">Bu bir araştırma fikridir. Öncelik puanı gelir, kazanma ihtimali veya sinyal isabeti değildir.</p>${block('01 / Bu nedir?',cat.simple||sector)}${block('02 / Kim para öder?',cat.buyer|| (m.category==='PİYASA FIRSATI'?'Müşteri gelir modeli değil; kendi sermayesiyle piyasa hipotezi.':'Müşteri profili pilotla doğrulanmalı.'))}${block('03 / Para nereden gelir?',cat.money||sector)}${block('04 / Nasıl kurulabilir?',cat.build||m.next_step)}${block('05 / En büyük engel ve risk',cat.obstacle||'Maliyet, veri kalitesi, erişim ve uygulama riski doğrulanmadı.')}${block('06 / İlk pilot',cat.pilot||m.next_step)}${block('07 / Ne zaman vazgeçeriz?',cat.kill||'Gerçekçi giderlerden sonra avantaj veya müşteri talebi yoksa pilot durdurulur.')}${cat.example?block('08 / Kaynaktaki açıklayıcı örnek (tahmin değil)',cat.example):''}${block('Bugünkü karar',`Durum: ${m.evidence?.stage||'CATALOG_ONLY'}. Doğrulanmış müşteri geliri: bağlı değil. Önerilen sonraki adım: ${m.next_step}`)}<a class="detail-link" href="${sourceRepo}/tree/main/web/fikir-laboratuvari" target="_blank" rel="noopener">57 modelin kaynak kataloğunu aç ↗</a></div>`;
    const d=$('modelDialog');if(d.showModal)d.showModal();else d.setAttribute('open','');
  }
  function renderSource(snapshot){const src=snapshot.source||{};
    const badge=$('sourceBadge');
    const valid=src.source_integrity==='VERIFIED';
    let old=false;
    if(src.snapshot_finished_at_utc){const age=(Date.now()-new Date(src.snapshot_finished_at_utc).getTime())/60000;old=!Number.isFinite(age)||age>45||age<-5;}
    badge.textContent=valid?(old?'Kaynak doğrulandı · veri artık eski':'Kaynak bütünlüğü doğrulandı'):(src.state==='REFRESH_FAILED'?'Veri alma başarısız':'İlk veri eşleşmesi bekleniyor');
    badge.className='source-status '+(valid&&!old?'good':src.state==='REFRESH_FAILED'?'error':'');
    $('sourceTime').textContent=time(src.snapshot_finished_at_utc);
    $('importTime').textContent=time(src.imported_at_utc);
    $('sourceHealth').textContent=src.source_health_status||src.state||'Bağlı değil';
    const parts=[];if(src.warnings?.length)parts.push(src.warnings.join(' · '));if(src.message)parts.push(src.message);
    parts.push(valid?'Kaynak kayıtları salt okunur; COIN.LIVE ile aynı kasa değildir.': 'İlk gerçek kaynak okumada veriler ve tarih bilgisi doğrulanacak.');
    $('sourceWarning').textContent=parts.join(' ');
    $('lastMarket').textContent=time(src.snapshot_finished_at_utc);
    $('lastResearch').textContent=time(snapshot.generated_at_utc);
  }
  function updateHistory(rows){$('updateList').innerHTML=rows.length?rows.slice(0,8).map(x=>`<div class="update-row"><strong>${esc(time(x.time_utc))} · ${esc(x.state)}</strong><small>Yapı: ${esc(x.build_id)} · Kaynak: ${esc((x.source_sha||'Henüz yok').slice(0,10))} · Ürün sürümü: ${esc(x.published_product_version)} (değişmedi)</small></div>`).join(''):'<p class="empty">Henüz kaynak araştırması çalıştırılmadı.</p>'}
  function renderRelease(r){$('productVersion').textContent=r.product_version==='UNASSIGNED'?'Henüz atanmadı':r.product_version;
    $('buildId').textContent=r.build_id||'—';$('buildDate').textContent=(r.updated_date||'').split('-').reverse().join('.');
    $('versionProposal').textContent=(r.recommended_version||'—')+' · Onay bekliyor';
    $('releaseStamp').textContent=r.build_id||'MAKİNE CORE';
    $('footerRelease').textContent=(r.build_id||'BUILD')+' · '+(r.updated_date||'Tarih yok');
  }
  function calculator(){const val=id=>Math.max(0,Math.min(1e9,Number($(id).value)||0));const users=Math.floor(val('customers')),price=val('price'),fixed=val('fixed'),variable=val('variable');const gross=users*price,expense=fixed+users*variable,net=gross-expense;
    const fmt=n=>(n<0?'−':'')+nf.format(Math.abs(n))+' ₺';
    $('netResult').textContent=(net>0?'+':'')+fmt(net);$('netResult').classList.toggle('negative',net<0);
    $('grossResult').textContent=fmt(gross);$('costResult').textContent=fmt(expense);
    $('breakEven').textContent=price<=variable?'Birim katkı yok':nf.format(Math.ceil(fixed/(price-variable)))+' müşteri';
  }
  function bind(){['searchInput','engineSelect','tierSelect'].forEach(id=>$(id).addEventListener('input',()=>{listLimit=12;renderModels()}));
    $('showMore').addEventListener('click',()=>{const total=filtered().length;listLimit=listLimit>=total?12:total;renderModels()});
    $('modelGrid').addEventListener('click',ev=>{const t=ev.target.closest('[data-model]');if(t)detail(Number(t.dataset.model))});
    $('dialogClose').addEventListener('click',()=>$('modelDialog').close());
    $('modelDialog').addEventListener('click',ev=>{if(ev.target===$('modelDialog'))$('modelDialog').close()});
    ['customers','price','fixed','variable'].forEach(id=>$(id).addEventListener('input',calculator));calculator();
  }
  async function getJSON(url){const res=await fetch(url,{cache:'no-store'});if(!res.ok)throw Error(`HTTP ${res.status} (${url})`);return res.json()}
  async function init(){bind();try{
       const [report,rel,hist]=await Promise.all([getJSON('./data/report.json'),getJSON('./data/release.json'),getJSON('./data/update-history.json')]);
       models=report.models||[];topIds=report.focus_ids||[];
       $('totalModels').textContent=String(models.length);$('totalEngines').textContent=String((report.engines||[]).length);$('topModels').textContent=String(topIds.length);
       $('actualIncome').textContent='—';$('incomeDesc').textContent='Ödeme kaynağı bağlı değil';
       drawEngines(report.engines||[]);renderModels();renderSource(report);renderRelease(rel);updateHistory(hist||[]);
    }catch(err){$('modelGrid').innerHTML='<div class="empty">Araştırma raporu yüklenemedi. İnternet bağlantısı veya site yayınını kontrol edin. Sahte veri gösterilmiyor.</div>';
       $('engineGrid').innerHTML='<div class="empty">Motor durumları rapordan yüklenemedi.</div>';console.error('MAKİNE source unavailable:',err);
    }}
  init();
})();
