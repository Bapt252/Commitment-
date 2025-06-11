/**
 * 🔧 FallbackEditor - Composant React saisie manuelle fluide
 * PROMPT 2 - SuperSmartMatch V2 - Fallback en cas d'échec parsing IA
 */

import React, { useState, useEffect } from 'react';
import { 
  Edit, 
  Save, 
  RotateCcw, 
  Upload, 
  AlertCircle, 
  CheckCircle2,
  Plus,
  Trash2,
  Copy,
  FileText,
  User,
  Mail,
  Phone,
  MapPin,
  Code,
  Heart,
  Briefcase,
  GraduationCap,
  Languages,
  Award,
  Building,
  DollarSign,
  Clock,
  Target
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

interface FallbackEditorProps {
  type: 'cv' | 'job';
  initialData?: Partial<CVData | JobData>;
  originalText?: string;
  onSave: (data: CVData | JobData) => void;
  onCancel: () => void;
  onRetryAI?: () => void;
  className?: string;
}

// Templates par défaut
const getDefaultCVData = (): CVData => ({
  nom: '',
  prenom: '',
  titre_professionnel: '',
  email: '',
  telephone: '',
  adresse: '',
  competences_techniques: [],
  soft_skills: [],
  logiciels_maitrises: [],
  langues: [],
  certifications: [],
  experience_professionnelle: [],
  formation_diplomes: []
});

const getDefaultJobData = (): JobData => ({
  titre_poste: '',
  niveau_poste: '',
  competences_requises: [],
  competences_souhaitees: [],
  experience_minimale: '',
  localisation: '',
  teletravail: 'Présentiel uniquement',
  fourchette_salariale: undefined,
  type_contrat: 'CDI',
  avantages: [],
  culture_entreprise: [],
  description_poste: '',
  missions_principales: [],
  profil_recherche: '',
  formations_requises: [],
  langues_requises: [],
  secteur_activite: '',
  taille_entreprise: ''
});

export const FallbackEditor: React.FC<FallbackEditorProps> = ({
  type,
  initialData,
  originalText,
  onSave,
  onCancel,
  onRetryAI,
  className = ''
}) => {
  const [data, setData] = useState(() => {
    const defaultData = type === 'cv' ? getDefaultCVData() : getDefaultJobData();
    return { ...defaultData, ...initialData } as CVData | JobData;
  });
  
  const [activeTab, setActiveTab] = useState('editor');
  const [showTemplateHints, setShowTemplateHints] = useState(true);
  const [completionScore, setCompletionScore] = useState(0);

  // Calcul du score de completion
  useEffect(() => {
    const calculateCompletion = () => {
      const fields = Object.entries(data);
      const filledFields = fields.filter(([key, value]) => {
        if (Array.isArray(value)) return value.length > 0;
        if (typeof value === 'object' && value !== null) return Object.keys(value).length > 0;
        return value && value.toString().trim() !== '';
      });
      
      return Math.round((filledFields.length / fields.length) * 100);
    };
    
    setCompletionScore(calculateCompletion());
  }, [data]);

  const updateField = (fieldName: string, value: any) => {
    setData(prev => ({ ...prev, [fieldName]: value }));
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

  // Suggestions intelligentes basées sur le texte original
  const generateSmartSuggestions = (fieldName: string): string[] => {
    if (!originalText) return [];
    
    const suggestions: Record<string, string[]> = {
      competences_techniques: ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Docker', 'Git'],
      soft_skills: ['Communication', 'Travail en équipe', 'Leadership', 'Autonomie', 'Créativité'],
      logiciels_maitrises: ['Microsoft Office', 'Photoshop', 'Figma', 'Slack', 'Jira'],
      competences_requises: ['Python', 'JavaScript', 'React', 'API REST', 'Git', 'Agile'],
      avantages: ['Télétravail', 'Tickets restaurant', 'Mutuelle', 'Formation', 'Congés'],
      missions_principales: ['Développement', 'Maintenance', 'Tests', 'Documentation', 'Support']
    };
    
    return suggestions[fieldName] || [];
  };

  // Composant pour champs simples
  const SimpleField: React.FC<{
    fieldName: string;
    label: string;
    value: string;
    icon: React.ReactNode;
    type?: string;
    multiline?: boolean;
    placeholder?: string;
    suggestions?: string[];
  }> = ({ fieldName, label, value, icon, type = 'text', multiline = false, placeholder, suggestions = [] }) => (
    <div className="space-y-2">
      <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
        {icon}
        <span>{label}</span>
        {suggestions.length > 0 && (
          <span className="text-xs text-blue-500">({suggestions.length} suggestions)</span>
        )}
      </label>
      
      {multiline ? (
        <div className="space-y-2">
          <textarea
            value={value}
            onChange={(e) => updateField(fieldName, e.target.value)}
            placeholder={placeholder || `Entrez ${label.toLowerCase()}`}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
            rows={4}
          />
          {suggestions.length > 0 && showTemplateHints && (
            <div className="flex flex-wrap gap-1">
              {suggestions.slice(0, 3).map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => updateField(fieldName, value + (value ? '. ' : '') + suggestion)}
                  className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                >
                  + {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => updateField(fieldName, e.target.value)}
          placeholder={placeholder || `Entrez ${label.toLowerCase()}`}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      )}
    </div>
  );

  // Composant pour champs de tableau
  const ArrayField: React.FC<{
    fieldName: string;
    label: string;
    values: string[];
    icon: React.ReactNode;
    placeholder?: string;
  }> = ({ fieldName, label, values, icon, placeholder }) => {
    const [newItem, setNewItem] = useState('');
    const suggestions = generateSmartSuggestions(fieldName);
    
    return (
      <div className="space-y-3">
        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
          {icon}
          <span>{label}</span>
          <span className="text-xs text-gray-500">({values.length})</span>
        </label>
        
        {/* Liste des éléments */}
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {values.map((item, index) => (
            <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
              <span className="flex-1 text-sm">{item}</span>
              <button
                onClick={() => removeFromArray(fieldName, index)}
                className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
        
        {/* Ajout d'élément */}
        <div className="flex space-x-2">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder={placeholder || `Ajouter ${label.toLowerCase()}`}
            className="flex-1 p-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
        
        {/* Suggestions rapides */}
        {suggestions.length > 0 && showTemplateHints && (
          <div className="space-y-1">
            <p className="text-xs text-gray-600">Suggestions rapides:</p>
            <div className="flex flex-wrap gap-1">
              {suggestions.slice(0, 6).map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    if (!values.includes(suggestion)) {
                      addToArray(fieldName, suggestion);
                    }
                  }}
                  disabled={values.includes(suggestion)}
                  className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  + {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Rendu des champs CV
  const renderCVEditor = (cvData: CVData) => (
    <div className="space-y-8">
      {/* Informations personnelles */}
      <section className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
          <User className="w-5 h-5" />
          <span>Informations personnelles</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SimpleField fieldName="nom" label="Nom" value={cvData.nom} icon={<User className="w-4 h-4" />} />
          <SimpleField fieldName="prenom" label="Prénom" value={cvData.prenom} icon={<User className="w-4 h-4" />} />
          <SimpleField fieldName="titre_professionnel" label="Titre professionnel" value={cvData.titre_professionnel} icon={<Target className="w-4 h-4" />} />
          <SimpleField fieldName="email" label="Email" value={cvData.email} icon={<Mail className="w-4 h-4" />} type="email" />
          <SimpleField fieldName="telephone" label="Téléphone" value={cvData.telephone} icon={<Phone className="w-4 h-4" />} type="tel" />
          <SimpleField fieldName="adresse" label="Adresse" value={cvData.adresse} icon={<MapPin className="w-4 h-4" />} multiline />
        </div>
      </section>

      {/* Compétences */}
      <section className="bg-blue-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
          <Code className="w-5 h-5" />
          <span>Compétences</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ArrayField fieldName="competences_techniques" label="Compétences techniques" values={cvData.competences_techniques} icon={<Code className="w-4 h-4" />} />
          <ArrayField fieldName="soft_skills" label="Soft skills" values={cvData.soft_skills} icon={<Heart className="w-4 h-4" />} />
          <ArrayField fieldName="logiciels_maitrises" label="Logiciels maîtrisés" values={cvData.logiciels_maitrises} icon={<FileText className="w-4 h-4" />} />
          <ArrayField fieldName="certifications" label="Certifications" values={cvData.certifications} icon={<Award className="w-4 h-4" />} />
        </div>
      </section>
    </div>
  );

  // Rendu des champs Job
  const renderJobEditor = (jobData: JobData) => (
    <div className="space-y-8">
      {/* Informations du poste */}
      <section className="bg-purple-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
          <Target className="w-5 h-5" />
          <span>Informations du poste</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SimpleField fieldName="titre_poste" label="Titre du poste" value={jobData.titre_poste} icon={<Target className="w-4 h-4" />} />
          <SimpleField fieldName="niveau_poste" label="Niveau du poste" value={jobData.niveau_poste} icon={<Building className="w-4 h-4" />} />
          <SimpleField fieldName="type_contrat" label="Type de contrat" value={jobData.type_contrat} icon={<FileText className="w-4 h-4" />} />
          <SimpleField fieldName="localisation" label="Localisation" value={jobData.localisation} icon={<MapPin className="w-4 h-4" />} />
          <SimpleField fieldName="experience_minimale" label="Expérience minimale" value={jobData.experience_minimale} icon={<Clock className="w-4 h-4" />} />
          <SimpleField fieldName="secteur_activite" label="Secteur d'activité" value={jobData.secteur_activite} icon={<Building className="w-4 h-4" />} />
        </div>
      </section>

      {/* Compétences requises */}
      <section className="bg-green-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
          <Code className="w-5 h-5" />
          <span>Compétences et exigences</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ArrayField fieldName="competences_requises" label="Compétences requises" values={jobData.competences_requises} icon={<Code className="w-4 h-4" />} />
          <ArrayField fieldName="competences_souhaitees" label="Compétences souhaitées" values={jobData.competences_souhaitees} icon={<Heart className="w-4 h-4" />} />
          <ArrayField fieldName="missions_principales" label="Missions principales" values={jobData.missions_principales} icon={<Briefcase className="w-4 h-4" />} />
          <ArrayField fieldName="avantages" label="Avantages" values={jobData.avantages} icon={<Award className="w-4 h-4" />} />
        </div>
      </section>

      {/* Description */}
      <section className="bg-yellow-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Description détaillée</h3>
        <div className="space-y-4">
          <SimpleField 
            fieldName="description_poste" 
            label="Description du poste" 
            value={jobData.description_poste} 
            icon={<FileText className="w-4 h-4" />} 
            multiline
            placeholder="Décrivez le poste, les responsabilités, l'environnement de travail..."
          />
          <SimpleField 
            fieldName="profil_recherche" 
            label="Profil recherché" 
            value={jobData.profil_recherche} 
            icon={<User className="w-4 h-4" />} 
            multiline
            placeholder="Décrivez le profil idéal, les qualités recherchées..."
          />
        </div>
      </section>
    </div>
  );

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-orange-50 to-red-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Edit className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800">
                Saisie manuelle {type === 'cv' ? 'CV' : 'Offre d\'emploi'}
              </h2>
              <p className="text-sm text-gray-600">
                Le parsing automatique a échoué - Complétez manuellement les informations
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Score de completion */}
            <div className="text-center">
              <div className={`text-2xl font-bold ${
                completionScore >= 80 ? 'text-green-600' : 
                completionScore >= 50 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {completionScore}%
              </div>
              <div className="text-xs text-gray-500">Complété</div>
            </div>
            
            {/* Toggle hints */}
            <button
              onClick={() => setShowTemplateHints(!showTemplateHints)}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              {showTemplateHints ? 'Masquer' : 'Afficher'} les suggestions
            </button>
          </div>
        </div>
        
        {/* Barre de progression */}
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                completionScore >= 80 ? 'bg-green-500' : 
                completionScore >= 50 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${completionScore}%` }}
            />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          <button
            onClick={() => setActiveTab('editor')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'editor'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Edit className="w-4 h-4" />
              <span>Éditeur</span>
            </div>
          </button>
          
          {originalText && (
            <button
              onClick={() => setActiveTab('original')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'original'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4" />
                <span>Texte original</span>
              </div>
            </button>
          )}
        </nav>
      </div>

      {/* Contenu */}
      <div className="p-6">
        {activeTab === 'editor' ? (
          type === 'cv' ? renderCVEditor(data as CVData) : renderJobEditor(data as JobData)
        ) : (
          originalText && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Texte original extrait</h3>
              <div className="bg-gray-50 p-4 rounded-lg border">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 max-h-96 overflow-y-auto">
                  {originalText}
                </pre>
              </div>
              <div className="flex items-center space-x-2 text-sm text-blue-600">
                <Copy className="w-4 h-4" />
                <button 
                  onClick={() => navigator.clipboard.writeText(originalText)}
                  className="hover:underline"
                >
                  Copier le texte
                </button>
              </div>
            </div>
          )
        )}
      </div>
      
      {/* Footer */}
      <div className="p-6 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {onRetryAI && (
              <button
                onClick={onRetryAI}
                className="px-4 py-2 text-blue-700 bg-blue-100 border border-blue-300 rounded-md hover:bg-blue-200 flex items-center space-x-2"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Réessayer l'IA</span>
              </button>
            )}
            
            <div className="text-sm text-gray-600">
              <span className="flex items-center space-x-1">
                <AlertCircle className="w-4 h-4" />
                <span>
                  Complété à {completionScore}% - {
                    completionScore >= 80 ? 'Prêt à sauvegarder' :
                    completionScore >= 50 ? 'Ajoutez plus d\'informations' :
                    'Informations insuffisantes'
                  }
                </span>
              </span>
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 flex items-center space-x-2"
            >
              <span>Annuler</span>
            </button>
            
            <button
              onClick={() => onSave(data)}
              disabled={completionScore < 30}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>Sauvegarder ({completionScore}%)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FallbackEditor;
