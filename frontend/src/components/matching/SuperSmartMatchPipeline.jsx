/**
 * SuperSmartMatch Unified - Composant React pour le pipeline des 3 étapes
 * 1. Parsing automatique → 2. Questionnaire → 3. Matching intelligent
 */

import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle, Clock, Award, TrendingUp, Brain, Target } from 'lucide-react';

const SuperSmartMatchPipeline = () => {
  // État du pipeline
  const [currentStep, setCurrentStep] = useState(1);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parsedData, setParsedData] = useState(null);
  const [matchingResult, setMatchingResult] = useState(null);
  const [error, setError] = useState(null);

  // État des fichiers uploadés
  const [cvFile, setCvFile] = useState(null);
  const [jobFile, setJobFile] = useState(null);

  // État du questionnaire
  const [questionnaireData, setQuestionnaireData] = useState({
    motivation: 7,
    disponibilite: 8,
    mobilite: 5,
    salaire_souhaite: '',
    experience_specifique: '',
    objectifs_carriere: ''
  });

  const API_BASE_URL = process.env.NEXT_PUBLIC_SUPERSMARTMATCH_URL || 'http://localhost:5052';

  // Génération d'un ID de session unique
  useEffect(() => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  // ÉTAPE 1: Démarrage du parsing
  const startParsing = async () => {
    if (!cvFile && !jobFile) {
      setError('Veuillez sélectionner au moins un fichier (CV ou Offre)');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      if (cvFile) formData.append('cv_file', cvFile);
      if (jobFile) formData.append('job_file', jobFile);
      formData.append('session_id', sessionId);

      const response = await fetch(`${API_BASE_URL}/api/unified-match/start`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.error) {
        throw new Error(result.error);
      }

      if (result.status === 'waiting_questionnaire') {
        setParsedData(result.parsed_data);
        setCurrentStep(2);
      }
    } catch (error) {
      setError(`Erreur de parsing: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // ÉTAPE 3: Finalisation avec questionnaire
  const completeMatching = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/unified-match/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          questionnaire_data: {
            ...questionnaireData,
            salaire_souhaite: parseInt(questionnaireData.salaire_souhaite) || 0
          }
        }),
      });

      const result = await response.json();

      if (result.error) {
        throw new Error(result.error);
      }

      setMatchingResult(result);
      setCurrentStep(3);
    } catch (error) {
      setError(`Erreur de matching: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Gestion des fichiers
  const handleFileUpload = (file, type) => {
    if (file && file.size > 10 * 1024 * 1024) {
      setError('Fichier trop volumineux (max 10MB)');
      return;
    }

    if (type === 'cv') {
      setCvFile(file);
    } else if (type === 'job') {
      setJobFile(file);
    }

    setError(null);
  };

  // Mise à jour du questionnaire
  const updateQuestionnaire = (field, value) => {
    setQuestionnaireData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Obtenir la classe CSS du score
  const getScoreClass = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 65) return 'text-blue-600 bg-blue-100';
    if (score >= 50) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  // Redémarrer le processus
  const resetPipeline = () => {
    setCurrentStep(1);
    setParsedData(null);
    setMatchingResult(null);
    setCvFile(null);
    setJobFile(null);
    setError(null);
    setQuestionnaireData({
      motivation: 7,
      disponibilite: 8,
      mobilite: 5,
      salaire_souhaite: '',
      experience_specifique: '',
      objectifs_carriere: ''
    });
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
          🚀 SuperSmartMatch Unifié
        </h1>
        <p className="text-xl text-gray-600">
          Algorithme de matching intelligent avec pipeline des 3 étapes
        </p>
      </div>

      {/* Indicateur d'étapes */}
      <div className="flex justify-center mb-8">
        <div className="flex items-center space-x-8">
          {[
            { num: 1, title: 'Parsing', icon: FileText, desc: 'Analyse documents' },
            { num: 2, title: 'Questionnaire', icon: CheckCircle, desc: 'Infos complémentaires' },
            { num: 3, title: 'Matching', icon: Award, desc: 'Résultats intelligents' }
          ].map(({ num, title, icon: Icon, desc }) => (
            <div key={num} className={`flex flex-col items-center ${
              currentStep === num ? 'text-blue-600' : 
              currentStep > num ? 'text-green-600' : 'text-gray-400'
            }`}>
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-2 ${
                currentStep === num ? 'bg-blue-100 border-2 border-blue-600' :
                currentStep > num ? 'bg-green-100 border-2 border-green-600' :
                'bg-gray-100 border-2 border-gray-300'
              }`}>
                <Icon size={24} />
              </div>
              <h3 className="font-semibold">{title}</h3>
              <p className="text-sm text-center">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Messages d'erreur */}
      {error && (
        <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          <h3 className="font-semibold">❌ Erreur</h3>
          <p>{error}</p>
        </div>
      )}

      {/* Loader */}
      {isLoading && (
        <div className="mb-6 p-6 bg-blue-50 border border-blue-200 rounded-lg text-center">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mb-4"></div>
          <p className="text-blue-800 font-semibold">
            {currentStep === 1 ? '🔍 Parsing des documents en cours...' : '⚡ Calcul du matching...'}
          </p>
        </div>
      )}

      {/* ÉTAPE 1: Upload des fichiers */}
      {currentStep === 1 && (
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <FileText className="mr-2" /> Étape 1: Upload et Parsing des Documents
          </h2>
          <p className="text-gray-600 mb-6">
            Uploadez vos documents pour démarrer l'analyse automatique avec notre technologie de parsing avancée.
          </p>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* Upload CV */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
              <div className="mb-4">
                <FileText size={48} className="mx-auto text-gray-400" />
              </div>
              <h3 className="font-semibold mb-2">CV / Curriculum Vitae</h3>
              <p className="text-sm text-gray-600 mb-4">PDF, DOC, DOCX - Max 10MB</p>
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(e) => handleFileUpload(e.target.files[0], 'cv')}
                className="hidden"
                id="cv-upload"
              />
              <label
                htmlFor="cv-upload"
                className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-blue-700 transition-colors"
              >
                Choisir un fichier CV
              </label>
              {cvFile && (
                <div className="mt-4 p-3 bg-green-100 rounded-lg">
                  <p className="text-green-800 font-semibold">📄 {cvFile.name}</p>
                  <p className="text-sm text-green-600">{(cvFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              )}
            </div>

            {/* Upload Job */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
              <div className="mb-4">
                <FileText size={48} className="mx-auto text-gray-400" />
              </div>
              <h3 className="font-semibold mb-2">Offre d'Emploi</h3>
              <p className="text-sm text-gray-600 mb-4">PDF, DOC, DOCX - Max 10MB</p>
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(e) => handleFileUpload(e.target.files[0], 'job')}
                className="hidden"
                id="job-upload"
              />
              <label
                htmlFor="job-upload"
                className="inline-block bg-purple-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-purple-700 transition-colors"
              >
                Choisir une offre
              </label>
              {jobFile && (
                <div className="mt-4 p-3 bg-green-100 rounded-lg">
                  <p className="text-green-800 font-semibold">📋 {jobFile.name}</p>
                  <p className="text-sm text-green-600">{(jobFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={startParsing}
            disabled={(!cvFile && !jobFile) || isLoading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold text-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            🚀 Démarrer l'Analyse et le Matching
          </button>
        </div>
      )}

      {/* ÉTAPE 2: Questionnaire */}
      {currentStep === 2 && parsedData && (
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <CheckCircle className="mr-2" /> Étape 2: Questionnaire de Matching
          </h2>

          {/* Résultats du parsing */}
          <div className="bg-white rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4">✅ Résultats du parsing automatique</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold">📄 CV Analysé</h4>
                <p className="text-sm mt-2">
                  {parsedData.cv_data ? 
                    `✅ ${parsedData.cv_data.competences?.length || 0} compétences détectées` :
                    '❌ Erreur de parsing'
                  }
                </p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <h4 className="font-semibold">📋 Offre Analysée</h4>
                <p className="text-sm mt-2">
                  {parsedData.job_data ? 
                    `✅ ${parsedData.job_data.competences_requises?.length || 0} compétences requises` :
                    '❌ Erreur de parsing'
                  }
                </p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <h4 className="font-semibold">🎯 Confiance</h4>
                <p className="text-sm mt-2">
                  {(parsedData.parsing_confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>

          {/* Formulaire questionnaire */}
          <div className="bg-white rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-6">Informations complémentaires pour un matching optimal</h3>
            
            <div className="space-y-6">
              {/* Sliders */}
              {[
                { key: 'motivation', label: '🎯 Motivation pour ce poste', icon: Target },
                { key: 'disponibilite', label: '⏰ Disponibilité', icon: Clock },
                { key: 'mobilite', label: '🚗 Mobilité géographique', icon: TrendingUp }
              ].map(({ key, label, icon: Icon }) => (
                <div key={key} className="">
                  <label className="block font-semibold mb-2 flex items-center">
                    <Icon size={20} className="mr-2" />
                    {label} (1-10)
                  </label>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm">1</span>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={questionnaireData[key]}
                      onChange={(e) => updateQuestionnaire(key, parseInt(e.target.value))}
                      className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <span className="text-sm">10</span>
                    <span className="font-bold text-blue-600 min-w-[30px] text-center">
                      {questionnaireData[key]}
                    </span>
                  </div>
                </div>
              ))}

              {/* Champs texte */}
              <div>
                <label className="block font-semibold mb-2">💰 Salaire souhaité (€/an)</label>
                <input
                  type="number"
                  placeholder="45000"
                  value={questionnaireData.salaire_souhaite}
                  onChange={(e) => updateQuestionnaire('salaire_souhaite', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold mb-2">🎓 Expérience spécifique dans le domaine</label>
                <textarea
                  rows="3"
                  placeholder="Décrivez votre expérience pertinente pour ce poste..."
                  value={questionnaireData.experience_specifique}
                  onChange={(e) => updateQuestionnaire('experience_specifique', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold mb-2">🎯 Objectifs de carrière</label>
                <textarea
                  rows="3"
                  placeholder="Vos objectifs professionnels à court et moyen terme..."
                  value={questionnaireData.objectifs_carriere}
                  onChange={(e) => updateQuestionnaire('objectifs_carriere', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <button
              onClick={completeMatching}
              disabled={isLoading}
              className="w-full mt-6 bg-gradient-to-r from-green-600 to-blue-600 text-white py-4 px-6 rounded-lg font-semibold text-lg hover:from-green-700 hover:to-blue-700 disabled:opacity-50 transition-all"
            >
              ⚡ Lancer le Matching Complet
            </button>
          </div>
        </div>
      )}

      {/* ÉTAPE 3: Résultats */}
      {currentStep === 3 && matchingResult && (
        <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-6 flex items-center">
            <Award className="mr-2" /> Résultats du Matching SuperSmartMatch Unifié
          </h2>

          {/* Scores principaux */}
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div className="bg-white rounded-lg p-6 text-center">
              <h3 className="text-lg font-semibold mb-2 flex items-center justify-center">
                <Target className="mr-2" /> Score Entreprise
              </h3>
              <div className={`text-4xl font-bold rounded-lg py-4 ${
                getScoreClass(matchingResult.matching_score_entreprise)
              }`}>
                {matchingResult.matching_score_entreprise.toFixed(1)}%
              </div>
              <p className="text-gray-600 mt-2">Adéquation du candidat au poste</p>
            </div>

            <div className="bg-white rounded-lg p-6 text-center">
              <h3 className="text-lg font-semibold mb-2 flex items-center justify-center">
                <Brain className="mr-2" /> Score Candidat
              </h3>
              <div className={`text-4xl font-bold rounded-lg py-4 ${
                getScoreClass(matchingResult.matching_score_candidat)
              }`}>
                {matchingResult.matching_score_candidat.toFixed(1)}%
              </div>
              <p className="text-gray-600 mt-2">Attrait du poste pour le candidat</p>
            </div>
          </div>

          {/* Analyse détaillée */}
          <div className="bg-white rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4">📊 Analyse Détaillée</h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-2">🚀 Contributions au Score</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Boost Questionnaire:</span>
                    <span className="font-bold text-green-600">
                      +{(matchingResult.questionnaire_boost * 100).toFixed(1)}%
                    </span>
                  </div>
                  {matchingResult.semantic_boost && (
                    <div className="flex justify-between">
                      <span>Boost Sémantique:</span>
                      <span className="font-bold text-blue-600">
                        +{(matchingResult.semantic_boost * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">🎯 Qualité des Données</h4>
                <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-blue-500 h-4 rounded-full transition-all duration-1000"
                    style={{width: `${matchingResult.parsing_quality.total_data_quality * 100}%`}}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">
                  {(matchingResult.parsing_quality.total_data_quality * 100).toFixed(1)}% de données complètes
                </p>
              </div>
            </div>
          </div>

          {/* Recommandations */}
          <div className="bg-white rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4">💡 Recommandations</h3>
            <ul className="space-y-3">
              {matchingResult.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Actions */}
          <div className="flex space-x-4">
            <button className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors">
              💾 Sauvegarder les Résultats
            </button>
            <button className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
              📄 Exporter PDF
            </button>
            <button 
              onClick={resetPipeline}
              className="flex-1 bg-gray-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
            >
              🔄 Nouveau Matching
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuperSmartMatchPipeline;