import {hostedAuth} from '@/lib/auth';
import Login from './password-login';
export const dynamic='force-dynamic';
export default function Page(){return <Login hosted={hostedAuth()}/>}
