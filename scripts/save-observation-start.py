import sqlite3,uuid
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
files=[p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite'];assert len(files)==1
db=sqlite3.connect(files[0]);plan='440e0f51-8d99-479a-a682-ef49ebae4984'
assert db.execute('SELECT 1 FROM plans p JOIN users u ON u.id=p.owner_id WHERE p.id=? AND u.email=?',(plan,'gkacksdnjs22@gmail.com')).fetchone()
text='5일 관찰 기준 (10월 8일 확정)\n1일차: 10월 6일\n2일차: 10월 7일\n3일차: 10월 8일\n4일차: 10월 9일 (예정)\n5일차: 10월 10일 (예정)\n\n첫 이틀은 대화·작업 기록에 근거한 소급 정리다. 지표는 하루 할 일 완료율(완료 수÷계획 수×100). 사전에 고정한 일일 계획 수가 확인되지 않은 날짜의 완료율은 미정으로 두며 임의의 수치를 넣지 않는다. 관찰 3일차와 유효한 완료율 기록 3개는 구분한다.'
rid='t07-observation-start-20261006'
with db:
 db.execute('INSERT INTO reviews(id,plan_id,start_date,end_date,improvement,created_at) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET improvement=excluded.improvement',(rid,plan,'2026-10-06','2026-10-08',text,datetime.now(timezone.utc).isoformat()))
assert db.execute('SELECT improvement FROM reviews WHERE id=?',(rid,)).fetchone()[0]==text
print('Observation dates saved to review.')
