import {headers} from 'next/headers';
import {redirect} from 'next/navigation';
import {currentUser,isSiteOwnerEmail,AuthError} from '@/lib/auth';
import RestoreForm from './restore-form';
export const dynamic='force-dynamic';
export default async function Page(){try{const user=await currentUser(new Request('http://local/',{headers:await headers()}));if(!isSiteOwnerEmail(user.email))return <main><h1>기록 복원 권한이 없습니다</h1><a href="/">내 일지로 돌아가기</a></main>}catch(e){if(e instanceof AuthError)redirect('/login');throw e}return <RestoreForm/>}
