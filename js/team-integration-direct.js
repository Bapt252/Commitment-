// Solution directe pour l'intégration des membres d'équipe
// Ce script s'exécute dès qu'il est chargé, sans attendre l'événement DOMContentLoaded

// Ajout des styles CSS
(function addStyles() {
  console.log("Ajout des styles CSS");
  const styleElement = document.createElement('style');
  styleElement.textContent = `
    .team-members-list {
      max-height: 300px;
      overflow-y: auto;
      margin-top: 15px;
      border: 1px solid #eee;
      border-radius: 8px;
    }
    
    .team-member-card {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 15px;
      border-bottom: 1px solid #eee;
      transition: background-color 0.2s;
    }
    
    .team-member-card:hover {
      background-color: #f8f9fa;
    }
    
    .team-member-card:last-child {
      border-bottom: none;
    }
    
    .member-info {
      flex: 1;
    }
    
    .member-name {
      font-weight: 600;
      color: #333;
    }
    
    .member-role {
      font-size: 0.85rem;
      color: #666;
    }
    
    .member-email {
      font-size: 0.8rem;
      color: #888;
    }
    
    .role-badge {
      display: inline-block;
      font-size: 0.7rem;
      padding: 2px 8px;
      border-radius: 12px;
      margin-top: 5px;
    }
    
    .badge-admin {
      background-color: #ffd166;
      color: #664d00;
    }
    
    .badge-manager {
      background-color: #118ab2;
      color: white;
    }
    
    .badge-recruiter {
      background-color: #06d6a0;
      color: #004d3d;
    }
    
    .badge-member {
      background-color: #ced4da;
      color: #495057;
    }
    
    .checkbox-container {
      position: relative;
      cursor: pointer;
      user-select: none;
      width: 22px;
      height: 22px;
    }
    
    .checkbox-container input {
      position: absolute;
      opacity: 0;
      cursor: pointer;
      height: 0;
      width: 0;
    }
    
    .checkmark {
      position: absolute;
      top: 0;
      left: 0;
      height: 22px;
      width: 22px;
      background-color: #fff;
      border: 2px solid #6c5ce7;
      border-radius: 4px;
    }
    
    .checkbox-container:hover input ~ .checkmark {
      background-color: #f0f0f0;
    }
    
    .checkbox-container input:checked ~ .checkmark {
      background-color: #6c5ce7;
    }
    
    .checkmark:after {
      content: "";
      position: absolute;
      display: none;
    }
    
    .checkbox-container input:checked ~ .checkmark:after {
      display: block;
    }
    
    .checkbox-container .checkmark:after {
      left: 7px;
      top: 3px;
      width: 5px;
      height: 10px;
      border: solid white;
      border-width: 0 2px 2px 0;
      transform: rotate(45deg);
    }
  `;
  document.head.appendChild(styleElement);
})();

// Membres d'équipe par défaut - utilisés directement dans le gestionnaire de clic
const defaultMembers = [
  { firstName: 'Marie', lastName: 'DURAND', role: 'Chargée recrutement', roleType: 'Manager', email: 'marie.durand@example.com', fullName: 'Marie DURAND' },
  { firstName: 'Joseph', lastName: 'EUX', role: 'DAF', roleType: 'Admin', email: 'joseph.eux@example.com', fullName: 'Joseph EUX' },
  { firstName: 'Sophia', lastName: 'MARTIN', role: 'Assistante RH', roleType: 'Recruteur', email: 'sophia.martin@example.com', fullName: 'Sophia MARTIN' },
  { firstName: 'Thomas', lastName: 'MARTIN', role: 'Directeur des Ressources Humaines', roleType: 'Admin', email: 'thomas.martin@example.com', fullName: 'Thomas MARTIN' }
];

