// Script pour rendre fonctionnels les boutons sur la page de candidature
document.addEventListener('DOMContentLoaded', function() {
    // 1. Bouton "Poser une question"
    const questionButtons = document.querySelectorAll('.btn.btn-primary');
    questionButtons.forEach(btn => {
        if (btn.textContent.includes('Poser une question')) {
            btn.addEventListener('click', function() {
                // Créer une modale pour poser une question
                const modalHTML = `
                <div class="modal fade" id="questionModal" tabindex="-1" aria-labelledby="questionModalLabel" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="questionModalLabel">Poser une question</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <form id="questionForm">
                                    <div class="mb-3">
                                        <label for="questionSubject" class="form-label">Sujet</label>
                                        <input type="text" class="form-control" id="questionSubject" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="questionContent" class="form-label">Votre question</label>
                                        <textarea class="form-control" id="questionContent" rows="4" required></textarea>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                                <button type="button" class="btn btn-primary" id="sendQuestion">Envoyer</button>
                            </div>
                        </div>
                    </div>
                </div>
                `;
                
                // Ajouter la modale au document s'il n'existe pas déjà
                if (!document.getElementById('questionModal')) {
                    document.body.insertAdjacentHTML('beforeend', modalHTML);
                    
                    // Gestionnaire d'événement pour le bouton Envoyer
                    document.getElementById('sendQuestion').addEventListener('click', function() {
                        const subject = document.getElementById('questionSubject').value;
                        const content = document.getElementById('questionContent').value;
                        
                        if (subject && content) {
                            // Simuler l'envoi de la question (à remplacer par un vrai appel API)
                            alert('Votre question a été envoyée avec succès !');
                            
                            // Fermer la modale
                            const modal = bootstrap.Modal.getInstance(document.getElementById('questionModal'));
                            modal.hide();
                        } else {
                            alert('Veuillez remplir tous les champs obligatoires.');
                        }
                    });
                }
                
                // Afficher la modale
                const modal = new bootstrap.Modal(document.getElementById('questionModal'));
                modal.show();
            });
        }
    });
    
    // 2. Bouton "Annuler ma candidature"
    const cancelButtons = document.querySelectorAll('.btn.btn-outline-danger');
    cancelButtons.forEach(btn => {
        if (btn.textContent.includes('Annuler ma candidature')) {
            btn.addEventListener('click', function() {
                // Créer une modale de confirmation
                const modalHTML = `
                <div class="modal fade" id="cancelModal" tabindex="-1" aria-labelledby="cancelModalLabel" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="cancelModalLabel">Confirmation</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <p>Êtes-vous sûr de vouloir annuler votre candidature ?</p>
                                <p class="text-danger">Cette action est irréversible.</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Non, retour</button>
                                <button type="button" class="btn btn-danger" id="confirmCancel">Oui, annuler ma candidature</button>
                            </div>
                        </div>
                    </div>
                </div>
                `;
                
                // Ajouter la modale au document s'il n'existe pas déjà
                if (!document.getElementById('cancelModal')) {
                    document.body.insertAdjacentHTML('beforeend', modalHTML);
                    
                    // Gestionnaire d'événement pour le bouton de confirmation
                    document.getElementById('confirmCancel').addEventListener('click', function() {
                        // Simuler l'annulation de la candidature (à remplacer par un vrai appel API)
                        alert('Votre candidature a été annulée.');
                        
                        // Fermer la modale
                        const modal = bootstrap.Modal.getInstance(document.getElementById('cancelModal'));
                        modal.hide();
                        
                        // Rediriger vers la page des candidatures
                        setTimeout(() => {
                            window.location.href = 'candidate-dashboard.html?email=demo.utilisateur@nexten.fr&password=s';
                        }, 1000);
                    });
                }
                
                // Afficher la modale
                const modal = new bootstrap.Modal(document.getElementById('cancelModal'));
                modal.show();
            });
        }
    });
    
    // 3. Bouton "Modifier le rendez-vous"
    const modifyButtons = document.querySelectorAll('.btn.btn-outline');
    modifyButtons.forEach(btn => {
        if (btn.textContent.includes('Modifier le rendez-vous')) {
            btn.addEventListener('click', function() {
                // Créer une modale pour modifier le rendez-vous
                const modalHTML = `
                <div class="modal fade" id="appointmentModal" tabindex="-1" aria-labelledby="appointmentModalLabel" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="appointmentModalLabel">Modifier le rendez-vous</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <form id="appointmentForm">
                                    <div class="mb-3">
                                        <label for="appointmentDate" class="form-label">Date</label>
                                        <input type="date" class="form-control" id="appointmentDate" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="appointmentTime" class="form-label">Heure</label>
                                        <input type="time" class="form-control" id="appointmentTime" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="appointmentType" class="form-label">Type de rendez-vous</label>
                                        <select class="form-select" id="appointmentType" required>
                                            <option value="">Choisir...</option>
                                            <option value="présentiel">En présentiel</option>
                                            <option value="visio">Visio-conférence</option>
                                            <option value="téléphone">Téléphone</option>
                                        </select>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                                <button type="button" class="btn btn-primary" id="saveAppointment">Enregistrer</button>
                            </div>
                        </div>
                    </div>
                </div>
                `;
                
                // Ajouter la modale au document s'il n'existe pas déjà
                if (!document.getElementById('appointmentModal')) {
                    document.body.insertAdjacentHTML('beforeend', modalHTML);
                    
                    // Préremplir avec la date actuelle
                    const today = new Date();
                    const formattedDate = today.toISOString().split('T')[0];
                    document.getElementById('appointmentDate').value = formattedDate;
                    
                    // Gestionnaire d'événement pour le bouton Enregistrer
                    document.getElementById('saveAppointment').addEventListener('click', function() {
                        const date = document.getElementById('appointmentDate').value;
                        const time = document.getElementById('appointmentTime').value;
                        const type = document.getElementById('appointmentType').value;
                        
                        if (date && time && type) {
                            // Simuler la modification du rendez-vous (à remplacer par un vrai appel API)
                            alert(`Votre rendez-vous a été modifié pour le ${date} à ${time} en ${type}.`);
                            
                            // Fermer la modale
                            const modal = bootstrap.Modal.getInstance(document.getElementById('appointmentModal'));
                            modal.hide();
                            
                            // Mettre à jour l'affichage sur la page
                            const dateStr = new Date(date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' });
                            const nearestDateDisplay = btn.closest('.opportunity-card').querySelector('.interview-date');
                            if (nearestDateDisplay) {
                                nearestDateDisplay.innerHTML = `<i class="fas fa-calendar-alt"></i> ${dateStr}, ${time}`;
                            }
                        } else {
                            alert('Veuillez remplir tous les champs obligatoires.');
                        }
                    });
                }
                
                // Afficher la modale
                const modal = new bootstrap.Modal(document.getElementById('appointmentModal'));
                modal.show();
            });
        }
    });
    
    // 4. Bouton "Messagerie"
    const messageButtons = document.querySelectorAll('.btn.btn-outline.btn-icon-text');
    messageButtons.forEach(btn => {
        if (btn.textContent.includes('Messagerie')) {
            btn.addEventListener('click', function() {
                // Créer une modale pour la messagerie
                const modalHTML = `
                <div class="modal fade" id="messageModal" tabindex="-1" aria-labelledby="messageModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="messageModalLabel">Messagerie</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="message-container mb-3" style="height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
                                    <!-- Messages factices -->
                                    <div class="message received mb-2">
                                        <div class="message-header">
                                            <strong>Thomas MARTIN</strong> <span class="text-muted">- 27 Mars, 10:30</span>
                                        </div>
                                        <div class="message-content p-2 bg-light rounded">
                                            Bonjour, nous sommes ravis de vous rencontrer pour discuter du poste de Chef de Projet Digital.
                                        </div>
                                    </div>
                                    <div class="message sent mb-2 text-end">
                                        <div class="message-header">
                                            <strong>Vous</strong> <span class="text-muted">- 27 Mars, 11:15</span>
                                        </div>
                                        <div class="message-content p-2 bg-primary text-white rounded">
                                            Bonjour ! Merci pour votre message. Je suis également impatient(e) de vous rencontrer.
                                        </div>
                                    </div>
                                    <div class="message received mb-2">
                                        <div class="message-header">
                                            <strong>Thomas MARTIN</strong> <span class="text-muted">- 27 Mars, 14:22</span>
                                        </div>
                                        <div class="message-content p-2 bg-light rounded">
                                            Parfait ! N'hésitez pas à préparer vos questions pour notre entretien.
                                        </div>
                                    </div>
                                </div>
                                <form id="messageForm">
                                    <div class="mb-3">
                                        <label for="messageContent" class="form-label">Nouveau message</label>
                                        <textarea class="form-control" id="messageContent" rows="3" required></textarea>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                                <button type="button" class="btn btn-primary" id="sendMessage">Envoyer</button>
                            </div>
                        </div>
                    </div>
                </div>
                `;
                
                // Ajouter la modale au document s'il n'existe pas déjà
                if (!document.getElementById('messageModal')) {
                    document.body.insertAdjacentHTML('beforeend', modalHTML);
                    
                    // Gestionnaire d'événement pour le bouton Envoyer
                    document.getElementById('sendMessage').addEventListener('click', function() {
                        const content = document.getElementById('messageContent').value;
                        
                        if (content) {
                            // Créer un nouveau message
                            const now = new Date();
                            const formattedDate = now.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' });
                            const formattedTime = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
                            
                            const messageHTML = `
                            <div class="message sent mb-2 text-end">
                                <div class="message-header">
                                    <strong>Vous</strong> <span class="text-muted">- ${formattedDate}, ${formattedTime}</span>
                                </div>
                                <div class="message-content p-2 bg-primary text-white rounded">
                                    ${content}
                                </div>
                            </div>
                            `;
                            
                            // Ajouter le message à la conversation
                            const container = document.querySelector('.message-container');
                            container.insertAdjacentHTML('beforeend', messageHTML);
                            
                            // Faire défiler vers le bas
                            container.scrollTop = container.scrollHeight;
                            
                            // Effacer le champ de texte
                            document.getElementById('messageContent').value = '';
                        } else {
                            alert('Veuillez saisir un message avant d\'envoyer.');
                        }
                    });
                }
                
                // Afficher la modale
                const modal = new bootstrap.Modal(document.getElementById('messageModal'));
                modal.show();
            });
        }
    });
});