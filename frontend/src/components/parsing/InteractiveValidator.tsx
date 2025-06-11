/**
 * InteractiveValidator - Composant de validation interactive des données extraites
 * 
 * PROMPT 2 Features:
 * ✅ Validation interactive des données extraites par l'utilisateur
 * ✅ Corrections à la volée avec auto-sauvegarde
 * ✅ Suggestions intelligentes basées sur IA
 * ✅ Interface intuitive avec édition en ligne
 * ✅ Scoring de confiance par champ
 */

import React, { useState, useEffect, useCallback } from 'react';
import ConfidenceIndicator from './ConfidenceIndicator';
import SmartSuggestions from './SmartSuggestions';

interface ExtractedField {
  key: string;
  label: string;
  value: string;
  confidence: number;
  suggestions?: string[];
  required?: boolean;
  type?: 'text' | 'email' | 'phone' | 'date' | 'array' | 'number';
  category?: 'personal' | 'contact' | 'experience' | 'skills' | 'education';
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  suggestions: string[];
  confidence: number;
}

interface InteractiveValidatorProps {
  taskId: string;
  extractedData: ExtractedField[];
  onValidationComplete: (validatedData: ExtractedField[]) => void;
  onFieldUpdate?: (field: string, value: string) => void;
  apiUrl?: string;
}

