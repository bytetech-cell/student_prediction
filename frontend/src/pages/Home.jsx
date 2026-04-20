import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ShieldAlert, Sparkles, TrendingUp } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="max-w-5xl mx-auto space-y-12 animate-in fade-in slide-in-from-bottom-6 duration-700">
      
      {/* Hero Section */}
      <div className="text-center space-y-6 pt-12 lg:pt-20">
        <div className="inline-flex items-center space-x-2 bg-indigo-50 text-indigo-700 px-4 py-1.5 rounded-full text-sm font-semibold mb-2">
          <Sparkles className="w-4 h-4" />
          <span>AI-Powered Prediction Engine</span>
        </div>
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
          Supercharge Academic Success with <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-indigo-600">EduPredict</span>
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Leverage a robust Soft Voting Ensemble (RF, SVM, LR) to predict student performance, detect early risks, and generate personalized study pathways with 91.1% accuracy.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
          <button 
            onClick={() => navigate('/predict')}
            className="group relative flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(79,70,229,0.4)] hover:shadow-[0_0_30px_rgba(79,70,229,0.7)] hover:-translate-y-1"
          >
            <span>Run Prediction Engine</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            <div className="absolute inset-0 rounded-xl bg-white/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity"></div>
          </button>
          <button 
            onClick={() => navigate('/analytics')}
            className="flex items-center space-x-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-8 py-4 rounded-xl font-bold transition-all shadow-sm hover:shadow-md hover:-translate-y-1"
          >
            <span>View System Analytics</span>
          </button>
        </div>
      </div>

      {/* Value Pillars */}
      <div className="grid md:grid-cols-3 gap-6 pt-10">
        <div className="glass-card p-6 flex flex-col items-center text-center space-y-4 hover:-translate-y-1 transition-transform duration-300">
          <div className="w-14 h-14 bg-red-50 text-red-500 rounded-2xl flex items-center justify-center">
            <ShieldAlert size={28} />
          </div>
          <h3 className="text-xl font-bold text-slate-800">Early Risk Detection</h3>
          <p className="text-slate-600 text-sm">
            Identify high-risk students early with an advanced scoring system to prevent academic dropout or failure.
          </p>
        </div>

        <div className="glass-card p-6 flex flex-col items-center text-center space-y-4 hover:-translate-y-1 transition-transform duration-300 transform md:-translate-y-4">
          <div className="w-14 h-14 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center">
            <TrendingUp size={28} />
          </div>
          <h3 className="text-xl font-bold text-slate-800">Data-Driven Intervention</h3>
          <p className="text-slate-600 text-sm">
            Intervene before it's too late using feature importance explanations identifying exact friction points.
          </p>
        </div>

        <div className="glass-card p-6 flex flex-col items-center text-center space-y-4 hover:-translate-y-1 transition-transform duration-300">
          <div className="w-14 h-14 bg-emerald-50 text-emerald-500 rounded-2xl flex items-center justify-center">
            <Sparkles size={28} />
          </div>
          <h3 className="text-xl font-bold text-slate-800">Personalized Learning</h3>
          <p className="text-slate-600 text-sm">
            Generate dynamic, spaced-repetition study schedules individually tailored to weak areas and availability.
          </p>
        </div>
      </div>

    </div>
  );
};

export default Home;
