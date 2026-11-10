import React from 'react';
import { useState } from 'react';
import { Home, CommandSquare, User, BarChart3, Settings, LogOut, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

const sidebarItems = [
  { icon: Home, label: 'Dashboard', href: '/', key: 'dashboard' },
  { icon: CommandSquare, label: 'Command Control', href: '/commands', key: 'commands' },
  { icon: User, label: 'User Profiles', href: '/profiles', key: 'profiles' },
  { icon: BarChart3, label: 'Analytics', href: '/analytics', key: 'analytics' },
  { icon: Settings, label: 'Server Settings', href: '/settings', key: 'settings' },
];

export function Sidebar() {
  const [botStatus, setBotStatus] = useState('online');
  const [isOpen, setIsOpen] = useState(false);

  const statusColors = {
    online: 'bg-green-500 shadow-green-500/50',
    idle: 'bg-yellow-500 shadow-yellow-500/50',
    dnd: 'bg-red-500 shadow-red-500/50',
    offline: 'bg-gray-500 shadow-gray-500/50',
  };

  const statusLabels = {
    online: 'Online',
    idle: 'Idle',
    dnd: 'DND',
    offline: 'Offline',
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-slate-900 border border-white/10"
      >
        <CommandSquare className="w-6 h-6 text-white" />
      </button>

      <motion.aside
        initial={false}
        animate={{ x: isOpen ? 0 : -300 }}
        className={cn(
          'fixed left-0 top-0 h-full w-72 bg-slate-900 border-r border-white/10 p-6',
          'transform transition-transform duration-300 lg:translate-x-0 lg:static'
        )}
      >
        <div className="flex flex-col h-full">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Discord Manager
            </h1>
            <p className="text-sm text-gray-400 mt-1">Bot Administration Dashboard</p>
         _airline
          </div>

          <div className="mb-6 p-4 rounded-lg bg-slate-800 border border-white/10">
            <div className="flex items-center gap-3 mb-3">
              <div className={cn('w-3 h-3 rounded-full animate-pulse', statusColors[botStatus as keyof typeof statusColors])} />
              <span className="text-sm font-medium text-white">Bot Status: {statusLabels[botStatus as keyof typeof statusLabels]}</span>
            </div>

            <div className="flex gap-2 mt-3">
              <button
                onClick={() => setBotStatus('online')}
                className={cn('px-3 py-1 text-xs rounded-full transition-all', botStatus === 'online' ? 'bg-green-500 text-white' : 'bg-slate-800 text-gray-400')}
              >
                Online
              </button>
              <button
                onClick={() => setBotStatus('idle')}
                className={cn('px-3 py-1 text-xs rounded-full transition-all', botStatus === 'idle' ? 'bg-yellow-500 text-white' : 'bg-slate-800 text-gray-400')}
              >
                Idle
              </button>
              <button
                onClick={() => setBotStatus('dnd')}
                className={cn('px-3 py-1 text-xs rounded-full transition-all', botStatus === 'dnd' ? 'bg-red-500 text-white' : 'bg-slate-800 text-gray-400')}
              >
                DND
              </button>
              <button
                onClick={() => setBotStatus('offline')}
                className={cn('px-3 py-1 text-xs rounded-full transition-all', botStatus === 'offline' ? 'bg-gray-500 text-white' : 'bg-slate-800 text-gray-400')}
              >
                Offline
              </button>
            </div>
          </div>

          <nav className="flex-1 space-y-2">
            {sidebarItems.map((item) => (
              <a
                key={item.key}
                href={item.href}
                className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white transition-all duration-200"
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </a>
            ))}
          </nav>

          <div className="mt-auto pt-6 border-t border-white/10">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-white">Byte X Bot</div>
                <div className="text-xs text-gray-400">Bot ID: 12345678</div>
              </div>
            </div>

            <button className="w-full mt-3 flex items-center gap-2 px-4 py-2 rounded-lg text-gray-300 hover:bg-red-500/20 hover:text-red-400 transition-all">
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </motion.aside>

      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
        />
      )}
    </>
  );
}