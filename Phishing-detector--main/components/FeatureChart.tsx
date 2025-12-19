import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell
} from 'recharts';
import { FeatureWeight } from '../types';

interface FeatureChartProps {
  features: FeatureWeight[];
}

const FeatureChart: React.FC<FeatureChartProps> = ({ features }) => {
  // Process data for the chart
  const data = features.map(f => ({
    name: f.featureName,
    weight: f.weight,
    desc: f.description
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-600 p-3 rounded-lg shadow-xl text-xs sm:text-sm">
          <p className="font-bold text-slate-200 mb-1">{label}</p>
          <p className="text-slate-300">Weight: <span className={payload[0].value > 0 ? "text-red-400" : "text-green-400"}>{payload[0].value}</span></p>
          <p className="text-slate-400 italic mt-1 max-w-[200px]">{payload[0].payload.desc}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-[300px] sm:h-[400px] bg-slate-900/50 rounded-xl p-4 border border-slate-700">
      <h3 className="text-slate-300 text-sm font-semibold mb-4 text-center">Feature Contribution (Simulated Logistic Regression Weights)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
          <XAxis type="number" stroke="#94a3b8" fontSize={12} />
          <YAxis 
            dataKey="name" 
            type="category" 
            stroke="#94a3b8" 
            width={100} 
            fontSize={11}
            tickFormatter={(value) => value.length > 15 ? `${value.substring(0, 15)}...` : value}
          />
          <Tooltip content={<CustomTooltip />} cursor={{fill: '#334155', opacity: 0.4}} />
          <ReferenceLine x={0} stroke="#64748b" />
          <Bar dataKey="weight" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.weight > 0 ? '#ef4444' : '#22c55e'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FeatureChart;