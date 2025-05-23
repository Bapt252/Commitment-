// Script pour ajouter l'option de suppression du processus de recrutement

// Fonction pour ajouter le bouton de suppression à la modale
function ajouterBoutonSuppression() {
  // Sélectionner la modale
  const modal = document.querySelector('.modal-content') || document.getElementById('job-offer-modal');
  
  if (!modal) return; // Sortir si la modale n'existe pas
  
  // Vérifier si le bouton existe déjà
  if (document.getElementById('btn-supprimer-offre')) return;
  
  // Trouver les boutons d'action
  const formActions = modal.querySelector('.form-actions');
  if (!formActions) return;
  
  // Chercher le bouton "Annuler"
  const cancelButton = formActions.querySelector('#cancel-job-btn, button[type="button"]:not([id="assign-job-member"])');
  if (!cancelButton) return;
  
  // Créer le bouton de suppression
  const deleteButton = document.createElement('button');
  deleteButton.id = 'btn-supprimer-offre';
  deleteButton.className = 'btn btn-danger';
  deleteButton.type = 'button';
  deleteButton.textContent = 'Supprimer';
  
  // Appliquer les styles pour placer le bouton à côté de "Annuler"
  formActions.style.display = 'flex';
  formActions.style.flexDirection = 'row';
  formActions.style.justifyContent = 'space-between';
  formActions.style.alignItems = 'center';
  
  // Créer un conteneur flex pour les boutons de gauche (Annuler et Supprimer)
  const leftButtons = document.createElement('div');
  leftButtons.style.display = 'flex';
  leftButtons.style.gap = '10px'; // Espace entre les boutons
  
  // Déplacer le bouton Annuler dans le conteneur de gauche
  cancelButton.parentNode.insertBefore(leftButtons, cancelButton);
  leftButtons.appendChild(cancelButton);
  
  // Ajouter le bouton Supprimer dans le conteneur de gauche
  leftButtons.appendChild(deleteButton);
  
  // Chercher le bouton Enregistrer
  const submitButton = formActions.querySelector('button[type="submit"]');
  if (submitButton) {
    // S'assurer que le bouton d'enregistrement est à droite
    submitButton.style.marginLeft = 'auto';
  }
  
  // Ajouter les styles pour le bouton de suppression
  deleteButton.style.backgroundColor = '#dc3545';
  deleteButton.style.borderColor = '#dc3545';
  deleteButton.style.color = 'white';
  
  // Ajouter un style au survol
  deleteButton.addEventListener('mouseenter', function() {
    this.style.backgroundColor = '#c82333';
    this.style.borderColor = '#bd2130';
  });
  
  deleteButton.addEventListener('mouseleave', function() {
    this.style.backgroundColor = '#dc3545';
    this.style.borderColor = '#dc3545';
  });
  
  // Ajouter l'écouteur d'événement pour la suppression
  deleteButton.addEventListener('click', supprimerOffreEmploi);
}

// Fonction pour supprimer l'offre d'emploi
function supprimerOffreEmploi() {
  // Récupérer l'ID de l'offre actuellement ouverte
  const currentJobId = document.querySelector('.modal').dataset.jobId || localStorage.getItem('currentEditingJobId');
  
  if (!currentJobId) {
    alert("Impossible de trouver l'identifiant de l'offre d'emploi.");
    return;
  }
  
  // Demander confirmation avant de supprimer
  if (confirm("Êtes-vous sûr de vouloir supprimer cette offre d'emploi? Cette action est irréversible.")) {
    // Récupérer les offres existantes
    let jobOffers = JSON.parse(localStorage.getItem('jobOffers') || '[]');
    let commitmentJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
    
    // Filtrer l'offre à supprimer
    jobOffers = jobOffers.filter(job => job.id !== currentJobId);
    commitmentJobs = commitmentJobs.filter(job => job.id !== currentJobId);
    
    // Sauvegarder les offres mises à jour
    localStorage.setItem('jobOffers', JSON.stringify(jobOffers));
    localStorage.setItem('commitment_jobs', JSON.stringify(commitmentJobs));
    
    // Fermer la modale
    const closeBtn = document.querySelector('.modal .close') || document.querySelector('.modal .btn-close') || document.querySelector('.modal-close');
    if (closeBtn) closeBtn.click();
    
    // Rafraîchir la page pour afficher les changements
    setTimeout(() => {
      location.reload();
    }, 300);
    
    // Afficher une notification de succès
    if (typeof showNotification === 'function') {
      showNotification("Offre d'emploi supprimée avec succès", "success");
    }
  }
}

// Observer les changements du DOM pour détecter l'ouverture de la modale
const observer = new MutationObserver(mutations => {
  mutations.forEach(mutation => {
    if (mutation.type === 'childList' && mutation.addedNodes.length) {
      // Chercher si une modale a été ajoutée
      const modalAdded = Array.from(mutation.addedNodes).some(node => 
        node.nodeType === Node.ELEMENT_NODE && 
        (node.classList && node.classList.contains('modal') || node.querySelector('.modal'))
      );
      
      if (modalAdded) {
        // Attendre un court instant que la modale soit complètement chargée
        setTimeout(ajouterBoutonSuppression, 100);
      }
    }
  });
});

// Commencer à observer les changements dans le document
observer.observe(document.body, { childList: true, subtree: true });

// Alternative: Surcharger la fonction existante d'ouverture de modale si elle existe
document.addEventListener('DOMContentLoaded', () => {
  if (typeof openJobOfferModal === 'function' || window.openJobOfferModal) {
    const originalOpenModal = openJobOfferModal || window.openJobOfferModal;
    window.openJobOfferModal = function(jobId) {
      // Appeler la fonction originale
      originalOpenModal(jobId);
      // Stocker l'ID actuel pour la suppression
      localStorage.setItem('currentEditingJobId', jobId);
      // Ajouter notre bouton
      setTimeout(ajouterBoutonSuppression, 100);
    };
  }
  
  // Ajouter un écouteur d'événement pour le bouton "Modifier"
  document.querySelectorAll('.edit-job-btn').forEach(button => {
    button.addEventListener('click', function(e) {
      const jobId = this.getAttribute('data-job-id');
      localStorage.setItem('currentEditingJobId', jobId);
      setTimeout(ajouterBoutonSuppression, 300);
    });
  });
  
  // Ajouter des styles CSS pour le bouton de suppression
  const style = document.createElement('style');
  style.textContent = `
    .btn-danger {
      background-color: #dc3545;
      border-color: #dc3545;
      color: white;
    }
    .btn-danger:hover {
      background-color: #c82333;
      border-color: #bd2130;
    }
  `;
  document.head.appendChild(style);
  
  // Exécuter une fois au chargement de la page pour les modales déjà ouvertes
  setTimeout(ajouterBoutonSuppression, 300);
});