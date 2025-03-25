// Fonction pour rendre les boutons "Envoyer un message" fonctionnels
function activateMessageButtons() {
  // Sélectionner tous les boutons "Envoyer un message"
  const messageButtons = document.querySelectorAll('.send-message-btn');
  
  // Ajouter un écouteur d'événement à chaque bouton
  messageButtons.forEach(button => {
    button.addEventListener('click', function(event) {
      // Empêcher le comportement par défaut du bouton
      event.preventDefault();
      
      // Récupérer l'ID du candidat depuis l'attribut data-candidate-id
      const candidateId = this.getAttribute('data-candidate-id');
      
      // Récupérer le nom du candidat (le texte du premier élément parent avec la classe candidate-card)
      const candidateCard = this.closest('.candidate-card');
      let candidateName = '';
      
      if (candidateCard) {
        // Le nom est généralement le premier élément de texte dans la carte
        const nameElement = candidateCard.querySelector('.candidate-name');
        if (nameElement) {
          candidateName = nameElement.textContent.trim();
        }
      }
      
      // Rediriger vers la page de messagerie avec les paramètres
      window.location.href = `https://bapt252.github.io/Commitment-/templates/messagerie-candidat.html?id=${candidateId}&name=${encodeURIComponent(candidateName)}`;
    });
  });
}

// Exécuter la fonction lorsque le document est chargé
document.addEventListener('DOMContentLoaded', activateMessageButtons);

// Si la page est déjà chargée, exécuter la fonction immédiatement
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  activateMessageButtons();
}