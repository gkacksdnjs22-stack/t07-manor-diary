import sqlite3
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
files=[p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite']
assert len(files)==1
db=sqlite3.connect(files[0]);db.row_factory=sqlite3.Row
plan='440e0f51-8d99-479a-a682-ef49ebae4984'
assert db.execute('SELECT 1 FROM plans p JOIN users u ON u.id=p.owner_id WHERE p.id=? AND u.email=?',(plan,'gkacksdnjs22@gmail.com')).fetchone()
out=root/'outputs/map-task-records'
with sqlite3.connect(out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-before-date-correction.sqlite')) as b:db.backup(b)
items=[
 ('b8135b62-32c9-4827-9b04-e1c03f90f17f','9월 29일 · 初期平面'.replace('初期平面','초기 평면 설계도 제작'),'2026-09-29T06:16:42.000Z',
  '최초 제작: 2026년 9월 29일. 서울 기준 15:16 대화에서 대저택 1층 콘셉트 평면도를 제작했고, 15:22에는 2층, 15:31에는 3층 평면도를 제작했다. 이후 계단과 기둥 위치를 수정했다. 10월 6일은 기존 층별 도면을 제작 과정 페이지에 넣고 지하계단 제거·비밀 진입 표시를 갱신한 날이다. 대화 시각은 작업시간이 아니며 실제 소요 시간은 미상이다.'),
 ('1b443a29-a82c-49a0-b928-b283b49cfd21','9월 29일 · 평면 설계 기반 입체도 제작','2026-09-29T06:26:26.000Z',
  '최초 제작: 2026년 9월 29일. 서울 기준 15:26 대화에서 1층 평면도를 입체도로 변환했고, 15:33부터 1·2·3층 연결 입체도를 제작·수정했다. 별도 대화의 16:11부터 층별 입체도를 합쳤고 16:18에는 지하를 합쳤다. 10월 6일에는 기존 입체 자료와 실행 화면을 제작 과정 페이지에 배치했다. 대화 시각은 작업시간이 아니며 실제 소요 시간은 미상이다.')
]
with db:
 for rid,title,stamp,body in items:
  assert len(body)<=300
  r=db.execute('SELECT 1 FROM executions e JOIN tasks t ON t.id=e.task_id WHERE e.id=? AND t.plan_id=?',(rid,plan)).fetchone();assert r
  db.execute('UPDATE executions SET title=?,start_at=?,end_at=?,schedule=?,ongoing=0,actual_known=0,actual_minutes=0 WHERE id=?',(title,stamp,stamp,body,rid))
print('Corrected original design dates to September 29; October 6 retained as later page updates. Completion statuses preserved.')
