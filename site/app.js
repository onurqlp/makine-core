'use strict';
const $=id=>document.getElementById(id);
const fmt=iso=>{if(!iso)return "Zaman yok";const d=new Date(iso);return Number.isFinite(+d)?new Intl.DateTimeFormat("tr-TR",{timeZone:"Europe/Istanbul",dateStyle:"medium",timeStyle:"short"}).format(d):"Geçersiz zaman"};
const age=iso=>{let t=Date.parse(iso||"");return Number.isFinite(t)?(Date.now()-t)/60000:Infinity};
const label=s=>({FRESH:"GÜNCEL",PARTIAL:"KISMİ",STALE:"ESKİ",INVALID:"GEÇERSİZ",INVALID_TIME:"TARİH HATALI",UNAVAILABLE:"ERİŞİLEMİYOR",OBSERVING:"GÖZLEM VAR",BLOCKED_SOURCE:"GİRDİ EKSİK",DEGRADED:"KISITLI",HEALTHY:"SAĞLIKLI"})[s]||s||"BİLİNMİYOR";
function el(type,text,cls){let n=document.createElement(type);n.textContent=String(text??"");if(cls)n.className=cls;return n}
function stateNow(source,max){if(age(source?.observed_at_utc)>max)return "STALE";if(age(source?.observed_at_utc)<-5)return "INVALID_TIME";return source?.state||"UNAVAILABLE"}
async function load(name){const r=await fetch("./data/"+name+"?v="+Date.now(),{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status+" "+name);return r.json()}
function render(report,tasks){
  const coin=report.sources?.coinlive||{},alti=report.sources?.alti||{};
  const cstate=stateNow(coin,45),astate=stateNow(alti,120);
  $("health").textContent=cstate==="FRESH"&&astate==="FRESH"?"GÜNCEL":"KISITLI";
  $("coinState").textContent=label(cstate);$("altiState").textContent=label(astate);
  $("coinMeta").textContent="Piyasa anı: "+fmt(coin.observed_at_utc)+" · Kaynak: "+(coin.health_status||"doğrulanamadı");
  $("altiMeta").textContent="Tarama: "+fmt(alti.observed_at_utc)+" · "+(alti.provider_error_count||0)+" sağlayıcı uyarısı";
  const mbox=$("moduleGrid");mbox.replaceChildren();
  const mods=report.modules||[];
  $("working").textContent=String(mods.filter(m=>m.state==="OBSERVING"&&astate!=="STALE").length);
  for(const m of mods){
    let card=el("article","","module");
    const hdr=el("div","","modhead");
    hdr.append(el("span",m.id,"mid"),el("span",label(m.state),"chip "+(m.state==="OBSERVING"?"good":"warn")));
    card.append(hdr,el("h3",m.name),el("p",m.coinlive_support),
      el("div","ALTI durum: "+(m.source_strategy_status||"DOĞRULANAMADI"),"statusline"),
      el("div",m.state==="OBSERVING"?"Gerçekleşmiş veri yalnız bağlam için kullanılır.":m.blocker||"Veri bağlantısı doğrulanamadı.","detail"));
    mbox.append(card);
  }
  if(mods.length!==6)mbox.prepend(el("p","Altı modül sözleşmesi eksik!","error"));
  const feed=report.coinlive_feed||{};
  const good=feed.status==="LIMITED_CONTEXT"&&astate!=="STALE"&&cstate!=="STALE"&&cstate!=="INVALID"&&astate!=="INVALID";
  $("fundingBadge").textContent=good?"SALT OKUNUR":"GÜNCEL BAĞLAM YOK";
  $("fundingBadge").className="chip "+(good?"good":"warn");
  const box=$("fundingList");box.replaceChildren();
  const records=good?(feed.funding_event_context||[]):[];
  if(!records.length)box.append(el("p","İşlenebilir funding gözlemi bulunmuyor. Bu durum işlem kararı değildir.","muted"));
  for(const f of records){
    const item=el("div","","fundrow");
    const percentage=Number.isFinite(Number(f.last_realized_fraction_per_event))?(Number(f.last_realized_fraction_per_event)*100).toFixed(5)+"%":"Doğrulanmadı";
    item.append(el("b",f.symbol+" · "+f.venue),el("strong",percentage),
                el("small","Gerçekleşen olay: "+fmt(f.last_realized_time_utc)),
                el("small",f.interval_hours+" saatlik dönem · AL/SAT SİNYALİ DEĞİL"));
    box.append(item);
  }
  const list=$("taskList");list.replaceChildren();
  const open=tasks.open_tasks||[];$("taskCount").textContent=open.length+" açık";
  for(const task of open){
    const div=el("div","","task");
    div.append(el("b",task.title),el("p","Sorumlu: "+task.owner+" · "+task.next_step));list.append(div);
  }
  if(!open.length)list.append(el("p","Şu anda kayıtlı bir girdi engeli yok.","muted"));
  const stale=age(report.generated_at_utc)>90;
  $("lastRun").textContent="Son MAKİNE çalışması: "+fmt(report.generated_at_utc)+" · "+
     (stale?"RAPOR ESKİ":(report.runtime?.trigger==="schedule"?"GitHub zamanlayıcısı":"Tetikleme: "+(report.runtime?.trigger||"BELİRSİZ")));
  if(stale){$("working").textContent="—";$("health").textContent="RAPOR ESKİ";}
}
let loading=false;async function refresh(){if(loading)return;loading=true;$("refresh").disabled=true;try{
  const [report,tasks]=await Promise.all([load("support.json"),load("tasks.json")]);
  if(report.schema!=="makine-coinlive-support-v2"||report.module_count!==6)throw Error("Support schema mismatch");
  render(report,tasks);
 }catch(err){
  $("moduleGrid").replaceChildren(el("p","Güncel altı modül raporu alınamadı. Yanlış ya da eski sinyal gösterilmiyor.","empty"));
  $("working").textContent="—";$("health").textContent="VERİ YOK";
  $("fundingList").replaceChildren(el("p","Bağlam doğrulanamadı.","muted"));
  $("taskList").replaceChildren(el("p","Görev kaynağına erişilemedi.","muted"));
  console.error("MAKINE support unavailable",err);
 }finally{loading=false;$("refresh").disabled=false}}
$("refresh").addEventListener("click",refresh);
refresh();
