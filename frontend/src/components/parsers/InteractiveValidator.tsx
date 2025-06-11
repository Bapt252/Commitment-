/**
 * ✅ InteractiveValidator - Composant React validation interactive
 * PROMPT 2 - SuperSmartMatch V2 - Validation et correction en temps réel
 */

import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  Edit3, 
  Save, 
  X, 
  Plus, 
  Trash2,
  Sparkles,
  Target,
  User,
  Mail,
  Phone,
  MapPin,
  Code,
  Heart,
  Briefcase,
  GraduationCap,
  Languages,
  Award
} from 'lucide-react';

interface CVData {
  nom: string;
  prenom: string;
  titre_professionnel: string;
  email: string;
  telephone: string;
  adresse: string;
  competences_techniques: string[];
  soft_skills: string[];
  logiciels_maitrises: string[];
  langues: Array<{ langue: string; niveau: string }>;
  certifications: string[];
  experience_professionnelle: Array<{
    poste: string;
    entreprise: string;
    duree: string;
    description: string;
  }>;
  formation_diplomes: Array<{
    diplome: string;
    etablissement: string;
    annee: string;
    specialite: string;
  }>;
}

interface JobData {
  titre_poste: string;
  niveau_poste: string;
  competences_requises: string[];
  competences_souhaitees: string[];
  experience_minimale: string;
  localisation: string;
  teletravail: string;
  fourchette_salariale?: {
    min_salary: number;
    max_salary: number;
    currency: string;
    period: string;
  };
  type_contrat: string;
  avantages: string[];
  culture_entreprise: string[];
  description_poste: string;
  missions_principales: string[];
  profil_recherche: string;
  formations_requises: string[];
  langues_requises: Array<{ langue: string; niveau: string }>;
  secteur_activite: string;
  taille_entreprise: string;
}

interface ValidationIssue {
  field: string;
  severity: 'error' | 'warning' | 'suggestion';
  message: string;
  autofix?: string;
}

interface InteractiveValidatorProps {
  data: CVData | JobData;
  type: 'cv' | 'job';
  confidence: number;
  suggestions: string[];
  onSave: (data: CVData | JobData) => void;
  onCancel: () => void;
  className?: string;
}

