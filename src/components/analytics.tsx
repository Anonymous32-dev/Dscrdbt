import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Users, Zap, Coins, Activity, Shield, Crown, Award } from 'lucide-react';

const usageData = [
  { name: 'Jan', commands: 4000, users: 2400 },
  { name: 'Feb', commands: 3000, users: 1398 },
  { name: 'Mar', commands: 2000, users: 3800 },
  { name: 'Apr', commands: 2780, users: 3908 },
  { name: 'May', commands: 1890, users: 4800 },
  { name: 'Jun', commands: 2390, users: 3800 },
];

const commandCategoryData = [
  { name: 'General', value: 35, color: '#8B5CF6' },
  { name: 'Moderation', value: 25, color: '#06B6D4' },
  { name: 'Music', value: 20, color: '#10B981' },
  { name: 'Economy', value: 15, color: '#F59E0B' },
  { name: 'Fun', value: 5, color: '#EF4444' },
];

const stats = [
  { icon: Users, label: 'Total Users', value: '12,345', change: '+12%', trend: 'up' },
  { icon: Zap, label: 'Commands Executed', value: '89,234', change: '+23%', trend: 'up' },
  { icon: Coins, label: 'Economy Volume', value: '₹45,678', change: '+8%', trend: 'up' },
  { icon: Activity, label: 'Uptime', value: '99.9%', change: '+0.1%', trend: 'stable' },
  { icon: Shield, label: 'Security Events', value: '12', change: '-5%', trend: 'down' },
  { icon: Crown, label: 'Premium Users', value: '1,234', change: '+18%', trend: 'up' },
];

export function Analytics() {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Analytics</h1>
        <p className="text-gray-400">Bot performance and usage statistics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-slate-800 border border-white/10 rounded-lg p-6">
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
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Command Usage Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={usageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#E5E7EB' }}
                itemStyle={{ color: '#E5E7EB' }}
              />
              <Line type="monotone" dataKey="commands" stroke="#8B5CF6" strokeWidth={2} dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Command Categories Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={commandCategoryData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`}
                labelLine={false}
              >
                {commandCategoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#E5E7EB' }}
                itemStyle={{ color: '#E5E&quot; }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">User Growth</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={usageData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#E5E7EB' }}
              itemStyle={{ color: '#E5E7EB' }}
            />
            <Bar dataKey="users" fill="#06B6D4" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}