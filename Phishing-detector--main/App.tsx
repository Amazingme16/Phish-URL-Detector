import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Search, Activity, Lock, AlertOctagon } from 'lucide-react';
import { analyzeUrlWithGemini } from './services/geminiService';
import { AnalysisResult, AnalysisStatus, ThreatLevel } from './types';
import FeatureChart from './components/FeatureChart';
import ProbabilityGauge from './components/ProbabilityGauge';

const App: React.FC = () => {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState<AnalysisStatus>(AnalysisStatus.IDLE);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    // Basic client-side validation
    if (!url.includes('.') || url.length < 4) {
      setError("Please enter a valid URL.");
      return;
    }

    setStatus(AnalysisStatus.ANALYZING);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeUrlWithGemini(url);
      setResult(data);
      setStatus(AnalysisStatus.COMPLETED);
    } catch (err: any) {
      setStatus(AnalysisStatus.ERROR);
      setError(err.message || "An unexpected error occurred.");
    }
  };

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <header className="bg-surface border-b border-slate-700 py-4 sticky top-0 z-50">
        <div className="container mx-auto px-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="w-8 h-8 text-primary" />
            <h1 className="text-xl font-bold tracking-tight text-white">
              PhishGuard <span className="text-primary font-light">AI</span>
            </h1>
          </div>
          <div className="text-xs text-slate-400 hidden sm:block">
            Powered by Gemini 2.5 Flash
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow container mx-auto px-4 py-8 max-w-5xl">
        
        {/* Intro */}
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">
            Intelligent Phishing Detection
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Uses simulated logistic regression analysis powered by Gemini AI to detect malicious URLs, analyzing patterns, domain reputation, and structural anomalies.
          </p>
        </div>

        {/* Input Section */}
        <section className="max-w-3xl mx-auto mb-12">
          <form onSubmit={handleAnalyze} className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-teal-500 rounded-lg blur opacity-30 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative flex items-center bg-surface rounded-lg p-2 shadow-2xl">
              <Lock className="w-5 h-5 text-slate-400 ml-3" />
              <input
                type="text"
                placeholder="Enter URL to analyze (e.g., http://suspicious-bank-login.com)"
                className="w-full bg-transparent border-none focus:ring-0 text-white placeholder-slate-500 px-4 py-3"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <button
                type="submit"
                disabled={status === AnalysisStatus.ANALYZING}
                className={`
                  ml-2 px-6 py-3 rounded-md font-semibold text-white transition-all
                  ${status === AnalysisStatus.ANALYZING 
                    ? 'bg-slate-600 cursor-not-allowed' 
                    : 'bg-primary hover:bg-blue-600 shadow-lg shadow-blue-500/30'}
                `}
              >
                {status === AnalysisStatus.ANALYZING ? (
                  <div className="flex items-center">
                    <Activity className="w-4 h-4 animate-spin mr-2" />
                    Scanning...
                  </div>
                ) : (
                  <div className="flex items-center">
                    <Search className="w-4 h-4 mr-2" />
                    Analyze
                  </div>
                )}
              </button>
            </div>
          </form>
          {error && (
            <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded text-red-200 text-sm flex items-center">
              <AlertOctagon className="w-4 h-4 mr-2" />
              {error}
            </div>
          )}
        </section>

        {/* Results Section */}
        {status === AnalysisStatus.COMPLETED && result && (
          <div className="animate-fade-in-up space-y-6">
            
            {/* Top Grid: Gauge & Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Gauge Card */}
              <div className="md:col-span-1">
                <ProbabilityGauge 
                  probability={result.probability} 
                  threatLevel={result.threatLevel} 
                />
              </div>

              {/* Summary Card */}
              <div className="md:col-span-2 bg-surface rounded-xl p-6 border border-slate-700 shadow-lg flex flex-col justify-center">
                <h3 className="text-lg font-semibold text-white mb-2 flex items-center">
                  <Activity className="w-5 h-5 text-primary mr-2" />
                  Analysis Summary
                </h3>
                <p className="text-slate-300 leading-relaxed text-sm md:text-base">
                  {result.reasoning}
                </p>
                <div className="mt-4 pt-4 border-t border-slate-700 flex flex-wrap gap-2">
                   {result.threatLevel === ThreatLevel.PHISHING ? (
                     <span className="flex items-center text-red-400 text-sm font-medium">
                       <AlertTriangle className="w-4 h-4 mr-1" /> Dangerous Pattern Detected
                     </span>
                   ) : result.threatLevel === ThreatLevel.SUSPICIOUS ? (
                     <span className="flex items-center text-yellow-400 text-sm font-medium">
                       <AlertTriangle className="w-4 h-4 mr-1" /> Caution Advised
                     </span>
                   ) : (
                     <span className="flex items-center text-green-400 text-sm font-medium">
                       <CheckCircle className="w-4 h-4 mr-1" /> No Threats Detected
                     </span>
                   )}
                </div>
              </div>
            </div>

            {/* Bottom: Feature Chart */}
            <div className="w-full">
               <FeatureChart features={result.features} />
            </div>

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 mt-12 bg-slate-900">
        <div className="container mx-auto px-4 text-center text-slate-500 text-xs">
          <p className="mb-2">
            PhishGuard AI uses advanced heuristic analysis and machine learning simulation. 
          </p>
          <p>
            Disclaimer: This tool is for educational and assistive purposes. Always verify URLs manually and use dedicated antivirus software.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;