/**
 * 🎯 ParsingProgressBar - Composant React avec WebSocket temps réel
 * PROMPT 2 - SuperSmartMatch V2 - Barre de progression ultra-responsive
 */

import React, { useState, useEffect, useRef } from 'react';
import { AlertCircle, CheckCircle2, Loader2, Wifi, WifiOff } from 'lucide-react';

interface ProgressData {
  task_id: string;
  status: 'processing' | 'completed' | 'error';
  progress: number;
  confidence: number;
  current_step: string;
  eta_seconds?: number;
}

interface ParsingProgressBarProps {
  taskId: string;
  wsUrl: string;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
  type?: 'cv' | 'job';
  className?: string;
}

export const ParsingProgressBar: React.FC<ParsingProgressBarProps> = ({
  taskId,
  wsUrl,
  onComplete,
  onError,
  type = 'cv',
  className = ''
}) => {
  const [progress, setProgress] = useState<ProgressData>({
    task_id: taskId,
    status: 'processing',
    progress: 0,
    confidence: 0,
    current_step: 'Initialisation...'
  });
  
  const [connected, setConnected] = useState(false);
  const [animatedProgress, setAnimatedProgress] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const animationRef = useRef<number>();

  // Animation fluide de la barre de progression
  useEffect(() => {
    const animate = () => {
      setAnimatedProgress(prev => {
        const diff = progress.progress - prev;
        if (Math.abs(diff) < 0.1) return progress.progress;
        return prev + diff * 0.1;
      });
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animationRef.current = requestAnimationFrame(animate);
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [progress.progress]);

  // Connexion WebSocket
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}${wsUrl}`;
        
        wsRef.current = new WebSocket(wsUrl);
        
        wsRef.current.onopen = () => {
          setConnected(true);
          console.log(`WebSocket connected for ${type} parsing:`, taskId);
        };
        
        wsRef.current.onmessage = (event) => {
          try {
            const data: ProgressData = JSON.parse(event.data);
            setProgress(data);
            
            if (data.status === 'completed' && onComplete) {
              onComplete(data);
            } else if (data.status === 'error' && onError) {
              onError(data.current_step);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnected(false);
          if (onError) {
            onError('Erreur de connexion WebSocket');
          }
        };
        
        wsRef.current.onclose = () => {
          setConnected(false);
          console.log('WebSocket disconnected');
        };
        
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [taskId, wsUrl, onComplete, onError, type]);

  // Formatage du temps restant
  const formatETA = (seconds?: number): string => {
    if (!seconds) return '';
    if (seconds < 60) return `${seconds}s restantes`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s restantes`;
  };

  // Couleurs selon le type et status
  const getProgressColor = (): string => {
    if (progress.status === 'error') return 'bg-red-500';
    if (progress.status === 'completed') return 'bg-green-500';
    return type === 'cv' ? 'bg-blue-500' : 'bg-purple-500';
  };

  const getBackgroundColor = (): string => {
    if (progress.status === 'error') return 'bg-red-50';
    if (progress.status === 'completed') return 'bg-green-50';
    return type === 'cv' ? 'bg-blue-50' : 'bg-purple-50';
  };

  const getTextColor = (): string => {
    if (progress.status === 'error') return 'text-red-700';
    if (progress.status === 'completed') return 'text-green-700';
    return type === 'cv' ? 'text-blue-700' : 'text-purple-700';
  };

  const getIcon = () => {
    if (progress.status === 'error') {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
    if (progress.status === 'completed') {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    }
    return <Loader2 className="w-5 h-5 animate-spin text-blue-500" />;
  };

  return (
    <div className={`w-full space-y-4 ${className}`}>
      {/* Header avec statut de connexion */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {getIcon()}
          <h3 className={`font-semibold ${getTextColor()}`}>
            {type === 'cv' ? 'Parsing CV' : 'Parsing Offre d\'emploi'}
          </h3>
        </div>
        
        <div className="flex items-center space-x-2">
          {connected ? (
            <Wifi className="w-4 h-4 text-green-500" />
          ) : (
            <WifiOff className="w-4 h-4 text-red-500" />
          )}
          <span className="text-sm text-gray-500">
            {connected ? 'Connecté' : 'Déconnecté'}
          </span>
        </div>
      </div>

      {/* Barre de progression principale */}
      <div className={`rounded-lg p-4 ${getBackgroundColor()}`}>
        <div className="space-y-3">
          {/* Barre de progression */}
          <div className="relative">
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-300 ease-out ${getProgressColor()}`}
                style={{ 
                  width: `${animatedProgress}%`,
                  background: progress.status === 'processing' 
                    ? `linear-gradient(90deg, ${type === 'cv' ? '#3B82F6' : '#8B5CF6'} 0%, ${type === 'cv' ? '#60A5FA' : '#A78BFA'} 50%, ${type === 'cv' ? '#3B82F6' : '#8B5CF6'} 100%)`
                    : undefined,
                  backgroundSize: '200% 100%',
                  animation: progress.status === 'processing' ? 'shimmer 2s infinite linear' : 'none'
                }}
              />
            </div>
            
            {/* Pourcentage affiché sur la barre */}
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-semibold text-white drop-shadow-lg">
                {Math.round(animatedProgress)}%
              </span>
            </div>
          </div>

          {/* Informations détaillées */}
          <div className="flex items-center justify-between text-sm">
            <span className={`font-medium ${getTextColor()}`}>
              {progress.current_step}
            </span>
            
            <div className="flex items-center space-x-4">
              {/* Score de confiance */}
              {progress.confidence > 0 && (
                <div className="flex items-center space-x-1">
                  <span className="text-gray-600">Confiance:</span>
                  <span 
                    className={`font-semibold ${
                      progress.confidence >= 0.8 
                        ? 'text-green-600' 
                        : progress.confidence >= 0.6 
                        ? 'text-yellow-600' 
                        : 'text-red-600'
                    }`}
                  >
                    {Math.round(progress.confidence * 100)}%
                  </span>
                </div>
              )}
              
              {/* Temps restant */}
              {progress.eta_seconds && progress.status === 'processing' && (
                <span className="text-gray-500">
                  {formatETA(progress.eta_seconds)}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Étapes du processus */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { step: 1, label: 'Upload', min: 0 },
          { step: 2, label: 'Extraction', min: 20 },
          { step: 3, label: 'Analyse IA', min: 40 },
          { step: 4, label: 'Finalisation', min: 80 }
        ].map(({ step, label, min }) => (
          <div 
            key={step}
            className={`text-center p-2 rounded transition-all duration-300 ${
              progress.progress >= min
                ? `${getBackgroundColor()} ${getTextColor()}`
                : 'bg-gray-100 text-gray-400'
            }`}
          >
            <div className={`w-6 h-6 rounded-full mx-auto mb-1 flex items-center justify-center text-xs font-bold ${
              progress.progress >= min
                ? `${getProgressColor()} text-white`
                : 'bg-gray-300 text-gray-500'
            }`}>
              {progress.progress > min + 15 ? '✓' : step}
            </div>
            <div className="text-xs font-medium">{label}</div>
          </div>
        ))}
      </div>

      {/* Task ID pour debug */}
      {process.env.NODE_ENV === 'development' && (
        <div className="text-xs text-gray-400 font-mono">
          Task ID: {taskId}
        </div>
      )}

      {/* Styles pour l'animation shimmer */}
      <style jsx>{`
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
      `}</style>
    </div>
  );
};

export default ParsingProgressBar;
