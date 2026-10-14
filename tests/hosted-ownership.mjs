import assert from 'node:assert/strict';
import {writeFileSync,globSync} from 'node:fs';
import {DatabaseSync} from 'node:sqlite';
const base='http://127.0.0.1:5190';
const dbFile=globSync('.wrangler/hosted-auth-test/**/*.sqlite').find(p=>!p.endsWith('metadata.sqlite'));
assert.ok(dbFile);const db=new DatabaseSync(dbFile);
const stamp=crypto.randomUUID(),subjects=[`owner-${stamp}`,`other-${stamp}`],results=[],evidence=[];
// Synthetic upstream headers simulate dispatch only in this isolated local Worker.
async function call(i,path='/api/diary',method='GET',body){
 const r=await fetch(base+path,{method,headers:{Origin:base,...(i===null?{}:{'oai-authenticated-user-id':subjects[i],'oai-authenticated-user-email':i===0?'owner@synthetic.invalid':'other@synthetic.invalid'}),...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})});
 const data=await r.json();evidence.push({request:{syntheticSubject:i,path,method,body},response:{status:r.status,body:data}});return {status:r.status,data};
}
async function check(name,fn){await fn();results.push({name,status:'PASS'});console.log('PASS '+name)}
try{
 await check('anonymous data, account and identity APIs reject access',async()=>{for(const p of ['/api/diary','/api/auth','/api/account'])assert.equal((await call(null,p)).status,401)});
 const legacy=crypto.randomUUID();db.prepare('INSERT INTO plans(id,title,start_date,end_date,priority,success_criteria,estimated_minutes,created_at) VALUES(?,?,?,?,?,?,?,?)').run(legacy,'Synthetic legacy','2026-10-14','2026-10-14',2,'Test',0,new Date().toISOString());
 await check('other user cannot claim unowned legacy records',async()=>{assert.ok(!(await call(1)).data.plans.some(p=>p.id===legacy));assert.equal(db.prepare('SELECT owner_id FROM plans WHERE id=?').get(legacy).owner_id,null)});
 await check('verified owner claims legacy without changing its content',async()=>{assert.ok((await call(0)).data.plans.some(p=>p.id===legacy));const row=db.prepare('SELECT owner_id,title FROM plans WHERE id=?').get(legacy);assert.equal(row.owner_id,'chatgpt:'+subjects[0]);assert.equal(row.title,'Synthetic legacy');assert.ok(!(await call(1)).data.plans.some(p=>p.id===legacy))});
 const plans=[],tasks=[],executions=[],reviews=[];
 await check('both identities create private records',async()=>{for(let i=0;i<2;i++){
  const p=await call(i,'/api/diary','POST',{action:'createPlan',title:'Synthetic '+i,startDate:'2026-10-14',endDate:'2026-10-14',priority:2,successCriteria:'Test',estimatedMinutes:0});assert.equal(p.status,201);plans[i]=p.data.id;
  const t=await call(i,'/api/diary','POST',{action:'createTask',planId:plans[i],title:'Synthetic task',dueDate:'2026-10-14',priority:2,tags:'synthetic',estimatedMinutes:0});assert.equal(t.status,201);tasks[i]=t.data.id;
  const e=await call(i,'/api/diary','POST',{action:'createExecution',taskId:tasks[i],startAt:'2026-10-14T09:00:00+09:00',endAt:'2026-10-14T09:01:00+09:00',requestKey:stamp+i,blockedReason:''});assert.equal(e.status,201);executions[i]=e.data.id;
  const r=await call(i,'/api/diary','POST',{action:'createReview',planId:plans[i],startDate:'2026-10-14',endDate:'2026-10-14',improvement:'Synthetic'});assert.equal(r.status,201);reviews[i]=r.data.id;
 }});
 await check('cross-account read, update, delete and create rejected in both directions',async()=>{for(let i=0;i<2;i++){
  const j=1-i,before=(await call(j)).data;
  for(const [table,id,action] of [['plans',plans[j],'deletePlan'],['tasks',tasks[j],'deleteTask'],['executions',executions[j],'deleteExecution'],['reviews',reviews[j],'updateReview']]){
   assert.equal((await call(i,`/api/diary?table=${table}&id=${id}`)).status,404);
   assert.equal((await call(i,'/api/diary','POST',{action,id,improvement:'ATTACK'})).status,404);
  }
  assert.equal((await call(i,'/api/diary','POST',{action:'updateExecution',id:executions[j],taskId:tasks[i],startAt:'2026-10-14T09:00:00+09:00',endAt:'2026-10-14T09:01:00+09:00',requestKey:'attack'})).status,404);
  assert.equal((await call(i,'/api/diary','POST',{action:'createTask',planId:plans[j],title:'Attack',dueDate:'2026-10-14',priority:2,estimatedMinutes:0})).status,404);
  assert.deepEqual((await call(j)).data,before);
 }});
 await check('forged owner query ignored; export stays account-scoped',async()=>{for(let i=0;i<2;i++){
  const r=await call(i,'/api/diary?userId=chatgpt:'+subjects[1-i]);assert.ok(r.data.plans.every(p=>p.ownerId==='chatgpt:'+subjects[i]));
  const e=await call(i,'/api/account');assert.equal(e.status,200);assert.ok(e.data.plans.every(p=>p.ownerId==='chatgpt:'+subjects[i]));assert.ok(!JSON.stringify(e.data).includes('password_hash'));
 }});
 await check('hosted password APIs disabled and logout uses platform route',async()=>{assert.equal((await call(0,'/api/auth','POST',{action:'register'})).status,400);assert.equal((await call(0,'/api/auth','POST',{action:'changePassword'})).status,400);const r=await call(0,'/api/auth','POST',{action:'logout'});assert.equal(r.status,200);assert.equal(r.data.redirect,'/signout-with-chatgpt?return_to=%2Flogin')});
}finally{db.close();writeFileSync('tests/hosted-ownership-results.json',JSON.stringify({at:new Date().toISOString(),environment:'isolated local built Worker; synthetic dispatch identity headers; NOT two actual public accounts',results,evidence},null,2))}
