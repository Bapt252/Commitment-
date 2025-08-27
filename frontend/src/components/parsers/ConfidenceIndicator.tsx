/**
 * 📊 ConfidenceIndicator - Composant React indicateur de confiance visuel
 * PROMPT 2 - SuperSmartMatch V2 - Score de confiance par champ en temps réel
 */

import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  ShieldCheck, 
  ShieldAlert, 
  ShieldX,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Eye,
  EyeOff,
  Info,
  CheckCircle2,
  AlertTriangle,
  XCircle
} from 'lucide-react';

interface FieldConfidence {
  field: string;
  confidence: number; // 0.0 - 1.0
  reasons: string[];
  suggestions?: string[];
  auto_corrected?: boolean;
  previous_confidence?: number;
}

interface ConfidenceIndicatorProps {
  fieldConfidences: FieldConfidence[];
  globalConfidence: number;
  showDetails?: boolean;
  onFieldClick?: (field: string) => void;
  type?: 'cv' | 'job';
  className?: string;
  compact?: boolean;
}

const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  fieldConfidences,
  globalConfidence,
  showDetails = true,
  onFieldClick,
  type = 'cv',
  className = '',
  compact = false
}) => {
  const [expandedField, setExpandedField] = useState<string | null>(null);
  const [showLowConfidence, setShowLowConfidence] = useState(true);
  const [animateChanges, setAnimateChanges] = useState(true);

  // Animation des changements de confiance
  useEffect(() => {
    setAnimateChanges(true);
    const timer = setTimeout(() => setAnimateChanges(false), 1000);
    return () => clearTimeout(timer);
  }, [fieldConfidences]);

  // Fonctions utilitaires
  const getConfidenceLevel = (confidence: number): 'excellent' | 'good' | 'fair' | 'poor' => {
    if (confidence >= 0.9) return 'excellent';
    if (confidence >= 0.7) return 'good';
    if (confidence >= 0.5) return 'fair';
    return 'poor';
  };

  const getConfidenceColor = (confidence: number): string => {
    const level = getConfidenceLevel(confidence);
    const colors = {
      excellent: 'text-green-600 bg-green-50 border-green-200',
      good: 'text-blue-600 bg-blue-50 border-blue-200',
      fair: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      poor: 'text-red-600 bg-red-50 border-red-200'
    };
    return colors[level];
  };

  const getConfidenceIcon = (confidence: number, size: string = 'w-4 h-4') => {
    const level = getConfidenceLevel(confidence);
    const iconProps = { className: size };
    
    switch (level) {
      case 'excellent': return <ShieldCheck {...iconProps} className={`${size} text-green-600`} />;
      case 'good': return <Shield {...iconProps} className={`${size} text-blue-600`} />;
      case 'fair': return <ShieldAlert {...iconProps} className={`${size} text-yellow-600`} />;
      case 'poor': return <ShieldX {...iconProps} className={`${size} text-red-600`} />;
    }
  };

  const getFieldDisplayName = (field: string): string => {
    const fieldNames: Record<string, string> = {
      nom: 'Nom',
      prenom: 'Prénom',
      email: 'Email',
      telephone: 'Téléphone',
      adresse: 'Adresse',
      titre_professionnel: 'Titre professionnel',
      competences_techniques: 'Compétences techniques',
      soft_skills: 'Soft skills',
      logiciels_maitrises: 'Logiciels maîtrisés',
      experience_professionnelle: 'Expérience professionnelle',
      formation_diplomes: 'Formation',
      langues: 'Langues',
      certifications: 'Certifications',
      
      // Job fields
      titre_poste: 'Titre du poste',
      niveau_poste: 'Niveau du poste',
      competences_requises: 'Compétences requises',
      competences_souhaitees: 'Compétences souhaitées',
      experience_minimale: 'Expérience minimale',
      localisation: 'Localisation',
      fourchette_salariale: 'Fourchette salariale',
      type_contrat: 'Type de contrat',
      missions_principales: 'Missions principales',
      avantages: 'Avantages',
      description_poste: 'Description du poste'
    };
    
    return fieldNames[field] || field;
  };

  const getTrendIcon = (current: number, previous?: number) => {
    if (!previous) return null;
    
    if (current > previous) {
      return <TrendingUp className="w-3 h-3 text-green-500" />;
    } else if (current < previous) {
      return <TrendingDown className="w-3 h-3 text-red-500" />;
    }
    return null;
  };

  // Filtrage des champs selon les préférences
  const filteredFields = fieldConfidences.filter(field => 
    showLowConfidence || field.confidence >= 0.7
  );

  // Statistiques globales
  const stats = {
    excellent: fieldConfidences.filter(f => getConfidenceLevel(f.confidence) === 'excellent').length,
    good: fieldConfidences.filter(f => getConfidenceLevel(f.confidence) === 'good').length,
    fair: fieldConfidences.filter(f => getConfidenceLevel(f.confidence) === 'fair').length,
    poor: fieldConfidences.filter(f => getConfidenceLevel(f.confidence) === 'poor').length,
  };

  if (compact) {
    return (
      <div className={`inline-flex items-center space-x-2 ${className}`}>
        {getConfidenceIcon(globalConfidence)}
        <span className="text-sm font-medium">
          {Math.round(globalConfidence * 100)}%
        </span>
        <div className="flex space-x-1">
          {fieldConfidences.slice(0, 5).map((field, idx) => (
            <div
              key={idx}
              className={`w-2 h-2 rounded-full ${
                getConfidenceLevel(field.confidence) === 'excellent' ? 'bg-green-500' :
                getConfidenceLevel(field.confidence) === 'good' ? 'bg-blue-500' :
                getConfidenceLevel(field.confidence) === 'fair' ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              title={`${getFieldDisplayName(field.field)}: ${Math.round(field.confidence * 100)}%`}
            />
          ))}
          {fieldConfidences.length > 5 && (
            <span className="text-xs text-gray-400">+{fieldConfidences.length - 5}</span>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">
                Indicateur de confiance
              </h3>
              <p className="text-sm text-gray-600">
                Score global: <span className={`font-semibold ${
                  globalConfidence >= 0.8 ? 'text-green-600' : 
                  globalConfidence >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {Math.round(globalConfidence * 100)}%
                </span>
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowLowConfidence(!showLowConfidence)}
              className="text-sm text-gray-600 hover:text-gray-800 flex items-center space-x-1"
            >
              {showLowConfidence ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              <span>{showLowConfidence ? 'Masquer' : 'Voir'} faible confiance</span>
            </button>
          </div>
        </div>
        
        {/* Barre de progression globale */}
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                globalConfidence >= 0.8 ? 'bg-gradient-to-r from-green-400 to-green-600' :
                globalConfidence >= 0.6 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                'bg-gradient-to-r from-red-400 to-red-600'
              }`}
              style={{ 
                width: `${globalConfidence * 100}%`,
                animation: animateChanges ? 'pulse 0.5s' : 'none'
              }}
            />
          </div>
        </div>
        
        {/* Statistiques rapides */}
        <div className="mt-3 flex items-center justify-between text-xs">
          <div className="flex space-x-4">
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Excellent: {stats.excellent}</span>
            </span>
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Bon: {stats.good}</span>
            </span>
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span>Moyen: {stats.fair}</span>
            </span>
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span>Faible: {stats.poor}</span>
            </span>
          </div>
        </div>
      </div>
      
      {/* Liste des champs */}
      <div className="p-4 space-y-2 max-h-96 overflow-y-auto">
        {filteredFields.map((field, idx) => (
          <div
            key={field.field}
            className={`border rounded-lg p-3 transition-all duration-200 hover:shadow-md ${
              getConfidenceColor(field.confidence)
            } ${
              onFieldClick ? 'cursor-pointer' : ''
            } ${
              expandedField === field.field ? 'ring-2 ring-blue-300' : ''
            }`}
            onClick={() => {
              if (onFieldClick) onFieldClick(field.field);
              setExpandedField(expandedField === field.field ? null : field.field);
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getConfidenceIcon(field.confidence)}
                <div>
                  <span className="font-medium text-sm">
                    {getFieldDisplayName(field.field)}
                  </span>
                  {field.auto_corrected && (
                    <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                      Auto-corrigé
                    </span>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {getTrendIcon(field.confidence, field.previous_confidence)}
                <span className="font-semibold text-sm">
                  {Math.round(field.confidence * 100)}%
                </span>
                <Info className="w-3 h-3 text-gray-400" />
              </div>
            </div>
            
            {/* Barre de progression du champ */}
            <div className="mt-2">
              <div className="w-full bg-white bg-opacity-50 rounded-full h-1.5">
                <div
                  className={`h-full rounded-full transition-all duration-300 ${
                    field.confidence >= 0.9 ? 'bg-green-600' :
                    field.confidence >= 0.7 ? 'bg-blue-600' :
                    field.confidence >= 0.5 ? 'bg-yellow-600' : 'bg-red-600'
                  }`}
                  style={{ width: `${field.confidence * 100}%` }}
                />
              </div>
            </div>
            
            {/* Détails expandus */}
            {expandedField === field.field && showDetails && (
              <div className="mt-3 space-y-2 text-sm">
                {/* Raisons de la confiance */}
                {field.reasons.length > 0 && (
                  <div>
                    <h5 className="font-medium text-gray-800 mb-1">Facteurs de confiance:</h5>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      {field.reasons.map((reason, idx) => (
                        <li key={idx} className="text-xs">{reason}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Suggestions d'amélioration */}
                {field.suggestions && field.suggestions.length > 0 && (
                  <div>
                    <h5 className="font-medium text-gray-800 mb-1">Suggestions d'amélioration:</h5>
                    <ul className="space-y-1">
                      {field.suggestions.map((suggestion, idx) => (
                        <li key={idx} className="flex items-start space-x-2">
                          <CheckCircle2 className="w-3 h-3 text-blue-500 mt-0.5 flex-shrink-0" />
                          <span className="text-xs text-gray-700">{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Historique de confiance */}
                {field.previous_confidence !== undefined && (
                  <div className="flex items-center space-x-2 text-xs text-gray-600">
                    <span>Précédent: {Math.round(field.previous_confidence * 100)}%</span>
                    <span>→</span>
                    <span>Actuel: {Math.round(field.confidence * 100)}%</span>
                    <span className={`font-medium ${
                      field.confidence > field.previous_confidence ? 'text-green-600' : 
                      field.confidence < field.previous_confidence ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      ({field.confidence > field.previous_confidence ? '+' : ''}
                      {Math.round((field.confidence - field.previous_confidence) * 100)}%)
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Footer avec actions */}
      {showDetails && (
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-sm">
            <div className="text-gray-600">
              {filteredFields.length} champs analysés
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => setExpandedField(null)}
                className="text-gray-600 hover:text-gray-800"
              >
                Fermer tous
              </button>
              
              <button
                onClick={() => {
                  const lowConfidenceFields = fieldConfidences.filter(f => f.confidence < 0.7);
                  if (lowConfidenceFields.length > 0) {
                    setExpandedField(lowConfidenceFields[0].field);
                  }
                }}
                className="text-blue-600 hover:text-blue-800"
              >
                Voir problèmes
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Styles pour animations */}
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.8; }
        }
      `}</style>
    </div>
  );
};

// Hook utilitaire pour calculer la confiance des champs
export const useFieldConfidence = (data: any, type: 'cv' | 'job') => {
  const [fieldConfidences, setFieldConfidences] = useState<FieldConfidence[]>([]);
  
  useEffect(() => {
    const calculateFieldConfidences = (): FieldConfidence[] => {
      const confidences: FieldConfidence[] = [];
      
      Object.entries(data).forEach(([field, value]) => {
        let confidence = 0;
        const reasons: string[] = [];
        const suggestions: string[] = [];
        
        // Logique de calcul de confiance selon le type de champ
        if (typeof value === 'string') {
          if (value.trim().length > 0) {
            confidence += 0.5;
            reasons.push('Champ rempli');
            
            // Validation spécifique selon le champ
            if (field === 'email') {
              if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                confidence += 0.4;
                reasons.push('Format email valide');
              } else {
                suggestions.push('Vérifier le format de l\'email');
              }
            } else if (field === 'telephone') {
              if (/^(?:\+33|0)[1-9](?:[0-9]{8})$/.test(value.replace(/[\s.-]/g, ''))) {
                confidence += 0.4;
                reasons.push('Format téléphone français valide');
              } else {
                suggestions.push('Vérifier le format du téléphone');
              }
            } else if (value.length > 10) {
              confidence += 0.3;
              reasons.push('Contenu détaillé');
            }
          } else {
            suggestions.push('Remplir ce champ requis');
          }
        } else if (Array.isArray(value)) {
          if (value.length > 0) {
            confidence += 0.6;
            reasons.push(`${value.length} éléments trouvés`);
            
            if (value.length >= 3) {
              confidence += 0.3;
              reasons.push('Liste complète');
            }
          } else {
            confidence = 0.1;
            suggestions.push('Ajouter des éléments à cette liste');
          }
        } else if (typeof value === 'object' && value !== null) {
          const filledFields = Object.values(value).filter(v => v && v.toString().trim() !== '').length;
          const totalFields = Object.keys(value).length;
          confidence = filledFields / totalFields;
          reasons.push(`${filledFields}/${totalFields} sous-champs remplis`);
        }
        
        // Assurer que la confiance est entre 0 et 1
        confidence = Math.min(1, Math.max(0, confidence));
        
        confidences.push({
          field,
          confidence,
          reasons,
          suggestions: suggestions.length > 0 ? suggestions : undefined
        });
      });
      
      return confidences;
    };
    
    setFieldConfidences(calculateFieldConfidences());
  }, [data, type]);
  
  const globalConfidence = fieldConfidences.length > 0 
    ? fieldConfidences.reduce((sum, field) => sum + field.confidence, 0) / fieldConfidences.length 
    : 0;
    
  return { fieldConfidences, globalConfidence };
};

export default ConfidenceIndicator;
