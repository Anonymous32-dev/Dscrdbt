import React from 'react';
import { Sidebar } from '@/components/sidebar';
import { useApp } from '@/context/app-context';

export default function Layout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { sidebarOpen } = useApp();

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-hidden">
      <div className="flex">
        <Sidebar />
        
        <main className="flex-1 lg:ml-72 transition-all duration-300">
          <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}