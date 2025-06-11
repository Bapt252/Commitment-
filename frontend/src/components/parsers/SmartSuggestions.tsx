/**
 * 🤖 SmartSuggestions - Composant React suggestions IA intelligentes
 * PROMPT 2 - SuperSmartMatch V2 - Suggestions contextuelles basées sur l'IA
 */

import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Brain, 
  Lightbulb, 
  ThumbsUp, 
  ThumbsDown,
  Check,
  Plus,
  ArrowRight,
  Zap,
  Target,
  TrendingUp,
  Award,
  Users,
  Clock,
  DollarSign,
  MapPin,
  RefreshCw,
  X,
  ChevronDown,
  ChevronUp,
  Filter
} from 'lucide-react';

interface SmartSuggestion {
  id: string;
  type: 'improvement' | 'addition' | 'correction' | 'optimization' | 'insight';
  category: string;
  title: string;
  description: string;
  field?: string;
  priority: 'high' | 'medium' | 'low';
  confidence: number;
  action?: {
    type: 'apply' | 'add' | 'edit';
    value: any;
    preview?: string;
  };
  reasoning: string[];
  impact: string;
  examples?: string[];
}

interface SmartSuggestionsProps {
  data: any;
  type: 'cv' | 'job';
  originalText?: string;
  onApplySuggestion?: (suggestion: SmartSuggestion) => void;
  onDismissSuggestion?: (suggestionId: string) => void;
  onGenerateMore?: () => void;
  className?: string;
  maxSuggestions?: number;
}

