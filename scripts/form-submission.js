// Modification du script pour rediriger vers la page de recommandation candidats après la soumission du questionnaire

document.addEventListener('DOMContentLoaded', function() {
    // Soumettre le formulaire
    const form = document.getElementById('client-questionnaire-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Sauvegarder les données du formulaire
            saveFormData();
            
            // Afficher un message de succès
            showNotification('Votre demande a été envoyée avec succès!', 'success');
            
            // Vérifier la réponse à la question de recrutement
            const recruitmentNeeded = sessionStorage.getItem('recruitmentNeeded') || 'no';
            
            // Rediriger vers la page de recommandation si recrutement nécessaire, sinon vers le dashboard
            if (recruitmentNeeded === 'yes') {
                setTimeout(() => {
                    window.location.href = 'candidate-recommendation.html';
                }, 1500);
            } else {
                setTimeout(() => {
                    window.location.href = 'company-dashboard.html';
                }, 1500);
            }
        });
    }
    
    // Fonction pour sauvegarder les données du formulaire
    function saveFormData() {
        const formData = {
            companyName: document.getElementById('company-name')?.value || '',
            companyAddress: document.getElementById('company-address')?.value || '',
            companyWebsite: document.getElementById('company-website')?.value || '',
            companyDescription: document.getElementById('company-description')?.value || '',
            companySize: document.getElementById('company-size')?.value || '',
            contactName: document.getElementById('contact-name')?.value || '',
            contactTitle: document.getElementById('contact-title')?.value || '',
            contactEmail: document.getElementById('contact-email')?.value || '',
            contactPhone: document.getElementById('contact-phone')?.value || '',
            contactPreferred: document.getElementById('contact-preferred')?.value || '',
            recruitmentNeeded: document.querySelector('input[name="recruitment-need"]:checked')?.value || 'no',
            // Ajouter d'autres données du formulaire ici
        };
        
        // Récupérer les données du job parser si disponibles
        const jobInfo = document.getElementById('job-info-container');
        if (jobInfo && jobInfo.style.display !== 'none') {
            formData.jobTitle = document.getElementById('job-title-value')?.textContent || '';
            formData.jobLocation = document.getElementById('job-location-value')?.textContent || '';
            formData.jobContract = document.getElementById('job-contract-value')?.textContent || '';
            formData.jobExperience = document.getElementById('job-experience-value')?.textContent || '';
            formData.jobEducation = document.getElementById('job-education-value')?.textContent || '';
            formData.jobSalary = document.getElementById('job-salary-value')?.textContent || '';
        }
        
        // Stocker les données dans sessionStorage
        sessionStorage.setItem('clientFormData', JSON.stringify(formData));
    }
});