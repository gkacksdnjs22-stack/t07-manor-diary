import sqlite3, uuid
from pathlib import Path
from datetime import datetime, timezone
root=Path(__file__).resolve().parents[1]
files=[p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite']
assert len(files)==1
db=sqlite3.connect(files[0]); db.row_factory=sqlite3.Row
plan=db.execute('SELECT p.* FROM plans p JOIN users u ON u.id=p.owner_id WHERE p.id=? AND u.email=?',('440e0f51-8d99-479a-a682-ef49ebae4984','gkacksdnjs22@gmail.com')).fetchone()
assert plan
out=root/'outputs/map-task-records';out.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-before.sqlite')) as backup: db.backup(backup)
updates=[
 ('b8135b62-32c9-4827-9b04-e1c03f90f17f','방 배치와 이동 동선을 층별 평면 도면으로 정리했다. 10월 6일 대화에서 지하·1층·2층·3층 도면을 제작 과정 페이지에 넣고 지하계단 제거와 2층 숨겨진 진입 표시를 반영한 것을 확인했다. 초기 자료는 보존했다.','남은 작업: 이후 재설계된 현실 3층과 승강기의 최종 구조를 도면에 갱신하기.'),
 ('1b443a29-a82c-49a0-b928-b283b49cfd21','평면 설계를 바탕으로 층별 입체 디자인과 저택 참고 이미지를 제작했다. 10월 6일 대화에서 연결 입체 이미지, 실제 중앙홀 실행 화면과 층별 도면을 제작 과정 페이지에 정리한 것을 확인했다. 초기·중간 이미지는 보존했다.','남은 작업: 현실 3층 연구 공간과 승강기 변경을 최종 입체 자료에 반영하기.'),
 ('321d32dd-5cfb-43b0-9526-255863ab9163','전체 층 도면과 계단·복도 연결을 검토했다. 10월 6일에는 기존 1·2층 외피 GPU 검수를 마치고 지하계단을 제거했다. 2층 비밀 진입부와 현실 3층 연구 구역을 구현·검증했으며 승강기 연결은 검증 중이다.','남은 작업: 승강기 회귀 검증, 이공간·스토리 연결과 최종 도면 갱신. 현실 3층 구조 재설계는 완료됐다.')
]
new=[
 ('26299991-8d48-4893-b854-2a2beeb4eb7f','10월 6일 · 전체 층 연결 동선 정리','기존 중앙홀과 1·2층 메인 계단을 보존했다. 1층→지하 계단을 제거하고 2층 숨겨진 문→비밀계단→이공간 예약 지점의 동선을 구축했다. 현실 3층은 9개 연구 구역으로 재설계했으며 3층↔지하 전용 승강기는 구현 후 검증 중이다.','남은 작업: 이공간에서 현실 3층으로 이어지는 스토리 연결, 승강기 전체 회귀 검증과 지하 콘텐츠.'),
 ('ee5bca3a-7290-458d-a5c2-8eb46583e2ce','10월 6일 · 맵 디자인 현황 정리','고고학자의 대저택을 기준으로 평면·입체 자료, 중앙홀·층별 실행 화면을 정리했다. 1·2층 기존 가구·벽 마감과 외피 보수는 보존했다. 새 현실 3층은 구조와 동선만 완성된 빈 연구 공간이며 최종 인테리어·조명·공포 연출 단계는 남아 있다.','남은 작업: 현실 3층 연구실 인테리어, 지하 공간 디자인과 전체 시각 품질 보완. 디자인 전체 완료로 판정하지 않는다.')
]
now=datetime.now(timezone.utc).isoformat()
with db:
 for rid,body,pending in updates:
  assert len(body)<=300
  db.execute('UPDATE executions SET schedule=?,blocked_reason=? WHERE id=? AND task_id IN (SELECT id FROM tasks WHERE plan_id=?)',(body,pending,rid,plan['id']))
 for tid,title,body,pending in new:
  assert db.execute('SELECT 1 FROM tasks WHERE id=? AND plan_id=?',(tid,plan['id'])).fetchone()
  key=plan['owner_id']+':map-task-summary-oct06-'+tid
  if db.execute('SELECT 1 FROM executions WHERE request_key=?',(key,)).fetchone():continue
  db.execute('INSERT INTO executions (id,task_id,start_at,end_at,actual_minutes,blocked_reason,request_key,created_at,title,ongoing,actual_known,assets,schedule) VALUES (?,?,?,?,0,?,?,?,?,0,0,?,?)',(str(uuid.uuid4()),tid,'2026-10-05T15:00:00.000Z','2026-10-05T15:00:00.000Z',pending,key,now,title,'',body))
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
print('Filled all five map tasks; existing statuses and dates preserved.')
