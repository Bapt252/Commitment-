// Script pour intégrer les membres de l'équipe de la page organisation vers la planification d'entretien

document.addEventListener('DOMContentLoaded', function() {
  console.log("Script d'intégration des membres d'équipe chargé");
  
  // Fonction pour récupérer les membres de l'équipe depuis la page organisation
  async function fetchTeamMembers() {
    try {
      // Chemin absolu pour éviter les problèmes de chemin relatif
      const response = await fetch('/Commitment-/templates/organization.html');
      const html = await response.text();
      console.log("Page organisation récupérée, longueur:", html.length);
      
      // Créer un DOM temporaire à partir du HTML récupéré
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      
      // Sélectionner tous les membres de l'équipe depuis le tableau
      const teamMembersRows = doc.querySelectorAll('#contactsTable tbody tr');
      console.log("Nombre de membres trouvés:", teamMembersRows.length);
      
      const teamMembers = [];
      
      teamMembersRows.forEach(row => {
        const columns = row.querySelectorAll('td');
        if (columns.length >= 4) {
          const firstName = columns[0].textContent.trim();
          const lastName = columns[1].textContent.trim();
          const role = columns[2].textContent.trim().split('\n')[0].trim();
          const email = columns[3].textContent.trim();
          
          // Détecter le type de rôle (Admin, Manager, Recruteur)
          let roleType = 'Membre';
          if (row.querySelector('.status-admin')) {
            roleType = 'Admin';
          } else if (row.querySelector('.status-manager')) {
            roleType = 'Manager';
          } else if (row.querySelector('.status-recruiter')) {
            roleType = 'Recruteur';
          }
          
          teamMembers.push({
            firstName,
            lastName,
            role,
            roleType,
            email,
            fullName: `${firstName} ${lastName}`
          });
        }
      });
      
      console.log("Membres d'équipe extraits:", teamMembers.length);
      return teamMembers;
    } catch (error) {
      console.error('Erreur lors de la récupération des membres:', error);
      // En cas d'erreur, renvoyer les membres par défaut
      console.log("Utilisation des membres par défaut");
      return [
        { firstName: 'Marie', lastName: 'DURAND', role: 'Chargée recrutement', roleType: 'Manager', email: 'marie.durand@example.com', fullName: 'Marie DURAND' },
        { firstName: 'Joseph', lastName: 'EUX', role: 'DAF', roleType: 'Admin', email: 'joseph.eux@example.com', fullName: 'Joseph EUX' },
        { firstName: 'Sophia', lastName: 'MARTIN', role: 'Assistante RH', roleType: 'Recruteur', email: 'sophia.martin@example.com', fullName: 'Sophia MARTIN' }
      ];
    }
  }

  // Fonction pour afficher les membres de l'équipe dans la modal
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

  // Fonction d'initialisation pour les boutons d'assignation
  async function initParticipantAssignment() {
    console.log("Initialisation des boutons d'assignation");
    
    // Sélectionner tous les boutons d'assignation par ID et par texte
    const assignButtons = document.querySelectorAll('#assign-interview-participants, #assign-interaction-members, #assign-event-members, #assign-job-member');
    console.log("Nombre de boutons d'assignation trouvés:", assignButtons.length);
    
    const teamMembers = await fetchTeamMembers();
    
    assignButtons.forEach(button => {
      console.log("Ajout d'un écouteur d'événement au bouton:", button.id || button.textContent);
      
      button.addEventListener('click', function(event) {
        console.log("Bouton d'assignation cliqué:", button.id || button.textContent);
        
        // Empêcher la navigation ou soumission du formulaire
        event.preventDefault();
        
        // Sélectionner ou créer le conteneur modal pour les membres
        let memberContainer = document.querySelector('#team-members-container');
        if (!memberContainer) {
          console.log("Création d'un nouveau conteneur de membres");
          
          // Si le conteneur n'existe pas, le créer et l'ajouter à la modal active
          const modal = document.querySelector('.modal:not([style*="display: none"])') || document.querySelector('.modal.fade.show');
          
          if (modal) {
            console.log("Modal active trouvée:", modal.id);
            memberContainer = document.createElement('div');
            memberContainer.id = 'team-members-container';
            memberContainer.className = 'team-members-list mt-3';
            
            // Ajouter le conteneur au body de la modal
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) {
              modalBody.appendChild(memberContainer);
              console.log("Conteneur ajouté à la modal");
            } else {
              console.log("Body de la modal non trouvé");
            }
          } else {
            console.log("Aucune modal active trouvée");
          }
        } else {
          console.log("Conteneur de membres existant trouvé");
        }
        
        // Si le conteneur existe maintenant, afficher les membres
        if (memberContainer) {
          displayTeamMembers(teamMembers, memberContainer);
        } else {
          console.log("Impossible de créer ou trouver le conteneur de membres");
        }
      });
    });
    
    // Initialiser également l'événement pour le bouton "planifier un entretien"
    console.log("Initialisation des boutons 'planifier un entretien'");
    const scheduleButtons = document.querySelectorAll('.action-button.schedule-interview-btn');
    console.log("Nombre de boutons de planification trouvés:", scheduleButtons.length);
    
    scheduleButtons.forEach(button => {
      button.addEventListener('click', function() {
        console.log("Bouton 'planifier un entretien' cliqué");
        
        // Attendre un court instant pour que la modal s'ouvre
        setTimeout(() => {
          console.log("Recherche de la modal et du bouton d'assignation");
          
          // Trouver la modal ouverte
          const modal = document.querySelector('.modal:not([style*="display: none"])') || document.querySelector('.modal.fade.show');
          
          if (modal) {
            console.log("Modal trouvée:", modal.id);
            
            // Trouver le bouton d'assignation dans cette modal
            const assignButton = modal.querySelector('#assign-interview-participants');
            
            if (assignButton) {
              console.log("Bouton d'assignation trouvé, simulation de clic");
              assignButton.click();
            } else {
              console.log("Bouton d'assignation non trouvé, création directe du conteneur");
              
              // Si le bouton n'est pas trouvé, tenter d'injecter directement les membres
              let memberContainer = modal.querySelector('#team-members-container');
              if (!memberContainer) {
                memberContainer = document.createElement('div');
                memberContainer.id = 'team-members-container';
                memberContainer.className = 'team-members-list mt-3';
                
                const modalBody = modal.querySelector('.modal-body');
                if (modalBody) {
                  modalBody.appendChild(memberContainer);
                  displayTeamMembers(teamMembers, memberContainer);
                  console.log("Conteneur créé et membres affichés directement");
                } else {
                  console.log("Body de la modal non trouvé");
                }
              }
            }
          } else {
            console.log("Aucune modal ouverte trouvée après le clic");
          }
        }, 500);
      });
    });
  }

  // Styles CSS pour l'affichage des membres d'équipe
  function addStyles() {
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
  }

  // Initialiser l'application
  console.log("Démarrage de l'initialisation");
  addStyles();
  initParticipantAssignment();
  console.log("Initialisation terminée");
});

