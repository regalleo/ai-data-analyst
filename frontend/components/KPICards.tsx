'use client';

import { TrendingUp, TrendingDown, Database, DollarSign, Hash, Users, Tag } from 'lucide-react';

interface KPICard {
  title: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: string;
}

interface KPICardsProps {
  kpis: KPICard[];
}

export default function KPICards({ kpis }: KPICardsProps) {
  if (!kpis || kpis.length === 0) return null;

  const getIcon = (iconName?: string) => {
    const iconProps = { className: "w-5 h-5" };
    
    switch (iconName) {
      case 'database':
        return <Database {...iconProps} />;
      case 'dollar-sign':
        return <DollarSign {...iconProps} />;
      case 'hash':
        return <Hash {...iconProps} />;
      case 'users':
        return <Users {...iconProps} />;
      case 'tag':
        return <Tag {...iconProps} />;
      case 'trending-up':
        return <TrendingUp {...iconProps} />;
      default:
        return <Database {...iconProps} />;
    }
  };

  const getTrendColor = (trend?: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-400';
      case 'down':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4" />;
      case 'down':
        return <TrendingDown className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-4">
      {kpis.map((kpi, index) => (
        <div
          key={index}
          className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg p-4 border border-gray-700 hover:border-blue-500 transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/20"
        >
          <div className="flex items-start justify-between mb-2">
            <div className={`p-2 rounded-lg bg-blue-500/10 ${getTrendColor(kpi.trend)}`}>
              {getIcon(kpi.icon)}
            </div>
            {kpi.change && (
              <div className={`flex items-center gap-1 text-xs font-medium ${getTrendColor(kpi.trend)}`}>
                {getTrendIcon(kpi.trend)}
                <span>{kpi.change}</span>
              </div>
            )}
          </div>
          
          <div className="mt-2">
            <h3 className="text-2xl font-bold text-white mb-1">{kpi.value}</h3>
            <p className="text-xs text-gray-400 font-medium">{kpi.title}</p>
          </div>
        </div>
      ))}
    </div>
  );
}