export const SmartSuggestions: React.FC<SmartSuggestionsProps> = ({
  data,
  type,
  originalText,
  onApplySuggestion,
  onDismissSuggestion,
  onGenerateMore,
  className = '',
  maxSuggestions = 10
}) => {
  const [suggestions, setSuggestions] = useState<SmartSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedSuggestion, setExpandedSuggestion] = useState<string | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [appliedSuggestions, setAppliedSuggestions] = useState<Set<string>>(new Set());

  // Génération des suggestions intelligentes
  useEffect(() => {
    generateSmartSuggestions();
  }, [data, type, originalText]);

  const generateSmartSuggestions = async () => {
    setLoading(true);
    
    try {
      // Simuler un appel API vers l'IA pour générer des suggestions contextuelles
      const suggestions = await generateAISuggestions(data, type, originalText);
      setSuggestions(suggestions);
    } catch (error) {
      console.error('Erreur génération suggestions:', error);
      // Fallback avec suggestions statiques
      setSuggestions(generateStaticSuggestions(data, type));
    } finally {
      setLoading(false);
    }
  };

  // Génération de suggestions avec IA (simulé)
  const generateAISuggestions = async (data: any, type: 'cv' | 'job', originalText?: string): Promise<SmartSuggestion[]> => {
    // En production, ceci ferait appel à l'API OpenAI
    const suggestions: SmartSuggestion[] = [];
    
    if (type === 'cv') {
      // Suggestions pour CV
      if (!data.competences_techniques || data.competences_techniques.length < 3) {
        suggestions.push({
          id: 'cv-skills-enhance',
          type: 'improvement',
          category: 'Compétences',
          title: 'Enrichir les compétences techniques',
          description: 'Votre profil gagnerait en attractivité avec plus de compétences techniques détaillées.',
          field: 'competences_techniques',
          priority: 'high',
          confidence: 0.85,
          action: {
            type: 'add',
            value: ['React', 'Node.js', 'Docker', 'Git'],
            preview: '+4 compétences suggérées'
          },
          reasoning: [
            'Profil technique détecté',
            'Tendances marché 2025',
            'Complémentarité avec compétences existantes'
          ],
          impact: 'Augmente l\'attractivité du profil de 40%',
          examples: ['React.js', 'TypeScript', 'Docker', 'Kubernetes', 'Git', 'Jenkins']
        });
      }
      
      if (!data.experience_professionnelle || data.experience_professionnelle.length === 0) {
        suggestions.push({
          id: 'cv-experience-add',
          type: 'addition',
          category: 'Expérience',
          title: 'Ajouter l\'expérience professionnelle',
          description: 'L\'expérience professionnelle est cruciale pour attirer les recruteurs.',
          field: 'experience_professionnelle',
          priority: 'high',
          confidence: 0.95,
          reasoning: ['Champ vide détecté', 'Information critique pour recruteurs'],
          impact: 'Essentiel pour crédibilité du CV'
        });
      }
      
      if (data.soft_skills && data.soft_skills.length > 0) {
        suggestions.push({
          id: 'cv-soft-skills-optimize',
          type: 'optimization',
          category: 'Soft Skills',
          title: 'Optimiser les soft skills pour 2025',
          description: 'Certaines soft skills sont particulièrement recherchées cette année.',
          field: 'soft_skills',
          priority: 'medium',
          confidence: 0.75,
          action: {
            type: 'add',
            value: ['Intelligence émotionnelle', 'Adaptabilité', 'Pensée critique'],
            preview: 'Ajouter les soft skills tendance'
          },
          reasoning: [
            'Analyse des tendances RH 2025',
            'Complémentarité avec profil existant'
          ],
          impact: 'Améliore l\'alignement avec attentes marché',
          examples: ['Intelligence émotionnelle', 'Agilité mentale', 'Collaboration à distance']
        });
      }
      
    } else {
      // Suggestions pour Job
      if (!data.fourchette_salariale) {
        suggestions.push({
          id: 'job-salary-add',
          type: 'addition',
          category: 'Rémunération',
          title: 'Ajouter la fourchette salariale',
          description: 'Les offres avec salaire affiché reçoivent 3x plus de candidatures.',
          field: 'fourchette_salariale',
          priority: 'high',
          confidence: 0.88,
          reasoning: [
            'Transparence salariale tendance',
            'Augmente taux de candidature',
            'Attire profils qualifiés'
          ],
          impact: '+200% candidatures de qualité'
        });
      }
      
      if (!data.teletravail || data.teletravail === 'Présentiel uniquement') {
        suggestions.push({
          id: 'job-remote-optimize',
          type: 'optimization',
          category: 'Modalités',
          title: 'Considérer le télétravail hybride',
          description: '85% des candidats recherchent de la flexibilité en 2025.',
          field: 'teletravail',
          priority: 'high',
          confidence: 0.82,
          action: {
            type: 'edit',
            value: 'Télétravail hybride',
            preview: 'Télétravail hybride (2-3j/semaine)'
          },
          reasoning: [
            'Tendance marché 2025',
            'Attire talents top-tier',
            'Compétitivité accrue'
          ],
          impact: 'Élargit le bassin de candidats de 60%'
        });
      }
      
      if (data.competences_requises && data.competences_requises.length > 8) {
        suggestions.push({
          id: 'job-skills-reduce',
          type: 'optimization',
          category: 'Compétences',
          title: 'Simplifier les compétences requises',
          description: 'Trop de compétences peuvent décourager les candidats.',
          field: 'competences_requises',
          priority: 'medium',
          confidence: 0.70,
          reasoning: [
            'Liste trop longue détectée',
            'Risque de découragement candidats',
            'Focus sur l\'essentiel recommandé'
          ],
          impact: 'Augmente le taux de candidature de 25%'
        });
      }
    }
    
    // Suggestions contextuelles basées sur le texte original
    if (originalText) {
      if (originalText.toLowerCase().includes('startup') || originalText.toLowerCase().includes('scale-up')) {
        suggestions.push({
          id: 'context-startup',
          type: 'insight',
          category: 'Contexte',
          title: 'Profil startup détecté',
          description: 'Valorisez l\'agilité et la polyvalence pour ce type d\'environnement.',
          priority: 'medium',
          confidence: 0.78,
          reasoning: ['Contexte startup identifié', 'Soft skills spécifiques valorisées'],
          impact: 'Meilleur alignement culturel'
        });
      }
    }
    
    return suggestions.slice(0, maxSuggestions);
  };

  // Fallback avec suggestions statiques
  const generateStaticSuggestions = (data: any, type: 'cv' | 'job'): SmartSuggestion[] => {
    const suggestions: SmartSuggestion[] = [];
    
    if (type === 'cv') {
      suggestions.push({
        id: 'static-cv-contact',
        type: 'improvement',
        category: 'Contact',
        title: 'Vérifier les informations de contact',
        description: 'Assurez-vous que email et téléphone sont corrects.',
        priority: 'high',
        confidence: 0.9,
        reasoning: ['Information critique'],
        impact: 'Évite la perte d\'opportunités'
      });
    } else {
      suggestions.push({
        id: 'static-job-desc',
        type: 'improvement',
        category: 'Description',
        title: 'Enrichir la description du poste',
        description: 'Une description détaillée attire de meilleurs candidats.',
        priority: 'medium',
        confidence: 0.8,
        reasoning: ['Description importante'],
        impact: 'Améliore la qualité des candidatures'
      });
    }
    
    return suggestions;
  };

  // Filtrage des suggestions
  const filteredSuggestions = suggestions.filter(suggestion => {
    const categoryMatch = filterCategory === 'all' || suggestion.category === filterCategory;
    const priorityMatch = filterPriority === 'all' || suggestion.priority === filterPriority;
    const notApplied = !appliedSuggestions.has(suggestion.id);
    
    return categoryMatch && priorityMatch && notApplied;
  });

  // Application d'une suggestion
  const applySuggestion = (suggestion: SmartSuggestion) => {
    if (onApplySuggestion) {
      onApplySuggestion(suggestion);
    }
    setAppliedSuggestions(prev => new Set([...prev, suggestion.id]));
  };

  // Rejet d'une suggestion
  const dismissSuggestion = (suggestionId: string) => {
    if (onDismissSuggestion) {
      onDismissSuggestion(suggestionId);
    }
    setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
  };

  // Icônes par type
  const getTypeIcon = (type: SmartSuggestion['type']) => {
    const icons = {
      improvement: <TrendingUp className="w-4 h-4" />,
      addition: <Plus className="w-4 h-4" />,
      correction: <Check className="w-4 h-4" />,
      optimization: <Zap className="w-4 h-4" />,
      insight: <Lightbulb className="w-4 h-4" />
    };
    return icons[type];
  };

  // Couleurs par priorité
  const getPriorityColor = (priority: SmartSuggestion['priority']) => {
    const colors = {
      high: 'text-red-600 bg-red-50 border-red-200',
      medium: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      low: 'text-blue-600 bg-blue-50 border-blue-200'
    };
    return colors[priority];
  };

  // Catégories uniques
  const categories = [...new Set(suggestions.map(s => s.category))];

  return (
    <div className={`bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-800">
                Suggestions intelligentes
              </h3>
              <p className="text-sm text-gray-600">
                {filteredSuggestions.length} suggestions • IA basée sur les tendances 2025
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {onGenerateMore && (
              <button
                onClick={onGenerateMore}
                disabled={loading}
                className="px-3 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Actualiser</span>
              </button>
            )}
          </div>
        </div>
        
        {/* Filtres */}
        <div className="mt-4 flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1"
            >
              <option value="all">Toutes catégories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
          
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="all">Toutes priorités</option>
            <option value="high">Haute priorité</option>
            <option value="medium">Moyenne priorité</option>
            <option value="low">Basse priorité</option>
          </select>
        </div>
      </div>
      
      {/* Liste des suggestions */}
      <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="flex items-center space-x-2 text-gray-600">
              <RefreshCw className="w-5 h-5 animate-spin" />
              <span>Génération de suggestions personnalisées...</span>
            </div>
          </div>
        ) : filteredSuggestions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Sparkles className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>Aucune suggestion disponible</p>
            <p className="text-sm">Toutes les améliorations ont été appliquées !</p>
          </div>
        ) : (
          filteredSuggestions.map((suggestion) => (
            <div
              key={suggestion.id}
              className={`border rounded-lg p-4 transition-all duration-200 hover:shadow-md ${getPriorityColor(suggestion.priority)}`}
            >
              {/* En-tête de suggestion */}
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className={`p-2 rounded-lg ${
                    suggestion.priority === 'high' ? 'bg-red-100' :
                    suggestion.priority === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'
                  }`}>
                    {getTypeIcon(suggestion.type)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-semibold text-gray-800">{suggestion.title}</h4>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        suggestion.priority === 'high' ? 'bg-red-200 text-red-800' :
                        suggestion.priority === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                        'bg-blue-200 text-blue-800'
                      }`}>
                        {suggestion.priority === 'high' ? 'Priorité haute' :
                         suggestion.priority === 'medium' ? 'Priorité moyenne' : 'Priorité basse'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {Math.round(suggestion.confidence * 100)}% confiance
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-700 mb-2">{suggestion.description}</p>
                    
                    {/* Impact */}
                    <div className="flex items-center space-x-2 text-xs text-gray-600 mb-2">
                      <Target className="w-3 h-3" />
                      <span>Impact: {suggestion.impact}</span>
                    </div>
                    
                    {/* Actions */}
                    <div className="flex items-center space-x-2">
                      {suggestion.action && (
                        <button
                          onClick={() => applySuggestion(suggestion)}
                          className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 flex items-center space-x-1"
                        >
                          <Check className="w-3 h-3" />
                          <span>Appliquer</span>
                          {suggestion.action.preview && (
                            <span className="ml-1 text-green-200">({suggestion.action.preview})</span>
                          )}
                        </button>
                      )}
                      
                      <button
                        onClick={() => setExpandedSuggestion(
                          expandedSuggestion === suggestion.id ? null : suggestion.id
                        )}
                        className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded hover:bg-gray-200 flex items-center space-x-1"
                      >
                        <span>Détails</span>
                        {expandedSuggestion === suggestion.id ? 
                          <ChevronUp className="w-3 h-3" /> : 
                          <ChevronDown className="w-3 h-3" />
                        }
                      </button>
                      
                      <button
                        onClick={() => dismissSuggestion(suggestion.id)}
                        className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded hover:bg-gray-200 flex items-center space-x-1"
                      >
                        <X className="w-3 h-3" />
                        <span>Ignorer</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Détails étendus */}
              {expandedSuggestion === suggestion.id && (
                <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
                  {/* Raisonnement */}
                  <div>
                    <h5 className="text-sm font-medium text-gray-800 mb-2">Raisonnement IA:</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {suggestion.reasoning.map((reason, idx) => (
                        <li key={idx} className="text-xs text-gray-600">{reason}</li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Exemples */}
                  {suggestion.examples && suggestion.examples.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-gray-800 mb-2">Exemples suggérés:</h5>
                      <div className="flex flex-wrap gap-1">
                        {suggestion.examples.map((example, idx) => (
                          <span key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            {example}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Catégorie et champ */}
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>Catégorie: {suggestion.category}</span>
                    {suggestion.field && <span>Champ: {suggestion.field}</span>}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* Footer avec statistiques */}
      {!loading && suggestions.length > 0 && (
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-sm">
            <div className="text-gray-600">
              {appliedSuggestions.size} suggestions appliquées • {filteredSuggestions.length} restantes
            </div>
            
            <div className="flex items-center space-x-4 text-xs">
              <span className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span>Haute: {suggestions.filter(s => s.priority === 'high').length}</span>
              </span>
              <span className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span>Moyenne: {suggestions.filter(s => s.priority === 'medium').length}</span>
              </span>
              <span className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Basse: {suggestions.filter(s => s.priority === 'low').length}</span>
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartSuggestions;
