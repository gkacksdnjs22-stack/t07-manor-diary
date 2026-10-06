import {rawDb} from '@/db/raw';
import {AuthError,authJson,authFailure,currentUser,passwordMatches,sameOrigin,sessionCookie} from '@/lib/auth';
import {GET as diaryGet} from '@/app/api/diary/route';
export const dynamic='force-dynamic';
export async function GET(req:Request){const response=await diaryGet(req);if(!response.ok)return response;const data:any=await response.json();return authJson({schemaVersion:3,timeZone:'Asia/Seoul',unit:'minutes',exportedAt:new Date().toISOString(),...data},200,{'Content-Disposition':'attachment; filename="my-diary.json"'})}
export async function POST(req:Request){try{sameOrigin(req);const user=await currentUser(req),raw=await req.text();if(raw.length>1000)throw new AuthError('입력이 너무 깁니다.',400);let p:any;try{p=JSON.parse(raw)}catch{throw new AuthError('입력 형식을 확인해 주세요.',400)}if(p.action!=='deleteAccount'||p.confirm!=='내 계정 삭제')throw new AuthError('계정 삭제 확인 문구를 입력해 주세요.',400);const db=rawDb(),row=await db.prepare('SELECT password_hash FROM users WHERE id=?').bind(user.id).first<any>();if(typeof p.password!=='string'||new TextEncoder().encode(p.password).length>72||!await passwordMatches(p.password,row.password_hash))throw new AuthError('비밀번호를 확인해 주세요.',400);
 const plans='SELECT id FROM plans WHERE owner_id=?',tasks=`SELECT id FROM tasks WHERE plan_id IN (${plans})`;
 await db.batch([
 db.prepare(`DELETE FROM completions WHERE task_id IN (${tasks})`).bind(user.id),db.prepare(`DELETE FROM executions WHERE task_id IN (${tasks})`).bind(user.id),
 db.prepare(`UPDATE plans SET source_review_id=NULL WHERE owner_id=?`).bind(user.id),db.prepare(`DELETE FROM reviews WHERE plan_id IN (${plans})`).bind(user.id),db.prepare(`DELETE FROM plan_versions WHERE plan_id IN (${plans})`).bind(user.id),db.prepare(`DELETE FROM tasks WHERE plan_id IN (${plans})`).bind(user.id),db.prepare('DELETE FROM plans WHERE owner_id=?').bind(user.id),db.prepare('DELETE FROM auth_sessions WHERE user_id=?').bind(user.id),db.prepare('DELETE FROM users WHERE id=?').bind(user.id)]);
 return authJson({ok:true},200,{'Set-Cookie':sessionCookie(req,'',0)});
 }catch(e){return authFailure(e)}}
