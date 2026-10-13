import sqlite3,uuid
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
files=[p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite'];assert len(files)==1
db=sqlite3.connect(files[0]);task='ee5bca3a-7290-458d-a5c2-8eb46583e2ce'
owner=db.execute('SELECT p.owner_id FROM tasks t JOIN plans p ON p.id=t.plan_id JOIN users u ON u.id=p.owner_id WHERE t.id=? AND u.email=?',(task,'gkacksdnjs22@gmail.com')).fetchone();assert owner
out=root/'outputs/map-task-records';out.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-before-oct12.sqlite')) as b:db.backup(b)
records=[
 ('furnishing','10월 12일 · 1·2층 가구 정리·3층 연구 가구 배치 완료','1층 서재·응접실·식당의 가구 간격과 방향을 정리했다. 2층 드레서·욕실 거울·수납을 보강하고 드레스룸 통로와 초상화 예약 벽면을 확보했다. 3층 9개 연구구역에 용도별 가구를 배치하고 문서장·지도 작업대·드레서·전신거울·벽거울 5종을 제작했다. 가구 176개 검사, 이동 1,030지점 실패 0, GPU 화면 47장 검수와 C# 빌드를 통과했다. 건축·계단·승강기·지하는 보존했다.','후속 작업: 최종 조명·PBR·초상화 이미지·스토리 기능.'),
 ('research','10월 12일 · 메인연구실 모델·재질·연구 자료 개선','3층 메인연구실의 책상 몰딩 오류, 의자·책장, 문틀·천장 몰딩을 보완하고 목재 무늬·반사를 낮췄다. 텍스처 밉맵·압축을 적용했다. 자료 보드·조사 노트·유물 트레이·보관함을 추가해 연구 흔적과 재료 구분을 강화했다. 연구실 이동 122지점·전체 1,030지점 실패 0, 보호 항목 391개 동일, 비밀문·승강기·퍼즐·저장 검사를 통과했다.','남은 문제: 근거리 가구·그림자 마감과 GPU 비용. 근접 구도 35.6ms로 60FPS 예산 초과. 다른 방 확대와 최종 연출은 미완료.'),
 ('design','10월 12일 · 서재 책상·서가·의자 디자인 시안 개선','별도 게임 수정본에서 책상 상판·패널·받침·조각과 목재 UV·PBR를 개선했다. 책상 삼각형을 33,212→18,856개로 줄였다. 서가 13개를 적용하고 원목·금속·가죽·크림 마감을 조정했다. 의자 3개의 곡선 등받이·팔걸이·쿠션·프레임과 천장 곡면 몰딩을 보완했다. 책상·구조·충돌·가구 위치 보존 및 국소 검사를 통과했다. 시안은 소프트웨어 렌더 기준이며 PC 원본에는 미반영이다.','남은 점검: 실제 GPU 시각·성능 검수와 디자인 승인. 2차 시안 소프트웨어 측정 비용은 손전등 +38.6%, 검수조명 +73.7% 증가. 최신 국소 변경에서 전역 회귀는 재실행하지 않았다.')
]
with db:
 for suffix,title,body,pending in records:
  assert len(body)<=300
  key=owner[0]+':daily-manor-work-2026-10-12-'+suffix
  old=db.execute('SELECT id FROM executions WHERE request_key=?',(key,)).fetchone()
  if old:db.execute('UPDATE executions SET title=?,schedule=?,blocked_reason=? WHERE id=?',(title,body,pending,old[0]))
  else:db.execute('INSERT INTO executions(id,task_id,start_at,end_at,actual_minutes,blocked_reason,request_key,created_at,title,ongoing,actual_known,assets,schedule) VALUES(?,?,?,?,0,?,?,?,?,0,0,?,?)',(str(uuid.uuid4()),task,'2026-10-11T15:00:00Z','2026-10-11T15:00:00Z',pending,key,datetime.now(timezone.utc).isoformat(),title,'',body))
assert db.execute("SELECT count(*) FROM executions WHERE request_key LIKE '%:daily-manor-work-2026-10-12-%'").fetchone()[0]==3
print('Saved and verified 3 game-only October 12 records.')
