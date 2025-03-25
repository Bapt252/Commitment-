// Script pour intégrer les membres de l'équipe de la page organisation vers la planification d'entretien

document.addEventListener('DOMContentLoaded', function() {
  // Fonction pour récupérer les membres de l'équipe depuis la page organisation
  async function fetchTeamMembers() {
    try {
      const response = await fetch('organization.html');
      const html = await response.text();
      
      // Créer un DOM temporaire à partir du HTML récupéré
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      
      // Sélectionner tous les membres de l'équipe depuis le tableau
      const teamMembersRows = doc.querySelectorAll('#contactsTable tbody tr');
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
      
      return teamMembers;
    } catch (error) {
      console.error('Erreur lors de la récupération des membres:', error);
      // En cas d'erreur, renvoyer les membres par défaut
      return [
        { firstName: 'Marie', lastName: 'DURAND', role: 'Chargée recrutement', roleType: 'Manager', email: 'marie.durand@example.com', fullName: 'Marie DURAND' },
        { firstName: 'Joseph', lastName: 'EUX', role: 'DAF', roleType: 'Admin', email: 'joseph.eux@example.com', fullName: 'Joseph EUX' },
        { firstName: 'Sophia', lastName: 'MARTIN', role: 'Assistante RH', roleType: 'Recruteur', email: 'sophia.martin@example.com', fullName: 'Sophia MARTIN' }
      ];
    }
  }

  // Fonction pour afficher les membres de l'équipe dans la modal
  function displayTeamMembers(members, container) {
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
    // Sélectionner tous les boutons d'assignation
    const assignButtons = document.querySelectorAll('.btn[class*="assigner-participants"], .btn[class*="assigner-des-participants"]');
    const teamMembers = await fetchTeamMembers();
    
    assignButtons.forEach(button => {
      button.addEventListener('click', function(event) {
        // Empêcher la navigation ou soumission du formulaire
        event.preventDefault();
        
        // Sélectionner ou créer le conteneur modal pour les membres
        let memberContainer = document.querySelector('#team-members-container');
        if (!memberContainer) {
          // Si le conteneur n'existe pas, le créer et l'ajouter à la modal
          const modal = document.querySelector('.modal.fade.show') || document.querySelector('.modal[id*="assign"]');
          if (modal) {
            memberContainer = document.createElement('div');
            memberContainer.id = 'team-members-container';
            memberContainer.className = 'team-members-list mt-3';
            
            // Ajouter le conteneur avant le footer de la modal ou à la fin du body de la modal
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) {
              modalBody.appendChild(memberContainer);
            }
          }
        }
        
        // Si le conteneur existe maintenant, afficher les membres
        if (memberContainer) {
          displayTeamMembers(teamMembers, memberContainer);
        }
      });
    });
    
    // Initialiser également l'événement pour le bouton "planifier un entretien"
    const scheduleButtons = document.querySelectorAll('.action-button.schedule-interview-btn');
    scheduleButtons.forEach(button => {
      button.addEventListener('click', async function() {
        // Attendre un court instant pour que la modal s'ouvre
        setTimeout(async () => {
          // Sélectionner le bouton "assigner des participants" dans la modal qui vient de s'ouvrir
          const assignButton = document.querySelector('.modal.fade.show .btn[class*="assigner-des-participants"]');
          if (assignButton) {
            // Simuler un clic sur ce bouton pour déclencher l'affichage des membres
            assignButton.click();
          } else {
            // Si le bouton n'est pas trouvé, tenter d'injecter directement les membres
            const modal = document.querySelector('.modal.fade.show');
            if (modal) {
              let memberContainer = modal.querySelector('#team-members-container');
              if (!memberContainer) {
                memberContainer = document.createElement('div');
                memberContainer.id = 'team-members-container';
                memberContainer.className = 'team-members-list mt-3';
                
                const modalBody = modal.querySelector('.modal-body');
                if (modalBody) {
                  modalBody.appendChild(memberContainer);
                  displayTeamMembers(teamMembers, memberContainer);
                }
              }
            }
          }
        }, 300);
      });
    });
  }

  // Styles CSS pour l'affichage des membres d'équipe
  function addStyles() {
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
  addStyles();
  initParticipantAssignment();
});
