/**
 * Index des composants de parsing ultra-optimisés PROMPT 2
 * 
 * 🚀 Composants temps réel avec WebSocket:
 * - ParsingProgressBar: Progression streaming <500ms
 * - InteractiveValidator: Validation et corrections à la volée
 * - FallbackEditor: Saisie manuelle fluide avec auto-suggestions
 * - ConfidenceIndicator: Scoring visuel par champ
 * - SmartSuggestions: Suggestions IA contextuelles
 */

export { default as ParsingProgressBar } from './ParsingProgressBar';
export { default as InteractiveValidator } from './InteractiveValidator';
export { default as FallbackEditor } from './FallbackEditor';
export { default as ConfidenceIndicator, ConfidenceLegend } from './ConfidenceIndicator';
export { default as SmartSuggestions } from './SmartSuggestions';

// Types communs pour les composants de parsing
export interface ParsedData {
  taskId: string;
  status: 'processing' | 'completed' | 'error';
  progress: number;
  confidence: number;
  data: {[key: string]: any};
  suggestions?: string[];
  fallback_required: boolean;
}

export interface ExtractedField {
  key: string;
  label: string;
  value: string;
  confidence: number;
  suggestions?: string[];
  required?: boolean;
  type?: 'text' | 'email' | 'phone' | 'date' | 'array' | 'number';
  category?: 'personal' | 'contact' | 'experience' | 'skills' | 'education';
}

export interface ParsingConfig {
  apiUrl: string;
  websocketUrl: string;
  enableStreaming: boolean;
  enableValidation: boolean;
  enableFallback: boolean;
  maxFileSize: number;
  supportedFormats: string[];
}

// Hook personnalisé pour l'utilisation des composants de parsing
export const useParsingWorkflow = (config: ParsingConfig) => {
  return {
    // Configuration par défaut pour une expérience optimale
    defaultConfig: {
      apiUrl: config.apiUrl || 'http://localhost:5051',
      websocketUrl: config.websocketUrl || config.apiUrl || 'http://localhost:5051',
      enableStreaming: config.enableStreaming !== false, // true par défaut
      enableValidation: config.enableValidation !== false, // true par défaut
      enableFallback: config.enableFallback !== false, // true par défaut
      maxFileSize: config.maxFileSize || 10 * 1024 * 1024, // 10MB par défaut
      supportedFormats: config.supportedFormats || ['pdf', 'docx', 'doc', 'jpg', 'png', 'txt']
    },
    
    // États recommandés pour un workflow complet
    workflowStates: {
      UPLOADING: 'uploading',
      PARSING: 'parsing',
      VALIDATING: 'validating',
      FALLBACK: 'fallback',
      COMPLETED: 'completed',
      ERROR: 'error'
    }
  };
};

// Types d'événements WebSocket
export interface WebSocketEvents {
  // Événements entrants (du serveur)
  parsing_progress: (data: { progress: number; step: string; confidence: number }) => void;
  parsing_complete: (data: ParsedData) => void;
  parsing_error: (error: { message: string; code?: string }) => void;
  validation_result: (data: { field: string; isValid: boolean; suggestions: string[] }) => void;
  
  // Événements sortants (vers le serveur)
  subscribe_parsing: (data: { taskId: string }) => void;
  unsubscribe_parsing: (data: { taskId: string }) => void;
  field_update: (data: { taskId: string; field: string; value: string }) => void;
}

// Constantes utiles
export const PARSING_CONSTANTS = {
  // Seuils de confiance
  CONFIDENCE_THRESHOLDS: {
    EXCELLENT: 0.9,
    GOOD: 0.8,
    MODERATE: 0.7,
    LOW: 0.6,
    VERY_LOW: 0.4
  },
  
  // Délais recommandés
  TIMEOUTS: {
    WEBSOCKET_CONNECTION: 20000, // 20s
    PARSING_MAX: 300000, // 5min
    AUTO_SAVE: 2000, // 2s
    VALIDATION_DEBOUNCE: 500 // 0.5s
  },
  
  // Tailles de fichiers
  FILE_SIZES: {
    MAX_SIZE: 10 * 1024 * 1024, // 10MB
    WARNING_SIZE: 5 * 1024 * 1024, // 5MB
    OPTIMAL_SIZE: 2 * 1024 * 1024 // 2MB
  },
  
  // Formats supportés
  SUPPORTED_FORMATS: {
    DOCUMENTS: ['pdf', 'docx', 'doc', 'txt', 'rtf'],
    IMAGES: ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],
    WEB: ['html', 'htm']
  }
};