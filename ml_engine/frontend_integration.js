/**
 * Module d'intégration du moteur ML avec le frontend existant
 * Ce script remplace la fonction parseJobDescription par une version qui utilise l'API ML
 */

// Sauvegarder la fonction originale basée sur des règles
const parseJobDescriptionRuleBased = window.parseJobDescription;

// Nouvelle fonction qui utilise l'API ML
async function parseJobDescriptionML(jobDescription) {
  try {
    // Appeler l'API ML
    const response = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: jobDescription }),
    });

    if (!response.ok) {
      console.warn('Erreur lors de l\'appel à l\'API ML, utilisation du système basé sur des règles.', response.status);
      return parseJobDescriptionRuleBased(jobDescription);
    }

    const mlResult = await response.json();
    
    // Convertir le format de l'API ML au format attendu par le frontend
    return {
      jobTitle: mlResult.job_title || '',
      experience: mlResult.experience || '',
      skills: mlResult.skills || [],
      education: mlResult.education || '',
      contract: mlResult.contract || '',
      location: mlResult.location || '',
      salary: mlResult.salary || '',
      rawText: jobDescription,
      confidence: mlResult.confidence_scores || {},
      ml_powered: true, // Indicateur pour savoir qu'on utilise ML
      job_posting_id: mlResult.job_posting_id, // ID pour le feedback
      annotation_id: mlResult.annotation_id // ID pour le feedback
    };
    
  } catch (error) {
    console.warn('Erreur lors de l\'utilisation de l\'API ML, repli sur le système basé sur des règles.', error);
    return parseJobDescriptionRuleBased(jobDescription);
  }
}

// Fonction pour envoyer un feedback lorsque l'utilisateur corrige les résultats
async function sendFeedback(originalResults, correctedResults) {
  // Ne pas envoyer de feedback si l'analyse n'était pas basée sur ML
  if (!originalResults.ml_powered) {
    return;
  }
  
  try {
    // Construire l'objet de feedback
    const feedback = {
      job_posting_id: originalResults.job_posting_id,
      original_annotation_id: originalResults.annotation_id,
      corrected_annotation: {
        job_posting_id: originalResults.job_posting_id,
        job_title: correctedResults.jobTitle,
        experience: correctedResults.experience,
        skills: correctedResults.skills,
        education: correctedResults.education,
        contract: correctedResults.contract,
        location: correctedResults.location,
        salary: correctedResults.salary,
        confidence_scores: {},
        source: "feedback"
      },
      user_id: "frontend_user" // Idéalement, utilisez un identifiant utilisateur réel
    };
    
    // Envoyer le feedback à l'API
    const response = await fetch('http://localhost:8000/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedback),
    });

    if (!response.ok) {
      console.warn('Erreur lors de l\'envoi du feedback.', response.status);
      return false;
    }
    
    const result = await response.json();
    console.log('Feedback envoyé avec succès.', result);
    return true;
    
  } catch (error) {
    console.warn('Erreur lors de l\'envoi du feedback.', error);
    return false;
  }
}

// Fonction d'initialisation pour intégrer le ML dans le frontend existant
function initMLIntegration() {
  // Remplacer la fonction parseJobDescription par la version ML
  window.parseJobDescription = parseJobDescriptionML;
  
  // Ajouter une fonction pour le feedback
  window.sendMLFeedback = sendFeedback;
  
  // Si la page contient déjà le script job-description-parser.js
  document.addEventListener('DOMContentLoaded', function() {
    // Mettre à jour les boutons et interfaces pour activer le ML
    const analyzeTextBtn = document.getElementById('analyze-text-btn');
    const analyzeFileBtn = document.getElementById('analyze-file-btn');
    
    if (analyzeTextBtn) {
      const originalText = analyzeTextBtn.innerHTML;
      analyzeTextBtn.innerHTML = originalText.replace('Analyser', 'Analyser avec IA');
    }
    
    if (analyzeFileBtn) {
      const originalText = analyzeFileBtn.innerHTML;
      analyzeFileBtn.innerHTML = originalText.replace('Analyser', 'Analyser avec IA');
    }
    
    // Ajouter un listener pour le bouton d'application qui capture les corrections
    const applyAnalysisBtn = document.getElementById('apply-analysis-btn');
    if (applyAnalysisBtn) {
      // Sauvegarder le handler d'origine
      const originalOnClick = applyAnalysisBtn.onclick;
      
      applyAnalysisBtn.onclick = function() {
        // Si on a des résultats d'analyse
        if (window.analysisResults && window.analysisResults.ml_powered) {
          // Capturer les valeurs corrigées
          const correctedResults = {
            jobTitle: document.getElementById('preview-jobTitle').textContent,
            experience: document.getElementById('preview-experience').textContent,
            education: document.getElementById('preview-education').textContent,
            contract: document.getElementById('preview-contract').textContent,
            location: document.getElementById('preview-location').textContent,
            salary: document.getElementById('preview-salary').textContent,
            skills: Array.from(document.getElementById('preview-skills').querySelectorAll('.skill-tag'))
              .map(el => el.textContent)
          };
          
          // Envoyer le feedback si des corrections ont été apportées
          const originalResults = {...window.analysisResults};
          window.sendMLFeedback(originalResults, correctedResults)
            .then(success => {
              if (success) {
                console.log('Feedback ML envoyé avec succès');
              }
            });
        }
        
        // Appeler le handler d'origine
        if (originalOnClick) {
          originalOnClick.call(this);
        }
      };
    }
    
    // Ajouter un texte indiquant que l'analyse est alimentée par ML
    const previewHeader = document.querySelector('.preview-header .preview-title');
    if (previewHeader) {
      const mlBadge = document.createElement('span');
      mlBadge.className = 'ml-badge';
      mlBadge.textContent = 'IA';
      mlBadge.style.backgroundColor = '#7C3AED';
      mlBadge.style.color = 'white';
      mlBadge.style.padding = '2px 6px';
      mlBadge.style.borderRadius = '4px';
      mlBadge.style.fontSize = '0.7rem';
      mlBadge.style.marginLeft = '8px';
      mlBadge.style.fontWeight = 'bold';
      
      previewHeader.appendChild(mlBadge);
    }
  });
  
  console.log('Intégration ML activée: l\'analyse des fiches de poste utilise maintenant l\'IA.');
}

// Activer l'intégration ML
initMLIntegration();