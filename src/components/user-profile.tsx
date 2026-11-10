import React, { useState } from 'react';
import { User, Shield, Crown, Calendar, MapPin, Activity, Check, Zap, TrendingUp, Coins } from 'lucide-react';
import { motion } from 'framer-motion';

const mockUser = {
  id: 'user123',
  username: 'nighty_user',
  discriminator: '7342',
  avatar: 'https://i.pinimg.com/736x/32/2d/3e/322d3e9037387874bc0e4358832a4af3.jpg',
  banner: 'https://i.pinimg.com/736x/32/2d/3e/322d3e9037387874bc0e4358832a4af3.jpg',
  level: 42,
  xp: 15750,
  nextXp: 18000,
  coins: 2500,
  bank: 15000,
  badges: [
    { name: 'Developer', icon: Shield, color: 'bg-purple-500' },
    { name: 'Booster', icon: Crown, color: 'bg-yellow-500' },
    { name: 'Admin', icon: Shield, color: 'bg-red-500' },
  ],
  joinedAt: '2023-06-15T14:30:00Z',
  lastSeen: '2024-01-10T14:30:00Z',
  activities: [
    { id: '1', type: 'level_up', value: 42, time: '2024-01-10T14:30:00Z', description: 'Reached Level 42!' },
    { id: '2', type: 'coins', value: '+500', time: '2024-01-10T12:15:00Z', description: 'Won giveaway' },
    { id: '3', type: 'command', value: 'play', time: '2024-01-10T10:45:00Z', description: 'Executed !play Never Gonna Give You Up' },
  ]
};

export function UserProfile() {
  const [activeTab, setActiveTab] = useState('overview');

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'level_up': return <TrendingUp className="w-4 h-4" />;
      case 'coins': return <Coins className="w-4 h-4" />;
      case 'command': return <Zap className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">User Profiles</h1>
        <p className="text-gray-400">Manage and inspect user profiles and activity</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-1">
          <div className="bg-slate-800 border border-white/10 rounded-lg overflow-hidden">
            <div className="relative">
              <img
                src={mockUser.banner}
                alt="Banner"
                className="w-full h-32 object-cover"
              />
              <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2">
                <img
                  src={mockUser.avatar}
                  alt={mockUser.username}
                  className="w-24 h-24 rounded-full border-4 border-slate-900"
                />
              </div>
            </div>

            <div className="pt-16 pb-6 px-6 text-center">
              <h2 className="text-xl font-bold text-white mb-1">
                {mockUser.username}
                <span className="text-gray-400 ml-2">#{mockUser.discriminator}</span>
              </h2>
              <p className="text-gray-500 text-sm mb-4">User ID: {mockUser.id}</p>

              <div className="flex flex-wrap justify-center gap-2 mb-6">
                {mockUser.badges.map((badge, index) => (
                  <div
                    key={index}
                    className={`flex items-center gap-1 px-3 py-1 rounded-full ${badge.color} text-white text-xs font-medium`}
                  >
                    <badge.icon className="w-3 h-3" />
                    {badge.name}
                  </div>
                ))}
              </div>

              <div className="space-y-3 text-left">
                <div className="flex items-center gap-3">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-300">Joined {formatDate(mockUser.joinedAt)}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Activity className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-300">Last seen {formatTimeAgo(mockUser.lastSeen)}</span>
                </div>
                <div className="flex items-center gap-3">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-300">Level {mockUser.level}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 bg-slate-800 border border-white/10 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Level & XP</h3>
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-400 mb-2">
                <span>Level {mockUser.level}</span>
                <span>{mockUser.xp}/{mockUser.nextXp} XP</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(mockUser.xp / mockUser.nextXp) * 100}%` }}
                  className="bg-gradient-to-r from-purple-500 to-cyan-500 h-3 rounded-full"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-purple-400">{mockUser.level}</div>
                <div className="text-xs text-gray-400">Current Level</div>
              </div>
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-cyan-400">{(mockUser.xp / 100).toFixed(0)}</div>
                <div className="text-xs text-gray-400">Total XP</div>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="bg-slate-800 border border-white/10 rounded-lg">
            <div className="border-b border-white/10">
              <nav className="flex">
                {['overview', 'economy', 'activity'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 text-sm font-medium transition-all ${activeTab === tab
                      ? 'text-purple-400 border-b-2 border-purple-400 bg-white/5'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {activeTab === 'overview' && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Economy Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div className="p-4 bg-white/5 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-sm text-gray-400">Personal Coins</div>
                        <div className="text-xl font-bold text-yellow-400">{mockUser.coins}</div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-400">Bank Balance</div>
                        <div className="text-xl font-bold text-cyan-400">{mockUser.bank}</div>
                      </div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg">
                      <div className="text-sm text-gray-400 mb-2">Total Wealth</div>
                      <div className="text-xl font-bold text-green-400">{(mockUser.coins + mockUser.bank).toLocaleString()}</div>
                      <div className="text-xs text-gray-500 mt-1">All currency combined</div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'activity' && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    {mockUser.activities.map((activity, index) => (
                      <motion.div
                        key={activity.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all"
                      >
                        <div className={`p-2 rounded-full ${activity.type === 'level_up' ? 'bg-purple-500/20 text-purple-400' : activity.type === 'coins' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-cyan-500/20 text-cyan-400'}` }>
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="flex-1">
                          <div className="text-sm text-white font-medium">{activity.description}</div>
                          <div className="text-xs text-gray-400">{formatTimeAgo(activity.time)}</div>
                        shelved
                        </div>
                        <div className="text-sm font-bold" className={
                          activity.type === 'level_up' ? 'text-purple-400' :
                          activity.type === 'coins' ? 'text-yellow-400' :
                          activity.type === 'command' ? 'text-cyan-400' : 'text-gray-400'
                        }>
                          {activity.value}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'economy' && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Economy Details</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-white/5 rounded-lg">
                      <div className="text-sm text-gray-400 mb-2">Currency Distribution</div>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-300">Personal</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 bg-gray-700 rounded-full h-2">
                              <div className="bg-yellow-400 h-2 rounded-full" style={{ width: '10%' }}></div>
                            </div>
                            <span className="text-sm font-medium text-yellow-400">10%</span>
                          </div>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-300">Bank</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 bg-gray-700 rounded-full h-2">
                              <div className="bg-cyan-400 h-2 rounded-full" style={{ width: '90%' }}></div>
                            </div>
                            <span className="text-sm font-medium text-cyan-400">90%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}