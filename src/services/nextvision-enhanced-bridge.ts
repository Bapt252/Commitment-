/**
 * 🌉 Nextvision Enhanced Bridge - Services TypeScript pour Commitment-
 * 
 * Services d'intégration pour connecter Commitment- avec Nextvision Enhanced:
 * - Enhanced Universal Parser v4.0 → Enhanced Bridge → Matching Bidirectionnel
 * - Système ChatGPT → Enhanced Bridge → Matching Bidirectionnel
 * - Auto-fix intelligence + Validation robuste
 * - Gestion d'erreurs et retry logic
 * - Performance optimisée avec cache
 * 
 * Author: NEXTEN Team
 * Version: 2.0.0 - Frontend Enhanced Integration
 */

// Types Enhanced Bridge
export interface EnhancedBridgeConfig {
  apiBaseUrl: string;
  timeout: number;
  retryAttempts: number;
  enableCache: boolean;
  enableAutoFix: boolean;
  debugMode: boolean;
}

export interface EnhancedParserV4Data {
  personal_info: {
    firstName: string;
    lastName: string;
    email: string;
    phone?: string;
    age?: number;
    linkedin_url?: string;
  };
  skills: string[];
  experience: {
    total_years: number | string;
  };
  softwares: string[];
  languages: Record<string, string>;
  work_experience: Array<{
    position: string;
    company: string;
    duration: string;
    description?: string;
    skills_acquired?: string[];
  }>;
  education?: string;
  parsing_confidence: number;
  extraction_time_ms?: number;
}

export interface ChatGPTCommitmentData {
  titre: string;
  localisation: string;
  contrat: string;
  salaire: string;
  competences_requises: string[];
  experience_requise: string;
  missions: string[];
  avantages: string[];
  badges_auto_rempli: string[];
  fiche_poste_originale?: string;
  parsing_confidence: number;
  extraction_time_ms?: number;
}

export interface QuestionnaireData {
  // Candidat
  raison_ecoute?: string;
  salary_min?: number;
  salary_max?: number;
  current_salary?: number;
  preferred_location?: string;
  max_distance?: number;
  remote_ok?: boolean;
  preferred_sectors?: string[];
  motivations?: string[];
  blockers?: string[];
  career_goals?: string;
  
  // Entreprise
  company_name?: string;
  sector?: string;
  company_size?: string;
  company_description?: string;
  website?: string;
  urgence?: 'critique' | 'urgent' | 'normal' | 'long terme';
  priority_criteria?: string[];
  eliminatory_criteria?: string[];
  positions_count?: number;
  horaires?: string;
  remote_possible?: boolean;
  work_environment?: string;
}

export interface EnhancedConversionResponse {
  status: string;
  converted_data: {
    candidat?: any;
    entreprise?: any;
  };
  performance_metrics: {
    candidat?: {
      conversion_time_ms: number;
      auto_fix_time_ms: number;
      auto_fixes_count: number;
      fields_processed: number;
      cache_used: boolean;
    };
    entreprise?: {
      conversion_time_ms: number;
      auto_fix_time_ms: number;
      auto_fixes_count: number;
      fields_processed: number;
      cache_used: boolean;
    };
  };
  enhanced_bridge_stats: any;
  processing_time_ms: number;
  timestamp: string;
  message: string;
  features_used: {
    auto_fix_intelligence: boolean;
    robust_validation: boolean;
    performance_caching: boolean;
    retry_logic: boolean;
  };
}

export interface DirectMatchResponse {
  matching_score: number;
  confidence: number;
  compatibility: string;
  component_scores: {
    semantique_score: number;
    semantique_details: any;
    salaire_score: number;
    salaire_details: any;
    experience_score: number;
    experience_details: any;
    localisation_score: number;
    localisation_details: any;
  };
  adaptive_weighting: any;
  recommandations_candidat: string[];
  recommandations_entreprise: string[];
  points_forts: string[];
  points_attention: string[];
  processing_time_ms: number;
}

export interface BatchConversionResponse {
  status: string;
  results: {
    candidats?: {
      successful: any[];
      failed: any[];
    };
    entreprises?: {
      successful: any[];
      failed: any[];
    };
    performance_summary: {
      total_processed: number;
      total_successful: number;
      total_failed: number;
      success_rate_percent: number;
      avg_processing_time_ms: number;
      throughput_items_per_sec: number;
    };
    processing_time_ms: number;
  };
  enhanced_bridge_stats: any;
  timestamp: string;
  message: string;
}

/**
 * 🌉 Service principal Enhanced Bridge
 */
