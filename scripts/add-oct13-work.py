import sqlite3,uuid
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
files=[p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite'];assert len(files)==1
db=sqlite3.connect(files[0]);task='ee5bca3a-7290-458d-a5c2-8eb46583e2ce'
owner=db.execute('SELECT p.owner_id FROM tasks t JOIN plans p ON p.id=t.plan_id JOIN users u ON u.id=p.owner_id WHERE t.id=? AND u.email=?',(task,'gkacksdnjs22@gmail.com')).fetchone();assert owner
out=root/'outputs/map-task-records';out.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-before-oct13.sqlite')) as b:db.backup(b)
records=[
 ('layout','10월 13일 · 서재 공간 재배치·연구 역사 자료 보강','서가 13→6개, 가구 21→14개로 정리하고 집무·문헌/지도·유물 조사·독서 영역을 구성했다. Blender 작업대·도면함 2종과 연구 소품을 제작했다. 기록 묶음·자료꽂이 2종, 시대별 비교 도판 17장을 추가했다. 각 단계 국소 검사 597개·924개를 통과하고 실제 PC GPU 화면을 확인했다. 구조·동선·게임 기능과 조명은 보존했다. 별도 수정본 기준이며 OneDrive 원본은 변경하지 않았다.','남은 문제: 긴 빈 바닥과 반복 서가 인상, 천장 그림자. 장시간 성능·전역 회귀 및 최종 디자인 승인은 미완료.'),
 ('finish','10월 13일 · 서재 벽 마감·작업대·문서장 표면 개선','Blender로 벽판·허리벽 cap·걸레받이·회벽 프레임 4종을 제작하고 기존 작업대 하부를 재사용해 상판을 수정했다. Godot에 연결해 실제 GPU 적용을 확인했다. 문서장 ResearchShelf2의 서랍 X자 반사·곡면·월넛·분류표를 개선하고 국소 687개 검사를 통과했다. 근거리·전체방·야간 전후 6장을 확보했다. 근거리 GPU 중앙값은 45.36→34.49ms이나 일부 p95는 악화했다.','남은 점검: 단일 성능 표본의 변동과 전체방·야간 p95 악화, 최종 디자인 승인. 천장 코니스 형상은 기존 Godot 메시를 유지했다.')
]
with db:
 for suffix,title,body,pending in records:
  assert len(body)<=300
  key=owner[0]+':daily-manor-work-2026-10-13-'+suffix
  old=db.execute('SELECT id FROM executions WHERE request_key=?',(key,)).fetchone()
  if old:db.execute('UPDATE executions SET schedule=?,blocked_reason=? WHERE id=?',(body,pending,old[0]))
  else:db.execute('INSERT INTO executions(id,task_id,start_at,end_at,actual_minutes,blocked_reason,request_key,created_at,title,ongoing,actual_known,assets,schedule) VALUES(?,?,?,?,0,?,?,?,?,0,0,?,?)',(str(uuid.uuid4()),task,'2026-10-12T15:00:00Z','2026-10-12T15:00:00Z',pending,key,datetime.now(timezone.utc).isoformat(),title,'',body))
assert db.execute("SELECT count(*) FROM executions WHERE request_key LIKE '%:daily-manor-work-2026-10-13-%'").fetchone()[0]==2
print('Saved and verified two October 13 game records.')
