// Fonction pour gérer les paramètres d'URL et mettre à jour l'interface
function setupMessagerieFromParams() {
  // Récupérer les paramètres de l'URL
  const urlParams = new URLSearchParams(window.location.search);
  const candidateId = urlParams.get('id');
  const candidateName = urlParams.get('name');
  
  // Si nous avons un nom de candidat, mettre à jour le titre
  if (candidateName) {
    // Mettre à jour le titre principal (généralement h3 dans l'en-tête de conversation)
    const interlocutorName = document.querySelector('.interlocutor-details h3');
    if (interlocutorName) {
      interlocutorName.textContent = candidateName;
    }
    
    // Mettre à jour l'avatar (initiales)
    const avatarElement = document.querySelector('.interlocutor-info .avatar');
    if (avatarElement) {
      // Prendre les initiales du nom (première lettre du prénom et première lettre du nom si disponible)
      const nameParts = candidateName.split(' ');
      let initials = nameParts[0].charAt(0).toUpperCase();
      if (nameParts.length > 1) {
        initials += '-' + nameParts[1].charAt(0).toUpperCase();
      }
      avatarElement.textContent = initials;
    }
    
    // Mettre à jour le titre de la page
    document.title = `Messagerie - ${candidateName}`;
    
    // Mettre à jour l'en-tête de la messagerie
    const messageHeader = document.querySelector('.page-header h2');
    if (messageHeader) {
      messageHeader.textContent = `MESSAGERIE : AVEC ${candidateName.toUpperCase()}`;
    }
    
    // Mettre à jour les avatars dans les messages
    const outgoingAvatars = document.querySelectorAll('.message.outgoing .message-avatar');
    outgoingAvatars.forEach(avatar => {
      avatar.textContent = 'T'; // T pour Thomas (l'utilisateur actuel)
    });
    
    const incomingAvatars = document.querySelectorAll('.message.incoming .message-avatar');
    incomingAvatars.forEach(avatar => {
      avatar.textContent = candidateName.charAt(0).toUpperCase();
    });
  }
}

// Exécuter la fonction lorsque le document est chargé
document.addEventListener('DOMContentLoaded', setupMessagerieFromParams);

// Si la page est déjà chargée, exécuter la fonction immédiatement
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  setupMessagerieFromParams();
}