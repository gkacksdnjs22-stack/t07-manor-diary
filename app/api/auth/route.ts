import {rawDb} from '@/db/raw';
import {AuthError,authJson,authFailure,currentUser,cookie,digest,newSession,password,passwordHash,passwordMatches,sameOrigin,sessionCookie} from '@/lib/auth';
export const dynamic='force-dynamic';
export async function GET(req:Request){try{return authJson({user:await currentUser(req)})}catch(e){return authFailure(e)}}
export async function POST(req:Request){try{
 sameOrigin(req);const raw=await req.text();if(raw.length>4000)throw new AuthError('입력이 너무 깁니다.',400);let p:any;try{p=JSON.parse(raw)}catch{throw new AuthError('입력 형식을 확인해 주세요.',400)}const db=rawDb();
 if(p.action==='logout'){const user=await currentUser(req);await db.prepare('DELETE FROM auth_sessions WHERE token_hash=? AND user_id=?').bind(await digest(cookie(req)),user.id).run();return authJson({ok:true},200,{'Set-Cookie':sessionCookie(req,'',0)})}
 if(p.action==='changePassword'){const user=await currentUser(req),row=await db.prepare('SELECT password_hash FROM users WHERE id=?').bind(user.id).first<any>();if(typeof p.currentPassword!=='string'||!await passwordMatches(p.currentPassword,row.password_hash))throw new AuthError('현재 비밀번호를 확인해 주세요.',400);const next=await passwordHash(password(p.password));await db.batch([db.prepare('UPDATE users SET password_hash=? WHERE id=?').bind(next,user.id),db.prepare('DELETE FROM auth_sessions WHERE user_id=?').bind(user.id)]);return authJson({ok:true},200,{'Set-Cookie':sessionCookie(req,'',0)})}
 if(!['register','login'].includes(p.action))throw new AuthError('지원하지 않는 동작입니다.',400);
 if(typeof p.email!=='string'||p.email.length>200||!/^\S+@\S+\.\S+$/.test(p.email))throw new AuthError('이메일을 확인해 주세요.',400);
 const email=p.email.trim().toLowerCase();const value=password(p.password);
 if(p.action==='register'){const hashed=await passwordHash(value),id=crypto.randomUUID();const result=await db.prepare('INSERT OR IGNORE INTO users(id,email,password_hash,created_at) VALUES(?,?,?,?)').bind(id,email,hashed,new Date().toISOString()).run();if(!result.meta.changes)throw new AuthError('가입할 수 없습니다. 입력 내용을 확인하거나 로그인해 주세요.',409);return authJson({ok:true},201,{'Set-Cookie':await newSession(req,id)})}
 const user=await db.prepare('SELECT id,password_hash FROM users WHERE email=?').bind(email).first<any>();
 // A dummy hash performs the same bcrypt verification for a nonexistent email.
 const hashed=user?.password_hash||'$2b$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jWMUW';
 const matches=await passwordMatches(value,hashed);if(!user||!matches)throw new AuthError('이메일 또는 비밀번호가 올바르지 않습니다.');return authJson({ok:true},200,{'Set-Cookie':await newSession(req,user.id)});
 }catch(e){return authFailure(e)}}
