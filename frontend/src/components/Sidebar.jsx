import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, LineChart, Calendar, BrainCircuit, X } from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { name: 'Home', path: '/', icon: Home },
  { name: 'Predict', path: '/predict', icon: BrainCircuit },
  { name: 'Study Plan', path: '/study-plan', icon: Calendar },
  { name: 'Analytics', path: '/analytics', icon: LineChart },
];

const Sidebar = ({ sidebarOpen, setSidebarOpen }) => {
  return (
    <>
      {/* Mobile background overlay */}
      <div 
        className={clsx(
          "fixed inset-0 bg-slate-900 bg-opacity-50 z-40 lg:hidden transition-opacity",
          sidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <div
        className={clsx(
          "flex flex-col absolute z-50 left-0 top-0 lg:static lg:left-auto lg:top-auto lg:translate-x-0 h-screen overflow-y-scroll lg:overflow-y-auto no-scrollbar w-64 lg:w-72 2xl:w-80 shrink-0 bg-slate-900 text-slate-100 transition-all duration-300 ease-in-out",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between p-6 bg-slate-950">
          <div className="flex items-center space-x-3">
             <BrainCircuit className="text-emerald-400 w-8 h-8" />
             <span className="text-xl font-bold tracking-tight">EduPredict <span className="text-emerald-400">AI</span></span>
          </div>
          <button 
            className="lg:hidden text-slate-400 hover:text-white"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={24} />
          </button>
        </div>

        <nav className="flex-1 px-4 py-8 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) => clsx(
                "flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors group",
                isActive 
                  ? "bg-indigo-600 text-white" 
                  : "text-slate-400 hover:bg-slate-800 hover:text-emerald-300"
              )}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-6 bg-slate-950/50">
          <div className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-2">System Status</div>
          <div className="flex items-center space-x-2 text-sm text-slate-400">
             <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
             <span>All models online</span>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
