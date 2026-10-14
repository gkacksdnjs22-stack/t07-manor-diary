import {headers} from 'next/headers';
import {redirect} from 'next/navigation';
import {currentUser,AuthError,isSiteOwnerEmail} from '@/lib/auth';
import Diary from './diary';
export const dynamic='force-dynamic';
export default async function Page(){let owner=false;try{const user=await currentUser(new Request('http://local/',{headers:await headers()}));owner=isSiteOwnerEmail(user.email)}catch(e){if(e instanceof AuthError)redirect('/login');return <main><h1>일지를 열지 못했습니다</h1><p>잠시 후 다시 시도해 주세요.</p></main>}return <Diary owner={owner}/>}
