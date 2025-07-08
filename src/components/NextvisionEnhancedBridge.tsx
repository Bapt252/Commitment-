/**
 * 🎯 Nextvision Enhanced Bridge - Composant React Principal
 * 
 * Interface complète pour l'intégration Commitment- ↔ Nextvision Enhanced:
 * - Upload CV → Enhanced Parser v4.0 → Auto-fix → Matching
 * - Fiche de poste → ChatGPT → Auto-fix → Matching
 * - Pipeline complet avec feedback temps réel
 * - Gestion d'erreurs et retry automatique
 * - Interface utilisateur moderne et responsive
 * 
 * Author: NEXTEN Team
 * Version: 2.0.0 - Enhanced UI Integration
 */

import React, { useState, useCallback, useEffect } from 'react';
import { 
  nextvisionEnhancedService, 
  EnhancedParserV4Data, 
  ChatGPTCommitmentData,
  QuestionnaireData,
  EnhancedConversionResponse,
  DirectMatchResponse 
} from '../services/nextvision-enhanced-bridge';

// Types pour l'interface
interface ProcessingState {
  stage: 'idle' | 'parsing' | 'auto-fixing' | 'matching' | 'completed' | 'error';
  message: string;
  progress: number;
  details?: any;
}

interface MatchingResult {
  score: number;
  compatibility: string;
  confidence: number;
  recommendations: {
    candidat: string[];
    entreprise: string[];
  };
  strengths: string[];
  concerns: string[];
  processingTime: number;
  enhancedMetrics?: any;
}

