/**
 * ParsingWorkflowDemo - Composant de démonstration intégrant tous les composants PROMPT 2
 * 
 * 🚀 Workflow complet:
 * 1. Upload et parsing temps réel avec ParsingProgressBar
 * 2. Validation interactive avec InteractiveValidator  
 * 3. Fallback manuel avec FallbackEditor si nécessaire
 * 4. Affichage final avec ConfidenceIndicator
 */

import React, { useState, useCallback } from 'react';
import {
  ParsingProgressBar,
  InteractiveValidator,
  FallbackEditor,
  ConfidenceIndicator,
  SmartSuggestions,
  ExtractedField,
  ParsedData,
  useParsingWorkflow,
  PARSING_CONSTANTS
} from './index';

interface ParsingWorkflowDemoProps {
  documentType: 'cv' | 'job';
  apiUrl?: string;
  onComplete?: (data: any) => void;
}

const ParsingWorkflowDemo: React.FC<ParsingWorkflowDemoProps> = ({
  documentType,
  apiUrl = 'http://localhost:5051',
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState<'upload' | 'parsing' | 'validating' | 'fallback' | 'completed'>('upload');
  const [taskId, setTaskId] = useState<string>('');
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  const [extractedFields, setExtractedFields] = useState<ExtractedField[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const { defaultConfig, workflowStates } = useParsingWorkflow({
    apiUrl,
    enableStreaming: true,
    enableValidation: true,
    enableFallback: true,
    maxFileSize: PARSING_CONSTANTS.FILE_SIZES.MAX_SIZE,
    supportedFormats: [...PARSING_CONSTANTS.SUPPORTED_FORMATS.DOCUMENTS, ...PARSING_CONSTANTS.SUPPORTED_FORMATS.IMAGES]
  });

  // Gestion de l'upload de fichier
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Vérifications de base
    if (file.size > defaultConfig.maxFileSize) {
      alert(`Le fichier est trop volumineux. Taille maximale: ${defaultConfig.maxFileSize / 1024 / 1024}MB`);
      return;
    }

    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    if (!fileExtension || !defaultConfig.supportedFormats.includes(fileExtension)) {
      alert(`Format non supporté. Formats acceptés: ${defaultConfig.supportedFormats.join(', ')}`);
      return;
    }

    setSelectedFile(file);
  };

  // Démarrage du parsing
  const startParsing = useCallback(async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    
    try {
      // Upload du fichier
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('documentType', documentType);
      
      const response = await fetch(`${apiUrl}/api/v2/parse/${documentType}/stream`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'upload');
      }

      const result = await response.json();
      setTaskId(result.taskId);
      setCurrentStep('parsing');
      
    } catch (error) {
      console.error('Erreur upload:', error);
      alert('Erreur lors de l\'upload du fichier');
    } finally {
      setIsUploading(false);
    }
  }, [selectedFile, documentType, apiUrl]);

  // Fin du parsing
  const handleParsingComplete = useCallback((data: ParsedData) => {
    setParsedData(data);
    
    // Conversion des données en ExtractedField
    const fields: ExtractedField[] = Object.entries(data.data).map(([key, value]) => ({
      key,
      label: key.charAt(0).toUpperCase() + key.slice(1),
      value: value?.toString() || '',
      confidence: data.confidence,
      required: ['firstName', 'lastName', 'email', 'jobTitle', 'company'].includes(key),
      type: key.includes('email') ? 'email' : key.includes('phone') ? 'phone' : 'text',
      category: getFieldCategory(key)
    }));
    
    setExtractedFields(fields);
    
    // Décider de l'étape suivante
    if (data.confidence < PARSING_CONSTANTS.CONFIDENCE_THRESHOLDS.MODERATE || data.fallback_required) {
      setCurrentStep('fallback');
    } else {
      setCurrentStep('validating');
    }
  }, []);

  // Catégorisation des champs
  const getFieldCategory = (key: string): ExtractedField['category'] => {
    if (['firstName', 'lastName', 'title'].includes(key)) return 'personal';
    if (['email', 'phone', 'address'].includes(key)) return 'contact';
    if (['skills', 'softSkills', 'languages'].includes(key)) return 'skills';
    if (['experience', 'previousJobs'].includes(key)) return 'experience';
    if (['education', 'degrees'].includes(key)) return 'education';
    return 'personal';
  };

  // Fin de la validation
  const handleValidationComplete = useCallback((validatedFields: ExtractedField[]) => {
    setExtractedFields(validatedFields);
    setCurrentStep('completed');
    
    // Conversion en format final
    const finalData = validatedFields.reduce((acc, field) => {
      acc[field.key] = field.value;
      return acc;
    }, {} as any);
    
    onComplete?.(finalData);
  }, [onComplete]);

  // Fin du fallback
  const handleFallbackComplete = useCallback((data: {[key: string]: any}) => {
    setCurrentStep('completed');
    onComplete?.(data);
  }, [onComplete]);

  // Erreur de parsing
  const handleParsingError = useCallback((error: string) => {
    console.error('Erreur parsing:', error);
    setCurrentStep('fallback');
  }, []);

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      {/* En-tête avec étapes */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          🚀 Parsing Ultra v2.0 - {documentType === 'cv' ? 'CV' : 'Fiche de poste'}
        </h2>
        
        {/* Indicateur d'étapes */}
        <div className="flex items-center space-x-4 mb-6">
          {[
            { key: 'upload', label: '📁 Upload', icon: '📁' },
            { key: 'parsing', label: '🔄 Parsing', icon: '🔄' },
            { key: 'validating', label: '✅ Validation', icon: '✅' },
            { key: 'fallback', label: '✏️ Saisie manuelle', icon: '✏️' },
            { key: 'completed', label: '🎉 Terminé', icon: '🎉' }
          ].map((step, index) => (
            <div key={step.key} className="flex items-center">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                currentStep === step.key 
                  ? 'bg-blue-600 text-white' 
                  : ['parsing', 'validating', 'fallback', 'completed'].indexOf(currentStep) > ['parsing', 'validating', 'fallback', 'completed'].indexOf(step.key)
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-600'
              }`}>
                <span>{step.icon}</span>
              </div>
              <span className="ml-2 text-sm text-gray-700">{step.label}</span>
              {index < 4 && <div className="w-8 h-0.5 bg-gray-300 mx-2"></div>}
            </div>
          ))}
        </div>
      </div>

      {/* Contenu selon l'étape */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {currentStep === 'upload' && (
          <div className="text-center">
            <h3 className="text-lg font-semibold mb-4">Sélectionnez votre {documentType === 'cv' ? 'CV' : 'fiche de poste'}</h3>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 mb-4">
              <input
                type="file"
                onChange={handleFileSelect}
                accept=".pdf,.docx,.doc,.jpg,.jpeg,.png,.txt"
                className="hidden"
                id="file-input"
              />
              <label
                htmlFor="file-input"
                className="cursor-pointer flex flex-col items-center"
              >
                <div className="text-4xl mb-2">📄</div>
                <div className="text-gray-600 mb-2">Cliquez pour sélectionner un fichier</div>
                <div className="text-sm text-gray-500">
                  PDF, Word, Images (max {defaultConfig.maxFileSize / 1024 / 1024}MB)
                </div>
              </label>
            </div>

            {selectedFile && (
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-center space-x-2">
                  <span>📄</span>
                  <span className="font-medium">{selectedFile.name}</span>
                  <span className="text-sm text-gray-500">
                    ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
              </div>
            )}

            <button
              onClick={startParsing}
              disabled={!selectedFile || isUploading}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
            >
              {isUploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Upload en cours...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>Démarrer le parsing</span>
                </>
              )}
            </button>
          </div>
        )}

        {currentStep === 'parsing' && taskId && (
          <ParsingProgressBar
            taskId={taskId}
            onComplete={handleParsingComplete}
            onError={handleParsingError}
            apiUrl={apiUrl}
          />
        )}

        {currentStep === 'validating' && extractedFields.length > 0 && (
          <InteractiveValidator
            taskId={taskId}
            extractedData={extractedFields}
            onValidationComplete={handleValidationComplete}
            apiUrl={apiUrl}
          />
        )}

        {currentStep === 'fallback' && (
          <FallbackEditor
            taskId={taskId}
            documentType={documentType}
            initialData={parsedData?.data || {}}
            onDataChange={(data) => console.log('Data changed:', data)}
            onComplete={handleFallbackComplete}
            apiUrl={apiUrl}
          />
        )}

        {currentStep === 'completed' && (
          <div className="text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h3 className="text-xl font-semibold text-green-600 mb-4">
              Parsing terminé avec succès !
            </h3>
            
            {parsedData && (
              <div className="mb-6">
                <ConfidenceIndicator
                  confidence={parsedData.confidence}
                  size="lg"
                  variant="circle"
                  className="mx-auto mb-4"
                />
                <p className="text-gray-600">
                  Confiance globale: {Math.round(parsedData.confidence * 100)}%
                </p>
              </div>
            )}

            <div className="flex justify-center space-x-4">
              <button
                onClick={() => {
                  setCurrentStep('upload');
                  setTaskId('');
                  setParsedData(null);
                  setExtractedFields([]);
                  setSelectedFile(null);
                }}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                Nouveau parsing
              </button>
              
              {parsedData && (
                <button
                  onClick={() => {
                    const blob = new Blob([JSON.stringify(parsedData.data, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `parsed_${documentType}_${Date.now()}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  📥 Télécharger JSON
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ParsingWorkflowDemo;