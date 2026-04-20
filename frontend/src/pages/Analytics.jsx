import React, { useEffect, useState } from 'react';
import { getAnalytics } from '../services/mockApi';
import { PieChart, Pie, Cell, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Users, AlertCircle, TrendingDown, BookOpen } from 'lucide-react';

const scatterData = [
  { attendance: 95, socialMedia: 1 },
  { attendance: 85, socialMedia: 2 },
  { attendance: 70, socialMedia: 4 },
  { attendance: 50, socialMedia: 6 },
  { attendance: 40, socialMedia: 8 },
  { attendance: 80, socialMedia: 3 },
  { attendance: 65, socialMedia: 5 },
  { attendance: 30, socialMedia: 9 },
];

const mockHighRiskStudents = [
  { id: 'STU089', name: 'Alex Johnson', score: 38, issue: 'Low Attendance (40%)' },
  { id: 'STU142', name: 'Sarah Williams', score: 41, issue: 'High Social Media (8h)' },
  { id: 'STU055', name: 'Michael Chen', score: 35, issue: 'Poor Assignment Marks' }
];

const Analytics = ({ role }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    getAnalytics().then(setData);
  }, []);

  if (role !== 'educator') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4 animate-in fade-in duration-500">
        <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center text-slate-400">
           <Users size={40} />
        </div>
        <h2 className="text-2xl font-bold text-slate-800">Educator Access Required</h2>
        <p className="text-slate-500 max-w-md">The analytics dashboard contains aggregated cohort data, performance trends, and risk management tools reserved for educators and administrators.</p>
      </div>
    );
  }

  if (!data) return <div className="p-8 text-center text-slate-500 animate-pulse font-medium">Loading aggregated analytics...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Cohort Analytics</h1>
          <p className="text-slate-500 text-sm mt-1">Review overall performance trends and monitor at-risk segments.</p>
        </div>
        <div className="flex space-x-3">
           <div className="bg-white border border-slate-200 shadow-sm rounded-lg px-4 py-2 flex items-center space-x-2">
             <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
             <span className="text-sm font-bold text-slate-700">Live Data Sync</span>
           </div>
        </div>
      </div>

      {/* Top Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-5 flex items-center space-x-4">
          <div className="p-3 bg-red-50 text-red-500 rounded-xl">
            <AlertCircle size={24} />
          </div>
          <div>
            <div className="text-2xl font-extrabold text-slate-800">20%</div>
            <div className="text-sm font-medium text-slate-500">High Risk Students</div>
          </div>
        </div>
        <div className="glass-card p-5 flex items-center space-x-4">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
            <TrendingDown size={24} />
          </div>
          <div>
            <div className="text-2xl font-extrabold text-slate-800">4.2h</div>
            <div className="text-sm font-medium text-slate-500">Avg. Social Media Usage</div>
          </div>
        </div>
        <div className="glass-card p-5 flex items-center space-x-4">
          <div className="p-3 bg-emerald-50 text-emerald-500 rounded-xl">
            <BookOpen size={24} />
          </div>
          <div>
            <div className="text-2xl font-extrabold text-slate-800">72%</div>
            <div className="text-sm font-medium text-slate-500">Avg. Cohort Score</div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Risk Distribution Pie Chart */}
        <div className="glass-card p-6">
          <h3 className="font-bold text-slate-800 mb-6">Risk Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.riskDistribution} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {data.riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Performance Trends Line Chart */}
        <div className="glass-card p-6">
          <h3 className="font-bold text-slate-800 mb-6">Performance Trends</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.performanceTrends}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dx={-10} domain={[40, 100]} />
                <Tooltip contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Line type="monotone" dataKey="avgScore" stroke="#6366f1" strokeWidth={3} dot={{r: 4, fill: '#6366f1', strokeWidth: 2, stroke: '#fff'}} activeDot={{r: 6}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Scatter Plot */}
        <div className="glass-card p-6 h-full">
          <h3 className="font-bold text-slate-800 mb-2">Impact Analysis</h3>
          <p className="text-xs text-slate-500 mb-4">Correlation between Social Media Usage and Attendance.</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="socialMedia" name="Social Media (h)" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dy={5} />
                <YAxis dataKey="attendance" name="Attendance (%)" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                <Tooltip cursor={{strokeDasharray: '3 3'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Scatter name="Students" data={scatterData} fill="#f43f5e" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* High Risk Students List */}
        <div className="glass-card p-6">
          <div className="flex justify-between items-center mb-6">
             <h3 className="font-bold text-slate-800">Attention Required</h3>
             <span className="bg-red-100 text-red-600 text-xs font-bold px-2 py-1 rounded-md">{mockHighRiskStudents.length} Students</span>
          </div>
          <div className="space-y-4">
            {mockHighRiskStudents.map(student => (
              <div key={student.id} className="flex items-center justify-between p-3 hover:bg-slate-50 rounded-xl transition-colors border border-transparent hover:border-slate-100 cursor-pointer">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-bold text-sm">
                    {student.name.charAt(0)}
                  </div>
                  <div>
                    <div className="font-semibold text-sm text-slate-800">{student.name} <span className="text-xs text-slate-400 font-normal ml-1">({student.id})</span></div>
                    <div className="text-xs text-red-500 font-medium">{student.issue}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-800">{student.score}</div>
                  <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Score</div>
                </div>
              </div>
            ))}
          </div>
          <button onClick={() => alert('Student list expansion is simulated for this demo.')} className="w-full mt-4 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors">
            View All Students
          </button>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
