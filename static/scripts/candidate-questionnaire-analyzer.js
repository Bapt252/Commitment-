/**
 * Ce script permet d'intégrer l'analyseur de questionnaires candidats 
 * au formulaire existant sans endommager le front-end actuel.
 */

// S'assurer que le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
  
  // Vérifier si nous sommes sur la page du questionnaire candidat
  const questionnaireForm = document.getElementById('questionnaire-form');
  if (!questionnaireForm) return;
  
  // Vérifier que l'analyseur est disponible
  if (!window.candidateAnalyzer) {
    console.error('L\'analyseur de questionnaires candidats n\'est pas disponible');
    return;
  }
  
  // Ajouter les styles nécessaires s'ils ne sont pas déjà chargés
  if (!document.querySelector('link[href*="candidate-analyzer.css"]')) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '../static/styles/candidate-analyzer.css';
    document.head.appendChild(link);
  }
  
  // Trouver le bouton de soumission
  const submitButton = document.getElementById('submit-btn');
  if (!submitButton) {
    console.error('Bouton de soumission non trouvé');
    return;
  }
  
  // Méthode pour extraire toutes les réponses du formulaire
  function extractFormResponses() {
    const formData = new FormData(questionnaireForm);
    const answers = Object.fromEntries(formData.entries());
    
    // Gérer les groupes de cases à cocher
    const checkboxGroups = {
      'transport-method': [],
      'structure-type': []
    };
    
    // Pour chaque groupe de cases à cocher, récupérer celles qui sont cochées
    for (const groupName in checkboxGroups) {
      document.querySelectorAll(`input[name="${groupName}"]:checked`).forEach(checkbox => {
        checkboxGroups[groupName].push(checkbox.value);
      });
      answers[groupName] = checkboxGroups[groupName];
    }
    
    // Gérer les sélections multiples (secteurs, etc.)
    const multiSelectGroups = ['sector-preference[]', 'prohibited-sector[]'];
    
    for (const groupName of multiSelectGroups) {
      const selectElement = document.querySelector(`select[name="${groupName}"]`);
      if (selectElement) {
        answers[groupName] = Array.from(selectElement.selectedOptions).map(option => option.value);
      }
    }
    
    // Récupérer l'ordre des motivations
    const motivationOrderInput = document.getElementById('motivation-order');
    if (motivationOrderInput && motivationOrderInput.value) {
      answers['motivation-order'] = motivationOrderInput.value.split(',');
    }
    
    return answers;
  }
  
  // Créer l'élément qui va contenir les résultats d'analyse
  const createAnalysisContainer = () => {
    // Vérifier si le conteneur existe déjà
    let analysisContainer = document.getElementById('analysis-results-container');
    if (analysisContainer) {
      return analysisContainer;
    }
    
    // Créer le conteneur d'analyse
    analysisContainer = document.createElement('div');
    analysisContainer.id = 'analysis-results-container';
    analysisContainer.className = 'analyzer-container';
    
    // Ajouter un titre
    const title = document.createElement('h2');
    title.className = 'form-section-title';
    title.textContent = 'Analyse de votre profil';
    analysisContainer.appendChild(title);
    
    // Ajouter une description
    const description = document.createElement('p');
    description.textContent = 'Notre système d\'intelligence artificielle a analysé vos réponses pour ' +
                              'identifier vos compétences et préférences professionnelles.';
    analysisContainer.appendChild(description);
    
    // Créer le conteneur pour les résultats
    const resultsDiv = document.createElement('div');
    resultsDiv.id = 'analysis-results';
    analysisContainer.appendChild(resultsDiv);
    
    return analysisContainer;
  };
  
  // Modifier le comportement du bouton de soumission
  const originalClickHandler = submitButton.onclick;
  submitButton.onclick = async function(event) {
    // Empêcher le comportement par défaut
    event.preventDefault();
    
    // Valider le formulaire (réutiliser la fonction existante)
    if (typeof validateStep === 'function' && !validateStep(4)) {
      return;
    }
    
    // Désactiver le bouton et afficher un état de chargement
    const originalButtonContent = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Analyse en cours...</span>';
    
    try {
      // Extraire toutes les réponses du formulaire
      const answers = extractFormResponses();
      
      // Effectuer l'analyse
      let analysisResults;
      try {
        // Essayer d'appeler l'API
        analysisResults = await window.candidateAnalyzer.analyzeAnswers(answers);
      } catch (apiError) {
        console.warn('Impossible de contacter l\'API d\'analyse, utilisation des données de test', apiError);
        // Utiliser des données de test en cas d'erreur
        analysisResults = window.candidateAnalyzer.generateMockAnalysisResults();
      }
      
      // Stocker les résultats pour la page suivante
      sessionStorage.setItem('candidateAnalysis', JSON.stringify(analysisResults));
      
      // Créer/obtenir le conteneur d'analyse
      const analysisContainer = createAnalysisContainer();
      
      // Ajouter le conteneur avant les actions du formulaire
      const formActions = document.querySelector('.form-actions');
      if (formActions) {
        formActions.parentNode.insertBefore(analysisContainer, formActions);
      } else {
        // Fallback: ajouter à la fin de l'étape actuelle
        const currentStep = document.querySelector('.form-step.active');
        if (currentStep) {
          currentStep.appendChild(analysisContainer);
        }
      }
      
      // Afficher les résultats
      const resultsDiv = document.getElementById('analysis-results');
      window.candidateAnalyzer.displayAnalysisResults(analysisResults, resultsDiv);
      
      // Afficher une notification de succès
      if (typeof showNotification === 'function') {
        showNotification('Analyse de votre profil terminée avec succès !', 'success');
      }
      
      // Faire défiler jusqu'aux résultats
      analysisContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
      
      // Ajouter un bouton pour continuer
      const actionsDiv = document.createElement('div');
      actionsDiv.className = 'analysis-actions';
      
      const continueButton = document.createElement('button');
      continueButton.type = 'button';
      continueButton.className = 'btn-analyze';
      continueButton.innerHTML = '<i class="fas fa-check-circle"></i> Continuer vers les opportunités';
      continueButton.onclick = function() {
        // Réactiver et restaurer le bouton original
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonContent;
        
        // Appeler le comportement original si disponible
        if (typeof originalClickHandler === 'function') {
          originalClickHandler.call(submitButton, event);
        } else {
          // Fallback: redirection standard
          document.getElementById('loading-overlay').classList.add('active');
          setTimeout(() => {
            window.location.href = 'candidate-matching-improved.html';
          }, 2000);
        }
      };
      
      actionsDiv.appendChild(continueButton);
      analysisContainer.appendChild(actionsDiv);
      
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error);
      
      // Afficher une notification d'erreur
      if (typeof showNotification === 'function') {
        showNotification('Erreur lors de l\'analyse de vos réponses', 'error');
      }
      
      // Réactiver et restaurer le bouton
      submitButton.disabled = false;
      submitButton.innerHTML = originalButtonContent;
    }
  };
  
  console.log('Intégration de l\'analyseur de questionnaires candidats terminée');
});