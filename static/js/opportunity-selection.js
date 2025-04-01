// Script pour les opportunités sélectionnées
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script de sélection d\'opportunités chargé');
    
    // Récupérer les cases à cocher et les boutons
    const checkboxes = document.querySelectorAll('.job-select input[type="checkbox"]');
    const confirmButton = document.getElementById('confirm-selection');
    
    if (confirmButton) {
        // Remplacer le gestionnaire d'événements existant
        confirmButton.addEventListener('click', function(e) {
            // Empêcher le comportement par défaut
            e.preventDefault();
            
            // Collecter les opportunités sélectionnées
            const selectedJobs = [];
            
            checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    const jobId = checkbox.getAttribute('data-job-id');
                    const jobCard = checkbox.closest('.job-card');
                    
                    if (jobCard && jobId) {
                        // Extraire les données du job
                        const title = jobCard.querySelector('.job-title-info h3').textContent;
                        const company = jobCard.querySelector('.job-info-item:nth-child(1) .info-value').textContent;
                        const salary = jobCard.querySelector('.job-info-item:nth-child(4) .info-value').textContent;
                        const location = jobCard.querySelector('.job-info-item:nth-child(3) .info-value').textContent;
                        const contractElement = jobCard.querySelector('.contract-badge');
                        const contract = contractElement ? contractElement.textContent : 'Type de contrat non spécifié';
                        const date = jobCard.querySelector('.job-info-item:nth-child(5) .info-value').textContent;
                        const experience = jobCard.querySelector('.job-info-item:nth-child(6) .info-value').textContent;
                        const matchPercentage = jobCard.querySelector('.match-percentage span').textContent;
                        
                        console.log('Job sélectionné:', { title, company, matchPercentage });
                        
                        selectedJobs.push({
                            id: jobId,
                            title,
                            company,
                            salary,
                            location,
                            contract,
                            date,
                            experience,
                            matchPercentage,
                            saveDate: new Date().toISOString()
                        });
                    }
                }
            });
            
            console.log('Opportunités sélectionnées:', selectedJobs);
            
            // Sauvegarder dans localStorage
            if (selectedJobs.length > 0) {
                localStorage.setItem('selectedOpportunities', JSON.stringify(selectedJobs));
                
                // Afficher une notification
                const notification = document.getElementById('selection-notification');
                if (notification) {
                    notification.classList.add('show');
                    
                    setTimeout(() => {
                        notification.classList.remove('show');
                        
                        // MODIFICATION: Rediriger vers le tableau de bord candidat
                        window.location.href = 'candidate-dashboard.html?email=demo.utilisateur%40nexten.fr&password=s';
                    }, 2000);
                } else {
                    // Si la notification n'existe pas, rediriger directement
                    window.location.href = 'candidate-dashboard.html?email=demo.utilisateur%40nexten.fr&password=s';
                }
            } else {
                alert('Veuillez sélectionner au moins une opportunité.');
            }
        });
        
        console.log('Écouteur d\'événements ajouté au bouton de confirmation');
    } else {
        console.error('Bouton de confirmation non trouvé');
    }
});