import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, Zap, Coins, Activity, Shield, Crown, Award, CommandSquare, User, BarChart3, Settings } from 'lucide-react';

const stats = [
  { icon: Users, label: 'Total Users', value: '12,345', change: '+12%', trend: 'up' },
  { icon: Zap, label: 'Commands Executed', value: '89,234', change: '+23%', trend: 'up' },
  { icon: Coins, label: 'Economy Volume', value: '₹45,678', change: '+8%', trend: 'up' },
  { icon: Activity, label: 'Uptime', value: '99.9%', change: '+0.1%', trend: 'stable' },
];

const recentActivity = [
  { id: 1, user: 'nighty_user', action: 'joined server', time: '5 min ago', type: 'join' },
  { id: 2, user: 'alex_gaming', action: 'executed !play Never Gonna Give You Up', time: '10 min ago', type: 'command' },
  { id: 3, user: 'sara_dev', action: 'reached level 42!', time: '15 min ago', type: 'level' },
  { id: 4, user: 'mike_admin', action: 'gave 500 coins to nighty_user', time: '20 min ago', type: 'economy' },
  { id: 5, user: 'emma_design', action: 'enabled auto-react', time: '25 min ago', type: 'settings' },
];

const quickCommands = [
  { name: 'ping', icon: '⚡', description: 'Check bot latency', category: 'General' },
  { name: 'ban', icon: '🔨', description: 'Ban a user', category: 'Moderation' },
  { name: 'play', icon: '🎵', description: 'Play music', category: 'Music' },
  { name: 'balance', icon: '💰', description: 'Check balance', category: 'Economy' },
];

export default function Dashboard() {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">Overview of your Discord bot performance</p>
      segments
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-800 border border-white/10 rounded-lg p-6 hover:border-purple-500/30 transition-all duration-300"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-lg bg-white/5">
                  <Icon className="w-6 h-6 text-purple-400" />
                </div>
                <div className={`flex items-center gap-1 text-sm font-medium ${stat.trend === 'up' ? 'text-green-400' : stat.trend === 'down' ? 'text-red-400' : 'text-gray-400'}` }>
                  {stat.trend === 'up' && '↗'}
                  {stat.trend === 'down' && '↘'}
                  {stat.trend === 'stable' && '→'}
                  {stat.change}
                </div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-gray-400">{stat.label}</div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-slate-800 border border-white/10 rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">Quick Actions</h2>
            <button className="text-sm text-purple-400 hover:text-purple-300">View All</button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {quickCommands.map((cmd, index) => (
              <motion.div
                key={cmd.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.02, y: -5 }}
                className="bg-gradient-to-r from-purple-500/10 to-cyan-500/10 border border-white/10 rounded-lg p-4 cursor-pointer hover:border-purple-500/30 transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="text-2xl mb-1">{cmd.icon}</div>
                  <div>
                    <div className="font-semibold text-white">{cmd.name}</div>
                    <div className="text-sm text-gray-400">{cmd.description}</div>
                    <div className="text-xs text-purple-400 mt-1">{cmd.category}</div>
                  </div>
                cadastro
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Bot Status</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-gray-300">Online - All systems operational</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-yellow-500 animate-pulse" />
              <span className="text-sm text-gray-300">2 commands in cooldown</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
              <span className="text-sm text-gray-300">1 error in last hour</span>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-sm font-medium text-gray-400 mb-3">Resource Usage</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">CPU</span>
                  <span className="text-green-400">23%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '23%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">Memory</span>
                  <span className="text-cyan-400">45%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-cyan-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">Disk</span>
                  <span className="text-purple-400">67%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: '67%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
          <button className="text-sm text-purple-400 hover:text-purple-300">View Timeline</button>
        </div>
        
        <div className="space-y-4">
          {recentActivity.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-4 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-all"
            >
              <div className={`w-2 h-2 rounded-full ${activity.type === 'join' ? 'bg-green-500' : activity.type === 'command' ? 'bg-purple-500' : activity.type === 'level' ? 'bg-yellow-500' : 'bg-cyan-500'}` } />
              <div className="flex-1">
                <div className="text-sm text-white">
                  <span className="font-medium">{activity.user}</span> {activity.action}
                </div>
                <div className="text-xs text-gray-400">{activity.time}</div>
              </div>
              <div className="text-xs text-gray-500">#{activity.id}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}