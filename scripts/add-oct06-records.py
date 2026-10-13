import sqlite3, uuid, json
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
files = [p for p in (root/'.wrangler/state/v3/d1').rglob('*.sqlite') if p.name != 'metadata.sqlite']
assert len(files) == 1
db = sqlite3.connect(files[0])
db.row_factory = sqlite3.Row
db.execute('PRAGMA foreign_keys=ON')
row = db.execute('SELECT e.*,p.owner_id FROM executions e JOIN tasks t ON t.id=e.task_id JOIN plans p ON p.id=t.plan_id JOIN users u ON u.id=p.owner_id WHERE e.id=? AND u.email=?', ('c3944bd7-d152-4aa3-b775-b5e16e657693','gkacksdnjs22@gmail.com')).fetchone()
assert row
out = root/'outputs/oct06-additional-records'
out.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).isoformat()
with sqlite3.connect(out/('before-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.sqlite')) as backup:
    db.backup(backup)
records = [
 ('real-third-floor','10월 6일 · 현실 3층 연구 공간 재설계 완료',
  '기존 생활실 복제 구조를 9개 연구 구역으로 교체했다. 진입 홀→자료·지도·발굴·유물 영역→메인 연구실→제한 연구실→승강기 대기 공간을 연결하고 40×34m 외곽과 기존 1·2층·비밀계단을 보존했다. 자동 이동 2,000지점과 GPU 이동 1,311지점 실패 0, 고립 공간·외피 누락 0, 실행 화면 10장 검수와 기존 퍼즐·상호작용·저장 검사를 통과했다. 시작·종료 시각과 소요 시간은 미상이다.',
  '후속 작업: 이공간·스토리 연결, 연구층 인테리어와 지하 콘텐츠는 미구현이다. 승강기 구현은 별도 진행 기록에 남겼다.'),
 ('basement-lift','10월 6일 · 3층↔지하 전용 승강기 구현·검증 진행',
  '3층과 지하만 연결하는 승강기 카·층문·샤프트와 지하 도착 포켓을 구현했다. 1·2층에는 문과 버튼을 노출하지 않았다. 실제 플레이어 탑승·왕복·하차와 문턱 접근 시 출발 취소를 확인했다. 이후 샤프트 위치·바닥 절개·충돌을 조정하며 기존 층의 동선을 재검사했다. 전체 검증 완료 전 작업이 중단되어 진행 중으로 기록한다. 시작·종료 시각과 소요 시간은 미상이다.',
  '남은 점검: 기존 1·2층 동선 회귀, 샤프트 외피·바닥 절개와 충돌, 부재층 차단문 및 GPU 최종 검수. 지하 엔딩 콘텐츠·이공간은 미구현이다.')
]
saved=[]
with db:
    for suffix,title,body,pending in records:
        assert len(body) <= 300
        key=row['owner_id']+':oct06-additional-'+suffix
        existing=db.execute('SELECT id FROM executions WHERE request_key=?',(key,)).fetchone()
        if existing:
            saved.append(existing['id']); continue
        rid=str(uuid.uuid4())
        # Unknown hours remain excluded from time totals. Work status is stated in title/body.
        db.execute('INSERT INTO executions (id,task_id,start_at,end_at,actual_minutes,blocked_reason,request_key,created_at,title,ongoing,actual_known,assets,schedule) VALUES (?,?,?,?,0,?,?,?,?,0,0,?,?)',
                   (rid,row['task_id'],'2026-10-05T15:00:00.000Z','2026-10-05T15:00:00.000Z',pending,key,stamp,title,'',body))
        saved.append(rid)
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
(out/'saved-records.json').write_text(json.dumps({'date':'2026-10-06','ids':saved,'records':records},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'saved':saved,'count':len(saved)}))
