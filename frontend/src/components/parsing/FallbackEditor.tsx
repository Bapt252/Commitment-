/**
 * FallbackEditor - Composant de saisie manuelle fluide avec auto-suggestions
 * 
 * PROMPT 2 Features:
 * ✅ Fallback manuel si parsing insatisfaisant
 * ✅ Saisie manuelle fluide avec auto-suggestions
 * ✅ Interface adaptative selon le type de données
 * ✅ Sauvegarde automatique
 * ✅ Templates prédéfinis
 */

import React, { useState, useEffect, useCallback } from 'react';
import SmartSuggestions from './SmartSuggestions';
import ConfidenceIndicator from './ConfidenceIndicator';

interface FieldTemplate {
  key: string;
  label: string;
  type: 'text' | 'email' | 'phone' | 'textarea' | 'select' | 'multiselect' | 'date';
  required: boolean;
  placeholder: string;
  options?: string[];
  category: string;
  suggestions?: string[];
}

interface FallbackEditorProps {
  taskId: string;
  documentType: 'cv' | 'job';
  initialData?: {[key: string]: any};
  onDataChange: (data: {[key: string]: any}) => void;
  onComplete: (data: {[key: string]: any}) => void;
  apiUrl?: string;
}

const FallbackEditor: React.FC<FallbackEditorProps> = ({
  taskId,
  documentType,
  initialData = {},
  onDataChange,
  onComplete,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5051'
}) => {
  const [formData, setFormData] = useState<{[key: string]: any}>(initialData);
  const [templates, setTemplates] = useState<FieldTemplate[]>([]);
  const [activeSection, setActiveSection] = useState<string>('');
  const [completionRate, setCompletionRate] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Templates prédéfinis selon le type de document
  const getDefaultTemplates = (): FieldTemplate[] => {
    if (documentType === 'cv') {
      return [
        // Informations personnelles
        { key: 'firstName', label: 'Prénom', type: 'text', required: true, placeholder: 'Votre prénom', category: 'personal', suggestions: [] },
        { key: 'lastName', label: 'Nom', type: 'text', required: true, placeholder: 'Votre nom de famille', category: 'personal', suggestions: [] },
        { key: 'email', label: 'Email', type: 'email', required: true, placeholder: 'votre@email.com', category: 'contact', suggestions: [] },
        { key: 'phone', label: 'Téléphone', type: 'phone', required: false, placeholder: '+33 6 12 34 56 78', category: 'contact', suggestions: [] },
        { key: 'address', label: 'Adresse', type: 'text', required: false, placeholder: 'Votre adresse complète', category: 'contact', suggestions: [] },
        { key: 'title', label: 'Titre professionnel', type: 'text', required: true, placeholder: 'Votre titre ou poste recherché', category: 'professional', suggestions: ['Développeur Full Stack', 'Chef de projet', 'Consultant', 'Ingénieur'] },
        
        // Compétences
        { key: 'skills', label: 'Compétences techniques', type: 'textarea', required: true, placeholder: 'Listez vos compétences principales...', category: 'skills', suggestions: ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'] },
        { key: 'softSkills', label: 'Compétences relationnelles', type: 'textarea', required: false, placeholder: 'Vos soft skills...', category: 'skills', suggestions: ['Leadership', 'Communication', 'Travail en équipe', 'Résolution de problèmes'] },
        { key: 'languages', label: 'Langues', type: 'textarea', required: false, placeholder: 'Langues parlées et niveaux...', category: 'skills', suggestions: ['Français (natif)', 'Anglais (courant)', 'Espagnol (intermédiaire)'] },
        
        // Expérience
        { key: 'experience', label: 'Expérience professionnelle', type: 'textarea', required: true, placeholder: 'Décrivez votre expérience...', category: 'experience', suggestions: [] },
        
        // Formation
        { key: 'education', label: 'Formation', type: 'textarea', required: true, placeholder: 'Votre parcours de formation...', category: 'education', suggestions: [] }
      ];
    } else {
      return [
        // Informations poste
        { key: 'jobTitle', label: 'Titre du poste', type: 'text', required: true, placeholder: 'Titre exact du poste', category: 'job', suggestions: [] },
        { key: 'company', label: 'Entreprise', type: 'text', required: true, placeholder: 'Nom de l\'entreprise', category: 'company', suggestions: [] },
        { key: 'location', label: 'Localisation', type: 'text', required: true, placeholder: 'Ville, région ou télétravail', category: 'job', suggestions: ['Paris', 'Lyon', 'Marseille', 'Télétravail', 'Hybride'] },
        { key: 'contractType', label: 'Type de contrat', type: 'select', required: true, placeholder: 'Type de contrat', category: 'job', options: ['CDI', 'CDD', 'Freelance', 'Stage', 'Alternance'] },
        
        // Exigences
        { key: 'requiredSkills', label: 'Compétences requises', type: 'textarea', required: true, placeholder: 'Compétences indispensables...', category: 'requirements', suggestions: [] },
        { key: 'desiredSkills', label: 'Compétences souhaitées', type: 'textarea', required: false, placeholder: 'Compétences appréciées...', category: 'requirements', suggestions: [] },
        { key: 'experience', label: 'Expérience requise', type: 'text', required: true, placeholder: 'Années d\'expérience minimales', category: 'requirements', suggestions: ['0-2 ans', '2-5 ans', '5-10 ans', '10+ ans'] },
        
        // Conditions
        { key: 'salary', label: 'Fourchette salariale', type: 'text', required: false, placeholder: 'Salaire proposé', category: 'conditions', suggestions: ['35-45k€', '45-55k€', '55-70k€', 'À négocier'] },
        { key: 'benefits', label: 'Avantages', type: 'textarea', required: false, placeholder: 'Avantages proposés...', category: 'conditions', suggestions: ['Télétravail', 'Tickets restaurant', 'Mutuelle', 'RTT', 'Formation'] },
        
        // Description
        { key: 'description', label: 'Description du poste', type: 'textarea', required: true, placeholder: 'Description détaillée du poste...', category: 'description', suggestions: [] },
        { key: 'missions', label: 'Missions principales', type: 'textarea', required: true, placeholder: 'Missions et responsabilités...', category: 'description', suggestions: [] }
      ];
    }
  };

  // Initialisation des templates
  useEffect(() => {
    const defaultTemplates = getDefaultTemplates();
    setTemplates(defaultTemplates);
    
    // Définir la première section comme active
    const firstCategory = defaultTemplates[0]?.category;
    if (firstCategory) {
      setActiveSection(firstCategory);
    }
  }, [documentType]);

  // Calcul du taux de completion
  useEffect(() => {
    const requiredFields = templates.filter(field => field.required);
    const completedFields = requiredFields.filter(field => {
      const value = formData[field.key];
      return value && value.toString().trim() !== '';
    });
    
    const rate = requiredFields.length > 0 ? (completedFields.length / requiredFields.length) * 100 : 0;
    setCompletionRate(rate);
  }, [formData, templates]);

  // Sauvegarde automatique
  const autoSave = useCallback(async () => {
    if (Object.keys(formData).length === 0) return;
    
    setIsSaving(true);
    try {
      const response = await fetch(`${apiUrl}/api/v2/parse/corrections/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: formData,
          source: 'fallback_editor',
          timestamp: new Date().toISOString()
        })
      });
      
      if (response.ok) {
        setLastSaved(new Date());
        onDataChange(formData);
      }
    } catch (error) {
      console.error('Erreur sauvegarde automatique:', error);
    } finally {
      setIsSaving(false);
    }
  }, [formData, taskId, apiUrl, onDataChange]);

  // Déclencher la sauvegarde automatique
  useEffect(() => {
    const timer = setTimeout(autoSave, 2000); // 2 secondes après la dernière modification
    return () => clearTimeout(timer);
  }, [formData, autoSave]);

  // Mise à jour d'un champ
  const updateField = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Grouper les champs par catégorie
  const groupedFields = templates.reduce((groups, field) => {
    const category = field.category;
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(field);
    return groups;
  }, {} as {[key: string]: FieldTemplate[]});

  const categoryLabels = {
    personal: '👤 Informations personnelles',
    contact: '📞 Contact',
    professional: '💼 Professionnel', 
    skills: '🛠️ Compétences',
    experience: '📈 Expérience',
    education: '🎓 Formation',
    job: '💼 Informations du poste',
    company: '🏢 Entreprise',
    requirements: '✅ Exigences',
    conditions: '💰 Conditions',
    description: '📝 Description'
  };

  // Finaliser la saisie
  const handleComplete = () => {
    const requiredFields = templates.filter(field => field.required);
    const missingFields = requiredFields.filter(field => {
      const value = formData[field.key];
      return !value || value.toString().trim() === '';
    });

    if (missingFields.length > 0) {
      alert(`Veuillez remplir les champs requis: ${missingFields.map(f => f.label).join(', ')}`);
      return;
    }

    onComplete(formData);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* En-tête */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-gray-800">
              ✏️ Saisie manuelle - {documentType === 'cv' ? 'CV' : 'Fiche de poste'}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Remplissez manuellement les informations non détectées automatiquement
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">
              {isSaving ? (
                <span className="flex items-center space-x-1">
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-500"></div>
                  <span>Sauvegarde...</span>
                </span>
              ) : lastSaved ? (
                <span>✅ Sauvegardé à {lastSaved.toLocaleTimeString()}</span>
              ) : (
                <span>Saisie en cours...</span>
              )}
            </div>
          </div>
        </div>

        {/* Barre de progression */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Progression</span>
            <span className="text-sm text-gray-500">{Math.round(completionRate)}% complété</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="h-2 bg-green-500 rounded-full transition-all duration-300"
              style={{ width: `${completionRate}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Navigation par sections */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {Object.keys(groupedFields).map(category => {
            const categoryFields = groupedFields[category];
            const completedInCategory = categoryFields.filter(field => {
              const value = formData[field.key];
              return value && value.toString().trim() !== '';
            }).length;
            
            return (
              <button
                key={category}
                onClick={() => setActiveSection(category)}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 flex items-center space-x-2 ${
                  activeSection === category 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span>{categoryLabels[category as keyof typeof categoryLabels] || category}</span>
                <span className="text-xs bg-white bg-opacity-20 px-1 rounded">
                  {completedInCategory}/{categoryFields.length}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Formulaire de la section active */}
      {activeSection && groupedFields[activeSection] && (
        <div className="space-y-6">
          <h4 className="text-lg font-medium text-gray-800 border-b pb-2">
            {categoryLabels[activeSection as keyof typeof categoryLabels] || activeSection}
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {groupedFields[activeSection].map(field => {
              const value = formData[field.key] || '';
              
              return (
                <div key={field.key} className={field.type === 'textarea' ? 'md:col-span-2' : ''}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  
                  {field.type === 'textarea' ? (
                    <textarea
                      value={value}
                      onChange={(e) => updateField(field.key, e.target.value)}
                      placeholder={field.placeholder}
                      rows={4}
                      className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : field.type === 'select' ? (
                    <select
                      value={value}
                      onChange={(e) => updateField(field.key, e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">{field.placeholder}</option>
                      {field.options?.map(option => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={field.type}
                      value={value}
                      onChange={(e) => updateField(field.key, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  )}
                  
                  {/* Suggestions intelligentes */}
                  {field.suggestions && field.suggestions.length > 0 && (
                    <div className="mt-2">
                      <SmartSuggestions
                        suggestions={field.suggestions}
                        onApplySuggestion={(suggestion) => updateField(field.key, suggestion)}
                        fieldType={field.type}
                        currentValue={value}
                        maxSuggestions={3}
                        showConfidence={false}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="mt-8 flex items-center justify-between pt-6 border-t">
        <div className="text-sm text-gray-600">
          {templates.filter(f => f.required && (!formData[f.key] || formData[f.key].toString().trim() === '')).length > 0 ? (
            <span className="text-red-600">⚠️ Certains champs requis sont manquants</span>
          ) : (
            <span className="text-green-600">✅ Tous les champs requis sont remplis</span>
          )}
        </div>
        
        <button
          onClick={handleComplete}
          disabled={completionRate < 100}
          className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <span>✅</span>
          <span>Finaliser la saisie</span>
        </button>
      </div>
    </div>
  );
};

export default FallbackEditor;