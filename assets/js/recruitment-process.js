/**
 * Recruitment Process Module
 * Provides drag-and-drop and other functionality for the recruitment process section
 */

document.addEventListener('DOMContentLoaded', function() {
  // Get the timeline container and recruitment items
  const timeline = document.getElementById('recruitment-timeline');
  const timelineItems = document.querySelectorAll('.timeline-item');
  let draggedItem = null;
  let dragSourceIndex = null;

  // Initialize the drag-and-drop functionality for existing items
  timelineItems.forEach(item => {
    if (!item.closest('.timeline-branch')) {
      initializeDragAndDrop(item);
    }
  });

  // Success/Delete timeline items functionality
  document.querySelectorAll('.timeline-action').forEach(button => {
    button.addEventListener('click', function() {
      const timelineItem = this.closest('.timeline-item');
      
      if (this.classList.contains('success')) {
        // Enable this step
        timelineItem.classList.add('enabled');
        timelineItem.classList.remove('disabled');
        
        // Show a success notification
        showNotification(`Étape "${timelineItem.querySelector('.timeline-title').textContent}" activée`);
      } else if (this.classList.contains('danger')) {
        // Remove this step (instead of disabling it)
        removeStep(timelineItem);
      }
    });
  });

  // Add member to step functionality
  document.querySelectorAll('.member-item').forEach(memberItem => {
    memberItem.addEventListener('click', function() {
      const timelineItem = this.closest('.timeline-item');
      openMemberSelectionModal(timelineItem);
    });
  });

  // Add new step button
  const addStepBtn = document.getElementById('add-step-btn');
  if (addStepBtn) {
    addStepBtn.addEventListener('click', function() {
      openAddStepModal();
    });
  }

  /**
   * Remove a step from the recruitment process
   * @param {HTMLElement} timelineItem - The timeline item to remove
   */
  function removeStep(timelineItem) {
    // Confirm deletion
    const stepTitle = timelineItem.querySelector('.timeline-title').textContent;
    
    // Add the removing class for animation
    timelineItem.classList.add('removing');
    
    // After animation completes, remove the element
    setTimeout(() => {
      timelineItem.remove();
      
      // Update step numbers
      updateStepNumbers();
      
      // Show notification
      showNotification(`Étape "${stepTitle}" supprimée`, 'danger');
    }, 500); // Match this with the CSS animation duration
  }

  /**
   * Initialize drag and drop functionality for a timeline item
   * @param {HTMLElement} item - The timeline item element
   */
  function initializeDragAndDrop(item) {
    // Make sure the item is draggable
    item.setAttribute('draggable', 'true');
    
    // Add event listeners
    item.addEventListener('dragstart', handleDragStart);
    item.addEventListener('dragend', handleDragEnd);
    
    // These events need to be on all potential drop targets
    timeline.addEventListener('dragover', handleDragOver);
    timeline.addEventListener('dragenter', handleDragEnter);
    timeline.addEventListener('dragleave', handleDragLeave);
    timeline.addEventListener('drop', handleDrop);
  }

  /**
   * Handle drag start event
   * @param {DragEvent} e - The drag event
   */
  function handleDragStart(e) {
    // Add a dragging class and set opacity
    this.classList.add('dragging');
    
    // Store the dragged item
    draggedItem = this;
    
    // Store the source index for proper placement later
    const items = [...timeline.querySelectorAll('.timeline-item:not(.timeline-branch .timeline-item)')];
    dragSourceIndex = items.indexOf(this);
    
    // Set the drag data
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
  }

  /**
   * Handle drag over event
   * @param {DragEvent} e - The drag event
   */
  function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    return false;
  }

  /**
   * Handle drag enter event
   * @param {DragEvent} e - The drag event
   */
  function handleDragEnter(e) {
    // Only if we're entering another timeline item, not the container itself
    if (e.target.classList.contains('timeline-item')) {
      e.target.classList.add('drag-over');
    }
  }

  /**
   * Handle drag leave event
   * @param {DragEvent} e - The drag event
   */
  function handleDragLeave(e) {
    if (e.target.classList.contains('timeline-item')) {
      e.target.classList.remove('drag-over');
    }
  }

  /**
   * Handle drop event
   * @param {DragEvent} e - The drag event
   */
  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Remove drag-over class from all items
    document.querySelectorAll('.timeline-item').forEach(item => {
      item.classList.remove('drag-over');
    });
    
    // Only process if we're dropping onto the timeline or another item
    if (e.target === timeline || e.target.classList.contains('timeline-item') || e.target.closest('.timeline-item')) {
      const dropTarget = e.target.classList.contains('timeline-item') ? 
                        e.target : 
                        e.target.closest('.timeline-item') || timeline;
      
      if (draggedItem !== dropTarget) {
        const items = [...timeline.querySelectorAll('.timeline-item:not(.timeline-branch .timeline-item)')];
        const dropTargetIndex = items.indexOf(dropTarget);
        
        if (dropTarget === timeline) {
          // We're dropping directly onto the timeline container
          timeline.appendChild(draggedItem);
        } else if (dragSourceIndex < dropTargetIndex) {
          // We're dropping after the source
          dropTarget.parentNode.insertBefore(draggedItem, dropTarget.nextSibling);
        } else {
          // We're dropping before the source
          dropTarget.parentNode.insertBefore(draggedItem, dropTarget);
        }
        
        // Update step numbers after drag and drop
        updateStepNumbers();
        
        // Show notification
        showNotification(`Ordre des étapes modifié`);
      }
    }
    
    return false;
  }

  /**
   * Handle drag end event
   * @param {DragEvent} e - The drag event
   */
  function handleDragEnd(e) {
    this.classList.remove('dragging');
    
    // Remove any drag-over classes
    document.querySelectorAll('.timeline-item').forEach(item => {
      item.classList.remove('drag-over');
    });
    
    draggedItem = null;
    dragSourceIndex = null;
  }

  /**
   * Update the step numbers after adding, removing, or reordering steps
   */
  function updateStepNumbers() {
    const timelineItems = document.querySelectorAll('#recruitment-timeline > .timeline-item');
    timelineItems.forEach((item, index) => {
      const stepCounter = item.querySelector('.step-counter');
      if (stepCounter) {
        stepCounter.textContent = (index + 1);
      }
    });
    
    // Update branch numbering if exists
    const branchItem = document.querySelector('#presentiel2-container .timeline-item');
    if (branchItem) {
      const mainItems = document.querySelectorAll('#recruitment-timeline > .timeline-item');
      const mainItemsCount = mainItems.length;
      const stepCounter = branchItem.querySelector('.step-counter');
      if (stepCounter) {
        // Find the index of the parent item (usually the item before the decision)
        const parentIndex = mainItemsCount - 2;
        // Make sure we don't get a negative index
        if (parentIndex >= 0) {
          stepCounter.textContent = `${parentIndex + 1}b`;
        } else {
          stepCounter.textContent = "1b";
        }
      }
    }
  }

  /**
   * Open the member selection modal for a timeline item
   * @param {HTMLElement} timelineItem - The timeline item element
   */
  function openMemberSelectionModal(timelineItem) {
    const modal = new bootstrap.Modal(document.getElementById('contactSelectionModal'));
    
    // We'll store which timeline item we're associating the member with
    document.getElementById('contactSelectionModal').dataset.targetStep = timelineItem.dataset.step;
    
    // Populate the contacts list
    loadContacts(timelineItem);
    
    // Show the modal
    modal.show();
  }

  /**
   * Load contacts into the contact selection modal
   * @param {HTMLElement} timelineItem - The timeline item we're adding a member to
   */
  function loadContacts(timelineItem) {
    const contactsContainer = document.getElementById('contacts-container');
    contactsContainer.innerHTML = '';
    
    // Demo contacts data - in a real app, this would come from an API
    const demoContacts = [
      { id: 1, firstName: 'Marie', lastName: 'DURAND', position: 'Chargée recrutement', email: 'marie.durand@example.com' },
      { id: 2, firstName: 'Joseph', lastName: 'EUX', position: 'DAF', email: 'joseph.eux@example.com' },
      { id: 3, firstName: 'Sophia', lastName: 'MARTIN', position: 'Assistante RH', email: 'sophia.martin@example.com' },
      { id: 4, firstName: 'Thomas', lastName: 'BERNARD', position: 'Responsable Technique', email: 'thomas.bernard@example.com' },
      { id: 5, firstName: 'Julie', lastName: 'PETIT', position: 'Responsable RH', email: 'julie.petit@example.com' }
    ];
    
    demoContacts.forEach(contact => {
      const contactElement = document.createElement('div');
      contactElement.className = 'contact-item';
      contactElement.dataset.id = contact.id;
      
      // Create initials for the avatar
      const initials = contact.firstName.charAt(0) + contact.lastName.charAt(0);
      
      contactElement.innerHTML = `
        <div class="contact-avatar">${initials}</div>
        <div class="contact-info">
          <div class="contact-name">${contact.firstName} ${contact.lastName}</div>
          <div class="contact-position">${contact.position}</div>
          <div class="contact-email">${contact.email}</div>
        </div>
      `;
      
      // Add event listener to associate this contact with the timeline item
      contactElement.addEventListener('click', function() {
        associateMemberWithStep(contact, timelineItem);
        
        // Hide the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('contactSelectionModal'));
        modal.hide();
      });
      
      contactsContainer.appendChild(contactElement);
    });
  }

  /**
   * Associate a member with a timeline step
   * @param {Object} contact - The contact object
   * @param {HTMLElement} timelineItem - The timeline item element
   */
  function associateMemberWithStep(contact, timelineItem) {
    // Find the member-item div in the timeline item
    const memberItem = timelineItem.querySelector('.member-item');
    
    // Create the associated member display
    const memberName = `${contact.firstName} ${contact.lastName}`;
    const initials = contact.firstName.charAt(0) + contact.lastName.charAt(0);
    
    // Replace the "Associate a member" with the actual member
    memberItem.innerHTML = `
      <div class="contact-avatar">${initials}</div>
      <div class="member-info">
        <div class="member-name">${memberName}</div>
        <div class="member-position">${contact.position}</div>
      </div>
      <button type="button" class="btn btn-sm btn-outline-danger remove-member ms-auto">
        <i class="fas fa-times"></i>
      </button>
    `;
    
    // Add event listener to remove button
    const removeButton = memberItem.querySelector('.remove-member');
    removeButton.addEventListener('click', function(e) {
      e.stopPropagation(); // Prevent opening the modal when clicking remove
      resetMemberItem(memberItem);
    });
    
    // Remove the click event for adding a member
    memberItem.removeEventListener('click', openMemberSelectionModal);
    
    // Show a success notification
    showNotification(`${memberName} a été associé à l'étape "${timelineItem.querySelector('.timeline-title').textContent}"`);
  }

  /**
   * Reset a member item to its original state
   * @param {HTMLElement} memberItem - The member item element
   */
  function resetMemberItem(memberItem) {
    memberItem.innerHTML = `
      <div class="member-icon">
        <i class="fas fa-user-plus"></i>
      </div>
      <span class="member-name">Associer un membre</span>
    `;
    
    // Re-add the click event for adding a member
    memberItem.addEventListener('click', function() {
      const timelineItem = this.closest('.timeline-item');
      openMemberSelectionModal(timelineItem);
    });
    
    // Show notification
    showNotification("Membre dissocié de l'étape", "warning");
  }

  /**
   * Open the add step modal
   */
  function openAddStepModal() {
    const modal = new bootstrap.Modal(document.getElementById('addStepModal'));
    
    // Reset the form
    document.getElementById('step-name').value = '';
    document.getElementById('step-description').value = '';
    document.getElementById('step-type').value = 'interview';
    document.getElementById('add-members-to-step').checked = false;
    
    // Add event listener to the save button
    const saveButton = document.getElementById('save-step-btn');
    
    // Remove existing event listeners to prevent duplicates
    const newSaveButton = saveButton.cloneNode(true);
    saveButton.parentNode.replaceChild(newSaveButton, saveButton);
    
    newSaveButton.addEventListener('click', function() {
      addNewStep();
      modal.hide();
    });
    
    modal.show();
  }

  /**
   * Add a new step to the recruitment process
   */
  function addNewStep() {
    const stepName = document.getElementById('step-name').value.trim();
    const stepDescription = document.getElementById('step-description').value.trim();
    const stepType = document.getElementById('step-type').value;
    const addMembers = document.getElementById('add-members-to-step').checked;
    
    if (!stepName) {
      showNotification('Veuillez entrer un nom d\'étape', 'danger');
      return;
    }
    
    // Create a unique ID for the step
    const stepId = 'step-' + Date.now();
    
    // Create the new timeline item
    const newStep = document.createElement('div');
    newStep.className = 'timeline-item new-item';
    newStep.dataset.step = stepId;
    
    // Get the next step number
    const nextStepNumber = document.querySelectorAll('#recruitment-timeline > .timeline-item').length + 1;
    
    // Create the content for the new step
    let stepContent = `
      <div class="step-counter">${nextStepNumber}</div>
      <div class="timeline-header">
        <h6 class="timeline-title">${stepName}</h6>
        <div class="timeline-actions">
          <button type="button" class="timeline-action success" title="Activer cette étape">
            <i class="fas fa-check"></i>
          </button>
          <button type="button" class="timeline-action danger" title="Supprimer cette étape">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      <div class="timeline-content">
        <p>${stepDescription || `Étape de type ${stepType}`}</p>
    `;
    
    if (addMembers) {
      stepContent += `
        <div class="member-item">
          <div class="member-icon">
            <i class="fas fa-user-plus"></i>
          </div>
          <span class="member-name">Associer un membre</span>
        </div>
      `;
    }
    
    stepContent += `</div>`;
    
    newStep.innerHTML = stepContent;
    
    // Add the new step to the timeline
    timeline.appendChild(newStep);
    
    // Initialize drag-and-drop for the new step
    initializeDragAndDrop(newStep);
    
    // Add event listeners for the action buttons
    const successButton = newStep.querySelector('.timeline-action.success');
    const dangerButton = newStep.querySelector('.timeline-action.danger');
    
    successButton.addEventListener('click', function() {
      newStep.classList.add('enabled');
      newStep.classList.remove('disabled');
      showNotification(`Étape "${stepName}" activée`);
    });
    
    dangerButton.addEventListener('click', function() {
      removeStep(newStep);
    });
    
    // Add event listener to the member item if present
    const memberItem = newStep.querySelector('.member-item');
    if (memberItem) {
      memberItem.addEventListener('click', function() {
        openMemberSelectionModal(newStep);
      });
    }
    
    // Update step numbers
    updateStepNumbers();
    
    // Show a success notification
    showNotification(`L'étape "${stepName}" a été ajoutée avec succès`);
    
    // Tooltip initialization for the new elements
    const tooltips = [].slice.call(newStep.querySelectorAll('[title]'));
    tooltips.forEach(el => {
      new bootstrap.Tooltip(el);
    });
  }

  /**
   * Show a notification
   * @param {string} message - The message to display
   * @param {string} type - The type of notification (success, danger, warning)
   */
  function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = 'position-fixed bottom-0 end-0 p-3';
    notification.style.zIndex = '9999';
    
    const icon = type === 'success' ? 'check-circle' : 
                (type === 'danger' ? 'times-circle' : 'exclamation-circle');
    
    const title = type === 'success' ? 'Succès' : 
                (type === 'danger' ? 'Action effectuée' : 'Attention');
    
    notification.innerHTML = `
      <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header bg-${type} text-white">
          <strong class="me-auto">${title}</strong>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
          <div class="d-flex align-items-center">
            <i class="fas fa-${icon} text-${type} me-2"></i>
            <span>${message}</span>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
      // Add fade out animation
      const toast = notification.querySelector('.toast');
      toast.style.transition = 'opacity 0.5s ease';
      toast.style.opacity = '0';
      
      setTimeout(() => {
        notification.remove();
      }, 500);
    }, 3000);
  }
  
  // Initialize tooltips for action buttons
  const actionButtons = document.querySelectorAll('.timeline-action');
  actionButtons.forEach(button => {
    if (button.classList.contains('success')) {
      button.setAttribute('title', 'Activer cette étape');
    } else if (button.classList.contains('danger')) {
      button.setAttribute('title', 'Supprimer cette étape');
    }
    
    new bootstrap.Tooltip(button);
  });
});