export const InteractiveValidator: React.FC<InteractiveValidatorProps> = ({
  data: initialData,
  type,
  confidence,
  suggestions,
  onSave,
  onCancel,
  className = ''
}) => {
  const [data, setData] = useState(initialData);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [validationIssues, setValidationIssues] = useState<ValidationIssue[]>([]);
  const [hasChanges, setHasChanges] = useState(false);

  // Validation automatique des données
  useEffect(() => {
    const issues = validateData(data, type);
    setValidationIssues(issues);
  }, [data, type]);

  const validateData = (data: CVData | JobData, type: 'cv' | 'job'): ValidationIssue[] => {
    const issues: ValidationIssue[] = [];

    if (type === 'cv') {
      const cvData = data as CVData;
      
      // Validation email
      if (cvData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cvData.email)) {
        issues.push({
          field: 'email',
          severity: 'error',
          message: 'Format d\'email invalide',
          autofix: cvData.email.toLowerCase()
        });
      }
      
      // Validation téléphone
      if (cvData.telephone && !/^(?:\+33|0)[1-9](?:[0-9]{8})$/.test(cvData.telephone.replace(/[\s.-]/g, ''))) {
        issues.push({
          field: 'telephone',
          severity: 'warning',
          message: 'Format de téléphone français recommandé'
        });
      }
      
      // Validation compétences
      if (cvData.competences_techniques.length === 0) {
        issues.push({
          field: 'competences_techniques',
          severity: 'warning',
          message: 'Aucune compétence technique détectée'
        });
      }
      
      // Validation expérience
      if (cvData.experience_professionnelle.length === 0) {
        issues.push({
          field: 'experience_professionnelle',
          severity: 'suggestion',
          message: 'Ajoutez l\'expérience professionnelle pour un CV complet'
        });
      }
      
    } else {
      const jobData = data as JobData;
      
      // Validation titre
      if (!jobData.titre_poste.trim()) {
        issues.push({
          field: 'titre_poste',
          severity: 'error',
          message: 'Le titre du poste est requis'
        });
      }
      
      // Validation compétences
      if (jobData.competences_requises.length === 0) {
        issues.push({
          field: 'competences_requises',
          severity: 'warning',
          message: 'Aucune compétence requise spécifiée'
        });
      }
      
      // Validation salaire
      if (jobData.fourchette_salariale) {
        const { min_salary, max_salary } = jobData.fourchette_salariale;
        if (min_salary >= max_salary) {
          issues.push({
            field: 'fourchette_salariale',
            severity: 'error',
            message: 'Le salaire minimum doit être inférieur au maximum'
          });
        }
      }
    }

    return issues;
  };

  const getFieldIcon = (fieldName: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      nom: <User className="w-4 h-4" />,
      prenom: <User className="w-4 h-4" />,
      email: <Mail className="w-4 h-4" />,
      telephone: <Phone className="w-4 h-4" />,
      adresse: <MapPin className="w-4 h-4" />,
      competences_techniques: <Code className="w-4 h-4" />,
      soft_skills: <Heart className="w-4 h-4" />,
      experience_professionnelle: <Briefcase className="w-4 h-4" />,
      formation_diplomes: <GraduationCap className="w-4 h-4" />,
      langues: <Languages className="w-4 h-4" />,
      certifications: <Award className="w-4 h-4" />,
      titre_poste: <Target className="w-4 h-4" />,
      competences_requises: <Code className="w-4 h-4" />,
      missions_principales: <Briefcase className="w-4 h-4" />
    };
    return iconMap[fieldName] || <Edit3 className="w-4 h-4" />;
  };

  const getIssuesByField = (fieldName: string) => {
    return validationIssues.filter(issue => issue.field === fieldName);
  };

  const getIssueColor = (severity: 'error' | 'warning' | 'suggestion') => {
    const colors = {
      error: 'text-red-600 bg-red-50 border-red-200',
      warning: 'text-orange-600 bg-orange-50 border-orange-200',
      suggestion: 'text-blue-600 bg-blue-50 border-blue-200'
    };
    return colors[severity];
  };

  const updateField = (fieldName: string, value: any) => {
    setData(prev => ({ ...prev, [fieldName]: value }));
    setHasChanges(true);
  };

  const addToArray = (fieldName: string, newItem: any) => {
    const currentArray = (data as any)[fieldName] || [];
    updateField(fieldName, [...currentArray, newItem]);
  };

  const removeFromArray = (fieldName: string, index: number) => {
    const currentArray = (data as any)[fieldName] || [];
    updateField(fieldName, currentArray.filter((_: any, i: number) => i !== index));
  };

  const updateArrayItem = (fieldName: string, index: number, newValue: any) => {
    const currentArray = [...((data as any)[fieldName] || [])];
    currentArray[index] = newValue;
    updateField(fieldName, currentArray);
  };

  const applyAutofix = (issue: ValidationIssue) => {
    if (issue.autofix) {
      updateField(issue.field, issue.autofix);
    }
  };

  // Composant pour éditer les champs simples
  const SimpleFieldEditor: React.FC<{ 
    fieldName: string; 
    label: string; 
    value: string; 
    type?: string;
    multiline?: boolean;
  }> = ({ fieldName, label, value, type = 'text', multiline = false }) => {
    const issues = getIssuesByField(fieldName);
    const isEditing = editingField === fieldName;
    
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
            {getFieldIcon(fieldName)}
            <span>{label}</span>
          </label>
          
          {!isEditing && (
            <button
              onClick={() => setEditingField(fieldName)}
              className="text-blue-600 hover:text-blue-800 text-sm flex items-center space-x-1"
            >
              <Edit3 className="w-3 h-3" />
              <span>Éditer</span>
            </button>
          )}
        </div>
        
        {isEditing ? (
          <div className="space-y-2">
            {multiline ? (
              <textarea
                value={value}
                onChange={(e) => updateField(fieldName, e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                placeholder={`Entrez ${label.toLowerCase()}`}
              />
            ) : (
              <input
                type={type}
                value={value}
                onChange={(e) => updateField(fieldName, e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={`Entrez ${label.toLowerCase()}`}
              />
            )}
            
            <div className="flex space-x-2">
              <button
                onClick={() => setEditingField(null)}
                className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 flex items-center space-x-1"
              >
                <Save className="w-3 h-3" />
                <span>Sauver</span>
              </button>
              <button
                onClick={() => {
                  setEditingField(null);
                  setData(initialData); // Reset
                }}
                className="px-3 py-1 bg-gray-400 text-white rounded text-sm hover:bg-gray-500 flex items-center space-x-1"
              >
                <X className="w-3 h-3" />
                <span>Annuler</span>
              </button>
            </div>
          </div>
        ) : (
          <div className={`p-3 rounded-lg border ${
            issues.length > 0 
              ? getIssueColor(issues[0].severity)
              : 'bg-gray-50 border-gray-200'
          }`}>
            <div className="text-sm">
              {value || <span className="text-gray-400 italic">Non renseigné</span>}
            </div>
          </div>
        )}
        
        {/* Issues pour ce champ */}
        {issues.map((issue, idx) => (
          <div key={idx} className={`p-2 rounded border text-xs ${getIssueColor(issue.severity)}`}>
            <div className="flex items-center justify-between">
              <span>{issue.message}</span>
              {issue.autofix && (
                <button
                  onClick={() => applyAutofix(issue)}
                  className="text-xs underline hover:no-underline"
                >
                  Corriger auto
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Composant pour éditer les tableaux
  const ArrayFieldEditor: React.FC<{ 
    fieldName: string; 
    label: string; 
    values: string[]; 
  }> = ({ fieldName, label, values }) => {
    const [newItem, setNewItem] = useState('');
    const issues = getIssuesByField(fieldName);
    
    return (
      <div className="space-y-2">
        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
          {getFieldIcon(fieldName)}
          <span>{label}</span>
          <span className="text-gray-400">({values.length})</span>
        </label>
        
        <div className="space-y-1">
          {values.map((item, index) => (
            <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
              <span className="flex-1 text-sm">{item}</span>
              <button
                onClick={() => removeFromArray(fieldName, index)}
                className="text-red-500 hover:text-red-700"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
        
        <div className="flex space-x-2">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder={`Ajouter ${label.toLowerCase()}`}
            className="flex-1 p-2 border border-gray-300 rounded text-sm"
            onKeyPress={(e) => {
              if (e.key === 'Enter' && newItem.trim()) {
                addToArray(fieldName, newItem.trim());
                setNewItem('');
              }
            }}
          />
          <button
            onClick={() => {
              if (newItem.trim()) {
                addToArray(fieldName, newItem.trim());
                setNewItem('');
              }
            }}
            className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-3 h-3" />
          </button>
        </div>
        
        {/* Issues */}
        {issues.map((issue, idx) => (
          <div key={idx} className={`p-2 rounded border text-xs ${getIssueColor(issue.severity)}`}>
            {issue.message}
          </div>
        ))}
      </div>
    );
  };

  const renderCVFields = (cvData: CVData) => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Informations personnelles */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
          Informations personnelles
        </h3>
        <SimpleFieldEditor fieldName="nom" label="Nom" value={cvData.nom} />
        <SimpleFieldEditor fieldName="prenom" label="Prénom" value={cvData.prenom} />
        <SimpleFieldEditor fieldName="titre_professionnel" label="Titre professionnel" value={cvData.titre_professionnel} />
        <SimpleFieldEditor fieldName="email" label="Email" value={cvData.email} type="email" />
        <SimpleFieldEditor fieldName="telephone" label="Téléphone" value={cvData.telephone} type="tel" />
        <SimpleFieldEditor fieldName="adresse" label="Adresse" value={cvData.adresse} multiline />
      </div>
      
      {/* Compétences */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
          Compétences
        </h3>
        <ArrayFieldEditor fieldName="competences_techniques" label="Compétences techniques" values={cvData.competences_techniques} />
        <ArrayFieldEditor fieldName="soft_skills" label="Soft skills" values={cvData.soft_skills} />
        <ArrayFieldEditor fieldName="logiciels_maitrises" label="Logiciels maîtrisés" values={cvData.logiciels_maitrises} />
        <ArrayFieldEditor fieldName="certifications" label="Certifications" values={cvData.certifications} />
      </div>
    </div>
  );

  const renderJobFields = (jobData: JobData) => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Informations du poste */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
          Informations du poste
        </h3>
        <SimpleFieldEditor fieldName="titre_poste" label="Titre du poste" value={jobData.titre_poste} />
        <SimpleFieldEditor fieldName="niveau_poste" label="Niveau du poste" value={jobData.niveau_poste} />
        <SimpleFieldEditor fieldName="type_contrat" label="Type de contrat" value={jobData.type_contrat} />
        <SimpleFieldEditor fieldName="localisation" label="Localisation" value={jobData.localisation} />
        <SimpleFieldEditor fieldName="teletravail" label="Télétravail" value={jobData.teletravail} />
        <SimpleFieldEditor fieldName="experience_minimale" label="Expérience minimale" value={jobData.experience_minimale} />
      </div>
      
      {/* Compétences et exigences */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
          Compétences et exigences
        </h3>
        <ArrayFieldEditor fieldName="competences_requises" label="Compétences requises" values={jobData.competences_requises} />
        <ArrayFieldEditor fieldName="competences_souhaitees" label="Compétences souhaitées" values={jobData.competences_souhaitees} />
        <ArrayFieldEditor fieldName="formations_requises" label="Formations requises" values={jobData.formations_requises} />
        <ArrayFieldEditor fieldName="missions_principales" label="Missions principales" values={jobData.missions_principales} />
        <ArrayFieldEditor fieldName="avantages" label="Avantages" values={jobData.avantages} />
      </div>
    </div>
  );

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-6 h-6 text-blue-500" />
            <div>
              <h2 className="text-xl font-semibold text-gray-800">
                Validation interactive {type === 'cv' ? 'CV' : 'Offre d\'emploi'}
              </h2>
              <p className="text-sm text-gray-600">
                Score de confiance: <span className={`font-semibold ${
                  confidence >= 0.8 ? 'text-green-600' : 
                  confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {Math.round(confidence * 100)}%
                </span>
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              validationIssues.filter(i => i.severity === 'error').length > 0
                ? 'bg-red-100 text-red-800'
                : validationIssues.filter(i => i.severity === 'warning').length > 0
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-green-100 text-green-800'
            }`}>
              {validationIssues.filter(i => i.severity === 'error').length} erreurs, {' '}
              {validationIssues.filter(i => i.severity === 'warning').length} avertissements
            </span>
          </div>
        </div>
        
        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="mt-4 space-y-2">
            <h4 className="text-sm font-medium text-gray-700">Suggestions:</h4>
            {suggestions.map((suggestion, idx) => (
              <div key={idx} className="flex items-start space-x-2 text-sm text-blue-700 bg-blue-50 p-2 rounded">
                <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{suggestion}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Content */}
      <div className="p-6">
        {type === 'cv' ? renderCVFields(data as CVData) : renderJobFields(data as JobData)}
      </div>
      
      {/* Footer */}
      <div className="p-6 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {hasChanges && (
              <span className="flex items-center space-x-1 text-orange-600">
                <AlertTriangle className="w-4 h-4" />
                <span>Modifications non sauvegardées</span>
              </span>
            )}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center space-x-2"
            >
              <X className="w-4 h-4" />
              <span>Annuler</span>
            </button>
            
            <button
              onClick={() => onSave(data)}
              disabled={validationIssues.filter(i => i.severity === 'error').length > 0}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Valider et sauvegarder</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveValidator;