export class NextvisionEnhancedBridgeService {
  private config: EnhancedBridgeConfig;
  private cache: Map<string, any>;
  private requestId: number;

  constructor(config: Partial<EnhancedBridgeConfig> = {}) {
    this.config = {
      apiBaseUrl: 'http://localhost:8000',
      timeout: 30000,
      retryAttempts: 3,
      enableCache: true,
      enableAutoFix: true,
      debugMode: false,
      ...config
    };
    
    this.cache = new Map();
    this.requestId = 0;
    
    if (this.config.debugMode) {
      console.log('🌉 NextvisionEnhancedBridgeService initialized', this.config);
    }
  }

  /**
   * 🔧 Conversion Enhanced avec auto-fix intelligent
   */
  async convertWithEnhanced(
    candidatData?: EnhancedParserV4Data,
    entrepriseData?: ChatGPTCommitmentData,
    candidatQuestionnaire?: QuestionnaireData,
    entrepriseQuestionnaire?: QuestionnaireData
  ): Promise<EnhancedConversionResponse> {
    const requestId = ++this.requestId;
    
    try {
      if (this.config.debugMode) {
        console.log(`🔧 [${requestId}] Starting Enhanced conversion`, {
          hasCandidatData: !!candidatData,
          hasEntrepriseData: !!entrepriseData,
          autoFixEnabled: this.config.enableAutoFix
        });
      }

      // Vérification cache
      const cacheKey = this.generateCacheKey('enhanced_conversion', {
        candidatData, entrepriseData, candidatQuestionnaire, entrepriseQuestionnaire
      });
      
      if (this.config.enableCache && this.cache.has(cacheKey)) {
        if (this.config.debugMode) {
          console.log(`⚡ [${requestId}] Using cached result`);
        }
        return this.cache.get(cacheKey);
      }

      // Préparation payload
      const payload = {
        candidat_data: candidatData || null,
        entreprise_data: entrepriseData || null,
        candidat_questionnaire: candidatQuestionnaire || null,
        entreprise_questionnaire: entrepriseQuestionnaire || null
      };

      // Appel API avec retry logic
      const response = await this.makeRequestWithRetry(
        '/api/v2/conversion/commitment/enhanced',
        'POST',
        payload,
        requestId
      );

      // Mise en cache
      if (this.config.enableCache && response.status === 'success') {
        this.cache.set(cacheKey, response);
      }

      if (this.config.debugMode) {
        console.log(`✅ [${requestId}] Enhanced conversion completed`, {
          processingTime: response.processing_time_ms,
          autoFixesUsed: response.features_used?.auto_fix_intelligence,
          cacheUsed: response.performance_metrics?.candidat?.cache_used || response.performance_metrics?.entreprise?.cache_used
        });
      }

      return response;
      
    } catch (error) {
      console.error(`❌ [${requestId}] Enhanced conversion failed:`, error);
      throw new Error(`Enhanced conversion failed: ${error.message}`);
    }
  }

  /**
   * 🚀 Pipeline complet Enhanced: Conversion + Matching direct
   */
  async convertAndMatchDirect(
    candidatData: EnhancedParserV4Data,
    entrepriseData: ChatGPTCommitmentData,
    candidatQuestionnaire?: QuestionnaireData,
    entrepriseQuestionnaire?: QuestionnaireData
  ): Promise<DirectMatchResponse> {
    const requestId = ++this.requestId;
    
    try {
      if (this.config.debugMode) {
        console.log(`🚀 [${requestId}] Starting Enhanced direct match pipeline`);
      }

      const payload = {
        candidat_data: candidatData,
        entreprise_data: entrepriseData,
        candidat_questionnaire: candidatQuestionnaire || null,
        entreprise_questionnaire: entrepriseQuestionnaire || null
      };

      const response = await this.makeRequestWithRetry(
        '/api/v2/conversion/commitment/enhanced/direct-match',
        'POST',
        payload,
        requestId
      );

      if (this.config.debugMode) {
        console.log(`✅ [${requestId}] Enhanced direct match completed`, {
          matchingScore: response.matching_score,
          compatibility: response.compatibility,
          processingTime: response.processing_time_ms
        });
      }

      return response;
      
    } catch (error) {
      console.error(`❌ [${requestId}] Enhanced direct match failed:`, error);
      throw new Error(`Enhanced direct match failed: ${error.message}`);
    }
  }

