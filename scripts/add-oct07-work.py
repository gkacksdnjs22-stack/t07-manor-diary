import sqlite3,uuid
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
files=[p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite'];assert len(files)==1
db=sqlite3.connect(files[0])
task='e670b9ec-49e3-48d9-ad0a-7977b17f07a1'
owner=db.execute('SELECT p.owner_id FROM tasks t JOIN plans p ON p.id=t.plan_id JOIN users u ON u.id=p.owner_id WHERE t.id=? AND u.email=?',(task,'gkacksdnjs22@gmail.com')).fetchone();assert owner
out=root/'outputs/map-task-records'
with sqlite3.connect(out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-before-oct07.sqlite')) as b:db.backup(b)
body='10月7日'.replace('10月7日','10월 7일')+' 대화를 확인했다. 승강기 두 정차층의 문 방향과 지하 하차 위치를 조정하고, 카가 없는 층의 문이 처음부터 닫히도록 수정했다. 분할 바닥 메시의 접합 오차도 보정했다. 왕복 운행·문턱 안전 검사는 통과했으나 샤프트와 1·2층 책장·책상 영역의 겹침이 발견돼 위치 및 전체 회귀 검증이 남았다. 작업은 중단 상태이며 실제 소요 시간은 미상이다.'
key=owner[0]+':daily-manor-work-2026-10-07'
# Conversation began at this timestamp; it is not a measured work start time.
stamp=datetime.fromtimestamp(1791360387,timezone.utc).isoformat()
with db:
 old=db.execute('SELECT id FROM executions WHERE request_key=?',(key,)).fetchone()
 if old:db.execute('UPDATE executions SET schedule=?,blocked_reason=? WHERE id=?',(body,'토큰 부족',old[0]))
 else:db.execute('INSERT INTO executions(id,task_id,start_at,end_at,actual_minutes,blocked_reason,request_key,created_at,title,ongoing,actual_known,assets,schedule) VALUES(?,?,?,?,0,?,?,?,?,0,0,?,?)',(str(uuid.uuid4()),task,stamp,stamp,'토큰 부족',key,datetime.now(timezone.utc).isoformat(),'10월 7일 · 승강기 문·바닥 접합 수정 및 검증','',body))
print('Saved October 7 work with blocked reason: token shortage.')