// 🎯 Composant principal Enhanced Bridge
export const NextvisionEnhancedBridge: React.FC = () => {
  // États principaux
  const [processingState, setProcessingState] = useState<ProcessingState>({
    stage: 'idle',
    message: 'Prêt pour l\'intégration Enhanced',
    progress: 0
  });
  
  const [candidatData, setCandidatData] = useState<EnhancedParserV4Data | null>(null);
  const [entrepriseData, setEntrepriseData] = useState<ChatGPTCommitmentData | null>(null);
  const [matchingResult, setMatchingResult] = useState<MatchingResult | null>(null);
  
  // États UI
  const [activeTab, setActiveTab] = useState<'candidat' | 'entreprise' | 'matching'>('candidat');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [enhancedStats, setEnhancedStats] = useState<any>(null);

  // Configuration questionnaires
  const [candidatQuestionnaire, setCandidatQuestionnaire] = useState<QuestionnaireData>({
    raison_ecoute: 'Rémunération trop faible',
    salary_min: 35000,
    salary_max: 50000,
    preferred_location: 'Paris',
    remote_ok: false
  });

  const [entrepriseQuestionnaire, setEntrepriseQuestionnaire] = useState<QuestionnaireData>({
    company_name: '',
    urgence: 'normal',
    remote_possible: false
  });

  // 🔄 Chargement stats Enhanced au montage
  useEffect(() => {
    loadEnhancedStats();
  }, []);

  const loadEnhancedStats = async () => {
    try {
      const stats = await nextvisionEnhancedService.getEnhancedStats();
      setEnhancedStats(stats);
    } catch (error) {
      console.warn('Could not load Enhanced stats:', error);
    }
  };

  // 🔧 Simulation parsing CV Enhanced (normalement connecté à votre parser)
  const simulateEnhancedCVParsing = useCallback(async (file: File): Promise<EnhancedParserV4Data> => {
    // Simulation du parsing Enhanced Universal Parser v4.0
    // Dans votre vraie implémentation, ceci appellerait votre parser existant
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      personal_info: {
        firstName: "Marie",
        lastName: "Dupont", 
        email: "marie.dupont@email.com",
        phone: "+33 6 12 34 56 78"
      },
      skills: [
        "Maîtrise du logiciel comptable CEGID",
        "Gestion comptable et fiscale",
        "Déclarations TVA et fiscales",
        "Analyse financière"
      ],
      experience: {
        total_years: 7
      },
      softwares: ["CEGID", "Excel", "SAP"],
      languages: {
        "Français": "Natif",
        "Anglais": "Courant"
      },
      work_experience: [
        {
          position: "Comptable Senior",
          company: "Cabinet ABC",
          duration: "3 ans",
          skills_acquired: ["CEGID", "Fiscalité"]
        }
      ],
      education: "Master Comptabilité Contrôle Audit",
      parsing_confidence: 0.92,
      extraction_time_ms: 1850
    };
  }, []);

  // 🔧 Simulation parsing Fiche de Poste ChatGPT (normalement connecté à votre système)
  const simulateChatGPTJobParsing = useCallback(async (jobText: string): Promise<ChatGPTCommitmentData> => {
    // Simulation du parsing ChatGPT Commitment-
    // Dans votre vraie implémentation, ceci appellerait votre système ChatGPT existant
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      titre: "Comptable Unique H/F",
      localisation: "Paris 8ème",
      contrat: "CDI",
      salaire: "35K à 38K annuels",
      competences_requises: [
        "Maîtrise du logiciel comptable CEGID",
        "Gestion comptable et fiscale",
        "Déclarations TVA",
        "Rigueur et autonomie"
      ],
      experience_requise: "5 ans - 10 ans",
      missions: [
        "Tenue comptabilité complète",
        "Déclarations fiscales et sociales",
        "Suivi trésorerie",
        "Relation clients"
      ],
      avantages: [
        "Tickets restaurant",
        "Mutuelle",
        "Prime annuelle"
      ],
      badges_auto_rempli: ["Auto-rempli"],
      fiche_poste_originale: jobText,
      parsing_confidence: 0.88,
      extraction_time_ms: 1420
    };
  }, []);

  // 🚀 Pipeline complet Enhanced
  const handleEnhancedMatching = async () => {
    if (!candidatData || !entrepriseData) {
      setProcessingState({
        stage: 'error',
        message: 'Données candidat et entreprise requises',
        progress: 0
      });
      return;
    }

    try {
      // Étape 1: Auto-fix et validation
      setProcessingState({
        stage: 'auto-fixing',
        message: 'Auto-fix intelligent en cours...',
        progress: 25
      });

      // Étape 2: Matching bidirectionnel
      setProcessingState({
        stage: 'matching',
        message: 'Matching bidirectionnel Enhanced...',
        progress: 50
      });

      const result = await nextvisionEnhancedService.convertAndMatchDirect(
        candidatData,
        entrepriseData,
        candidatQuestionnaire,
        entrepriseQuestionnaire
      );

      // Étape 3: Traitement résultat
      setProcessingState({
        stage: 'completed',
        message: 'Matching Enhanced terminé!',
        progress: 100,
        details: result
      });

      // Formatage résultat pour l'interface
      setMatchingResult({
        score: result.matching_score,
        compatibility: result.compatibility,
        confidence: result.confidence,
        recommendations: {
          candidat: result.recommandations_candidat,
          entreprise: result.recommandations_entreprise
        },
        strengths: result.points_forts,
        concerns: result.points_attention,
        processingTime: result.processing_time_ms,
        enhancedMetrics: result.component_scores?.semantique_details?.enhanced_metadata
      });

      // Rechargement stats
      await loadEnhancedStats();

    } catch (error) {
      console.error('Enhanced matching failed:', error);
      setProcessingState({
        stage: 'error',
        message: `Erreur: ${error.message}`,
        progress: 0
      });
    }
  };

  // 📁 Gestion upload CV
  const handleCVUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setProcessingState({
        stage: 'parsing',
        message: 'Parsing CV avec Enhanced Universal Parser v4.0...',
        progress: 30
      });

      const parsedData = await simulateEnhancedCVParsing(file);
      setCandidatData(parsedData);

      setProcessingState({
        stage: 'completed',
        message: 'CV parsé avec succès!',
        progress: 100
      });

    } catch (error) {
      setProcessingState({
        stage: 'error',
        message: `Erreur parsing CV: ${error.message}`,
        progress: 0
      });
    }
  };

  // 📋 Gestion parsing fiche de poste
  const handleJobPosting = async (jobText: string) => {
    if (!jobText.trim()) return;

    try {
      setProcessingState({
        stage: 'parsing',
        message: 'Parsing fiche de poste avec ChatGPT Commitment-...',
        progress: 40
      });

      const parsedData = await simulateChatGPTJobParsing(jobText);
      setEntrepriseData(parsedData);

      setProcessingState({
        stage: 'completed',
        message: 'Fiche de poste parsée avec succès!',
        progress: 100
      });

    } catch (error) {
      setProcessingState({
        stage: 'error',
        message: `Erreur parsing fiche: ${error.message}`,
        progress: 0
      });
    }
  };

  // 🎨 Fonction de rendu du score
  const renderMatchingScore = (score: number) => {
    const percentage = Math.round(score * 100);
    const color = percentage >= 80 ? 'text-green-600' : 
                  percentage >= 60 ? 'text-yellow-600' : 'text-red-600';
    
    return (
      <div className="text-center">
        <div className={`text-4xl font-bold ${color}`}>
          {percentage}%
        </div>
        <div className="text-sm text-gray-600">Score de matching</div>
      </div>
    );
  };

  // 🎨 Fonction de rendu de la compatibilité
  const renderCompatibility = (compatibility: string) => {
    const compatibilityConfig = {
      'excellent': { label: 'Excellent', color: 'bg-green-100 text-green-800', icon: '🎯' },
      'good': { label: 'Bon', color: 'bg-blue-100 text-blue-800', icon: '👍' },
      'average': { label: 'Moyen', color: 'bg-yellow-100 text-yellow-800', icon: '⚖️' },
      'poor': { label: 'Faible', color: 'bg-orange-100 text-orange-800', icon: '⚠️' },
      'incompatible': { label: 'Incompatible', color: 'bg-red-100 text-red-800', icon: '❌' }
    };

    const config = compatibilityConfig[compatibility] || compatibilityConfig['average'];

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        <span className="mr-2">{config.icon}</span>
        {config.label}
      </span>
    );
  };

  // 🎨 Rendu principal
  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      {/* En-tête Enhanced */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <span className="mr-3">🎯</span>
              Nextvision Enhanced Bridge
            </h1>
            <p className="text-gray-600 mt-2">
              Intégration révolutionnaire Commitment- ↔ Nextvision avec auto-fix intelligent
            </p>
          </div>
          
          {enhancedStats && (
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-blue-800">
                <div>🔧 Auto-fixes: {enhancedStats.enhanced_bridge_stats?.auto_fixes_applied || 0}</div>
                <div>✅ Succès: {enhancedStats.enhanced_bridge_stats?.success_rate_percent || 0}%</div>
                <div>⚡ Cache: {enhancedStats.enhanced_bridge_stats?.cache_hit_rate_percent || 0}%</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Barre de progression */}
      {processingState.stage !== 'idle' && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {processingState.message}
            </span>
            <span className="text-sm text-gray-500">
              {processingState.progress}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-500 ${
                processingState.stage === 'error' ? 'bg-red-600' :
                processingState.stage === 'completed' ? 'bg-green-600' : 'bg-blue-600'
              }`}
              style={{ width: `${processingState.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'candidat', label: '👤 Candidat', icon: '📄' },
            { id: 'entreprise', label: '🏢 Entreprise', icon: '📋' },
            { id: 'matching', label: '🎯 Matching', icon: '⚡' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        
        {/* Tab Candidat */}
        {activeTab === 'candidat' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload CV */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="mr-2">📄</span>
                Enhanced Universal Parser v4.0
              </h3>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleCVUpload}
                  className="hidden"
                  id="cv-upload"
                />
                <label htmlFor="cv-upload" className="cursor-pointer">
                  <div className="text-gray-600">
                    <span className="text-4xl mb-4 block">📁</span>
                    <p className="text-lg font-medium">Uploadez un CV</p>
                    <p className="text-sm mt-2">PDF, DOC, DOCX (max 10MB)</p>
                  </div>
                </label>
              </div>

              {candidatData && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center mb-2">
                    <span className="text-green-600 mr-2">✅</span>
                    <span className="font-medium">CV parsé avec succès!</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <div>👤 {candidatData.personal_info.firstName} {candidatData.personal_info.lastName}</div>
                    <div>💼 {candidatData.skills.length} compétences détectées</div>
                    <div>📈 {candidatData.experience.total_years} ans d'expérience</div>
                    <div>🎯 Confiance: {Math.round(candidatData.parsing_confidence * 100)}%</div>
                  </div>
                </div>
              )}
            </div>

            {/* Questionnaire Candidat */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">⚙️ Configuration Candidat</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Raison d'écoute
                  </label>
                  <select
                    value={candidatQuestionnaire.raison_ecoute}
                    onChange={(e) => setCandidatQuestionnaire(prev => ({
                      ...prev,
                      raison_ecoute: e.target.value
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Rémunération trop faible">Rémunération trop faible</option>
                    <option value="Poste ne coïncide pas avec poste proposé">Poste ne coïncide pas</option>
                    <option value="Poste trop loin de mon domicile">Poste trop loin</option>
                    <option value="Manque de flexibilité">Manque de flexibilité</option>
                    <option value="Manque de perspectives d'évolution">Manque de perspectives</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Salaire min (€)
                    </label>
                    <input
                      type="number"
                      value={candidatQuestionnaire.salary_min}
                      onChange={(e) => setCandidatQuestionnaire(prev => ({
                        ...prev,
                        salary_min: parseInt(e.target.value)
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Salaire max (€)
                    </label>
                    <input
                      type="number"
                      value={candidatQuestionnaire.salary_max}
                      onChange={(e) => setCandidatQuestionnaire(prev => ({
                        ...prev,
                        salary_max: parseInt(e.target.value)
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Localisation préférée
                  </label>
                  <input
                    type="text"
                    value={candidatQuestionnaire.preferred_location}
                    onChange={(e) => setCandidatQuestionnaire(prev => ({
                      ...prev,
                      preferred_location: e.target.value
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={candidatQuestionnaire.remote_ok}
                    onChange={(e) => setCandidatQuestionnaire(prev => ({
                      ...prev,
                      remote_ok: e.target.checked
                    }))}
                    className="mr-2"
                  />
                  <label className="text-sm text-gray-700">
                    Accepte le télétravail
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Entreprise */}
        {activeTab === 'entreprise' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Parsing Fiche de Poste */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <span className="mr-2">📋</span>
                ChatGPT Commitment- Parser
              </h3>
              
              <div className="space-y-4">
                <textarea
                  placeholder="Collez votre fiche de poste ici..."
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {
                    if (e.target.value.length > 100) {
                      handleJobPosting(e.target.value);
                    }
                  }}
                />
                
                <div className="text-xs text-gray-500">
                  💡 Le parsing automatique se déclenche dès que vous tapez plus de 100 caractères
                </div>
              </div>

              {entrepriseData && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center mb-2">
                    <span className="text-green-600 mr-2">✅</span>
                    <span className="font-medium">Fiche de poste parsée!</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <div>💼 {entrepriseData.titre}</div>
                    <div>📍 {entrepriseData.localisation}</div>
                    <div>💰 {entrepriseData.salaire}</div>
                    <div>🎯 Confiance: {Math.round(entrepriseData.parsing_confidence * 100)}%</div>
                  </div>
                </div>
              )}
            </div>

            {/* Questionnaire Entreprise */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">⚙️ Configuration Entreprise</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom de l'entreprise
                  </label>
                  <input
                    type="text"
                    value={entrepriseQuestionnaire.company_name}
                    onChange={(e) => setEntrepriseQuestionnaire(prev => ({
                      ...prev,
                      company_name: e.target.value
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Cabinet Comptable Excellence"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Urgence de recrutement
                  </label>
                  <select
                    value={entrepriseQuestionnaire.urgence}
                    onChange={(e) => setEntrepriseQuestionnaire(prev => ({
                      ...prev,
                      urgence: e.target.value as any
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="critique">🔴 Critique</option>
                    <option value="urgent">🟠 Urgent</option>
                    <option value="normal">🟡 Normal</option>
                    <option value="long terme">🟢 Long terme</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={entrepriseQuestionnaire.remote_possible}
                    onChange={(e) => setEntrepriseQuestionnaire(prev => ({
                      ...prev,
                      remote_possible: e.target.checked
                    }))}
                    className="mr-2"
                  />
                  <label className="text-sm text-gray-700">
                    Télétravail possible
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Matching */}
        {activeTab === 'matching' && (
          <div className="space-y-6">
            {/* Bouton Matching */}
            <div className="text-center">
              <button
                onClick={handleEnhancedMatching}
                disabled={!candidatData || !entrepriseData || processingState.stage === 'matching'}
                className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg text-lg flex items-center justify-center mx-auto"
              >
                <span className="mr-2">🚀</span>
                {processingState.stage === 'matching' ? 'Matching en cours...' : 'Lancer Matching Enhanced'}
              </button>
              
              {(!candidatData || !entrepriseData) && (
                <p className="text-sm text-gray-500 mt-2">
                  Veuillez d'abord parser un CV et une fiche de poste
                </p>
              )}
            </div>

            {/* Résultats Matching */}
            {matchingResult && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Score principal */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
                  {renderMatchingScore(matchingResult.score)}
                  <div className="mt-4">
                    {renderCompatibility(matchingResult.compatibility)}
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    Confiance: {Math.round(matchingResult.confidence * 100)}%
                  </div>
                </div>

                {/* Points forts */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h4 className="font-semibold text-green-800 mb-4 flex items-center">
                    <span className="mr-2">✅</span>
                    Points forts
                  </h4>
                  <ul className="space-y-2">
                    {matchingResult.strengths.map((strength, index) => (
                      <li key={index} className="text-sm text-green-700 flex items-start">
                        <span className="mr-2 mt-1">•</span>
                        {strength}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Points d'attention */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                  <h4 className="font-semibold text-yellow-800 mb-4 flex items-center">
                    <span className="mr-2">⚠️</span>
                    Points d'attention
                  </h4>
                  <ul className="space-y-2">
                    {matchingResult.concerns.map((concern, index) => (
                      <li key={index} className="text-sm text-yellow-700 flex items-start">
                        <span className="mr-2 mt-1">•</span>
                        {concern}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Recommandations */}
            {matchingResult && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h4 className="font-semibold text-blue-800 mb-4 flex items-center">
                    <span className="mr-2">👤</span>
                    Recommandations Candidat
                  </h4>
                  <ul className="space-y-2">
                    {matchingResult.recommendations.candidat.map((rec, index) => (
                      <li key={index} className="text-sm text-blue-700 flex items-start">
                        <span className="mr-2 mt-1">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                  <h4 className="font-semibold text-purple-800 mb-4 flex items-center">
                    <span className="mr-2">🏢</span>
                    Recommandations Entreprise
                  </h4>
                  <ul className="space-y-2">
                    {matchingResult.recommendations.entreprise.map((rec, index) => (
                      <li key={index} className="text-sm text-purple-700 flex items-start">
                        <span className="mr-2 mt-1">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Métriques Enhanced */}
            {matchingResult?.enhancedMetrics && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <h4 className="font-semibold text-gray-800 mb-4 flex items-center">
                  <span className="mr-2">🔧</span>
                  Métriques Enhanced Bridge
                </h4>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                  <div className="text-center">
                    <div className="font-semibold text-lg text-blue-600">
                      {matchingResult.enhancedMetrics.performance_breakdown?.total_auto_fixes || 0}
                    </div>
                    <div className="text-gray-600">Auto-fixes</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-lg text-green-600">
                      {matchingResult.processingTime.toFixed(0)}ms
                    </div>
                    <div className="text-gray-600">Temps total</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-lg text-purple-600">
                      {matchingResult.enhancedMetrics.performance_breakdown?.candidat_conversion_ms?.toFixed(0) || 0}ms
                    </div>
                    <div className="text-gray-600">Conv. candidat</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-lg text-orange-600">
                      {matchingResult.enhancedMetrics.performance_breakdown?.entreprise_conversion_ms?.toFixed(0) || 0}ms
                    </div>
                    <div className="text-gray-600">Conv. entreprise</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Options avancées */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-gray-600 hover:text-gray-800 flex items-center"
        >
          <span className="mr-2">{showAdvanced ? '▼' : '▶'}</span>
          Options avancées Enhanced Bridge
        </button>
        
        {showAdvanced && (
          <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-4">
            <button
              onClick={() => nextvisionEnhancedService.clearEnhancedCache()}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm"
            >
              🧹 Vider cache
            </button>
            <button
              onClick={loadEnhancedStats}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm"
            >
              🔄 Recharger stats
            </button>
            <button
              onClick={() => nextvisionEnhancedService.updateEnhancedConfig({ enable_auto_fix: true })}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm"
            >
              ⚙️ Config Enhanced
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default NextvisionEnhancedBridge;