  /**
   * 📦 Traitement batch Enhanced
   */
  async convertBatchEnhanced(
    candidatsData: EnhancedParserV4Data[] = [],
    entreprisesData: ChatGPTCommitmentData[] = [],
    enableParallel: boolean = true
  ): Promise<BatchConversionResponse> {
    const requestId = ++this.requestId;
    
    try {
      if (this.config.debugMode) {
        console.log(`📦 [${requestId}] Starting Enhanced batch processing`, {
          candidatsCount: candidatsData.length,
          entreprisesCount: entreprisesData.length,
          parallel: enableParallel
        });
      }

      const payload = {
        candidats_data: candidatsData,
        entreprises_data: entreprisesData,
        enable_parallel: enableParallel
      };

      const response = await this.makeRequestWithRetry(
        '/api/v2/conversion/commitment/enhanced/batch',
        'POST',
        payload,
        requestId,
        60000 // Timeout plus long pour batch
      );

      if (this.config.debugMode) {
        const summary = response.results?.performance_summary;
        console.log(`✅ [${requestId}] Enhanced batch completed`, {
          processed: summary?.total_processed,
          successRate: summary?.success_rate_percent,
          throughput: summary?.throughput_items_per_sec
        });
      }

      return response;
      
    } catch (error) {
      console.error(`❌ [${requestId}] Enhanced batch failed:`, error);
      throw new Error(`Enhanced batch failed: ${error.message}`);
    }
  }

  /**
   * 📊 Récupération statistiques Enhanced Bridge
   */
  async getEnhancedStats(): Promise<any> {
    try {
      const response = await this.makeRequestWithRetry(
        '/api/v2/conversion/commitment/enhanced/stats',
        'GET',
        null,
        0
      );
      
      return response;
      
    } catch (error) {
      console.error('❌ Failed to get Enhanced stats:', error);
      throw new Error(`Enhanced stats failed: ${error.message}`);
    }
  }

  /**
   * ⚙️ Mise à jour configuration Enhanced Bridge
   */
  async updateEnhancedConfig(configUpdates: Record<string, any>): Promise<any> {
    try {
      const response = await this.makeRequestWithRetry(
        '/api/v2/conversion/commitment/enhanced/config',
        'POST',
        configUpdates,
        0
      );
      
      if (this.config.debugMode) {
        console.log('⚙️ Enhanced config updated:', configUpdates);
      }
      
      return response;
      
    } catch (error) {
      console.error('❌ Failed to update Enhanced config:', error);
      throw new Error(`Enhanced config update failed: ${error.message}`);
    }
  }

  /**
   * 🧹 Vider cache Enhanced Bridge
   */
  async clearEnhancedCache(): Promise<any> {
    try {
      const response = await this.makeRequestWithRetry(
        '/api/v2/conversion/commitment/enhanced/cache',
        'DELETE',
        null,
        0
      );
      
      // Vider aussi cache local
      this.cache.clear();
      
      if (this.config.debugMode) {
        console.log('🧹 Enhanced cache cleared');
      }
      
      return response;
      
    } catch (error) {
      console.error('❌ Failed to clear Enhanced cache:', error);
      throw new Error(`Enhanced cache clear failed: ${error.message}`);
    }
  }

  /**
   * ❤️ Health check Enhanced Bridge
   */
  async healthCheck(): Promise<{ status: string; enhanced: boolean; features: any }> {
    try {
      const response = await this.makeRequestWithRetry(
        '/api/v1/health',
        'GET',
        null,
        0,
        5000 // Timeout court pour health check
      );
      
      return {
        status: response.status,
        enhanced: response.features?.enhanced_bridge || false,
        features: response.features || {}
      };
      
    } catch (error) {
      console.error('❌ Health check failed:', error);
      return {
        status: 'unhealthy',
        enhanced: false,
        features: {}
      };
    }
  }

  /**
   * 🔄 Utilitaire: Requête avec retry logic
   */
  private async makeRequestWithRetry(
    endpoint: string,
    method: string,
    payload: any,
    requestId: number,
    customTimeout?: number
  ): Promise<any> {
    const url = `${this.config.apiBaseUrl}${endpoint}`;
    const timeout = customTimeout || this.config.timeout;
    
    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        if (this.config.debugMode && attempt > 1) {
          console.log(`🔄 [${requestId}] Retry attempt ${attempt}/${this.config.retryAttempts}`);
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const options: RequestInit = {
          method,
          headers: {
            'Content-Type': 'application/json',
            'X-Request-ID': requestId.toString()
          },
          signal: controller.signal
        };

        if (payload && method !== 'GET') {
          options.body = JSON.stringify(payload);
        }

        const response = await fetch(url, options);
        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        return data;
        
      } catch (error) {
        if (attempt === this.config.retryAttempts) {
          throw error;
        }
        
        // Délai exponentiel entre les tentatives
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
        if (this.config.debugMode) {
          console.log(`⏱️ [${requestId}] Waiting ${delay}ms before retry...`);
        }
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  /**
   * 🔑 Génération clé cache
   */
  private generateCacheKey(operation: string, data: any): string {
    const dataString = JSON.stringify(data, Object.keys(data).sort());
    const hash = this.simpleHash(dataString);
    return `${operation}_${hash}`;
  }

  /**
   * 🔢 Hash simple pour cache
   */
  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36);
  }

