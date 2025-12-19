import React from 'react';
import { ThreatLevel } from '../types';

interface ProbabilityGaugeProps {
  probability: number;
  threatLevel: ThreatLevel;
}

const ProbabilityGauge: React.FC<ProbabilityGaugeProps> = ({ probability, threatLevel }) => {
  // Convert 0-1 to 0-100
  const percentage = Math.round(probability * 100);
  
  let colorClass = "text-green-500";
  let bgClass = "bg-green-500";
  let label = "Legitimate";

  if (threatLevel === ThreatLevel.PHISHING) {
    colorClass = "text-red-500";
    bgClass = "bg-red-500";
    label = "Phishing";
  } else if (threatLevel === ThreatLevel.SUSPICIOUS) {
    colorClass = "text-yellow-500";
    bgClass = "bg-yellow-500";
    label = "Suspicious";
  }

  // Calculate rotation for a semi-circle gauge (0 to 180 degrees)
  const rotation = (percentage / 100) * 180;

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-slate-800 rounded-xl border border-slate-700 shadow-lg">
      <div className="relative w-48 h-24 overflow-hidden mb-2">
        {/* Gauge Background */}
        <div className="absolute top-0 left-0 w-full h-full bg-slate-700 rounded-t-full"></div>
        
        {/* Gauge Fill (Simulated with transform) */}
        <div 
            className={`absolute top-0 left-0 w-full h-full origin-bottom transform transition-transform duration-1000 ease-out rounded-t-full ${bgClass} opacity-80`}
            style={{ transform: `rotate(${rotation - 180}deg)` }}
        ></div>

        {/* Needle Origin Cover (creates the arc effect) */}
        <div className="absolute bottom-0 left-1/2 w-36 h-18 -ml-[4.5rem] bg-slate-800 rounded-t-full"></div>
      </div>
      
      <div className="text-center z-10 -mt-8">
        <span className={`text-4xl font-bold ${colorClass}`}>{percentage}%</span>
        <p className="text-slate-400 text-sm mt-1 uppercase tracking-wider">Phishing Probability</p>
      </div>

      <div className={`mt-4 px-4 py-1 rounded-full text-sm font-bold border ${colorClass.replace('text-', 'border-')} ${colorClass} bg-opacity-10 bg-white`}>
        VERDICT: {label}
      </div>
    </div>
  );
};

export default ProbabilityGauge;