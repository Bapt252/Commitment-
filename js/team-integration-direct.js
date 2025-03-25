// Script simplifié et robuste pour l'intégration des membres d'équipe

document.addEventListener('click', function(event) {
  // Vérifier si l'élément cliqué est un bouton d'assignation
  if (event.target && (
    (event.target.id && (
      event.target.id === 'assign-interview-participants' ||
      event.target.id === 'assign-interaction-members' ||
      event.target.id === 'assign-event-members' ||
      event.target.id === 'assign-job-member'
    )) ||
    (event.target.textContent && (
      event.target.textContent.includes('Assigner des participant') ||
      event.target.textContent.includes('Assigner des membre')
    ))
  )) {
    console.log("Bouton d'assignation détecté:", event.target.id || event.target.textContent);
    
    // Empêcher la navigation ou soumission du formulaire
    event.preventDefault();
    
    // Supprimer tout conteneur existant
    const existingContainer = document.querySelector('#team-members-visible');
    if (existingContainer) {
      existingContainer.remove();
    }
    
    // Créer un nouveau conteneur visible
    const container = document.createElement('div');
    container.id = 'team-members-visible';
    container.style.maxHeight = '300px';
    container.style.overflowY = 'auto';
    container.style.marginTop = '15px';
    container.style.border = '1px solid #ccc';
    container.style.borderRadius = '8px';
    container.style.backgroundColor = '#fff';
    container.style.zIndex = '9999';
    container.style.position = 'relative';
    
    // Titre du conteneur
    const title = document.createElement('div');
    title.style.padding = '10px';
    title.style.borderBottom = '1px solid #eee';
    title.style.fontWeight = 'bold';
    title.textContent = 'Membres disponibles';
    container.appendChild(title);
    
    // Membres de l'équipe
    const members = [
      { firstName: 'Marie', lastName: 'DURAND', role: 'Chargée recrutement', roleType: 'Manager', email: 'marie.durand@example.com', fullName: 'Marie DURAND' },
      { firstName: 'Joseph', lastName: 'EUX', role: 'DAF', roleType: 'Admin', email: 'joseph.eux@example.com', fullName: 'Joseph EUX' },
      { firstName: 'Sophia', lastName: 'MARTIN', role: 'Assistante RH', roleType: 'Recruteur', email: 'sophia.martin@example.com', fullName: 'Sophia MARTIN' },
      { firstName: 'Thomas', lastName: 'MARTIN', role: 'Directeur des Ressources Humaines', roleType: 'Admin', email: 'thomas.martin@example.com', fullName: 'Thomas MARTIN' }
    ];
    
    members.forEach(member => {
      const memberDiv = document.createElement('div');
      memberDiv.style.padding = '10px';
      memberDiv.style.borderBottom = '1px solid #eee';
      memberDiv.style.display = 'flex';
      memberDiv.style.justifyContent = 'space-between';
      memberDiv.style.alignItems = 'center';
      
      const memberInfo = document.createElement('div');
      
      const memberName = document.createElement('div');
      memberName.style.fontWeight = 'bold';
      memberName.textContent = member.fullName;
      memberInfo.appendChild(memberName);
      
      const memberRole = document.createElement('div');
      memberRole.textContent = member.role;
      memberInfo.appendChild(memberRole);
      
      memberDiv.appendChild(memberInfo);
      
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.style.width = '20px';
      checkbox.style.height = '20px';
      memberDiv.appendChild(checkbox);
      
      container.appendChild(memberDiv);
    });
    
    // Ajouter le conteneur après le bouton d'assignation
    event.target.parentNode.insertBefore(container, event.target.nextSibling);
    
    console.log(`Conteneur créé avec ${members.length} membres après le bouton d'assignation`);
  }
  
  // Vérifier également les boutons de planification d'entretien
  if (event.target && (
    (event.target.className && event.target.className.includes('schedule-interview-btn')) ||
    (event.target.parentElement && event.target.parentElement.className && 
     event.target.parentElement.className.includes('schedule-interview-btn'))
  )) {
    console.log("Bouton de planification d'entretien détecté");
    
    // Attendre que la modale s'ouvre
    setTimeout(function() {
      const assignButton = document.querySelector('#assign-interview-participants');
      if (assignButton) {
        // Simuler un clic pour ouvrir la liste des membres
        assignButton.click();
      }
    }, 500);
  }
});

// Message de confirmation
console.log("Script d'intégration direct des membres d'équipe chargé avec succès");
