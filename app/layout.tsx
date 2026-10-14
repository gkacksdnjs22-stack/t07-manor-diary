import type { Metadata } from "next";
import {headers} from 'next/headers';
import {isSiteOwnerEmail} from '@/lib/auth';
import "./globals.css";

export async function generateMetadata():Promise<Metadata>{
 const owner=isSiteOwnerEmail((await headers()).get('oai-authenticated-user-email'));
 return {
  title: owner?"탈출게임 제작 일지 · Plan Do See":"내 작업 일지 · Plan Do See",
  description: "계획, 실제 작업, 다음 개선점을 이어가는 나의 작업 일지",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="antialiased">{children}</body>
    </html>
  );
}