const InteractiveValidator: React.FC<InteractiveValidatorProps> = ({
  taskId,
  extractedData,
  onValidationComplete,
  onFieldUpdate,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5051'
}) => {
  const [fields, setFields] = useState<ExtractedField[]>(extractedData);
  const [validationResults, setValidationResults] = useState<{[key: string]: ValidationResult}>({});
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [overallConfidence, setOverallConfidence] = useState(0);
  const [completionRate, setCompletionRate] = useState(0);

  // Calcul des métriques globales
  useEffect(() => {
    const totalFields = fields.length;
    const completedFields = fields.filter(field => field.value && field.value.trim() !== '').length;
    const totalConfidence = fields.reduce((sum, field) => sum + field.confidence, 0);
    
    setCompletionRate(totalFields > 0 ? (completedFields / totalFields) * 100 : 0);
    setOverallConfidence(totalFields > 0 ? totalConfidence / totalFields : 0);
  }, [fields]);

  // Validation automatique d'un champ
  const validateField = useCallback(async (field: ExtractedField) => {
    try {
      const response = await fetch(`${apiUrl}/api/v2/parse/validate/${taskId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          field: field.key,
          value: field.value,
          type: field.type,
          category: field.category
        })
      });

      if (response.ok) {
        const result = await response.json();
        setValidationResults(prev => ({
          ...prev,
          [field.key]: result
        }));
        return result;
      }
    } catch (error) {
      console.error('Erreur validation:', error);
    }

    return null;
  }, [taskId, apiUrl]);

  // Mise à jour d'un champ
  const updateField = useCallback(async (fieldKey: string, newValue: string) => {
    setFields(prev => prev.map(field => {
      if (field.key === fieldKey) {
        const updatedField = { ...field, value: newValue };
        
        // Validation automatique après une pause
        setTimeout(() => validateField(updatedField), 500);
        
        return updatedField;
      }
      return field;
    }));

    onFieldUpdate?.(fieldKey, newValue);
  }, [validateField, onFieldUpdate]);

  // Application d'une suggestion
  const applySuggestion = useCallback((fieldKey: string, suggestion: string) => {
    updateField(fieldKey, suggestion);
  }, [updateField]);

  // Validation globale
  const validateAll = useCallback(async () => {
    setIsValidating(true);
    
    try {
      const validationPromises = fields.map(field => validateField(field));
      await Promise.all(validationPromises);
      
      // Vérification que tous les champs requis sont remplis
      const missingRequired = fields.filter(field => 
        field.required && (!field.value || field.value.trim() === '')
      );
      
      if (missingRequired.length === 0) {
        onValidationComplete(fields);
      }
    } catch (error) {
      console.error('Erreur validation globale:', error);
    } finally {
      setIsValidating(false);
    }
  }, [fields, validateField, onValidationComplete]);

  // Obtenir l'icône du type de champ
  const getFieldIcon = (type: string, category: string) => {
    if (type === 'email') return '📧';
    if (type === 'phone') return '📞';
    if (type === 'date') return '📅';
    if (category === 'personal') return '👤';
    if (category === 'contact') return '📍';
    if (category === 'experience') return '💼';
    if (category === 'skills') return '🛠️';
    if (category === 'education') return '🎓';
    return '📝';
  };

  // Grouper les champs par catégorie
  const groupedFields = fields.reduce((groups, field) => {
    const category = field.category || 'other';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(field);
    return groups;
  }, {} as {[key: string]: ExtractedField[]});

  const categoryLabels = {
    personal: 'Informations personnelles',
    contact: 'Contact',
    experience: 'Expérience professionnelle',
    skills: 'Compétences',
    education: 'Formation',
    other: 'Autres informations'
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* En-tête avec métriques */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-800">Validation des données extraites</h3>
          <button
            onClick={validateAll}
            disabled={isValidating}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isValidating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Validation...</span>
              </>
            ) : (
              <>
                <span>✅</span>
                <span>Valider tout</span>
              </>
            )}
          </button>
        </div>

        {/* Indicateurs globaux */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{Math.round(completionRate)}%</div>
            <div className="text-sm text-gray-600">Complété</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{Math.round(overallConfidence * 100)}%</div>
            <div className="text-sm text-gray-600">Confiance</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{fields.length}</div>
            <div className="text-sm text-gray-600">Champs</div>
          </div>
        </div>

        {/* Barre de progression */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="h-2 bg-green-500 rounded-full transition-all duration-300"
            style={{ width: `${completionRate}%` }}
          ></div>
        </div>
      </div>

      {/* Champs groupés par catégorie */}
      <div className="space-y-6">
        {Object.entries(groupedFields).map(([category, categoryFields]) => (
          <div key={category} className="border border-gray-200 rounded-lg p-4">
            <h4 className="text-lg font-medium text-gray-800 mb-4 flex items-center space-x-2">
              <span>{getFieldIcon('', category)}</span>
              <span>{categoryLabels[category as keyof typeof categoryLabels] || category}</span>
              <span className="text-sm text-gray-500">({categoryFields.length})</span>
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {categoryFields.map((field) => {
                const validation = validationResults[field.key];
                const hasError = validation && !validation.isValid;
                
                return (
                  <div
                    key={field.key}
                    className={`border rounded-lg p-4 transition-all duration-200 ${
                      selectedField === field.key ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    } ${hasError ? 'border-red-300 bg-red-50' : ''}`}
                    onClick={() => setSelectedField(field.key)}
                  >
                    {/* Label et indicateur de confiance */}
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700 flex items-center space-x-2">
                        <span>{getFieldIcon(field.type || '', field.category || '')}</span>
                        <span>{field.label}</span>
                        {field.required && <span className="text-red-500">*</span>}
                      </label>
                      <ConfidenceIndicator confidence={field.confidence} size="sm" />
                    </div>

                    {/* Champ d'édition */}
                    <div className="mb-2">
                      {field.type === 'array' ? (
                        <textarea
                          value={field.value}
                          onChange={(e) => updateField(field.key, e.target.value)}
                          className="w-full p-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          rows={3}
                          placeholder={`Entrez ${field.label.toLowerCase()}...`}
                        />
                      ) : (
                        <input
                          type={field.type === 'email' ? 'email' : field.type === 'phone' ? 'tel' : 'text'}
                          value={field.value}
                          onChange={(e) => updateField(field.key, e.target.value)}
                          className="w-full p-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={`Entrez ${field.label.toLowerCase()}...`}
                        />
                      )}
                    </div>

                    {/* Messages de validation */}
                    {validation && (
                      <div className="mb-2">
                        {validation.errors.length > 0 && (
                          <div className="text-xs text-red-600 mb-1">
                            {validation.errors.map((error, index) => (
                              <div key={index}>❌ {error}</div>
                            ))}
                          </div>
                        )}
                        {validation.isValid && (
                          <div className="text-xs text-green-600">✅ Champ validé</div>
                        )}
                      </div>
                    )}

                    {/* Suggestions intelligentes */}
                    {selectedField === field.key && field.suggestions && field.suggestions.length > 0 && (
                      <SmartSuggestions
                        suggestions={field.suggestions}
                        onApplySuggestion={(suggestion) => applySuggestion(field.key, suggestion)}
                        fieldType={field.type}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Résumé et actions */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {fields.filter(f => f.required && (!f.value || f.value.trim() === '')).length > 0 ? (
              <span className="text-red-600">⚠️ Certains champs requis sont manquants</span>
            ) : (
              <span className="text-green-600">✅ Tous les champs requis sont remplis</span>
            )}
          </div>
          <div className="text-sm text-gray-500">
            Confiance globale: {Math.round(overallConfidence * 100)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveValidator;