import sqlite3,uuid
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
files=[p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite'];assert len(files)==1
db=sqlite3.connect(files[0])
task='e670b9ec-49e3-48d9-ad0a-7977b17f07a1'
owner=db.execute('SELECT p.owner_id FROM tasks t JOIN plans p ON p.id=t.plan_id JOIN users u ON u.id=p.owner_id WHERE t.id=? AND u.email=?',(task,'gkacksdnjs22@gmail.com')).fetchone();assert owner
out=root/'outputs/map-task-records';out.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-before-oct08.sqlite')) as b:db.backup(b)
body='2층 숨겨진 벽을 E키로 여는 개발용 기능을 연결하고 3층 통로 이동을 확인했다. 지하를 40×34m 외곽의 단일 엔딩 홀로 교체하고 승강기 하차부를 연결했다. 지하 자동 이동 2,165지점·GPU 이동 354지점 실패 0, 외피·충돌 검사와 기존 기능 회귀를 통과했다. 이어 1·2층 가구 재정리와 3층 연구 가구 배치를 시작해 신규 가구 4종·독립 씬·배치 모듈을 생성했다. 가구 충돌·동선·GPU 최종 검수는 미완료다. 실제 소요 시간은 미상이다.'
assert len(body)<=300
key=owner[0]+':daily-manor-work-2026-10-08'
stamp=datetime.fromtimestamp(1791436079,timezone.utc).isoformat()
with db:
 old=db.execute('SELECT id FROM executions WHERE request_key=?',(key,)).fetchone()
 if old:db.execute('UPDATE executions SET schedule=?,blocked_reason=? WHERE id=?',(body,'토큰 부족',old[0]))
 else:db.execute('INSERT INTO executions(id,task_id,start_at,end_at,actual_minutes,blocked_reason,request_key,created_at,title,ongoing,actual_known,assets,schedule) VALUES(?,?,?,?,0,?,?,?,?,0,0,?,?)',(str(uuid.uuid4()),task,stamp,stamp,'토큰 부족',key,datetime.now(timezone.utc).isoformat(),'10월 8일 · 비밀문 입력 연결·지하 구조 완성·가구 제작 진행','',body))
assert db.execute('SELECT blocked_reason FROM executions WHERE request_key=?',(key,)).fetchone()[0]=='토큰 부족'
print('October 8 record saved and verified.')
