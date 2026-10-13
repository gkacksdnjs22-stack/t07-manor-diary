import {rawDb} from '@/db/raw';
import {env} from 'cloudflare:workers';
import {compare,hash} from 'bcryptjs';
export const SESSION_SECONDS=8*60*60;
const COOKIE='diary_session';
export class AuthError extends Error {constructor(message:string,public status=401){super(message)}}
export const authJson=(value:unknown,status=200,extra:Record<string,string>={})=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',...extra}});
export function sameOrigin(req:Request){if(req.headers.get('Origin')!==new URL(req.url).origin)throw new AuthError('다른 사이트에서의 요청은 허용하지 않습니다.',403)}
export async function digest(value:string){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value))),b=>b.toString(16).padStart(2,'0')).join('')}
export function cookie(req:Request){return req.headers.get('Cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith(COOKIE+'='))?.slice(COOKIE.length+1)||''}
export function sessionCookie(req:Request,value:string,maxAge=SESSION_SECONDS){return `${COOKIE}=${value}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${maxAge}${new URL(req.url).protocol==='https:'?'; Secure':''}`}
export function hostedAuth(){return (env as any).DIARY_HOSTED_AUTH==='chatgpt'}
export async function currentUser(req:Request){
 if(hostedAuth()){
  // Sites dispatch supplies verified identity; email alone from form input is never trusted.
  const subject=req.headers.get('oai-authenticated-user-id'),email=req.headers.get('oai-authenticated-user-email');
  if(!subject||!email)throw new AuthError('로그인이 필요합니다.');
  const id='chatgpt:'+subject,db=rawDb();
  const exists=await db.prepare('SELECT id FROM users WHERE id=?').bind(id).first();
  if(!exists){const unusable=await passwordHash(crypto.randomUUID()+crypto.randomUUID());await db.prepare('INSERT OR IGNORE INTO users(id,email,password_hash,created_at) VALUES(?,?,?,?)').bind(id,subject+'@chatgpt.invalid',unusable,new Date().toISOString()).run()}
  if(email.trim().toLowerCase()===(env as any).DIARY_OWNER_EMAIL){await db.prepare('UPDATE plans SET owner_id=? WHERE owner_id IS NULL').bind(id).run()}
  return {id,email,provider:'chatgpt'};
 }
 const token=cookie(req);if(!/^[a-f0-9]{64}$/.test(token))throw new AuthError('로그인이 필요합니다.');const row=await rawDb().prepare('SELECT users.id,users.email FROM auth_sessions JOIN users ON users.id=auth_sessions.user_id WHERE auth_sessions.token_hash=? AND auth_sessions.expires_at>?').bind(await digest(token),new Date().toISOString()).first<{id:string;email:string;provider?:string}>();if(!row)throw new AuthError('로그인이 필요합니다.');return row}
export function password(value:unknown){if(typeof value!=='string'||value.length<12||new TextEncoder().encode(value).length>72)throw new AuthError('비밀번호는 12자 이상, UTF-8 72바이트 이하로 입력해 주세요.',400);return value}
export const passwordHash=(value:string)=>hash(value,12);
export const passwordMatches=compare;
export async function newSession(req:Request,userId:string){const token=Array.from(crypto.getRandomValues(new Uint8Array(32)),b=>b.toString(16).padStart(2,'0')).join('');const now=new Date();await rawDb().prepare('INSERT INTO auth_sessions(token_hash,user_id,created_at,expires_at) VALUES(?,?,?,?)').bind(await digest(token),userId,now.toISOString(),new Date(now.getTime()+SESSION_SECONDS*1000).toISOString()).run();return sessionCookie(req,token)}
export function authFailure(e:unknown){if(e instanceof AuthError)return authJson({error:e.message},e.status);console.error('auth_operation_failed');return authJson({error:'처리하지 못했습니다. 잠시 후 다시 시도해 주세요.'},503)}