  /**
   * 🧹 Nettoyage ressources
   */
  dispose(): void {
    this.cache.clear();
    if (this.config.debugMode) {
      console.log('🧹 NextvisionEnhancedBridgeService disposed');
    }
  }
}

/**
 * 🏗️ Factory pour création service Enhanced Bridge
 */
export class EnhancedBridgeServiceFactory {
  /**
   * Crée service pour développement
   */
  static createDevelopmentService(): NextvisionEnhancedBridgeService {
    return new NextvisionEnhancedBridgeService({
      apiBaseUrl: 'http://localhost:8000',
      debugMode: true,
      enableCache: true,
      enableAutoFix: true,
      retryAttempts: 2
    });
  }

  /**
   * Crée service pour production
   */
  static createProductionService(apiBaseUrl: string): NextvisionEnhancedBridgeService {
    return new NextvisionEnhancedBridgeService({
      apiBaseUrl,
      debugMode: false,
      enableCache: true,
      enableAutoFix: true,
      retryAttempts: 3,
      timeout: 30000
    });
  }

  /**
   * Crée service pour tests
   */
  static createTestService(): NextvisionEnhancedBridgeService {
    return new NextvisionEnhancedBridgeService({
      apiBaseUrl: 'http://localhost:8000',
      debugMode: true,
      enableCache: false,
      enableAutoFix: true,
      retryAttempts: 1,
      timeout: 10000
    });
  }
}

// Export instance par défaut pour développement
export const nextvisionEnhancedService = EnhancedBridgeServiceFactory.createDevelopmentService();

/**
 * 🎯 Hook React pour Enhanced Bridge (optionnel - si tu utilises React)
 */
export function useNextvisionEnhanced() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<any>(null);

  const convertWithEnhanced = async (
    candidatData?: EnhancedParserV4Data,
    entrepriseData?: ChatGPTCommitmentData,
    candidatQuestionnaire?: QuestionnaireData,
    entrepriseQuestionnaire?: QuestionnaireData
  ) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await nextvisionEnhancedService.convertWithEnhanced(
        candidatData, entrepriseData, candidatQuestionnaire, entrepriseQuestionnaire
      );
      setLastResult(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const convertAndMatchDirect = async (
    candidatData: EnhancedParserV4Data,
    entrepriseData: ChatGPTCommitmentData,
    candidatQuestionnaire?: QuestionnaireData,
    entrepriseQuestionnaire?: QuestionnaireData
  ) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await nextvisionEnhancedService.convertAndMatchDirect(
        candidatData, entrepriseData, candidatQuestionnaire, entrepriseQuestionnaire
      );
      setLastResult(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    lastResult,
    convertWithEnhanced,
    convertAndMatchDirect,
    clearError: () => setError(null)
  };
}

/**
 * 📱 Utilitaires pour intégration mobile/PWA
 */
export class EnhancedBridgeMobileUtils {
  /**
   * Détecte si l'appareil supporte les fonctionnalités Enhanced
   */
  static isMobileCompatible(): boolean {
    return 'fetch' in window && 'Promise' in window && 'AbortController' in window;
  }

  /**
   * Configuration optimisée pour mobile
   */
  static getMobileConfig(): Partial<EnhancedBridgeConfig> {
    return {
      timeout: 45000, // Plus long sur mobile
      retryAttempts: 2, // Moins de tentatives
      enableCache: true, // Important sur mobile
      debugMode: false
    };
  }

  /**
   * Détecte qualité de connexion
   */
  static getConnectionQuality(): 'fast' | 'slow' | 'offline' {
    if (!navigator.onLine) return 'offline';
    
    // @ts-ignore - navigator.connection est expérimental
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    if (connection) {
      const { effectiveType } = connection;
      if (effectiveType === '4g') return 'fast';
      if (effectiveType === '3g') return 'slow';
      return 'slow';
    }
    
    return 'fast'; // Par défaut
  }
}