// Fonction pour afficher les membres
function displayTeamMembers(members, container) {
  console.log("Affichage des membres dans le conteneur");
  container.innerHTML = '';
  
  members.forEach(member => {
    const memberElement = document.createElement('div');
    memberElement.className = 'team-member-card';
    
    // Définir la couleur du badge selon le rôle
    let badgeClass = '';
    switch(member.roleType) {
      case 'Admin':
        badgeClass = 'badge-admin';
        break;
      case 'Manager':
        badgeClass = 'badge-manager';
        break;
      case 'Recruteur':
        badgeClass = 'badge-recruiter';
        break;
      default:
        badgeClass = 'badge-member';
    }
    
    memberElement.innerHTML = `
      <div class="member-info">
        <div class="member-name">${member.fullName}</div>
        <div class="member-role">${member.role}</div>
        <div class="member-email">${member.email}</div>
        <span class="role-badge ${badgeClass}">${member.roleType}</span>
      </div>
      <div class="member-actions">
        <label class="checkbox-container">
          <input type="checkbox" class="member-select" data-email="${member.email}" data-name="${member.fullName}">
          <span class="checkmark"></span>
        </label>
      </div>
    `;
    
    container.appendChild(memberElement);
  });
}

// Utilisation d'une solution simplifiée avec un écouteur de clic global
document.addEventListener('click', function(event) {
  console.log("Clic détecté:", event.target.id, event.target.className, event.target.textContent.trim());
  
  // Vérifier si l'élément cliqué est un bouton d'assignation ou similaire
  if (event.target && (
    (event.target.id && (
      event.target.id === 'assign-interview-participants' || 
      event.target.id === 'assign-interaction-members' || 
      event.target.id === 'assign-event-members' || 
      event.target.id === 'assign-job-member'
    )) || 
    (event.target.textContent && (
      event.target.textContent.includes('Assigner des participants') ||
      event.target.textContent.includes('Assigner des membres')
    ))
  )) {
    console.log("Bouton d'assignation détecté:", event.target.id || event.target.textContent);
    
    // Empêcher la navigation ou soumission du formulaire
    event.preventDefault();
    
    // Attendre un court instant avant d'essayer d'afficher les membres
    setTimeout(function() {
      try {
        // Trouver la modal ouverte
        const modal = document.querySelector('.modal[style*="display: block"]') || document.querySelector('.modal.show');
        
        if (modal) {
          console.log("Modal trouvée:", modal.id);
          
          // Créer ou trouver le conteneur des membres
          let memberContainer = modal.querySelector('#team-members-container');
          if (!memberContainer) {
            memberContainer = document.createElement('div');
            memberContainer.id = 'team-members-container';
            memberContainer.className = 'team-members-list mt-3';
            
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) {
              modalBody.appendChild(memberContainer);
              console.log("Conteneur créé");
              displayTeamMembers(defaultMembers, memberContainer);
              console.log("Membres affichés");
            } else {
              console.log("Body de la modal non trouvé");
            }
          } else {
            console.log("Conteneur existant trouvé");
            displayTeamMembers(defaultMembers, memberContainer);
          }
        } else {
          console.log("Aucune modal ouverte trouvée");
        }
      } catch (error) {
        console.error("Erreur:", error);
      }
    }, 200);
  }
  
  // Également vérifier les boutons de planification d'entretien
  if (event.target && (
    (event.target.className && event.target.className.includes('schedule-interview-btn')) ||
    (event.target.parentElement && event.target.parentElement.className && 
     event.target.parentElement.className.includes('schedule-interview-btn'))
  )) {
    console.log("Bouton de planification d'entretien détecté");
    
    // Attendre que la modal s'ouvre
    setTimeout(function() {
      const interviewModal = document.querySelector('#interview-modal[style*="display: block"]') || 
                             document.querySelector('#interview-modal.show');
      
      if (interviewModal) {
        console.log("Modal d'entretien trouvée");
        
        // Trouver le bouton d'assignation et cliquer dessus
        const assignButton = interviewModal.querySelector('#assign-interview-participants');
        if (assignButton) {
          console.log("Bouton d'assignation trouvé, simulation de clic");
          assignButton.click();
        } else {
          console.log("Bouton d'assignation non trouvé");
        }
      } else {
        console.log("Modal d'entretien non trouvée");
      }
    }, 500);
  }
});

// Message de confirmation d'initialisation
console.log("Script d'intégration directe des membres d'équipe initialisé");
