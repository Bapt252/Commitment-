/**
 * ConfidenceIndicator - Indicateur visuel de confiance par champ
 * 
 * PROMPT 2 Features:
 * ✅ Scoring de confiance par champ extrait
 * ✅ Indicateurs visuels colorés et animés
 * ✅ Tooltips informatifs
 * ✅ Différentes tailles et variantes
 */

import React from 'react';

interface ConfidenceIndicatorProps {
  confidence: number; // 0 à 1
  size?: 'sm' | 'md' | 'lg';
  variant?: 'bar' | 'circle' | 'badge';
  showPercentage?: boolean;
  showTooltip?: boolean;
  className?: string;
}

const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  confidence,
  size = 'md',
  variant = 'bar',
  showPercentage = true,
  showTooltip = true,
  className = ''
}) => {
  const percentage = Math.round(confidence * 100);
  
  // Déterminer la couleur et le niveau de confiance
  const getConfidenceLevel = () => {
    if (confidence >= 0.9) return { level: 'Excellent', color: 'green', bgColor: 'bg-green-500' };
    if (confidence >= 0.8) return { level: 'Très bon', color: 'green', bgColor: 'bg-green-400' };
    if (confidence >= 0.7) return { level: 'Bon', color: 'blue', bgColor: 'bg-blue-500' };
    if (confidence >= 0.6) return { level: 'Moyen', color: 'yellow', bgColor: 'bg-yellow-500' };
    if (confidence >= 0.4) return { level: 'Faible', color: 'orange', bgColor: 'bg-orange-500' };
    return { level: 'Très faible', color: 'red', bgColor: 'bg-red-500' };
  };

  const { level, color, bgColor } = getConfidenceLevel();

  // Tailles des composants
  const sizes = {
    sm: { bar: 'h-1', circle: 'w-4 h-4', text: 'text-xs', badge: 'text-xs px-2 py-1' },
    md: { bar: 'h-2', circle: 'w-6 h-6', text: 'text-sm', badge: 'text-sm px-3 py-1' },
    lg: { bar: 'h-3', circle: 'w-8 h-8', text: 'text-base', badge: 'text-base px-4 py-2' }
  };

  const sizeClasses = sizes[size];

  // Rendu selon la variante
  const renderIndicator = () => {
    switch (variant) {
      case 'circle':
        return (
          <div className={`relative ${sizeClasses.circle} ${className}`} title={showTooltip ? `${level}: ${percentage}%` : undefined}>
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              {/* Cercle de fond */}
              <path
                className="fill-none stroke-gray-200"
                strokeWidth="3"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              {/* Cercle de progression */}
              <path
                className={`fill-none stroke-current transition-all duration-500 ease-in-out`}
                style={{ color: `var(--${color}-500)` }}
                strokeWidth="3"
                strokeDasharray={`${confidence * 100}, 100`}
                strokeLinecap="round"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            {size !== 'sm' && (
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`font-semibold ${sizeClasses.text}`} style={{ color: `var(--${color}-600)` }}>
                  {percentage}
                </span>
              </div>
            )}
          </div>
        );

      case 'badge':
        return (
          <span
            className={`inline-flex items-center rounded-full font-medium ${sizeClasses.badge} ${bgColor} text-white ${className}`}
            title={showTooltip ? `Confiance: ${level}` : undefined}
          >
            {showPercentage ? `${percentage}%` : level}
          </span>
        );

      case 'bar':
      default:
        return (
          <div className={`w-full ${className}`} title={showTooltip ? `${level}: ${percentage}%` : undefined}>
            {showPercentage && (
              <div className="flex justify-between items-center mb-1">
                <span className={`${sizeClasses.text} text-gray-600`}>Confiance</span>
                <span className={`${sizeClasses.text} font-semibold`} style={{ color: `var(--${color}-600)` }}>
                  {percentage}%
                </span>
              </div>
            )}
            <div className={`w-full bg-gray-200 rounded-full ${sizeClasses.bar} overflow-hidden`}>
              <div
                className={`${sizeClasses.bar} ${bgColor} rounded-full transition-all duration-500 ease-in-out`}
                style={{ width: `${percentage}%` }}
              >
                <div className="h-full bg-white bg-opacity-30 animate-pulse"></div>
              </div>
            </div>
            {size !== 'sm' && (
              <div className={`mt-1 ${sizeClasses.text} text-gray-500 text-center`}>
                {level}
              </div>
            )}
          </div>
        );
    }
  };

  return renderIndicator();
};

// Composant pour afficher plusieurs niveaux de confiance
interface ConfidenceLegendProps {
  className?: string;
}

const ConfidenceLegend: React.FC<ConfidenceLegendProps> = ({ className = '' }) => {
  const levels = [
    { range: '90-100%', label: 'Excellent', color: 'bg-green-500' },
    { range: '80-89%', label: 'Très bon', color: 'bg-green-400' },
    { range: '70-79%', label: 'Bon', color: 'bg-blue-500' },
    { range: '60-69%', label: 'Moyen', color: 'bg-yellow-500' },
    { range: '40-59%', label: 'Faible', color: 'bg-orange-500' },
    { range: '0-39%', label: 'Très faible', color: 'bg-red-500' }
  ];

  return (
    <div className={`p-4 bg-gray-50 rounded-lg ${className}`}>
      <h4 className="text-sm font-medium text-gray-700 mb-3">Niveaux de confiance</h4>
      <div className="space-y-2">
        {levels.map((level, index) => (
          <div key={index} className="flex items-center space-x-3">
            <div className={`w-4 h-2 rounded ${level.color}`}></div>
            <span className="text-sm text-gray-600">{level.range}</span>
            <span className="text-sm font-medium text-gray-800">{level.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export { ConfidenceIndicator, ConfidenceLegend };
export default ConfidenceIndicator;