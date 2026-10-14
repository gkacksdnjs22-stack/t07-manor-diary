import {currentUser,isSiteOwnerEmail,hostedAuth,sameOrigin,AuthError,authFailure,authJson} from '@/lib/auth';
import {rawDb} from '@/db/raw';
export const dynamic='force-dynamic';
export async function POST(req:Request){try{
 sameOrigin(req);if(hostedAuth()){const email=req.headers.get('oai-authenticated-user-email');if(!email||!req.headers.get('oai-authenticated-user-id'))throw new AuthError('로그인이 필요합니다.');if(!isSiteOwnerEmail(email))throw new AuthError('기록 복원 권한이 없습니다.',403)}const user=await currentUser(req);if(!isSiteOwnerEmail(user.email))throw new AuthError('기록 복원 권한이 없습니다.',403);
 const raw=await req.text();if(raw.length>500000)throw new AuthError('파일이 너무 큽니다.',400);
 const payload=JSON.parse(raw);if(payload.schemaVersion!==1||!Array.isArray(payload.executions)||payload.executions.length>100)throw new AuthError('기록 파일 형식을 확인해 주세요.',400);
 const db=rawDb(),owned=await db.prepare('SELECT tasks.id FROM tasks JOIN plans ON plans.id=tasks.plan_id WHERE plans.owner_id=?').bind(user.id).all<{id:string}>(),taskIds=new Set(owned.results.map(t=>t.id)),ids=new Set<string>(),statements=[];
 for(const r of payload.executions){
  if(typeof r.id!=='string'||! /^[a-f0-9-]{36}$/.test(r.id)||ids.has(r.id)||!taskIds.has(r.task_id))throw new AuthError('내 할 일에 속한 기록만 복원할 수 있습니다.',400);ids.add(r.id);
  for(const k of ['title','blocked_reason','assets','schedule','start_at','end_at','created_at'])if(typeof r[k]!=='string'||r[k].length>20000)throw new AuthError('기록 내용을 확인해 주세요.',400);
  if(![0,1].includes(r.actual_known)||![0,1].includes(r.ongoing)||!Number.isInteger(r.actual_minutes)||r.actual_minutes<0||r.actual_minutes>1000000||!Number.isFinite(Date.parse(r.start_at))||!Number.isFinite(Date.parse(r.end_at))||Date.parse(r.end_at)<Date.parse(r.start_at))throw new AuthError('날짜와 시간 형식을 확인해 주세요.',400);
  if(r.assets&&r.assets.split(',').some((p:string)=>!/^\/design\/[a-zA-Z0-9_./-]+\.(png|jpg|jpeg|webp|svg)$/.test(p)||p.includes('..')))throw new AuthError('이미지 경로를 확인해 주세요.',400);
  const existing=await db.prepare('SELECT tasks.plan_id,plans.owner_id FROM executions JOIN tasks ON tasks.id=executions.task_id JOIN plans ON plans.id=tasks.plan_id WHERE executions.id=?').bind(r.id).first<{owner_id:string}>();if(existing&&existing.owner_id!==user.id)throw new AuthError('다른 계정 기록은 변경할 수 없습니다.',403);
  statements.push(db.prepare('INSERT INTO executions(id,task_id,start_at,end_at,actual_minutes,blocked_reason,request_key,created_at,title,ongoing,actual_known,assets,schedule) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET task_id=excluded.task_id,start_at=excluded.start_at,end_at=excluded.end_at,actual_minutes=excluded.actual_minutes,blocked_reason=excluded.blocked_reason,title=excluded.title,ongoing=excluded.ongoing,actual_known=excluded.actual_known,assets=excluded.assets,schedule=excluded.schedule').bind(r.id,r.task_id,r.start_at,r.end_at,r.actual_minutes,r.blocked_reason,user.id+':restored:'+r.id,r.created_at,r.title,r.ongoing,r.actual_known,r.assets,r.schedule));
 }
 if(statements.length)await db.batch(statements);
 return authJson({ok:true,restored:statements.length});
}catch(e){if(e instanceof SyntaxError)return authJson({error:'JSON 파일을 확인해 주세요.'},400);return authFailure(e)}}
