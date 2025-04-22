// Fonctionnalités pour l'édition du profil
document.addEventListener('DOMContentLoaded', function() {
    // Référence au bouton Modifier
    const editButton = document.querySelector('.profile-actions .action-btn');
    
    // Vérifier si le bouton existe
    if (!editButton) {
        console.error("Bouton d'édition de profil non trouvé");
        return;
    }
    
    // Ajouter l'événement de clic pour ouvrir le modal d'édition
    editButton.addEventListener('click', function() {
        openProfileEditor();
    });
    
    // Fonction pour ouvrir l'éditeur de profil
    function openProfileEditor() {
        // Récupérer les valeurs actuelles du profil
        const currentName = document.querySelector('.info-line:nth-child(1) .profile-value').textContent.trim();
        const currentAddress = document.querySelector('.info-line:nth-child(2) .profile-value').textContent.trim();
        const currentPosition = document.querySelector('.info-line:nth-child(3) .profile-value').textContent.trim();
        const currentSalary = document.querySelector('.info-line:nth-child(4) .profile-value').textContent.trim();
        
        // Créer le modal d'édition
        const modal = document.createElement('div');
        modal.className = 'profile-edit-modal';
        modal.innerHTML = `
            <div class="profile-edit-content">
                <div class="profile-edit-header">
                    <h3><i class="fas fa-pen"></i> Modifier votre profil</h3>
                    <button class="profile-edit-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="profile-edit-body">
                    <form id="profile-edit-form">
                        <div class="form-group">
                            <label for="edit-name"><i class="fas fa-user"></i> Nom complet</label>
                            <input type="text" id="edit-name" value="${currentName}" placeholder="Prénom Nom">
                        </div>
                        <div class="form-group">
                            <label for="edit-address"><i class="fas fa-map-marker-alt"></i> Adresse</label>
                            <input type="text" id="edit-address" value="${currentAddress}" placeholder="Votre adresse">
                        </div>
                        <div class="form-group">
                            <label for="edit-position"><i class="fas fa-briefcase"></i> Poste</label>
                            <input type="text" id="edit-position" value="${currentPosition}" placeholder="Votre poste">
                        </div>
                        <div class="form-group">
                            <label for="edit-salary"><i class="fas fa-euro-sign"></i> Rémunération</label>
                            <input type="text" id="edit-salary" value="${currentSalary}" placeholder="Ex: 40K-45K">
                        </div>
                        <div class="form-group">
                            <label><i class="fas fa-briefcase"></i> Statut</label>
                            <div class="radio-group">
                                <label>
                                    <input type="radio" name="status" value="active" checked>
                                    <span>En recherche active</span>
                                </label>
                                <label>
                                    <input type="radio" name="status" value="passive">
                                    <span>En recherche passive</span>
                                </label>
                                <label>
                                    <input type="radio" name="status" value="not-available">
                                    <span>Pas disponible</span>
                                </label>
                            </div>
                        </div>
                        <div class="form-group profile-picture-upload">
                            <label><i class="fas fa-image"></i> Photo de profil</label>
                            <div class="upload-container">
                                <div class="current-photo"></div>
                                <div class="upload-buttons">
                                    <label for="profile-photo-upload" class="upload-btn">
                                        <i class="fas fa-upload"></i> Télécharger une photo
                                    </label>
                                    <input type="file" id="profile-photo-upload" accept="image/*" style="display: none;">
                                    <button type="button" class="remove-photo-btn"><i class="fas fa-trash-alt"></i> Supprimer</button>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="profile-edit-footer">
                    <button type="button" class="cancel-btn">Annuler</button>
                    <button type="button" class="save-btn">Enregistrer</button>
                </div>
            </div>
        `;
        
        // Ajouter le modal au document
        document.body.appendChild(modal);
        
        // Animer l'apparition du modal
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);
        
        // Gérer la fermeture du modal
        const closeBtn = modal.querySelector('.profile-edit-close');
        const cancelBtn = modal.querySelector('.cancel-btn');
        
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        // Fermeture en cliquant à l'extérieur du contenu
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
        
        // Fonction pour fermer le modal
        function closeModal() {
            modal.classList.remove('active');
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        }
        
        // Gérer le téléchargement de photo de profil
        const photoUpload = modal.querySelector('#profile-photo-upload');
        const currentPhoto = modal.querySelector('.current-photo');
        const removePhotoBtn = modal.querySelector('.remove-photo-btn');
        
        // Afficher la photo actuelle (si disponible)
        const profilePhoto = document.querySelector('.profile-photo');
        if (profilePhoto) {
            if (profilePhoto.style.backgroundImage) {
                currentPhoto.style.backgroundImage = profilePhoto.style.backgroundImage;
            } else {
                currentPhoto.innerHTML = '<i class="fas fa-user"></i>';
            }
        }
        
        // Gérer le téléchargement d'une nouvelle photo
        photoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    currentPhoto.style.backgroundImage = `url(${event.target.result})`;
                    currentPhoto.innerHTML = '';
                };
                reader.readAsDataURL(file);
            }
        });
        
        // Supprimer la photo
        removePhotoBtn.addEventListener('click', function() {
            currentPhoto.style.backgroundImage = '';
            currentPhoto.innerHTML = '<i class="fas fa-user"></i>';
            photoUpload.value = '';
        });
        
        // Gérer l'enregistrement des modifications
        const saveBtn = modal.querySelector('.save-btn');
        saveBtn.addEventListener('click', function() {
            // Récupérer les valeurs modifiées
            const newName = document.getElementById('edit-name').value;
            const newAddress = document.getElementById('edit-address').value;
            const newPosition = document.getElementById('edit-position').value;
            const newSalary = document.getElementById('edit-salary').value;
            const statusRadios = document.getElementsByName('status');
            let newStatus = 'active';
            
            for (const radio of statusRadios) {
                if (radio.checked) {
                    newStatus = radio.value;
                    break;
                }
            }
            
            // Mettre à jour les valeurs dans la page
            document.querySelector('.info-line:nth-child(1) .profile-value').textContent = newName;
            document.querySelector('.info-line:nth-child(2) .profile-value').textContent = newAddress;
            document.querySelector('.info-line:nth-child(3) .profile-value').textContent = newPosition;
            document.querySelector('.info-line:nth-child(4) .profile-value').textContent = newSalary;
            
            // Mettre à jour le statut
            const statusBadge = document.querySelector('.status-badge');
            if (statusBadge) {
                if (newStatus === 'active') {
                    statusBadge.innerHTML = '<i class="fas fa-search"></i> En recherche active';
                    statusBadge.className = 'status-badge active';
                } else if (newStatus === 'passive') {
                    statusBadge.innerHTML = '<i class="fas fa-binoculars"></i> En recherche passive';
                    statusBadge.className = 'status-badge passive';
                } else {
                    statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Pas disponible';
                    statusBadge.className = 'status-badge not-available';
                }
            }
            
            // Mettre à jour la photo de profil si elle a été modifiée
            if (currentPhoto.style.backgroundImage) {
                profilePhoto.style.backgroundImage = currentPhoto.style.backgroundImage;
                profilePhoto.innerHTML = '';
            } else {
                profilePhoto.style.backgroundImage = '';
                profilePhoto.innerHTML = '';
            }
            
            // Fermer le modal
            closeModal();
            
            // Afficher une notification de succès
            showToast('Profil mis à jour', 'Vos informations ont été mises à jour avec succès.');
        });
    }
    
    // Fonction pour afficher une notification
    function showToast(title, message) {
        if (window.showToast) {
            window.showToast(title, message);
        } else {
            // Fallback si la fonction globale n'est pas disponible
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = `
                <div class="toast-content">
                    <i class="fas fa-check-circle toast-icon"></i>
                    <div class="toast-message">
                        <strong>${title}</strong>
                        <p>${message}</p>
                    </div>
                    <button class="toast-close"><i class="fas fa-times"></i></button>
                </div>
            `;
            
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.classList.add('show');
            }, 10);
            
            const closeToast = () => {
                toast.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(toast);
                }, 300);
            };
            
            toast.querySelector('.toast-close').addEventListener('click', closeToast);
            
            setTimeout(closeToast, 5000);
        }
    }
});
