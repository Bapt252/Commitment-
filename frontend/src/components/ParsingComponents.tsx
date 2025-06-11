/**
 * 🚀 SuperSmartMatch V2 - Frontend Components Ultra v2.0
 * PROMPT 2: Composants React interactifs pour parsing temps réel
 * 
 * Composants requis:
 * - <ParsingProgressBar> avec WebSocket temps réel
 * - <InteractiveValidator> pour corrections à la volée
 * - <FallbackEditor> pour saisie manuelle fluide
 * - <ConfidenceIndicator> visuel par champ
 * - <SmartSuggestions> basées sur IA
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  CheckCircle, 
  AlertTriangle, 
  Edit2, 
  Save, 
  RefreshCw,
  Eye,
  EyeOff,
  TrendingUp,
  Lightbulb
} from 'lucide-react';

// Types pour TypeScript
interface ParseProgress {
  taskId: string;
  status: 'processing' | 'completed' | 'error';
  progress: number;
  confidence: number;
  currentStep: string;
  data?: any;
  suggestions: string[];
  fallbackRequired: boolean;
}

interface FieldValidation {
  fieldPath: string;
  value: any;
  confidence: number;
  isEditing: boolean;
  suggestions: string[];
}

// 🔄 ParsingProgressBar avec WebSocket temps réel
export const ParsingProgressBar: React.FC<{
  taskId: string;
  onComplete: (data: any) => void;
  onError: (error: string) => void;
  serviceType: 'cv' | 'job';
}> = ({ taskId, onComplete, onError, serviceType }) => {
  const [progress, setProgress] = useState<ParseProgress>({
    taskId,
    status: 'processing',
    progress: 0,
    confidence: 0,
    currentStep: 'Initialisation...',
    suggestions: [],
    fallbackRequired: false
  });
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!taskId) return;

    // Connexion WebSocket pour le streaming temps réel
    const wsUrl = `ws://localhost:${serviceType === 'cv' ? '5051' : '5053'}/v2/parse/${serviceType === 'cv' ? '' : 'job/'}status/${taskId}`;
    
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log(`WebSocket connecté pour ${serviceType} parsing:`, taskId);
    };

    wsRef.current.onmessage = (event) => {
      try {
        const update: ParseProgress = JSON.parse(event.data);
        setProgress(update);

        // Notification à <500ms selon spécifications PROMPT 2
        if (update.status === 'completed') {
          onComplete(update.data);
        } else if (update.status === 'error') {
          onError(update.currentStep);
        }
      } catch (error) {
        console.error('Erreur parsing WebSocket:', error);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('Erreur WebSocket:', error);
      onError('Erreur de connexion WebSocket');
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [taskId, serviceType, onComplete, onError]);

  const getProgressColor = () => {
    if (progress.status === 'error') return 'bg-red-500';
    if (progress.status === 'completed') return 'bg-green-500';
    if (progress.confidence > 0.8) return 'bg-blue-500';
    if (progress.confidence > 0.5) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  const getStatusIcon = () => {
    if (progress.status === 'error') return <AlertTriangle className="w-5 h-5 text-red-500" />;
    if (progress.status === 'completed') return <CheckCircle className="w-5 h-5 text-green-500" />;
    return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
  };

  return (
    <div className="w-full p-6 bg-white rounded-lg shadow-lg border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          {serviceType === 'cv' ? 'Analyse CV' : 'Analyse Offre d\'Emploi'} - Ultra v2.0
        </h3>
        {getStatusIcon()}
      </div>

      {/* Barre de progression avec animation fluide */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>{progress.currentStep}</span>
          <span>{Math.round(progress.progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            className={`h-full transition-all duration-300 ease-out ${getProgressColor()}`}
            style={{ width: `${progress.progress}%` }}
          />
        </div>
      </div>

      {/* Score de confiance en temps réel */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Confiance</span>
          <ConfidenceIndicator confidence={progress.confidence} />
        </div>
      </div>

      {/* Suggestions intelligentes */}
      {progress.suggestions.length > 0 && (
        <SmartSuggestions suggestions={progress.suggestions} />
      )}

      {/* Fallback si nécessaire */}
      {progress.fallbackRequired && (
        <div className="mt-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-orange-500 mt-0.5 mr-2" />
            <div>
              <h4 className="text-sm font-medium text-orange-800">Saisie manuelle requise</h4>
              <p className="text-sm text-orange-700 mt-1">
                Le parsing automatique n'a pas donné de résultats satisfaisants. 
                Vous pouvez utiliser l'éditeur manuel ci-dessous.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// 📊 ConfidenceIndicator visuel par champ
export const ConfidenceIndicator: React.FC<{
  confidence: number;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}> = ({ confidence, showLabel = true, size = 'md' }) => {
  const getConfidenceColor = () => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-100';
    if (confidence >= 0.7) return 'text-blue-600 bg-blue-100';
    if (confidence >= 0.5) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceLabel = () => {
    if (confidence >= 0.9) return 'Excellent';
    if (confidence >= 0.7) return 'Bon';
    if (confidence >= 0.5) return 'Moyen';
    return 'Faible';
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`rounded-full font-medium ${getConfidenceColor()} ${sizeClasses[size]}`}>
        {Math.round(confidence * 100)}%
      </div>
      {showLabel && (
        <span className="text-sm text-gray-600">
          {getConfidenceLabel()}
        </span>
      )}
    </div>
  );
};

// ✏️ InteractiveValidator pour corrections à la volée
export const InteractiveValidator: React.FC<{
  data: any;
  onValidate: (fieldPath: string, newValue: any, confidence?: number) => void;
  serviceType: 'cv' | 'job';
}> = ({ data, onValidate, serviceType }) => {
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<any>('');
  const [showConfidenceScores, setShowConfidenceScores] = useState(false);

  const handleStartEdit = (fieldPath: string, currentValue: any) => {
    setEditingField(fieldPath);
    setEditValue(Array.isArray(currentValue) ? currentValue.join(', ') : currentValue || '');
  };

  const handleSaveEdit = () => {
    if (!editingField) return;

    let processedValue = editValue;
    
    // Traitement spécial pour les listes
    if (editValue.includes(',')) {
      processedValue = editValue.split(',').map((item: string) => item.trim()).filter(Boolean);
    }

    onValidate(editingField, processedValue);
    setEditingField(null);
    setEditValue('');
  };

  const renderField = (label: string, value: any, fieldPath: string, confidence?: number) => {
    const isEditing = editingField === fieldPath;
    const displayValue = Array.isArray(value) ? value.join(', ') : value || 'Non spécifié';

    return (
      <div key={fieldPath} className="p-3 border rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
        <div className="flex items-center justify-between mb-2">
          <label className="font-medium text-gray-700">{label}</label>
          <div className="flex items-center gap-2">
            {confidence !== undefined && showConfidenceScores && (
              <ConfidenceIndicator confidence={confidence} size="sm" showLabel={false} />
            )}
            {!isEditing ? (
              <button
                onClick={() => handleStartEdit(fieldPath, value)}
                className="text-blue-600 hover:text-blue-800"
              >
                <Edit2 className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSaveEdit}
                className="text-green-600 hover:text-green-800"
              >
                <Save className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
        
        {isEditing ? (
          <div className="space-y-2">
            <input
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder={`Modifier ${label.toLowerCase()}...`}
              autoFocus
            />
            <div className="text-xs text-gray-500">
              Pour les listes, séparez par des virgules
            </div>
          </div>
        ) : (
          <div className="text-gray-800 bg-white p-2 rounded border">
            {displayValue}
          </div>
        )}
      </div>
    );
  };

  // Structure différente selon CV ou Job
  const renderCVFields = () => {
    if (!data || !data.personal_info) return null;

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Informations Personnelles</h3>
        {renderField('Prénom', data.personal_info.first_name, 'personal_info.first_name', data.personal_info.confidence_score)}
        {renderField('Nom', data.personal_info.last_name, 'personal_info.last_name', data.personal_info.confidence_score)}
        {renderField('Email', data.personal_info.email, 'personal_info.email', data.personal_info.confidence_score)}
        {renderField('Téléphone', data.personal_info.phone, 'personal_info.phone', data.personal_info.confidence_score)}
        {renderField('Titre', data.personal_info.title, 'personal_info.title', data.personal_info.confidence_score)}

        <h3 className="text-lg font-semibold mt-6">Compétences & Langues</h3>
        {renderField('Compétences', data.skills, 'skills')}
        {renderField('Langues', data.languages, 'languages')}
        {renderField('Certifications', data.certifications, 'certifications')}
      </div>
    );
  };

  const renderJobFields = () => {
    if (!data) return null;

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Informations Poste</h3>
        {renderField('Titre du poste', data.title, 'title')}
        {renderField('Niveau', data.level, 'level')}
        
        {data.requirements && (
          <>
            <h3 className="text-lg font-semibold mt-6">Exigences</h3>
            {renderField('Compétences requises', data.requirements.required_skills, 'requirements.required_skills')}
            {renderField('Compétences souhaitées', data.requirements.preferred_skills, 'requirements.preferred_skills')}
            {renderField('Expérience minimale', data.requirements.minimum_experience, 'requirements.minimum_experience')}
          </>
        )}

        {data.work_conditions && (
          <>
            <h3 className="text-lg font-semibold mt-6">Conditions de travail</h3>
            {renderField('Type de contrat', data.work_conditions.contract_type, 'work_conditions.contract_type')}
            {renderField('Localisation', data.work_conditions.location, 'work_conditions.location')}
            {renderField('Télétravail', data.work_conditions.remote_work, 'work_conditions.remote_work')}
          </>
        )}

        {data.compensation && (
          <>
            <h3 className="text-lg font-semibold mt-6">Rémunération</h3>
            {renderField('Salaire minimum', data.compensation.salary_min, 'compensation.salary_min')}
            {renderField('Salaire maximum', data.compensation.salary_max, 'compensation.salary_max')}
            {renderField('Avantages', data.compensation.other_benefits, 'compensation.other_benefits')}
          </>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-800">
          Validation Interactive - {serviceType === 'cv' ? 'CV' : 'Offre d\'Emploi'}
        </h2>
        <button
          onClick={() => setShowConfidenceScores(!showConfidenceScores)}
          className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          {showConfidenceScores ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          Scores de confiance
        </button>
      </div>

      {serviceType === 'cv' ? renderCVFields() : renderJobFields()}
    </div>
  );
};

// 🛠️ FallbackEditor pour saisie manuelle fluide
export const FallbackEditor: React.FC<{
  serviceType: 'cv' | 'job';
  onSave: (data: any) => void;
  initialData?: any;
}> = ({ serviceType, onSave, initialData }) => {
  const [manualData, setManualData] = useState(initialData || {});
  const [currentSection, setCurrentSection] = useState(0);

  const cvSections = [
    { id: 'personal', label: 'Informations personnelles', icon: '👤' },
    { id: 'skills', label: 'Compétences', icon: '🛠️' },
    { id: 'experience', label: 'Expérience', icon: '💼' },
    { id: 'education', label: 'Formation', icon: '🎓' }
  ];

  const jobSections = [
    { id: 'basic', label: 'Informations de base', icon: '📋' },
    { id: 'requirements', label: 'Exigences', icon: '✅' },
    { id: 'conditions', label: 'Conditions', icon: '📍' },
    { id: 'company', label: 'Entreprise', icon: '🏢' }
  ];

  const sections = serviceType === 'cv' ? cvSections : jobSections;

  const handleInputChange = (section: string, field: string, value: any) => {
    setManualData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const renderCVSection = (sectionId: string) => {
    switch (sectionId) {
      case 'personal':
        return (
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Prénom"
              value={manualData.personal_info?.first_name || ''}
              onChange={(e) => handleInputChange('personal_info', 'first_name', e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Nom"
              value={manualData.personal_info?.last_name || ''}
              onChange={(e) => handleInputChange('personal_info', 'last_name', e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="email"
              placeholder="Email"
              value={manualData.personal_info?.email || ''}
              onChange={(e) => handleInputChange('personal_info', 'email', e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Téléphone"
              value={manualData.personal_info?.phone || ''}
              onChange={(e) => handleInputChange('personal_info', 'phone', e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Titre professionnel"
              value={manualData.personal_info?.title || ''}
              onChange={(e) => handleInputChange('personal_info', 'title', e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        );
      case 'skills':
        return (
          <div className="space-y-4">
            <textarea
              placeholder="Compétences (séparées par des virgules)"
              value={Array.isArray(manualData.skills) ? manualData.skills.join(', ') : manualData.skills || ''}
              onChange={(e) => setManualData(prev => ({ ...prev, skills: e.target.value.split(',').map(s => s.trim()) }))}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 h-24"
            />
            <textarea
              placeholder="Langues (séparées par des virgules)"
              value={Array.isArray(manualData.languages) ? manualData.languages.join(', ') : manualData.languages || ''}
              onChange={(e) => setManualData(prev => ({ ...prev, languages: e.target.value.split(',').map(s => s.trim()) }))}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 h-24"
            />
          </div>
        );
      default:
        return <div>Section en construction...</div>;
    }
  };

  const renderJobSection = (sectionId: string) => {
    switch (sectionId) {
      case 'basic':
        return (
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Titre du poste"
              value={manualData.title || ''}
              onChange={(e) => setManualData(prev => ({ ...prev, title: e.target.value }))}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={manualData.level || ''}
              onChange={(e) => setManualData(prev => ({ ...prev, level: e.target.value }))}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sélectionner un niveau</option>
              <option value="Junior">Junior</option>
              <option value="Senior">Senior</option>
              <option value="Lead">Lead</option>
              <option value="Manager">Manager</option>
            </select>
            <textarea
              placeholder="Description du poste"
              value={manualData.description || ''}
              onChange={(e) => setManualData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 h-32"
            />
          </div>
        );
      case 'requirements':
        return (
          <div className="space-y-4">
            <textarea
              placeholder="Compétences requises (séparées par des virgules)"
              value={manualData.requirements?.required_skills?.join(', ') || ''}
              onChange={(e) => handleInputChange('requirements', 'required_skills', e.target.value.split(',').map(s => s.trim()))}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 h-24"
            />
            <input
              type="text"
              placeholder="Expérience minimale requise"
              value={manualData.requirements?.minimum_experience || ''}
              onChange={(e) => handleInputChange('requirements', 'minimum_experience', e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        );
      default:
        return <div>Section en construction...</div>;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-6">
        Saisie Manuelle - {serviceType === 'cv' ? 'CV' : 'Offre d\'Emploi'}
      </h2>

      {/* Navigation par onglets */}
      <div className="flex mb-6 border-b">
        {sections.map((section, index) => (
          <button
            key={section.id}
            onClick={() => setCurrentSection(index)}
            className={`px-4 py-2 font-medium text-sm ${
              currentSection === index 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <span className="mr-2">{section.icon}</span>
            {section.label}
          </button>
        ))}
      </div>

      {/* Contenu de la section */}
      <div className="mb-6">
        {serviceType === 'cv' 
          ? renderCVSection(sections[currentSection].id)
          : renderJobSection(sections[currentSection].id)
        }
      </div>

      {/* Boutons de navigation */}
      <div className="flex justify-between">
        <button
          onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
          disabled={currentSection === 0}
          className="px-4 py-2 text-gray-600 disabled:opacity-50"
        >
          Précédent
        </button>

        <div className="flex gap-2">
          <button
            onClick={() => onSave(manualData)}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Save className="w-4 h-4 inline mr-2" />
            Sauvegarder
          </button>

          {currentSection < sections.length - 1 && (
            <button
              onClick={() => setCurrentSection(Math.min(sections.length - 1, currentSection + 1))}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Suivant
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// 💡 SmartSuggestions basées sur IA
export const SmartSuggestions: React.FC<{
  suggestions: string[];
  onApplySuggestion?: (suggestion: string) => void;
}> = ({ suggestions, onApplySuggestion }) => {
  if (!suggestions.length) return null;

  return (
    <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="flex items-start">
        <Lightbulb className="w-5 h-5 text-blue-500 mt-0.5 mr-2" />
        <div className="flex-1">
          <h4 className="text-sm font-medium text-blue-800 mb-2">Suggestions intelligentes</h4>
          <ul className="space-y-1">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="text-sm text-blue-700 flex items-center justify-between">
                <span>• {suggestion}</span>
                {onApplySuggestion && (
                  <button
                    onClick={() => onApplySuggestion(suggestion)}
                    className="ml-2 text-xs px-2 py-1 bg-blue-200 text-blue-800 rounded hover:bg-blue-300"
                  >
                    Appliquer
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default {
  ParsingProgressBar,
  InteractiveValidator, 
  FallbackEditor,
  ConfidenceIndicator,
  SmartSuggestions
};
