"""Six-source health queue; notification only to MAKİNE's own GitHub issue."""
import hashlib,json,os
from pathlib import Path
import urllib.request
from .bridge import ROOT,save_json,now_utc,STAMP

BOARD=ROOT/"site/data/tasks.json"
COMMENT_URL="https://api.github.com/repos/onurqlp/makine-core/issues/1/comments"
STATUS_NAMES={"BLOCKED_SOURCE":"GİRDİ EKSİK","OBSERVING":"VERİ OKUYOR"}

def task_list(report):
    result=[]
    for x in report.get("modules",[]):
        if x.get("state")!="OBSERVING":
            result.append({"id":"SIX_"+x["id"],"owner":"ALTI","module":x["id"],
                "level":"INPUT_BLOCKED","title":x["name"]+" — veri/giriş kontrolü",
                "next_step":"ALTI upstream eksik veri sözleşmesini tamamlamalı. MAKİNE kaynak depoya yazmaz.",
                "reason":x.get("blocker"),"requires_approval":True})
    coin=(report.get("sources") or {}).get("coinlive") or {}
    if coin.get("state")!="FRESH":
        result.append({"id":"COINLIVE_INPUT","owner":"COIN.LIVE","module":None,
              "level":"SOURCE_HEALTH","title":"COIN.LIVE sağlık / tazelik kontrolü",
              "next_step":"COIN.LIVE kendi iş akışındaki veri bütünlüğü ve cron durumunu kontrol etmeli.",
              "reason":coin.get("state"),"requires_approval":True})
    return sorted(result,key=lambda x:x["id"])

def make_board(report,previous=None):
    previous=previous or {}
    tasks=task_list(report)
    names={x["id"] for x in tasks}
    old={x.get("id") for x in previous.get("open_tasks",[]) if isinstance(x,dict)}
    sig=hashlib.sha256(("|".join(sorted(names))).encode()).hexdigest()[:20]
    return {"schema":"makine-six-tasks-v2","generated_at_utc":report["generated_at_utc"],
      "mission":"INDEPENDENT_COINLIVE_SUPPORT","open_tasks":tasks,
      "changes":{"new":sorted(names-old),"resolved":sorted(old-names)},
      "signature":sig,"last_notified_signature":previous.get("last_notified_signature"),
      "notification_required":sig!=previous.get("last_notified_signature"),
      "notification":{"state":"NOT_ATTEMPTED"},
      "target_issue":"https://github.com/onurqlp/makine-core/issues/1",
      "cross_repo_writes":False,"auto_fix_code":False,"auto_trading":False}

def notify(board,token="",sender=None):
    if not board["notification_required"]:
        board["notification"]={"state":"UNCHANGED"};return board
    if not token or os.getenv("GITHUB_REPOSITORY","onurqlp/makine-core")!="onurqlp/makine-core":
        board["notification"]={"state":"TOKEN_OR_SCOPE_MISSING"};return board
    lines=["<!-- MAKINE-SIX-BRIDGE "+board["signature"]+" -->",
           "## MAKİNE · altı modül destek durumu",
           "Bu otomatik kontrol kodu başka depolarda değiştirmez; emir/sinyal üretmez.",
           "**Yeni engeller:** "+(", ".join(board["changes"]["new"]) or "yok"),
           "**Düzelen engeller:** "+(", ".join(board["changes"]["resolved"]) or "yok"),
           "**Açık destek kontrolü:** "+(", ".join(t["id"] for t in board["open_tasks"]) or "yok"),
           "Kaynak çıktısı: https://github.com/onurqlp/makine-core/blob/main/site/data/support.json",
           "ALTI kodu ve COIN.LIVE kodu değişmedi."]
    data={"body":"\n\n".join(lines)}
    try:
        if sender is None:
            req=urllib.request.Request(COMMENT_URL,json.dumps(data).encode(),
                  {"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
                   "Content-Type":"application/json","User-Agent":"MakineSixBridge/2.0"},method="POST")
            with urllib.request.urlopen(req,timeout=20) as r:
                if r.status!=201:raise ValueError("Comment not accepted")
                result=json.loads(r.read(100_000))
        else:result=sender(data)
        if not isinstance(result,dict) or not isinstance(result.get("id"),int):
            raise ValueError("No confirmed GitHub comment")
    except (OSError,ValueError,TimeoutError,TypeError):
        board["notification"]={"state":"FAILED_RETRY"};return board
    board["last_notified_signature"]=board["signature"]
    board["notification_required"]=False
    board["notification"]={"state":"POSTED"}
    return board

def main():
    report=json.loads((ROOT/"site/data/support.json").read_text("utf-8"))
    try:prev=json.loads(BOARD.read_text("utf-8"))
    except (OSError,ValueError):prev={}
    board=notify(make_board(report,prev),os.getenv("GITHUB_TOKEN",""))
    save_json(BOARD,board)
    print(json.dumps({"open":len(board["open_tasks"]),"notice":board["notification"]["state"],
                      "source_repo_writes":False}))
if __name__=="__main__":main()
