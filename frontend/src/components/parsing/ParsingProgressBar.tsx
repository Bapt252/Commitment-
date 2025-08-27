/**
 * ParsingProgressBar - Composant de progression temps réel avec WebSocket
 * 
 * PROMPT 2 Features:
 * ✅ WebSocket streaming pour feedback <500ms
 * ✅ Indicateur de progression visuel et animé
 * ✅ Étapes de parsing détaillées
 * ✅ Gestion des erreurs et timeout
 * ✅ Score de confiance temps réel
 */

import React, { useState, useEffect, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

interface ParsingStep {
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  confidence?: number;
  duration?: number;
}

interface ParsingProgressBarProps {
  taskId: string;
  onComplete?: (data: any) => void;
  onError?: (error: string) => void;
  apiUrl?: string;
}

const ParsingProgressBar: React.FC<ParsingProgressBarProps> = ({
  taskId,
  onComplete,
  onError,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5051'
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<'connecting' | 'processing' | 'completed' | 'error'>('connecting');
  const [currentStep, setCurrentStep] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [steps, setSteps] = useState<ParsingStep[]>([
    { name: 'Connexion', status: 'processing', progress: 0 },
    { name: 'Extraction texte', status: 'pending', progress: 0 },
    { name: 'Analyse IA', status: 'pending', progress: 0 },
    { name: 'Validation', status: 'pending', progress: 0 },
    { name: 'Finalisation', status: 'pending', progress: 0 }
  ]);
  const [startTime] = useState(Date.now());
  const [elapsedTime, setElapsedTime] = useState(0);

  // Timer pour temps écoulé
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(Date.now() - startTime);
    }, 100);

    return () => clearInterval(timer);
  }, [startTime]);

  // Connexion WebSocket
  useEffect(() => {
    const newSocket = io(apiUrl, {
      transports: ['websocket'],
      timeout: 20000
    });

    newSocket.on('connect', () => {
      console.log('🔌 WebSocket connecté');
      newSocket.emit('subscribe_parsing', { taskId });
      updateStep('Connexion', 'completed', 100);
    });

    newSocket.on('parsing_progress', (data) => {
      console.log('📊 Progression reçue:', data);
      handleProgressUpdate(data);
    });

    newSocket.on('parsing_complete', (data) => {
      console.log('✅ Parsing terminé:', data);
      handleComplete(data);
    });

    newSocket.on('parsing_error', (error) => {
      console.error('❌ Erreur parsing:', error);
      handleError(error.message || 'Erreur inconnue');
    });

    newSocket.on('disconnect', () => {
      console.log('📡 WebSocket déconnecté');
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [taskId, apiUrl]);

  const updateStep = useCallback((stepName: string, newStatus: ParsingStep['status'], newProgress: number, stepConfidence?: number) => {
    setSteps(prev => prev.map(step => {
      if (step.name === stepName) {
        return {
          ...step,
          status: newStatus,
          progress: newProgress,
          confidence: stepConfidence,
          duration: newStatus === 'completed' ? Date.now() - startTime : undefined
        };
      }
      return step;
    }));
  }, [startTime]);

  const handleProgressUpdate = useCallback((data: any) => {
    const { progress: newProgress, step, confidence: stepConfidence, status: stepStatus } = data;
    
    setProgress(newProgress);
    setCurrentStep(step || 'En cours...');
    setConfidence(stepConfidence || 0);
    setStatus('processing');

    // Mise à jour des étapes
    if (step) {
      if (step.includes('extraction') || step.includes('texte')) {
        updateStep('Extraction texte', stepStatus || 'processing', newProgress, stepConfidence);
      } else if (step.includes('IA') || step.includes('analyse')) {
        updateStep('Analyse IA', stepStatus || 'processing', newProgress, stepConfidence);
      } else if (step.includes('validation')) {
        updateStep('Validation', stepStatus || 'processing', newProgress, stepConfidence);
      } else if (step.includes('finalisation')) {
        updateStep('Finalisation', stepStatus || 'processing', newProgress, stepConfidence);
      }
    }
  }, [updateStep]);

  const handleComplete = useCallback((data: any) => {
    setProgress(100);
    setStatus('completed');
    setCurrentStep('Terminé');
    updateStep('Finalisation', 'completed', 100, data.confidence);
    onComplete?.(data);
  }, [onComplete, updateStep]);

  const handleError = useCallback((error: string) => {
    setStatus('error');
    setCurrentStep(`Erreur: ${error}`);
    onError?.(error);
  }, [onError]);

  const getStepIcon = (step: ParsingStep) => {
    switch (step.status) {
      case 'completed':
        return '✅';
      case 'processing':
        return '🔄';
      case 'error':
        return '❌';
      default:
        return '⏳';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'processing':
        return confidence > 0.8 ? 'bg-blue-500' : 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* En-tête avec statut global */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className={`w-4 h-4 rounded-full ${getStatusColor()} ${status === 'processing' ? 'animate-pulse' : ''}`}></div>
          <h3 className="text-lg font-semibold text-gray-800">
            {status === 'completed' ? 'Parsing terminé' : 
             status === 'error' ? 'Erreur de parsing' :
             'Parsing en cours...'}
          </h3>
        </div>
        <div className="text-sm text-gray-600">
          {formatTime(elapsedTime)}
        </div>
      </div>

      {/* Barre de progression principale */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">{currentStep}</span>
          <span className="text-sm text-gray-500">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-300 ${getStatusColor()}`}
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Score de confiance */}
      {confidence > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Score de confiance</span>
            <span className="text-sm font-semibold" style={{ 
              color: confidence > 0.8 ? '#10B981' : confidence > 0.6 ? '#F59E0B' : '#EF4444' 
            }}>
              {Math.round(confidence * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="h-2 rounded-full transition-all duration-300"
              style={{ 
                width: `${confidence * 100}%`,
                backgroundColor: confidence > 0.8 ? '#10B981' : confidence > 0.6 ? '#F59E0B' : '#EF4444'
              }}
            ></div>
          </div>
        </div>
      )}

      {/* Détail des étapes */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Étapes de traitement</h4>
        {steps.map((step, index) => (
          <div key={index} className="flex items-center space-x-3">
            <span className="text-lg">{getStepIcon(step)}</span>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className={`text-sm ${step.status === 'completed' ? 'text-gray-800 font-medium' : 'text-gray-600'}`}>
                  {step.name}
                </span>
                {step.confidence && (
                  <span className="text-xs text-gray-500">
                    {Math.round(step.confidence * 100)}%
                  </span>
                )}
                {step.duration && (
                  <span className="text-xs text-gray-400">
                    {step.duration}ms
                  </span>
                )}
              </div>
              {step.status === 'processing' && (
                <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                  <div 
                    className="h-1 bg-blue-500 rounded-full transition-all duration-300 animate-pulse"
                    style={{ width: `${step.progress}%` }}
                  ></div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Messages d'état */}
      {status === 'error' && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-700">Une erreur est survenue pendant le parsing. Veuillez réessayer.</p>
        </div>
      )}

      {status === 'completed' && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-700">
            ✅ Parsing terminé avec succès en {formatTime(elapsedTime)} 
            (confiance: {Math.round(confidence * 100)}%)
          </p>
        </div>
      )}
    </div>
  );
};

export default ParsingProgressBar;