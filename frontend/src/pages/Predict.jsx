import React, { useState } from 'react';
import { preventDefault } from 'react';
import { predictPerformance } from '../services/mockApi';
import { AlertTriangle, BrainCircuit, Activity, Clock, BarChart3, CheckCircle2 } from 'lucide-react';
import clsx from 'clsx';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Predict = () => {
  const [formData, setFormData] = useState({
    studyHours: 4,
    assignmentMarks: 75,
    attendance: 80,
    sleep: 7,
    socialMedia: 3,
    sgpa: 7.5,
    extracurricular: 'Moderate'
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await predictPerformance(formData);
      setResult(res);
      localStorage.setItem('lastPrediction', JSON.stringify({ form: formData, result: res }));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    if (risk === 'Low Risk') return 'text-emerald-500 bg-emerald-50 border-emerald-200';
    if (risk === 'Medium Risk') return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-500 bg-red-50 border-red-200';
  };

  const getRiskGradientString = (risk) => {
    if (risk === 'Low Risk') return 'from-emerald-400 to-emerald-600';
    if (risk === 'Medium Risk') return 'from-yellow-400 to-yellow-600';
    return 'from-red-500 to-red-700';
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Prediction Engine</h1>
          <p className="text-slate-500 text-sm">Input student metrics to compute risk score and insights.</p>
        </div>
        {result && (
          <div className="flex items-center space-x-2 bg-slate-100 px-3 py-1.5 rounded-full border border-slate-200">
            <Clock size={14} className="text-slate-400" />
            <span className="text-xs font-medium text-slate-600">Prediction latency &lt; 200ms ({result.latency})</span>
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Form Section */}
        <div className="lg:col-span-4 glass-card p-6 h-fit">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-sm font-semibold text-slate-700 flex justify-between">
                <span>Study Hours / Day</span>
                <span className="text-indigo-600">{formData.studyHours}h</span>
              </label>
              <input type="range" min="0" max="14" step="0.5" 
                value={formData.studyHours} 
                onChange={e => setFormData({...formData, studyHours: e.target.value})}
                className="w-full accent-indigo-600 mt-2" 
              />
            </div>
            
            <div>
              <label className="text-sm font-semibold text-slate-700 flex justify-between">
                <span>Assignment Marks (%)</span>
                <span className="text-indigo-600">{formData.assignmentMarks}%</span>
              </label>
              <input type="range" min="0" max="100" 
                value={formData.assignmentMarks} 
                onChange={e => setFormData({...formData, assignmentMarks: e.target.value})}
                className="w-full accent-indigo-600 mt-2" 
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 flex justify-between">
                <span>Attendance (%)</span>
                <span className="text-indigo-600">{formData.attendance}%</span>
              </label>
              <input type="range" min="0" max="100" 
                value={formData.attendance} 
                onChange={e => setFormData({...formData, attendance: e.target.value})}
                className="w-full accent-indigo-600 mt-2" 
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 flex justify-between">
                <span>Sleep Hours</span>
                <span className="text-indigo-600">{formData.sleep}h</span>
              </label>
              <input type="range" min="0" max="12" step="0.5"
                value={formData.sleep} 
                onChange={e => setFormData({...formData, sleep: e.target.value})}
                className="w-full accent-indigo-600 mt-2" 
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 flex justify-between">
                <span>Social Media (hrs/day)</span>
                <span className="text-indigo-600">{formData.socialMedia}h</span>
              </label>
              <input type="range" min="0" max="10" step="0.5"
                value={formData.socialMedia} 
                onChange={e => setFormData({...formData, socialMedia: e.target.value})}
                className="w-full accent-indigo-600 mt-2" 
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700 flex justify-between">
                <span>Previous SGPA</span>
                <span className="text-indigo-600">{formData.sgpa}</span>
              </label>
              <input type="range" min="0" max="10" step="0.1"
                value={formData.sgpa} 
                onChange={e => setFormData({...formData, sgpa: e.target.value})}
                className="w-full accent-indigo-600 mt-2" 
              />
            </div>

            <div>
              <label className="text-sm font-semibold text-slate-700">Extracurricular Load</label>
              <select 
                value={formData.extracurricular}
                onChange={e => setFormData({...formData, extracurricular: e.target.value})}
                className="w-full mt-2 border border-slate-200 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
              >
                <option value="Balanced">Balanced</option>
                <option value="Moderate">Moderate</option>
                <option value="Heavy">Heavy</option>
              </select>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="group relative w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-4 px-4 rounded-xl transition-all disabled:opacity-70 flex justify-center items-center space-x-2 shadow-[0_0_15px_rgba(79,70,229,0.4)] hover:shadow-[0_0_25px_rgba(79,70,229,0.7)] hover:-translate-y-0.5 overflow-hidden"
            >
              <div className="absolute inset-0 bg-white/20 blur-[8px] opacity-0 group-hover:opacity-100 transition-opacity"></div>
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin z-10" />
              ) : (
                <div className="flex items-center space-x-2 z-10">
                  <BrainCircuit size={18} />
                  <span>Generate Prediction</span>
                </div>
              )}
            </button>
          </form>
        </div>

        {/* Results Section */}
        {result ? (
          <div className="lg:col-span-8 flex flex-col space-y-6 animate-in slide-in-from-right-8 duration-500">
            {/* Risk Card */}
            <div className={clsx("glass-card p-6 border-l-4", getRiskColor(result.risk).split(' ')[2])}>
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-slate-800 mb-1">Risk Assessment</h2>
                  <div className={clsx("inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-sm font-bold", getRiskColor(result.risk))}>
                     {result.risk === 'High Risk' && <AlertTriangle size={16} />}
                     {result.risk === 'Low Risk' && <CheckCircle2 size={16} />}
                     {result.risk === 'Medium Risk' && <Activity size={16} />}
                     <span>{result.risk}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-extrabold text-slate-800">{result.score}</div>
                  <div className="text-xs text-slate-500 font-medium">/ 100 SCORE</div>
                </div>
              </div>
              
              <div className="mt-6">
                <div className="flex justify-between text-xs font-semibold mb-1 text-slate-500">
                  <span>High Risk (0-41)</span>
                  <span>Medium (42-67)</span>
                  <span>Low Risk (68-100)</span>
                </div>
                <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden flex relative">
                  <div className={clsx("h-full transition-all duration-1000 ease-out bg-gradient-to-r", getRiskGradientString(result.risk))} style={{ width: `${result.score}%` }} />
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Explainability (XAI) */}
              <div className="glass-card p-6">
                <div className="flex items-center space-x-2 mb-4 text-slate-800">
                  <BarChart3 className="text-indigo-500" />
                  <h3 className="font-bold">Explainability (XAI)</h3>
                </div>
                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={result.features} layout="vertical" margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                      <XAxis type="number" hide />
                      <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#64748b'}} width={100} />
                      <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}/>
                      <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                        {result.features.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.type === 'negative' ? '#ef4444' : '#6366f1'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-sm mt-4 p-3 bg-slate-50 rounded-lg text-slate-600 border border-slate-100 leading-relaxed font-medium">
                  <strong className="text-slate-800">Why this prediction?</strong> This prediction is heavily influenced by {result.features[0].name.toLowerCase()} (positive impact) and {result.features.find(f => f.type === 'negative')?.name.toLowerCase()} (negative impact).
                </p>
              </div>

              {/* Ensemble Contribution */}
              <div className="glass-card p-6">
                <div className="flex items-center space-x-2 mb-4 text-slate-800">
                  <BrainCircuit className="text-indigo-500" />
                  <h3 className="font-bold">Ensemble Impact</h3>
                </div>
                <div className="space-y-5 mt-4">
                  {[
                    { name: 'Random Forest', type: 'rf', color: 'bg-emerald-500' },
                    { name: 'Support Vector Machine', type: 'svm', color: 'bg-indigo-500' },
                    { name: 'Logistic Regression', type: 'lr', color: 'bg-slate-400' }
                  ].map((model) => (
                    <div key={model.type}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-semibold text-slate-700">{model.name}</span>
                        <span className="text-slate-500 font-medium">{(result.ensemble[model.type].weight * 100).toFixed(0)}% weight</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2">
                        <div className={`${model.color} h-2 rounded-full`} style={{ width: `${(result.ensemble[model.type].weight * 100)}%` }}></div>
                      </div>
                      <div className="text-xs text-slate-400 mt-1">Predicted Score: {result.ensemble[model.type].score}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

          </div>
        ) : (
          <div className="lg:col-span-8 flex flex-col items-center justify-center p-12 glass-card h-full opacity-60">
             <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-4">
               <BrainCircuit size={32} className="text-slate-400" />
             </div>
             <h3 className="text-xl font-bold text-slate-600">Awaiting Data</h3>
             <p className="text-slate-400 mt-2 text-center max-w-sm">Fill out the student metrics form and generate a prediction to see AI-driven insights and explainability metrics.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Predict;