// Ajouter un écouteur d'événement global pour détecter les clics sur les boutons d'assignation
// Ceci est une solution de secours au cas où l'initialisation normale échouerait
document.addEventListener('click', function(event) {
  // Vérifier si l'élément cliqué est un bouton d'assignation
  if (event.target && (
      (event.target.id && (
        event.target.id === 'assign-interview-participants' || 
        event.target.id === 'assign-interaction-members' || 
        event.target.id === 'assign-event-members' || 
        event.target.id === 'assign-job-member'
      )) || 
      (event.target.textContent && event.target.textContent.includes('Assigner des participant'))
    )) {
      
    console.log("Bouton d'assignation détecté par l'écouteur global");
    
    // Attendre un court instant avant d'essayer d'afficher les membres
    setTimeout(async function() {
      try {
        // Trouver la modal ouverte
        const modal = document.querySelector('.modal:not([style*="display: none"])') || document.querySelector('.modal.fade.show');
        
        if (modal) {
          console.log("Modal trouvée pour l'écouteur global:", modal.id);
          
          // Créer ou trouver le conteneur des membres
          let memberContainer = modal.querySelector('#team-members-container');
          if (!memberContainer) {
            memberContainer = document.createElement('div');
            memberContainer.id = 'team-members-container';
            memberContainer.className = 'team-members-list mt-3';
            
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) {
              modalBody.appendChild(memberContainer);
              console.log("Conteneur créé par l'écouteur global");
              
              // Membres par défaut (en cas d'échec de récupération)
              const defaultMembers = [
                { firstName: 'Marie', lastName: 'DURAND', role: 'Chargée recrutement', roleType: 'Manager', email: 'marie.durand@example.com', fullName: 'Marie DURAND' },
                { firstName: 'Joseph', lastName: 'EUX', role: 'DAF', roleType: 'Admin', email: 'joseph.eux@example.com', fullName: 'Joseph EUX' },
                { firstName: 'Sophia', lastName: 'MARTIN', role: 'Assistante RH', roleType: 'Recruteur', email: 'sophia.martin@example.com', fullName: 'Sophia MARTIN' }
              ];
              
              // Afficher les membres
              memberContainer.innerHTML = '';
              defaultMembers.forEach(member => {
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
                
                memberContainer.appendChild(memberElement);
              });
              
              console.log("Membres affichés par l'écouteur global");
            }
          }
        }
      } catch (error) {
        console.error("Erreur dans l'écouteur global:", error);
      }
    }, 300);
  }
});
