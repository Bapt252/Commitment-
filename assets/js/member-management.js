/**
 * Member Management for Recruitment Process
 * Handles the functionality to add and manage team members in the recruitment process
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Member Management initialized');
    
    // Elements
    const addMemberBtn = document.getElementById('add-member-btn');
    const orgMembersList = document.getElementById('org-members-list');
    const noMembersMessage = document.getElementById('no-members-message');
    
    // Initialize
    function init() {
        if (addMemberBtn) {
            setupAddMemberButton();
        }
        
        // Load existing members if any
        loadExistingMembers();
    }
    
    // Setup the Add Member button
    function setupAddMemberButton() {
        addMemberBtn.addEventListener('click', function() {
            openMemberSelectionModal();
        });
    }
    
    // Open member selection modal
    function openMemberSelectionModal() {
        const modal = new bootstrap.Modal(document.getElementById('contactSelectionModal'));
        
        // Set a flag to indicate we're selecting for the org members list
        document.getElementById('contactSelectionModal').dataset.selectionType = 'org-member';
        
        // Load the contacts
        loadContacts();
        
        modal.show();
    }
    
    // Load contacts into the selection modal
    function loadContacts() {
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
                // Check if we're selecting for org members list
                if (document.getElementById('contactSelectionModal').dataset.selectionType === 'org-member') {
                    addMemberToOrg(contact);
                } else {
                    // Handle other cases if needed
                    const targetStepId = document.getElementById('contactSelectionModal').dataset.targetStep;
                    if (targetStepId) {
                        const timelineItem = document.querySelector(`.timeline-item[data-step="${targetStepId}"]`);
                        if (timelineItem) {
                            associateMemberWithStep(contact, timelineItem);
                        }
                    }
                }
                
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
    
    // Add a member to the organization
    function addMemberToOrg(contact) {
        // Check if we have a members list
        if (!orgMembersList) return;
        
        // Create the list if it doesn't exist yet
        if (!orgMembersList.querySelector('table')) {
            orgMembersList.innerHTML = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>Nom</th>
                            <th>Email</th>
                            <th>Rôle</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            `;
        }
        
        // Check if the member is already added
        const tbody = orgMembersList.querySelector('tbody');
        const existingRow = tbody.querySelector(`tr[data-id="${contact.id}"]`);
        
        if (existingRow) {
            showToast(`${contact.firstName} ${contact.lastName} est déjà membre de l'équipe de recrutement`, 'warning');
            return;
        }
        
        // Create new row
        const newRow = document.createElement('tr');
        newRow.dataset.id = contact.id;
        
        newRow.innerHTML = `
            <td>${contact.firstName} ${contact.lastName}</td>
            <td>${contact.email}</td>
            <td>
                <select class="form-select form-select-sm">
                    <option value="interviewer">Recruteur</option>
                    <option value="manager">Manager</option>
                    <option value="hr">RH</option>
                    <option value="admin">Admin</option>
                </select>
            </td>
            <td>
                <button type="button" class="btn btn-sm btn-outline-danger remove-member">
                    <i class="fas fa-times"></i>
                </button>
            </td>
        `;
        
        // Add row to table
        tbody.appendChild(newRow);
        
        // Show the members list if hidden
        orgMembersList.style.display = 'block';
        
        // Hide the no members message
        if (noMembersMessage) {
            noMembersMessage.style.display = 'none';
        }
        
        // Add event listener to remove button
        const removeBtn = newRow.querySelector('.remove-member');
        removeBtn.addEventListener('click', function() {
            removeMemberFromOrg(newRow, contact);
        });
        
        // Show success message
        showToast(`${contact.firstName} ${contact.lastName} ajouté à l'équipe de recrutement`, 'success');
    }
    
    // Remove a member from the organization
    function removeMemberFromOrg(row, contact) {
        if (!confirm(`Voulez-vous vraiment retirer ${row.querySelector('td').textContent} de l'équipe de recrutement ?`)) {
            return;
        }
        
        // Remove the row
        row.remove();
        
        // If no more rows, hide the table and show the no members message
        const tbody = orgMembersList.querySelector('tbody');
        if (!tbody || tbody.querySelectorAll('tr').length === 0) {
            orgMembersList.style.display = 'none';
            
            if (noMembersMessage) {
                noMembersMessage.style.display = 'block';
            }
        }
        
        // Show message
        showToast(`Membre retiré de l'équipe de recrutement`, 'warning');
    }
    
    // Load existing members from storage (if any)
    function loadExistingMembers() {
        // In a real application, this would load from localStorage, API, etc.
        // For this demo, we'll start with an empty list
    }
    
    // Associate a member with a step (this is a duplicate for compatibility)
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
