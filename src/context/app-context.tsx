import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext({
  sidebarOpen: false,
  setSidebarOpen: () => {},
  botStatus: 'online',
  setBotStatus: () => {},
});

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [botStatus, setBotStatus] = useState('online');

  return (
    <AppContext.Provider value={{ sidebarOpen, setSidebarOpen, botStatus, setBotStatus }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}