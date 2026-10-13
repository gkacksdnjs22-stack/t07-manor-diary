import sqlite3
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
files=[p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite']
assert len(files)==1
db=sqlite3.connect(files[0])
plan='440e0f51-8d99-479a-a682-ef49ebae4984'
assert db.execute('SELECT 1 FROM plans p JOIN users u ON u.id=p.owner_id WHERE p.id=? AND u.email=?',(plan,'gkacksdnjs22@gmail.com')).fetchone()
out=root/'outputs/map-task-records';out.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-before-titles.sqlite')) as backup:db.backup(backup)
titles={
 '1c586eda-f3f6-4034-a574-14140645ae75':'층별 평면 설계도 갱신 · 현실 3층·승강기 변경 반영',
 'ded15124-556f-4551-bbf1-5ab6d2735d7f':'입체도 갱신 · 새 연구층과 승강기 구조 반영',
 '26299991-8d48-4893-b854-2a2beeb4eb7f':'층간 동선 완성 · 이공간→현실 3층 연결 및 승강기 검증',
 'e670b9ec-49e3-48d9-ad0a-7977b17f07a1':'구조 최종 검토 · 승강기 충돌·외피·기존 층 회귀 점검',
 'ee5bca3a-7290-458d-a5c2-8eb46583e2ce':'맵 디자인 구체화 · 현실 3층 연구실·지하 공간 보완'
}
with db:
 for tid,title in titles.items():
  row=db.execute('SELECT title FROM tasks WHERE id=? AND plan_id=? AND deleted_at IS NULL',(tid,plan)).fetchone()
  assert row
  if row[0]!=title:db.execute('UPDATE tasks SET title=?,version=version+1 WHERE id=?',(title,tid))
print('Updated five task titles. Preserved due dates, statuses, and linked records.')
