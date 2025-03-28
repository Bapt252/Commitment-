/**
 * Recruitment Process v2
 * Enhanced implementation with full drag-and-drop support and better UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Recruitment Process v2 initialized');
  
  // Elements
  const recruitmentTimeline = document.getElementById('recruitment-timeline');
  const addStepBtn = document.getElementById('add-step-btn');
  
  // Variables
  let draggedItem = null;
  let draggedItemIndex = null;
  
  // Initialize
  function init() {
    setupExistingItems();
    setupDragAndDrop();
    setupAddStepModal();
    setupContactSelection();
    setupStepSwitching();
    
    // Update step numbers on load
    updateStepNumbers();
  }
  
  // Setup event listeners for existing timeline items
  function setupExistingItems() {
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    timelineItems.forEach(item => {
      // Set up draggable attribute
      item.setAttribute('draggable', true);
      
      // Setup action buttons (enable/disable/delete)
      setupActionButtons(item);
      
      // Setup member association
      const memberItem = item.querySelector('.member-item');
      if (memberItem) {
        memberItem.addEventListener('click', function(e) {
          if (e.target.closest('.remove-member')) {
            // If clicking on a remove button, handle that separately
            return;
          }
          
          const timelineItem = this.closest('.timeline-item');
          openMemberSelectionModal(timelineItem);
        });
      }
    });
  }
  
  // Setup action buttons for a timeline item
  function setupActionButtons(item) {
    const successBtn = item.querySelector('.timeline-action.success');
    const dangerBtn = item.querySelector('.timeline-action.danger');
    
    if (successBtn) {
      successBtn.addEventListener('click', function() {
        item.classList.add('enabled');
        item.classList.remove('disabled');
        showToast(`Étape "${item.querySelector('.timeline-title').textContent}" activée`, 'success');
      });
    }
    
    if (dangerBtn) {
      dangerBtn.addEventListener('click', function() {
        // Ask for confirmation before removing the step
        if (confirm(`Voulez-vous supprimer l'étape "${item.querySelector('.timeline-title').textContent}" ?`)) {
          // Don't delete items in timeline-branch
          if (!item.closest('.timeline-branch')) {
            // Add removing class for animation
            item.classList.add('removing');
            
            // Remove after animation completes
            setTimeout(() => {
              item.remove();
              updateStepNumbers();
              showToast(`Étape supprimée`, 'warning');
            }, 300);
          } else {
            showToast(`Les étapes de branche ne peuvent pas être supprimées`, 'warning');
          }
        }
      });
    }
  }
  
  // Setup drag and drop functionality
  function setupDragAndDrop() {
    if (!recruitmentTimeline) return;
    
    // Event listeners for the timeline container
    recruitmentTimeline.addEventListener('dragover', handleDragOver);
    recruitmentTimeline.addEventListener('drop', handleDrop);
    
    // Event listeners for timeline items
    const timelineItems = document.querySelectorAll('.timeline-item');
    timelineItems.forEach(item => {
      if (!item.closest('.timeline-branch')) {  // Skip branch items
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
      }
    });
  }
  
  // Handle drag start
  function handleDragStart(e) {
    draggedItem = this;
    
    // Visual feedback
    this.classList.add('dragging');
    setTimeout(() => {
      this.style.opacity = '0.4';
    }, 0);
    
    // Store the index
    const items = [...recruitmentTimeline.querySelectorAll('.timeline-item:not(.timeline-branch .timeline-item)')];
    draggedItemIndex = items.indexOf(this);
    
    // Set transfer data
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
    
    // Add drop target indicators to other items
    document.querySelectorAll('.timeline-item:not(.dragging):not(.timeline-branch .timeline-item)').forEach(item => {
      item.classList.add('drop-target');
    });
  }
  
  // Handle drag over
  function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    // If we're over an item, highlight it
    const targetItem = e.target.closest('.timeline-item');
    if (targetItem && targetItem !== draggedItem && !targetItem.closest('.timeline-branch')) {
      // Remove highlighting from all items
      document.querySelectorAll('.timeline-item').forEach(item => {
        item.classList.remove('ready-to-drop');
      });
      
      // Add highlighting to this item
      targetItem.classList.add('ready-to-drop');
    }
    
    return false;
  }
  
  // Handle drop
  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Remove all drop indicators
    document.querySelectorAll('.timeline-item').forEach(item => {
      item.classList.remove('ready-to-drop', 'drop-target');
    });
    
    // Get the target item
    const dropTarget = e.target.closest('.timeline-item') || recruitmentTimeline;
    
    if (dropTarget !== draggedItem) {
      if (dropTarget === recruitmentTimeline) {
        // Dropping directly on the timeline - move to the end
        recruitmentTimeline.appendChild(draggedItem);
      } else if (!dropTarget.closest('.timeline-branch')) {
        // Dropping on another item
        const items = [...recruitmentTimeline.querySelectorAll('.timeline-item:not(.timeline-branch .timeline-item)')];
        const targetIndex = items.indexOf(dropTarget);
        
        if (draggedItemIndex < targetIndex) {
          // Insert after
          dropTarget.parentNode.insertBefore(draggedItem, dropTarget.nextSibling);
        } else {
          // Insert before
          dropTarget.parentNode.insertBefore(draggedItem, dropTarget);
        }
      }
      
      // Update step numbers
      updateStepNumbers();
      
      // Show success message
      showToast('Ordre des étapes modifié', 'success');
    }
    
    return false;
  }
  
  // Handle drag end
  function handleDragEnd() {
    // Remove visual effects
    this.classList.remove('dragging');
    this.style.opacity = '1';
    
    // Remove drop indicators
    document.querySelectorAll('.timeline-item').forEach(item => {
      item.classList.remove('ready-to-drop', 'drop-target');
    });
    
    // Clear references
    draggedItem = null;
    draggedItemIndex = null;
  }
  
  // Update step numbers
  function updateStepNumbers() {
    // Update main timeline items
    const timelineItems = document.querySelectorAll('#recruitment-timeline > .timeline-item');
    timelineItems.forEach((item, index) => {
      const stepCounter = item.querySelector('.step-counter');
      if (stepCounter) {
        stepCounter.textContent = (index + 1).toString();
      }
    });
    
    // Update branch item if it exists
    const branchItem = document.querySelector('#presentiel2-container .timeline-item');
    if (branchItem) {
      const stepCounter = branchItem.querySelector('.step-counter');
      if (stepCounter) {
        const mainItemsCount = timelineItems.length;
        const parentIndex = Math.max(1, mainItemsCount - 2);
        stepCounter.textContent = `${parentIndex}b`;
      }
    }
  }
  
  // Add new step
  function addNewStep() {
    const stepName = document.getElementById('step-name').value.trim();
    const stepDescription = document.getElementById('step-description').value.trim();
    const stepType = document.getElementById('step-type').value;
    const addMembers = document.getElementById('add-members-to-step').checked;
    
    if (!stepName) {
      showToast('Veuillez saisir un nom pour cette étape', 'danger');
      return;
    }
    
    // Create unique ID
    const stepId = 'step-' + Date.now();
    
    // Create new element
    const newStep = document.createElement('div');
    newStep.className = 'timeline-item new-item';
    newStep.dataset.step = stepId;
    
    // Get the next step number
    const nextStepNumber = document.querySelectorAll('#recruitment-timeline > .timeline-item').length + 1;
    
    // Create HTML
    newStep.innerHTML = `
      <div class="step-counter">${nextStepNumber}</div>
      <div class="timeline-header">
        <h6 class="timeline-title">${stepName}</h6>
        <div class="timeline-actions">
          <button type="button" class="timeline-action success" title="Approuver">
            <i class="fas fa-check"></i>
          </button>
          <button type="button" class="timeline-action danger" title="Supprimer">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      <div class="timeline-content">
        <p>${stepDescription || `Étape de type ${stepType}`}</p>
        ${addMembers ? `
          <div class="member-item">
            <div class="member-icon">
              <i class="fas fa-user-plus"></i>
            </div>
            <span class="member-name">Associer un membre</span>
          </div>
        ` : ''}
      </div>
    `;
    
    // Add to timeline
    recruitmentTimeline.appendChild(newStep);
    
    // Make draggable
    newStep.setAttribute('draggable', true);
    newStep.addEventListener('dragstart', handleDragStart);
    newStep.addEventListener('dragend', handleDragEnd);
    
    // Set up action buttons
    setupActionButtons(newStep);
    
    // Set up member association if needed
    if (addMembers) {
      const memberItem = newStep.querySelector('.member-item');
      memberItem.addEventListener('click', function() {
        openMemberSelectionModal(newStep);
      });
    }
    
    // Update step numbers
    updateStepNumbers();
    
    // Show success message
    showToast(`L'étape "${stepName}" a été ajoutée avec succès`, 'success');
  }
  
  // Set up the Add Step modal
  function setupAddStepModal() {
    if (!addStepBtn) return;
    
    addStepBtn.addEventListener('click', function() {
      const modal = new bootstrap.Modal(document.getElementById('addStepModal'));
      
      // Reset the form
      document.getElementById('step-name').value = '';
      document.getElementById('step-description').value = '';
      document.getElementById('step-type').value = 'interview';
      document.getElementById('add-members-to-step').checked = false;
      
      // Set up save button (remove old listeners first)
      const saveBtn = document.getElementById('save-step-btn');
      const newSaveBtn = saveBtn.cloneNode(true);
      saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
      
      newSaveBtn.addEventListener('click', function() {
        addNewStep();
        modal.hide();
      });
      
      modal.show();
    });
  }
  
  // Open member selection modal
  function openMemberSelectionModal(timelineItem) {
    const modal = new bootstrap.Modal(document.getElementById('contactSelectionModal'));
    
    // Store the target step
    document.getElementById('contactSelectionModal').dataset.targetStep = timelineItem.dataset.step;
    
    // Load the contacts
    loadContacts(timelineItem);
    
    modal.show();
  }
  
  // Load contacts into the selection modal
  function loadContacts(timelineItem) {
    const contactsContainer = document.getElementById('contacts-container');
    contactsContainer.innerHTML = '';
    
    // Demo contacts
    const demoContacts = [
      { id: 1, firstName: 'Marie', lastName: 'DURAND', position: 'Chargée recrutement', email: 'marie.durand@example.com' },
      { id: 2, firstName: 'Joseph', lastName: 'EUX', position: 'DAF', email: 'joseph.eux@example.com' },
      { id: 3, firstName: 'Sophia', lastName: 'MARTIN', position: 'Assistante RH', email: 'sophia.martin@example.com' },
      { id: 4, firstName: 'Thomas', lastName: 'DUPONT', position: 'Team Lead', email: 'thomas.dupont@example.com' },
      { id: 5, firstName: 'Julie', lastName: 'PETIT', position: 'Talent Acquisition', email: 'julie.petit@example.com' }
    ];
    
    demoContacts.forEach(contact => {
      const contactItem = document.createElement('div');
      contactItem.className = 'contact-item';
      contactItem.dataset.id = contact.id;
      
      // Create initials
      const initials = contact.firstName.charAt(0) + contact.lastName.charAt(0);
      
      contactItem.innerHTML = `
        <div class="contact-avatar">${initials}</div>
        <div class="contact-info">
          <div class="contact-name">${contact.firstName} ${contact.lastName}</div>
          <div class="contact-position">${contact.position}</div>
          <div class="contact-email">${contact.email}</div>
        </div>
      `;
      
      contactItem.addEventListener('click', function() {
        associateMemberWithStep(contact, timelineItem);
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('contactSelectionModal'));
        modal.hide();
      });
      
      contactsContainer.appendChild(contactItem);
    });
    
    // Set up search functionality
    const searchInput = document.getElementById('contact-search-input');
    if (searchInput) {
      searchInput.value = '';
      
      searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        contactsContainer.querySelectorAll('.contact-item').forEach(item => {
          const nameText = item.querySelector('.contact-name').textContent.toLowerCase();
          const positionText = item.querySelector('.contact-position').textContent.toLowerCase();
          const emailText = item.querySelector('.contact-email').textContent.toLowerCase();
          
          const isMatch = nameText.includes(searchTerm) || 
                          positionText.includes(searchTerm) || 
                          emailText.includes(searchTerm);
                          
          item.style.display = isMatch ? '' : 'none';
        });
      });
    }
  }
  
  // Associate a member with a step
  function associateMemberWithStep(contact, timelineItem) {
    const memberItem = timelineItem.querySelector('.member-item');
    if (!memberItem) return;
    
    const initials = contact.firstName.charAt(0) + contact.lastName.charAt(0);
    const fullName = `${contact.firstName} ${contact.lastName}`;
    
    // Update the member item to show the selected contact
    memberItem.innerHTML = `
      <div class="contact-avatar">${initials}</div>
      <div class="member-info">
        <div class="member-name">${fullName}</div>
        <div class="member-position">${contact.position}</div>
      </div>
      <button type="button" class="btn btn-sm btn-outline-danger remove-member ms-auto">
        <i class="fas fa-times"></i>
      </button>
    `;
    
    // Add functionality to the remove button
    const removeBtn = memberItem.querySelector('.remove-member');
    removeBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      resetMemberItem(memberItem);
      showToast('Membre retiré de cette étape', 'warning');
    });
    
    // Show success message
    showToast(`${fullName} a été associé à l'étape`, 'success');
  }
  
  // Reset a member item to default state
  function resetMemberItem(memberItem) {
    memberItem.innerHTML = `
      <div class="member-icon">
        <i class="fas fa-user-plus"></i>
      </div>
      <span class="member-name">Associer un membre</span>
    `;
    
    // Re-add click handler
    memberItem.addEventListener('click', function() {
      const timelineItem = this.closest('.timeline-item');
      openMemberSelectionModal(timelineItem);
    });
  }
  
  // Setup the contact selection
  function setupContactSelection() {
    const contactSearchInput = document.getElementById('contact-search-input');
    if (contactSearchInput) {
      contactSearchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const contactItems = document.querySelectorAll('#contacts-container .contact-item');
        
        contactItems.forEach(item => {
          const nameText = item.querySelector('.contact-name').textContent.toLowerCase();
          const positionText = item.querySelector('.contact-position').textContent.toLowerCase();
          const emailText = item.querySelector('.contact-email').textContent.toLowerCase();
          
          const isMatch = nameText.includes(searchTerm) || 
                          positionText.includes(searchTerm) || 
                          emailText.includes(searchTerm);
                          
          item.style.display = isMatch ? '' : 'none';
        });
      });
    }
  }
  
  // Set up step switching functionality (navigation between steps 1-5)
  function setupStepSwitching() {
    const progressSteps = document.querySelectorAll('.progress-step');
    const nextButtons = document.querySelectorAll('.next-step');
    const prevButtons = document.querySelectorAll('.prev-step');
    
    progressSteps.forEach(step => {
      step.addEventListener('click', function() {
        const stepNumber = parseInt(this.dataset.step);
        showStep(stepNumber);
      });
    });
    
    nextButtons.forEach(button => {
      button.addEventListener('click', function() {
        const nextStep = parseInt(this.dataset.step);
        showStep(nextStep);
      });
    });
    
    prevButtons.forEach(button => {
      button.addEventListener('click', function() {
        const prevStep = parseInt(this.dataset.step);
        showStep(prevStep);
      });
    });
    
    // Form submission
    const form = document.getElementById('create-job-form');
    if (form) {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate confirmation checkbox
        const confirmCheckbox = document.getElementById('confirm-validation');
        if (!confirmCheckbox.checked) {
          showToast('Veuillez confirmer les informations avant de continuer', 'warning');
          return;
        }
        
        // Success message
        showToast('Le poste a été créé avec succès', 'success');
        
        // In a real app, we would submit the form data to the server here
        console.log('Form submitted successfully');
        
        // Redirection vers planning.html après un court délai
        setTimeout(() => {
          window.location.href = 'planning.html';
        }, 1500); // Délai de 1.5 secondes pour permettre à l'utilisateur de voir le message de succès
      });
    }
  }
  
  // Show a specific step
  function showStep(stepNumber) {
    // Get elements
    const progressSteps = document.querySelectorAll('.progress-step');
    const stepContents = document.querySelectorAll('.step-content');
    
    // Hide all steps
    stepContents.forEach(content => {
      content.classList.remove('active');
    });
    
    // Show the selected step
    document.getElementById(`step-${stepNumber}`).classList.add('active');
    
    // Update progress indicators
    progressSteps.forEach(step => {
      const stepNum = parseInt(step.dataset.step);
      step.classList.remove('active', 'completed');
      
      if (stepNum === stepNumber) {
        step.classList.add('active');
      } else if (stepNum < stepNumber) {
        step.classList.add('completed');
      }
    });
    
    // If showing the final step, generate summary
    if (stepNumber === 5) {
      generateSummary();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  // Generate summary for final step
  function generateSummary() {
    // Main information
    const jobTitle = document.getElementById('job-title').value || 'Non spécifié';
    const jobDescription = document.getElementById('job-description').value || 'Non spécifié';
    
    let recruitmentContext = 'Non spécifié';
    const selectedContextCard = document.querySelector('.option-card.selected');
    if (selectedContextCard) {
      recruitmentContext = selectedContextCard.querySelector('.option-title').textContent;
    }
    
    const experienceSelect = document.getElementById('experience-required');
    const experience = experienceSelect ? experienceSelect.options[experienceSelect.selectedIndex].text : 'Non spécifié';
    
    document.getElementById('job-summary-main').innerHTML = `
      <div class="summary-item mb-2">
        <strong>Titre :</strong> ${jobTitle}
      </div>
      <div class="summary-item mb-2">
        <strong>Descriptif :</strong> ${jobDescription.length > 100 ? jobDescription.substring(0, 100) + '...' : jobDescription}
      </div>
      <div class="summary-item mb-2">
        <strong>Contexte :</strong> ${recruitmentContext}
      </div>
      <div class="summary-item mb-2">
        <strong>Expérience requise :</strong> ${experience}
      </div>
    `;
    
    // Environment
    const workEnv = document.querySelector('input[name="work-environment"]:checked');
    const workEnvValue = workEnv ? (workEnv.value === 'open-space' ? 'Open Space' : 'Bureau fermé') : 'Non spécifié';
    
    const teamComp = document.getElementById('team-composition').value || 'Non spécifié';
    const remotePossible = document.getElementById('remote-partial').checked || document.getElementById('remote-full').checked;
    
    document.getElementById('job-summary-environment').innerHTML = `
      <div class="summary-item mb-2">
        <strong>Espace de travail :</strong> ${workEnvValue}
      </div>
      <div class="summary-item mb-2">
        <strong>Télétravail possible :</strong> ${remotePossible ? 'Oui' : 'Non'}
      </div>
      <div class="summary-item mb-2">
        <strong>Composition de l'équipe :</strong> ${teamComp.length > 100 ? teamComp.substring(0, 100) + '...' : teamComp}
      </div>
    `;
    
    // Team members
    const orgMembersList = document.getElementById('org-members-list');
    if (orgMembersList && orgMembersList.style.display !== 'none') {
      let membersHtml = '<ul class="list-unstyled">';
      orgMembersList.querySelectorAll('tbody tr').forEach(row => {
        const name = row.querySelector('td:first-child').textContent;
        const role = row.querySelector('td:nth-child(3)').textContent;
        membersHtml += `<li class="mb-1"><i class="fas fa-user text-primary me-2"></i> ${name} <small>(${role})</small></li>`;
      });
      membersHtml += '</ul>';
      document.getElementById('job-summary-members').innerHTML = membersHtml;
    } else {
      document.getElementById('job-summary-members').innerHTML = '<p>Aucun membre ajouté</p>';
    }
    
    // Process
    const timelineItems = document.querySelectorAll('.timeline-item');
    if (timelineItems.length > 0) {
      let processHtml = '<ol class="ps-3">';
      timelineItems.forEach(item => {
        const title = item.querySelector('.timeline-title').textContent;
        const isEnabled = item.classList.contains('enabled');
        const isDisabled = item.classList.contains('disabled');
        const statusBadge = isEnabled ? 
          '<span class="badge bg-success ms-2">Activé</span>' : 
          (isDisabled ? '<span class="badge bg-danger ms-2">Désactivé</span>' : '');
        
        processHtml += `<li class="mb-1">${title} ${statusBadge}</li>`;
      });
      processHtml += '</ol>';
      document.getElementById('job-summary-process').innerHTML = processHtml;
    } else {
      document.getElementById('job-summary-process').innerHTML = '<p>Aucune étape définie</p>';
    }
  }
  
  // Show toast notification
  function showToast(message, type = 'success') {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '9999';
    
    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const headerClass = type === 'success' ? 'bg-success' : 
                        type === 'warning' ? 'bg-warning' : 
                        type === 'danger' ? 'bg-danger' : 'bg-primary';
    
    const iconClass = type === 'success' ? 'check-circle' : 
                        type === 'warning' ? 'exclamation-triangle' : 
                        type === 'danger' ? 'times-circle' : 'info-circle';
    
    const headerTextClass = type === 'warning' ? 'text-dark' : 'text-white';
    
    const title = type === 'success' ? 'Succès' : 
                 type === 'warning' ? 'Attention' : 
                 type === 'danger' ? 'Erreur' : 'Information';
    
    toast.innerHTML = `
      <div class="toast-header ${headerClass} ${headerTextClass}">
        <strong class="me-auto">${title}</strong>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        <div class="d-flex align-items-center">
          <i class="fas fa-${iconClass} text-${type} me-2"></i>
          <span>${message}</span>
        </div>
      </div>
    `;
    
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
      toast.style.transition = 'opacity 0.5s ease';
      toast.style.opacity = '0';
      
      setTimeout(() => {
        toastContainer.remove();
      }, 500);
    }, 3000);
  }
  
  // Initialize the module
  init();
});