import React, { useState } from 'react';
import { Search, Play, ToggleLeft, ToggleRight, Copy, Code2, Users, Shield, Zap, Calendar, TrendingUp, DollarSign } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const mockCommands = [
  {
    id: '1',
    name: 'ping',
    category: 'General',
    description: 'Check bot latency and status',
    usage: '`!ping`',
    permissions: 'everyone',
    enabled: true,
    cooldown: 2,
    icon: '⚡'
  },
  {
    id: '2',
    name: 'ban',
    category: 'Moderation',
    description: 'Ban a user from the server',
    usage: '`!ban <user> [reason]`',
    permissions: 'admin',
    enabled: true,
    cooldown: 10,
    icon: '🔨'
  },
  {
    id: '3',
    name: 'kick',
    category: 'Moderation',
    description: 'Kick a user from the server',
    usage: '`!kick <user> [reason]`',
    permissions: 'admin',
    enabled: true,
    cooldown: 5,
    icon: '👢'
  },
  {
    id: '4',
    name: 'play',
    category: 'Music',
    description: 'Play music from YouTube',
    usage: '`!play <song>`',
    permissions: 'everyone',
    enabled: true,
    cooldown: 1,
    icon: '🎵'
  },
  {
    id: '5',
    name: 'balance',
    category: 'Economy',
    description: 'Check your coin balance',
    usage: '`!balance <user>`',
    permissions: 'everyone',
    enabled: true,
    cooldown: 30,
    icon: '💰'
  },
  {
    id: '6',
    name: 'giveaway',
    category: 'Fun',
    description: 'Start a giveaway',
    usage: '`!giveaway <duration> <prize>`',
    permissions: 'admin',
    enabled: true,
    cooldown: 60,
    icon: '🎁'
  },
  {
    id: '7',
    name: 'afk',
    category: 'Auto',
    description: 'Set AFK status with reason',
    usage: '`!afk <reason>`',
    permissions: 'everyone',
    enabled: true,
    cooldown: 0,
    icon: '🏃'
  },
  {
    id: '8',
    name: 'prefix',
    category: 'Admin',
    description: 'Change bot command prefix',
    usage: '`!prefix <new_prefix>`',
    permissions: 'admin',
    enabled: true,
    cooldown: 30,
    icon: '🔧'
  }
];

const categories = ['All', 'Moderation', 'General', 'Music', 'Economy', 'Fun', 'Auto', 'Admin'];

export function CommandControl() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedCommand, setSelectedCommand] = useState<any>(null);
  const [enabledCommands, setEnabledCommands] = useState<{[key: string]: boolean}>({
    '1': true, '2': true, '3': true, '4': true, '5': true, '6': true, '7': true, '8': true
  });

  const filteredCommands = mockCommands.filter(command => {
    const matchesSearch = command.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         command.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || command.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getPermissionColor = (perm: string) => {
    switch (perm) {
      case 'admin': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'mod': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-green-500/20 text-green-400 border-green-500/30';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Command Control</h1>
        <p className="text-gray-400">Manage and test bot commands remotely</p>
      </div>

      <div className="mb-6">
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search commands..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-slate-900 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${selectedCategory === category
                ? 'bg-gradient-to-r from-purple-500 to-cyan-500 text-white shadow-lg shadow-purple-500/25'
                : 'bg-slate-800 text-gray-300 hover:bg-slate-700 border border-white/10'}
              `}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCommands.map((command, index) => (
          <motion.div
            key={command.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02, y: -5 }}
            className="bg-slate-800 border border-white/10 rounded-lg p-6 hover:border-purple-500/30 transition-all duration-300 cursor-pointer"
            onClick={() => setSelectedCommand(command)}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="text-3xl mb-2">{command.icon}</div>
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEnabledCommands(prev => ({
                      ...prev,
                      [command.id]: !prev[command.id]
                    }));
                  }}
                  className="p-2 rounded bg-white/5 hover:bg-white/10 transition-colors"
                >
                  {enabledCommands[command.id] ? (
                    <ToggleRight className="w-5 h-5 text-green-400" />
                  ) : (
                    <ToggleLeft className="w-5 h-5 text-gray-400" />
                  )}
                </button>
                <span className={`px-2 py-1 text-xs rounded border ${getPermissionColor(command.permissions)}` }>
                  {command.permissions}
                </span>
              </div>
            </div>

            <h3 className="text-lg font-semibold text-white mb-2">{command.name}</h3>
            <p className="text-gray-400 text-sm mb-3">{command.description}</p>

            <div className="flex items-center justify-between">
              <div className="text-xs text-gray-500">Cooldown: {command.cooldown}s</div>
              <div className="text-xs text-purple-400">Category: {command.category}</div>
            </div>

            <div className="mt-3 p-2 bg-black/30 rounded text-xs font-mono text-gray-300">
              {command.usage}
            </div>
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {selectedCommand && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedCommand(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-slate-900 border border-white/10 rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            >
              <div className="flex items-start justify-between mb-6">
                <div className="text-4xl mb-2">{selectedCommand.icon}</div>
                <button
                  onClick={() => setSelectedCommand(null)}
                  className="p-2 rounded bg-white/10 hover:bg-white/20 transition-colors"
                >
                  ✕
                </button>
              </div>

              <h2 className="text-2xl font-bold text-white mb-2">{selectedCommand.name}</h2>
              <p className="text-gray-400 mb-6">{selectedCommand.description}</p>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-white/5 rounded-lg">
                  <div className="text-sm text-gray-400 mb-1">Usage</div>
                  <div className="font-mono text-white">{selectedCommand.usage}</div>
                </div>
                <div className="p-4 bg-white/5 rounded-lg">
                  <div className="text-sm text-gray-400 mb-1">Cooldown</div>
                  <div className="text-white">{selectedCommand.cooldown}s</div>
                </div>
                <div className="p-4 bg-white/5 rounded-lg">
                  <div className="text-sm text-gray-400 mb-1">Permissions</div>
                  <div className={`inline-block px-2 py-1 rounded text-xs border ${getPermissionColor(selectedCommand.permissions)}` }>
                    {selectedCommand.permissions}
                  </div>
                </div>
                <div className="p-4 bg-white/5 rounded-lg">
                  <div className="text-sm text-gray-400 mb-1">Category</div>
                  <div className="text-white">{selectedCommand.category}</div>
                </div>
              </div>

              <div className="flex gap-3 mb-6">
                <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg text-white font-medium hover:shadow-lg hover:shadow-purple-500/25 transition-all">
                  <Play className="w-4 h-4" />
                  Execute Command
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all">
                  <Copy className="w-4 h-4" />
                  Copy Usage
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all">
                  <Code2 className="w-4 h-4" />
                  View Code
                </button>
              </div>

              <div className="p-4 bg-black/30 rounded-lg">
                <div className="text-sm text-gray-400 mb-2">Example Parameters:</div>
                <div className="font-mono text-sm text-gray-300">
                  {selectedCommand.name === 'ping' && '!ping'}
                  {selectedCommand.name === 'ban' && '!ban @user Spamming'}
                  {selectedCommand.name === 'play' && '!play Never Gonna Give You Up'}
                  {selectedCommand.name === 'balance' && '!balance'}
                  {selectedCommand.name === 'giveaway' && '!giveaway 1h Luxury Vacation'}
                  {selectedCommand.name === 'afk' && '!afk Studying for exams'}
                  {selectedCommand.name === 'prefix' && '!prefix !'}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}