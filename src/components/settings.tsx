import React, { useState } from 'react';
import { Settings as SettingsIcon, Bot, Shield, Bell, Palette, Database, HardDrive, Wifi, Save, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';

export function Settings() {
  const [activeSection, setActiveSection] = useState('bot');

  const settingsSections = [
    { id: 'bot', label: 'Bot Configuration', icon: Bot },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'storage', label: 'Storage', icon: HardDrive },
    { id: 'api', label: 'API & Integrations', icon: Wifi },
    { id: 'backup', label: 'Backup & Recovery', icon: Database },
  ];

  const renderSection = () => {
    switch (activeSection) {
      case 'bot':
        return (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Bot Basic Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Bot Name</label>
                  <input
                    type="text"
                    defaultValue="Byte X Bot"
                    className="w-full px-4 py-2 bg-slate-900 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500/50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Bot Description</label>
                  <input
                    type="text"
                    defaultValue="Advanced Discord Selfbot"
                    className="w-full px-4 py-2 bg-slate-900 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500/50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Command Prefix</label>
                  <input
                    type="text"
                    defaultValue="!"
                    className="w-full px-4 py-2 bg-slate-900 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500/50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Default Activity</label>
                  <select
                    defaultValue="playing"
                    className="w-full px-4 py-2 bg-slate-900 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500/50"
                  >
                    <option value="playing">Playing</option>
                    <option value="streaming">Streaming</option>
                    <option value="listening">Listening to</option>
                    <option value="watching">Watching</option>
                    <option value="competing">Competing in</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Activity Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-white">Bot Status</div>
                    <div className="text-xs text-gray-400">Current status displayed to users</div>
                  </div>
                  <select
                    defaultValue="online"
                    className="px-4 py-2 bg-slate-900 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500/50"
                  >
                    <option value="online">Online</option>
                    <option value="idle">Idle</option>
                    <option value="dnd">DND</option>
                    <option value="offline">Offline</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-white">Activity Rotation</div>
                    <div className="text-xs text-gray-400">Rotate between different activities</div>
                  </div>
                  <button className="px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors">
                    Configure
                  </button>
                </div>
              </div>
            </div>
          </div>
        );

      case 'security':
        return (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Security Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-white">Two-Factor Authentication</div>
                    <div className="text-xs text-gray-400">Require 2FA for admin actions</div>
                  </div>
                  <button className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors">
                    Enabled
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-white">Rate Limiting</div>
                    <div className="text-xs text-gray-400">Limit command usage per user</div>
                  </div>
                  <button className="px-4 py-2 bg-slate-700 text-gray-300 rounded-lg hover:bg-slate-600 transition-colors">
                    Configure
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-white">IP Whitelist</div>
                    <div className="text-xs text-gray-400">Restrict bot access to specific IPs</div>
                  </div>
                  <button className="px-4 py-2 bg-slate-700 text-gray-300 rounded-lg hover:bg-slate-600 transition-colors">
                    Configure
                  </button>
                </div>
              </div>
            </div>
          </div>
        );

      case 'appearance':
        return (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Theme Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Primary Color</label>
                  <div className="flex gap-2">
                    <div className="w-8 h-8 rounded-full bg-purple-500 cursor-pointer border-2 border-white" />
                    <div className="w-8 h-8 rounded-full bg-cyan-500 cursor-pointer" />
                    <div className="w-8 h-8 rounded-full bg-green-500 cursor-pointer" />
                    <div className="w-8 h-8 rounded-full bg-red-500 cursor-pointer" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-white">Compact Mode</div>
                    <div className="text-xs text-gray-400">Reduce spacing and padding</div>
                  </div>
                  <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-slate-700 transition-colors focus:outline-none">
                    <span className="h-4 w-4 rounded-full bg-white transform transition-transform translate-x-6" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        );

      case 'api':
        return (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-white/10 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">API Configuration</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Bot Token</label>
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value="xEYJ...ABC123"
                      readOnly
                      className="flex-1 px-4 py-2 bg-slate-900 border border-white/10 rounded-lg text-white focus:outline-none"
                    />
                    <button className="px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors">
                      <RefreshCw className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Webhook URL</label>
                  <input
                    type="text"
                    placeholder="https://discord.com/api/webhooks/..."
                    className="w-full px-4 py-2 bg-slate-900 border border-white/10 rounded-lg text-white focus:outline-none focus:border-purple-500/50"
                  />
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return <div>Section not found</div>;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Server Settings</h1>
        <p className="text-gray-400">Configure your Discord bot settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-slate-800 border border-white/10 rounded-lg p-4">
            <nav className="space-y-2">
              {settingsSections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all ${activeSection === section.id
                      ? 'bg-gradient-to-r from-purple-500/20 to-cyan-500/20 text-white border border-purple-500/30'
                      : 'text-gray-300 hover:bg-white/10'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-sm font-medium">{section.label}</span>
                  </button>
                );
              })}
            </nav>

            <div className="mt-6 p-4 bg-gradient-to-r from-purple-500/10 to-cyan-500/10 rounded-lg border border-purple-500/20">
              <div className="flex items-center gap-2 mb-2">
                <Save className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-white">Auto-save</span>
              </div>
              <p className="text-xs text-gray-400">Settings are automatically saved</p>
            </div>
          </div>
        </div>

        <div className="lg:col-span-3">
          {renderSection()}

          <div className="mt-6 flex gap-4">
            <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg text-white font-medium hover:shadow-lg hover:shadow-purple-500/25 transition-all">
              Save Changes
            </button>
            <button className="px-6 py-3 bg-slate-800 border border-white/10 rounded-lg text-white hover:bg-white/10 transition-all">
              Reset to Defaults
            </button>
         -locked
          </div>
        </div>
      </div>
    </div>
  );
}