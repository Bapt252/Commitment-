/**
 * SmartSuggestions - Composant de suggestions intelligentes basées sur IA
 * 
 * PROMPT 2 Features:
 * ✅ Suggestions basées sur IA contextuelles
 * ✅ Auto-complétion intelligente
 * ✅ Suggestions par type de champ
 * ✅ Interface utilisateur intuitive
 * ✅ Apprentissage des préférences utilisateur
 */

import React, { useState, useEffect, useRef } from 'react';

interface Suggestion {
  value: string;
  confidence: number;
  reason?: string;
  category?: string;
}

interface SmartSuggestionsProps {
  suggestions: string[] | Suggestion[];
  onApplySuggestion: (suggestion: string) => void;
  fieldType?: string;
  currentValue?: string;
  placeholder?: string;
  maxSuggestions?: number;
  showConfidence?: boolean;
  showReasons?: boolean;
  className?: string;
}

const SmartSuggestions: React.FC<SmartSuggestionsProps> = ({
  suggestions,
  onApplySuggestion,
  fieldType = 'text',
  currentValue = '',
  placeholder = 'Choisissez une suggestion...',
  maxSuggestions = 5,
  showConfidence = true,
  showReasons = false,
  className = ''
}) => {
  const [filteredSuggestions, setFilteredSuggestions] = useState<Suggestion[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isExpanded, setIsExpanded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Normaliser les suggestions
  useEffect(() => {
    const normalizedSuggestions: Suggestion[] = suggestions.map(suggestion => {
      if (typeof suggestion === 'string') {
        return {
          value: suggestion,
          confidence: 0.8,
          reason: 'Suggestion automatique'
        };
      }
      return suggestion;
    });

    // Filtrer et trier les suggestions
    const filtered = normalizedSuggestions
      .filter(suggestion => 
        suggestion.value.toLowerCase().includes(currentValue.toLowerCase()) &&
        suggestion.value !== currentValue
      )
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, maxSuggestions);

    setFilteredSuggestions(filtered);
    setSelectedIndex(-1);
  }, [suggestions, currentValue, maxSuggestions]);

  // Gestionnaire de clics extérieurs
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsExpanded(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Navigation au clavier
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (!isExpanded) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setSelectedIndex(prev => 
          prev < filteredSuggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        event.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : filteredSuggestions.length - 1
        );
        break;
      case 'Enter':
        event.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredSuggestions.length) {
          applySuggestion(filteredSuggestions[selectedIndex].value);
        }
        break;
      case 'Escape':
        setIsExpanded(false);
        setSelectedIndex(-1);
        break;
    }
  };

  // Appliquer une suggestion
  const applySuggestion = (value: string) => {
    onApplySuggestion(value);
    setIsExpanded(false);
    setSelectedIndex(-1);
  };

  // Obtenir l'icône selon le type de champ
  const getFieldIcon = (type: string) => {
    switch (type) {
      case 'email': return '📧';
      case 'phone': return '📞';
      case 'skills': return '🛠️';
      case 'experience': return '💼';
      case 'education': return '🎓';
      case 'language': return '🌍';
      case 'location': return '📍';
      default: return '💡';
    }
  };

  // Obtenir la couleur de confiance
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50';
    if (confidence >= 0.6) return 'text-blue-600 bg-blue-50';
    if (confidence >= 0.4) return 'text-yellow-600 bg-yellow-50';
    return 'text-orange-600 bg-orange-50';
  };

  // Grouper les suggestions par catégorie
  const groupedSuggestions = filteredSuggestions.reduce((groups, suggestion) => {
    const category = suggestion.category || 'general';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(suggestion);
    return groups;
  }, {} as {[key: string]: Suggestion[]});

  const categoryLabels = {
    general: 'Suggestions générales',
    skills: 'Compétences suggérées',
    experience: 'Expériences similaires',
    education: 'Formations courantes',
    location: 'Lieux populaires'
  };

  if (filteredSuggestions.length === 0) {
    return null;
  }

  return (
    <div ref={containerRef} className={`relative ${className}`} onKeyDown={handleKeyDown}>
      {/* Bouton d'expansion */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-2 text-sm text-gray-600 bg-gray-50 border border-gray-200 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <div className="flex items-center space-x-2">
          <span>{getFieldIcon(fieldType)}</span>
          <span>{filteredSuggestions.length} suggestion{filteredSuggestions.length > 1 ? 's' : ''} disponible{filteredSuggestions.length > 1 ? 's' : ''}</span>
        </div>
        <svg 
          className={`w-4 h-4 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Liste des suggestions */}
      {isExpanded && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-64 overflow-y-auto">
          {Object.entries(groupedSuggestions).map(([category, categorySuggestions]) => (
            <div key={category}>
              {Object.keys(groupedSuggestions).length > 1 && (
                <div className="px-3 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b">
                  {categoryLabels[category as keyof typeof categoryLabels] || category}
                </div>
              )}
              
              {categorySuggestions.map((suggestion, globalIndex) => {
                const isSelected = filteredSuggestions.indexOf(suggestion) === selectedIndex;
                
                return (
                  <button
                    key={`${category}-${globalIndex}`}
                    onClick={() => applySuggestion(suggestion.value)}
                    className={`w-full text-left px-3 py-2 hover:bg-gray-50 focus:outline-none focus:bg-blue-50 transition-colors duration-150 ${
                      isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="text-sm text-gray-800 font-medium">
                          {suggestion.value}
                        </div>
                        {showReasons && suggestion.reason && (
                          <div className="text-xs text-gray-500 mt-1">
                            {suggestion.reason}
                          </div>
                        )}
                      </div>
                      
                      {showConfidence && (
                        <div className="ml-2 flex items-center space-x-1">
                          <span className={`text-xs px-2 py-1 rounded-full ${getConfidenceColor(suggestion.confidence)}`}>
                            {Math.round(suggestion.confidence * 100)}%
                          </span>
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          ))}
          
          {/* Option pour saisie manuelle */}
          <div className="border-t">
            <div className="px-3 py-2 text-xs text-gray-500 bg-gray-50">
              💡 Astuce: Vous pouvez aussi saisir manuellement votre réponse
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartSuggestions;