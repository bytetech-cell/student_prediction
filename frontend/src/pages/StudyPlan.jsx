import React, { useEffect, useState } from 'react';
import { Calendar as CalendarIcon, Filter, Layers, BookOpen, Coffee, RefreshCw, Info } from 'lucide-react';
import clsx from 'clsx';
import { Link } from 'react-router-dom';

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const generateSchedule = (riskLevel) => {
  let slotsPerDay = 4;
  let focusSlots = 1;
  
  if (riskLevel === 'High Risk') {
    slotsPerDay = 5;
    focusSlots = 2; // Extra focus for high risk
  } else if (riskLevel === 'Low Risk') {
    slotsPerDay = 3;
    focusSlots = 1; // Standard focus for low risk
  }

  return DAYS.map(day => {
    const slots = [];
    for(let i=0; i<slotsPerDay; i++) {
       if(day === 'Sun' && i >= slotsPerDay - 2) {
         slots.push({ type: 'break', title: 'Free Time/Break', color: 'bg-slate-100 text-slate-600', icon: Coffee });
       } else if (i === 1 && (day === 'Tue' || day === 'Thu')) {
         slots.push({ type: 'revision', title: 'Spaced Repetition', color: 'bg-indigo-100 text-indigo-700 border-indigo-200', icon: RefreshCw });
       } else if (i < focusSlots + 2 && i >= 2) {
         slots.push({ type: 'study', title: 'Focus Subject', color: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: BookOpen });
       } else {
         slots.push({ type: 'study', title: 'Core Study', color: 'bg-white text-slate-800 border-slate-200', icon: Layers });
       }
    }
    return { day, slots };
  });
};

const StudyPlan = () => {
  const [schedule, setSchedule] = useState([]);
  const [riskData, setRiskData] = useState(null);

  useEffect(() => {
    const cached = localStorage.getItem('lastPrediction');
    let risk = 'Medium Risk';
    if (cached) {
      const parsed = JSON.parse(cached);
      if (parsed?.result?.risk) {
        risk = parsed.result.risk;
        setRiskData({ risk, score: parsed.result.score });
      }
    } else {
      setRiskData({ risk: 'Default', score: null });
    }
    setSchedule(generateSchedule(risk));
  }, []);

  if (schedule.length === 0) return null;

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Dynamic Study Schedule</h1>
          <p className="text-slate-500 text-sm mt-1">AI-generated timetable utilizing spaced repetition to maximize retention.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button onClick={() => alert('Parameter adjustment is simulated in this demo.')} className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 shadow-sm rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">
            <Filter size={16} />
            <span>Adjust Parameters</span>
          </button>
          <button onClick={() => alert('Calendar export workflow is disabled in the prototype.')} className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-200 rounded-lg text-sm font-bold text-white transition-all">
            <CalendarIcon size={16} />
            <span>Export to Calendar</span>
          </button>
        </div>
      </div>

      {riskData?.score === null && (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-xl flex items-start space-x-3 text-sm">
           <Info className="shrink-0 w-5 h-5" />
           <div>
             <strong>Showing default schedule.</strong> You haven't run a prediction yet! <Link to="/predict" className="underline font-semibold hover:text-blue-900">Run one now</Link> to get a risk-tailored schedule dynamically generated based on your inputs.
           </div>
        </div>
      )}
      
      {riskData?.score !== null && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl flex items-start space-x-3 text-sm">
           <Info className="shrink-0 w-5 h-5" />
           <div>
             <strong>Personalized generated plan!</strong> Modulated for <span className="font-bold">{riskData.risk}</span> profile. Notice how the study blocks and focus slots natively adapt to address the weakest input metrics detected.
           </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap gap-4 pt-2">
        <div className="flex items-center space-x-2 text-sm">
          <div className="w-4 h-4 rounded bg-emerald-100 border border-emerald-200"></div>
          <span className="text-slate-600 font-medium">Focus Subjects (Weaknesses)</span>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <div className="w-4 h-4 rounded bg-indigo-100 border border-indigo-200"></div>
          <span className="text-slate-600 font-medium">Spaced Repetition (Revision)</span>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <div className="w-4 h-4 rounded bg-slate-100"></div>
          <span className="text-slate-600 font-medium">Breaks / Free</span>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4 pt-4">
        {schedule.map((col, idx) => (
          <div key={idx} className="space-y-4">
            <div className="text-center font-bold text-slate-700 uppercase tracking-widest text-sm bg-slate-100 py-2 rounded-lg">
              {col.day}
            </div>
            
            <div className="space-y-3">
              {col.slots.map((slot, sIdx) => {
                const Icon = slot.icon;
                return (
                  <div 
                    key={sIdx} 
                    className={clsx(
                      "p-4 rounded-xl border shadow-sm transition-all hover:-translate-y-1 hover:shadow-md cursor-pointer flex flex-col items-start space-y-2",
                      slot.color
                    )}
                  >
                    <Icon size={18} className="opacity-80" />
                    <span className="font-semibold text-sm">{slot.title}</span>
                    <span className="text-xs opacity-70">2 Hrs</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};

export default StudyPlan;
