import React from 'react';
import { Menu, Search, Bell, UserCircle } from 'lucide-react';
import clsx from 'clsx';

const Header = ({ sidebarOpen, setSidebarOpen, role, setRole }) => {
  return (
    <header className="sticky top-0 bg-white/80 backdrop-blur-md border-b border-slate-200 z-30">
      <div className="flex items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
        <div className="flex items-center">
          <button
            className="text-slate-500 hover:text-slate-600 lg:hidden mr-4"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={24} />
          </button>
          <div className="hidden sm:block relative text-slate-400 focus-within:text-indigo-500 max-w-sm">
             <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2" />
             <input type="text" placeholder="Search insights..." className="w-full bg-slate-100 border-transparent focus:bg-white focus:border-indigo-500 focus:ring-0 rounded-full text-sm py-2 pl-10 pr-4 text-slate-900 placeholder:text-slate-400 transition-colors" />
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center bg-slate-100 rounded-lg p-1">
            <button
              onClick={() => setRole('student')}
              className={clsx(
                "px-3 py-1.5 text-xs font-semibold rounded-md transition-all",
                role === 'student' ? "bg-white text-indigo-600 shadow-sm" : "text-slate-600 hover:text-slate-900"
              )}
            >
              Student
            </button>
            <button
              onClick={() => setRole('educator')}
              className={clsx(
                "px-3 py-1.5 text-xs font-semibold rounded-md transition-all",
                role === 'educator' ? "bg-white text-indigo-600 shadow-sm" : "text-slate-600 hover:text-slate-900"
              )}
            >
              Educator
            </button>
          </div>

          <button onClick={() => alert('Notifications panel is simulated for this demo.')} className="text-slate-400 hover:text-indigo-500 transition-colors relative">
            <Bell size={20} />
            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 border-2 border-white rounded-full"></span>
          </button>
          <button onClick={() => alert('User profile settings are disabled in the prototype.')} className="text-slate-400 hover:text-indigo-500 transition-colors">
            <UserCircle size={24} />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
