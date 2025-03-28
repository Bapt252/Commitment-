/**
 * Recruitment Process Module - Improved Version
 * Enhanced drag-and-drop, UI feedback and better handling of dynamic elements
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Recruitment Process Improved Module Loaded');

  // Variables and elements
  const timeline = document.getElementById('recruitment-timeline');
  const timelineContainer = document.querySelector('.timeline-container');
  let draggedItem = null;
  let dragSourceIndex = null;
  let currentlyDragging = false;

  /**
   * Initialize the module
   */
  function init() {
    initializeTimelineItems();
    setupAddStepButton();
    setupDeleteConfirmation();
    
    // Add some UI improvements
    addStepNumbers();
    addDraggableIndication();
    
    // Set up the observer to watch for changes in the timeline
    setupMutationObserver();
  }

  /**
   * Add visual indication that items can be dragged
   */
  function addDraggableIndication() {
    const style = document.createElement('style');
    style.textContent = `
      .timeline-item:hover:before {
        content: "☰";
        position: absolute;
        top: 10px;
        left: 10px;
        color: #ccc;
        font-size: 16px;
        opacity: 0.7;
        cursor: move;
      }
      .timeline-item.ready-to-drop {
        border: 2px dashed var(--primary-color);
        background-color: rgba(115, 102, 255, 0.05);
      }
      .delete-confirmation {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(255, 71, 87, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10;
        border-radius: 8px;
        backdrop-filter: blur(2px);
      }
      .delete-confirmation-buttons {
        display: flex;
        gap: 10px;
        margin-top: 10px;
      }
      .timeline-item.deletion-pending {
        box-shadow: 0 0 0 2px #ff4757, 0 0 10px rgba(255, 71, 87, 0.3);
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Add step numbers visually to the timeline
   */
  function addStepNumbers() {
    // Numbers are already added via HTML, this function re-numbers them if needed
    updateStepNumbers();
  }

  /**
   * Update the step numbers of all timeline items
   */
  function updateStepNumbers() {
    const timelineItems = document.querySelectorAll('#recruitment-timeline > .timeline-item');
    timelineItems.forEach((item, index) => {
      const stepCounter = item.querySelector('.step-counter');
      if (stepCounter) {
        stepCounter.textContent = (index + 1).toString();
      }
    });
    
    // Update branch numbering if exists
    const branchItem = document.querySelector('#presentiel2-container .timeline-item');
    if (branchItem) {
      const mainItems = document.querySelectorAll('#recruitment-timeline > .timeline-item');
      const mainItemsCount = mainItems.length;
      const stepCounter = branchItem.querySelector('.step-counter');
      if (stepCounter) {
        const parentIndex = mainItemsCount - 2 > 0 ? mainItemsCount - 2 : 1;
        stepCounter.textContent = `${parentIndex}b`;
      }
    }
  }

  /**
   * Initialize all timeline items with drag and drop functionality and event listeners
   */
  function initializeTimelineItems() {
    const timelineItems = document.querySelectorAll('.timeline-item');
    timelineItems.forEach(item => {
      setupTimelineItem(item);
    });

    // Add event listeners for associating members
    document.querySelectorAll('.member-item').forEach(memberItem => {
      memberItem.addEventListener('click', function(e) {
        if (this.querySelector('.remove-member')) {
          // Don't trigger when clicking on the remove button
          if (e.target.closest('.remove-member')) return;
        }
        const timelineItem = this.closest('.timeline-item');
        openMemberSelectionModal(timelineItem);
      });
    });
  }

  /**
   * Setup a single timeline item with all necessary event listeners
   * @param {HTMLElement} item - The timeline item to set up
   */
  function setupTimelineItem(item) {
    if (item.classList.contains('setup-complete')) return;
    
    // Make sure the item is draggable
    item.setAttribute('draggable', 'true');
    
    // Add a class to identify this as set up
    item.classList.add('setup-complete');
    
    // Drag events
    item.addEventListener('dragstart', handleDragStart);
    item.addEventListener('dragend', handleDragEnd);
    
    // Action buttons (enable/disable/delete)
    setupActionButtons(item);

    // Member item inside timeline
    setupMemberItem(item);
  }

  /**
   * Set up action buttons for a timeline item
   * @param {HTMLElement} item - Timeline item containing action buttons
   */
  function setupActionButtons(item) {
    const successButton = item.querySelector('.timeline-action.success');
    const dangerButton = item.querySelector('.timeline-action.danger');
    const actionsContainer = item.querySelector('.timeline-actions');
    
    // Add delete button if it doesn't exist yet
    if (!actionsContainer.querySelector('.timeline-action.delete')) {
      const deleteButton = document.createElement('button');
      deleteButton.className = 'timeline-action delete';
      deleteButton.title = 'Supprimer';
      deleteButton.innerHTML = '<i class="fas fa-trash"></i>';
      deleteButton.style.backgroundColor = '#ff4757';
      actionsContainer.appendChild(deleteButton);
      
      deleteButton.addEventListener('click', function() {
        showDeleteConfirmation(item);
      });
    }
    
    if (successButton) {
      successButton.addEventListener('click', function() {
        item.classList.add('enabled');
        item.classList.remove('disabled');
        item.setAttribute('data-status', 'enabled');
        
        // Visual feedback
        pulseElement(this, 'success');
        showToast('Étape activée', 'success');
      });
    }
    
    if (dangerButton) {
      dangerButton.addEventListener('click', function() {
        item.classList.add('disabled');
        item.classList.remove('enabled');
        item.setAttribute('data-status', 'disabled');
        
        // Visual feedback
        pulseElement(this, 'danger');
        showToast('Étape désactivée', 'warning');
      });
    }
  }

  /**
   * Add a quick visual pulse to an element to indicate an action
   * @param {HTMLElement} element - Element to apply pulse effect to
   * @param {string} type - Type of pulse (success/danger/etc)
   */
  function pulseElement(element, type) {
    const originalBackground = element.style.backgroundColor;
    const originalTransform = element.style.transform;
    
    element.style.transform = 'scale(1.2)';
    
    setTimeout(() => {
      element.style.transform = originalTransform;
    }, 200);
  }

  /**
   * Create and show a toast notification
   * @param {string} message - Message to display
   * @param {string} type - Type of notification (success, warning, danger)
   */
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
      <div class="toast-icon">
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'exclamation-circle'}"></i>
      </div>
      <div class="toast-message">${message}</div>
    `;
    
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.backgroundColor = type === 'success' ? '#37b679' : type === 'warning' ? '#f8961e' : '#ff4757';
    toast.style.color = 'white';
    toast.style.padding = '10px 15px';
    toast.style.borderRadius = '5px';
    toast.style.boxShadow = '0 3px 10px rgba(0,0,0,0.2)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '10px';
    toast.style.zIndex = '9999';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    toast.style.transition = 'all 0.3s ease';
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(20px)';
      
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 3000);
  }

  /**
   * Setup member item in a timeline item
   * @param {HTMLElement} item - Timeline item containing a member item
   */
  function setupMemberItem(item) {
    const memberItem = item.querySelector('.member-item');
    
    if (memberItem) {
      // Make sure we're not attaching multiple event listeners
      memberItem.removeEventListener('click', memberItemClickHandler);
      memberItem.addEventListener('click', memberItemClickHandler);
    }
  }

  /**
   * Handler for clicks on member items
   * @param {Event} e - Click event
   */
  function memberItemClickHandler(e) {
    // If clicking the remove button, don't open the modal
    if (e.target.closest('.remove-member')) {
      e.stopPropagation();
      
      // Get the member item and reset it
      const memberItem = e.target.closest('.member-item');
      resetMemberItem(memberItem);
      
      // Show a notification
      showToast('Membre retiré de cette étape', 'warning');
      return;
    }
    
    // If this member item already has an assigned member, don't do anything
    if (this.querySelector('.member-info')) return;
    
    // Otherwise, open the modal to select a member
    const timelineItem = this.closest('.timeline-item');
    openMemberSelectionModal(timelineItem);
  }

  /**
   * Reset a member item to its default state
   * @param {HTMLElement} memberItem - The member item to reset
   */
  function resetMemberItem(memberItem) {
    memberItem.innerHTML = `
      <div class="member-icon">
        <i class="fas fa-user-plus"></i>
      </div>
      <span class="member-name">Associer un membre</span>
    `;
    
    // Add click event back
    memberItem.addEventListener('click', memberItemClickHandler);
  }

  /**
   * Open the member selection modal for a timeline item
   * @param {HTMLElement} timelineItem - The timeline item to associate a member with
   */
  function openMemberSelectionModal(timelineItem) {
    const modal = new bootstrap.Modal(document.getElementById('contactSelectionModal'));
    
    // Store reference to the timeline item
    document.getElementById('contactSelectionModal').dataset.targetStep = timelineItem.dataset.step;
    
    // Load contacts
    loadContacts(timelineItem);
    
    // Show modal
    modal.show();
  }

  /**
   * Load contacts into the modal
   * @param {HTMLElement} timelineItem - The timeline item that will get the contact
   */
  function loadContacts(timelineItem) {
    const contactsContainer = document.getElementById('contacts-container');
    contactsContainer.innerHTML = '';
    
    // Demo data - in a real app, this would come from an API
    const demoContacts = [
      { id: 1, firstName: 'Marie', lastName: 'DURAND', position: 'Chargée recrutement', email: 'marie.durand@example.com' },
      { id: 2, firstName: 'Joseph', lastName: 'EUX', position: 'DAF', email: 'joseph.eux@example.com' },
      { id: 3, firstName: 'Sophia', lastName: 'MARTIN', position: 'Assistante RH', email: 'sophia.martin@example.com' },
      { id: 4, firstName: 'Marc', lastName: 'BERNARD', position: 'CTO', email: 'marc.bernard@example.com' },
      { id: 5, firstName: 'Julie', lastName: 'PETIT', position: 'Team Lead Design', email: 'julie.petit@example.com' }
    ];
    
    if (demoContacts.length === 0) {
      contactsContainer.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-users"></i>
          <p>Aucun contact trouvé</p>
        </div>
      `;
      return;
    }
    
    // Create contact items
    demoContacts.forEach(contact => {
      const contactItem = document.createElement('div');
      contactItem.className = 'contact-item';
      
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
    
    // Add search functionality
    const searchInput = document.getElementById('contact-search-input');
    if (searchInput) {
      searchInput.value = ''; // Reset search
      
      searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        contactsContainer.querySelectorAll('.contact-item').forEach(item => {
          const contactName = item.querySelector('.contact-name').textContent.toLowerCase();
          const contactPosition = item.querySelector('.contact-position').textContent.toLowerCase();
          const contactEmail = item.querySelector('.contact-email').textContent.toLowerCase();
          
          const isMatch = contactName.includes(searchTerm) || 
                          contactPosition.includes(searchTerm) || 
                          contactEmail.includes(searchTerm);
          
          item.style.display = isMatch ? '' : 'none';
        });
      });
    }
  }

  /**
   * Associate a member with a timeline step
   * @param {Object} contact - The contact information
   * @param {HTMLElement} timelineItem - The timeline item to add the member to
   */
  function associateMemberWithStep(contact, timelineItem) {
    const memberItem = timelineItem.querySelector('.member-item');
    if (!memberItem) return;
    
    const initials = contact.firstName.charAt(0) + contact.lastName.charAt(0);
    const fullName = `${contact.firstName} ${contact.lastName}`;
    
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
    
    // Add event listener to the remove button
    const removeButton = memberItem.querySelector('.remove-member');
    removeButton.addEventListener('click', function(e) {
      e.stopPropagation();
      resetMemberItem(memberItem);
      showToast('Membre retiré de cette étape', 'warning');
    });
    
    // Success notification
    showToast(`${fullName} a été associé à l'étape`, 'success');
  }

  /**
   * Setup the Add Step button
   */
  function setupAddStepButton() {
    const addStepBtn = document.getElementById('add-step-btn');
    if (!addStepBtn) return;
    
    addStepBtn.addEventListener('click', function() {
      openAddStepModal();
    });
    
    // Setup the save button in the modal
    const saveStepBtn = document.getElementById('save-step-btn');
    if (saveStepBtn) {
      // Remove existing event listeners
      const newSaveBtn = saveStepBtn.cloneNode(true);
      saveStepBtn.parentNode.replaceChild(newSaveBtn, saveStepBtn);
      
      newSaveBtn.addEventListener('click', function() {
        addNewStep();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addStepModal'));
        modal.hide();
      });
    }
  }

  /**
   * Open the Add Step modal
   */
  function openAddStepModal() {
    const modal = new bootstrap.Modal(document.getElementById('addStepModal'));
    
    // Reset form
    document.getElementById('step-name').value = '';
    document.getElementById('step-description').value = '';
    document.getElementById('step-type').value = 'interview';
    document.getElementById('add-members-to-step').checked = false;
    
    modal.show();
  }

  /**
   * Add a new step to the process
   */
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
    const stepId = 'step-custom-' + Date.now();
    
    // Create step element
    const stepElement = document.createElement('div');
    stepElement.className = 'timeline-item';
    stepElement.setAttribute('data-step', stepId);
    
    // Calculate the next number for this step
    const existingItems = document.querySelectorAll('#recruitment-timeline > .timeline-item');
    const nextNumber = existingItems.length + 1;
    
    // Build HTML
    stepElement.innerHTML = `
      <div class="step-counter">${nextNumber}</div>
      <div class="timeline-header">
        <h6 class="timeline-title">${stepName}</h6>
        <div class="timeline-actions">
          <button type="button" class="timeline-action success" title="Approuver">
            <i class="fas fa-check"></i>
          </button>
          <button type="button" class="timeline-action danger" title="Rejeter">
            <i class="fas fa-times"></i>
          </button>
          <button type="button" class="timeline-action delete" title="Supprimer" style="background-color: #ff4757;">
            <i class="fas fa-trash"></i>
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
    timeline.appendChild(stepElement);
    
    // Setup the new item
    setupTimelineItem(stepElement);
    
    // Update step numbers
    updateStepNumbers();
    
    // Show success notification
    showToast(`L'étape "${stepName}" a été ajoutée`, 'success');
  }

  /**
   * Handle drag start event
   * @param {DragEvent} e - The drag event
   */
  function handleDragStart(e) {
    currentlyDragging = true;
    draggedItem = this;
    
    // Add visual indicator
    this.classList.add('dragging');
    this.style.opacity = '0.4';
    
    // Store the index for later use
    const items = [...timeline.querySelectorAll('.timeline-item:not(.timeline-branch .timeline-item)')];
    dragSourceIndex = items.indexOf(this);
    
    // Set drag data
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
    
    // Add drop indicators to all potential drop targets
    document.querySelectorAll('.timeline-item:not(.dragging):not(.timeline-branch .timeline-item)').forEach(item => {
      item.classList.add('drop-target');
    });
  }

  /**
   * Handle drag end event
   */
  function handleDragEnd() {
    currentlyDragging = false;
    
    // Remove visual indicators
    this.classList.remove('dragging');
    this.style.opacity = '1';
    
    document.querySelectorAll('.timeline-item').forEach(item => {
      item.classList.remove('drop-target', 'ready-to-drop', 'drag-over');
    });
    
    // Clear references
    draggedItem = null;
    dragSourceIndex = null;
    
    // Update step numbers
    updateStepNumbers();
  }

  /**
   * Set up handlers for the timeline container
   */
  function setupTimelineDragAndDrop() {
    if (!timeline) return;
    
    // These handlers are on the container to catch all drag events
    timeline.addEventListener('dragover', function(e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      
      // Find the closest timeline item if we're over one
      const targetItem = e.target.closest('.timeline-item');
      if (targetItem && targetItem !== draggedItem && !targetItem.closest('.timeline-branch')) {
        // Remove ready-to-drop from all items
        document.querySelectorAll('.timeline-item').forEach(item => {
          item.classList.remove('ready-to-drop');
        });
        
        // Add ready-to-drop to this one
        targetItem.classList.add('ready-to-drop');
      }
    });
    
    timeline.addEventListener('dragleave', function(e) {
      const targetItem = e.target.closest('.timeline-item');
      if (targetItem) {
        targetItem.classList.remove('ready-to-drop');
      }
    });
    
    timeline.addEventListener('drop', function(e) {
      e.preventDefault();
      
      if (!draggedItem) return;
      
      // Find the target (could be an item or the timeline itself)
      const dropTarget = e.target.closest('.timeline-item') || this;
      
      if (dropTarget === timeline) {
        // Dropping on the container - append to the end
        timeline.appendChild(draggedItem);
      } else if (dropTarget !== draggedItem && !dropTarget.closest('.timeline-branch')) {
        // Dropping on another item
        const allItems = [...timeline.querySelectorAll('.timeline-item:not(.timeline-branch .timeline-item)')];
        const targetIndex = allItems.indexOf(dropTarget);
        
        if (dragSourceIndex < targetIndex) {
          // Insert after
          dropTarget.parentNode.insertBefore(draggedItem, dropTarget.nextSibling);
        } else {
          // Insert before
          dropTarget.parentNode.insertBefore(draggedItem, dropTarget);
        }
      }
      
      // Remove highlighting
      document.querySelectorAll('.timeline-item').forEach(item => {
        item.classList.remove('ready-to-drop', 'drop-target');
      });
      
      // Update step numbers
      updateStepNumbers();
      
      // Show success notification
      if (draggedItem) {
        const stepName = draggedItem.querySelector('.timeline-title').textContent;
        showToast(`Étape "${stepName}" repositionnée`, 'success');
      }
      
      return false;
    });
  }

  /**
   * Set up the delete confirmation system
   */
  function setupDeleteConfirmation() {
    // This is handled through event delegation
    document.addEventListener('click', function(e) {
      const deleteButton = e.target.closest('.timeline-action.delete');
      if (deleteButton) {
        const timelineItem = deleteButton.closest('.timeline-item');
        showDeleteConfirmation(timelineItem);
      }
      
      // Handle confirmation buttons
      if (e.target.classList.contains('confirm-delete')) {
        const timelineItem = e.target.closest('.timeline-item');
        deleteTimelineItem(timelineItem);
      }
      
      if (e.target.classList.contains('cancel-delete')) {
        const timelineItem = e.target.closest('.timeline-item');
        hideDeleteConfirmation(timelineItem);
      }
    });
  }

  /**
   * Show a confirmation dialog before deleting an item
   * @param {HTMLElement} item - The timeline item to delete
   */
  function showDeleteConfirmation(item) {
    // Add deletion pending class
    item.classList.add('deletion-pending');
    
    // Create confirmation overlay
    const confirmationOverlay = document.createElement('div');
    confirmationOverlay.className = 'delete-confirmation';
    
    const stepName = item.querySelector('.timeline-title').textContent;
    
    confirmationOverlay.innerHTML = `
      <p style="font-weight: 600; color: #333; margin-bottom: 5px;">Supprimer cette étape ?</p>
      <p style="font-size: 13px; color: #666; margin-bottom: 10px;">Cette action est irréversible.</p>
      <div class="delete-confirmation-buttons">
        <button class="btn btn-sm btn-outline-secondary cancel-delete">Annuler</button>
        <button class="btn btn-sm btn-danger confirm-delete">Supprimer</button>
      </div>
    `;
    
    // Add to item
    item.appendChild(confirmationOverlay);
  }

  /**
   * Hide the delete confirmation
   * @param {HTMLElement} item - The timeline item
   */
  function hideDeleteConfirmation(item) {
    item.classList.remove('deletion-pending');
    const confirmation = item.querySelector('.delete-confirmation');
    if (confirmation) {
      confirmation.remove();
    }
  }

  /**
   * Delete a timeline item
   * @param {HTMLElement} item - The timeline item to delete
   */
  function deleteTimelineItem(item) {
    // Get the name for notification
    const stepName = item.querySelector('.timeline-title').textContent;
    
    // Remove from DOM
    item.remove();
    
    // Update step numbers
    updateStepNumbers();
    
    // Show notification
    showToast(`Étape "${stepName}" supprimée`, 'warning');
  }

  /**
   * Set up mutation observer to watch for changes to the timeline
   */
  function setupMutationObserver() {
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
          // If we added nodes, set them up
          mutation.addedNodes.forEach(node => {
            if (node.nodeType === 1 && node.classList.contains('timeline-item')) {
              setupTimelineItem(node);
            }
          });
          
          // Update step numbers
          updateStepNumbers();
        }
      });
    });
    
    observer.observe(timeline, { childList: true, subtree: true });
  }

  // Initialize module
  init();
  setupTimelineDragAndDrop();
});
