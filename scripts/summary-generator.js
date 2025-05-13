// Fonction pour générer le récapitulatif des informations
function generateSummary() {
    const summaryContainer = document.getElementById('summary-content');
    if (!summaryContainer) return;
    
    // Récupérer les données de sessionStorage ou localStorage
    let clientData = {};
    
    try {
        // Essayer de récupérer les données du formulaire client
        const storedData = sessionStorage.getItem('clientFormData');
        if (storedData) {
            clientData = JSON.parse(storedData);
        }
        
        // Récupérer aussi les données de parsing de poste si disponibles
        const jobData = sessionStorage.getItem('parsedJobData');
        if (jobData) {
            clientData.jobData = JSON.parse(jobData);
        }
    } catch (error) {
        console.error('Erreur lors de la récupération des données :', error);
    }
    
    // Si aucune donnée n'est disponible, récupérer directement depuis les formulaires
    if (Object.keys(clientData).length === 0) {
        collectFormData();
    }
    
    // Construire le HTML du récapitulatif
    let summaryHTML = `
        <div class="summary-section">
            <h3>Informations sur la structure</h3>
            <table class="summary-table">
                <tbody>
                    <tr>
                        <td><strong>Nom de la structure :</strong></td>
                        <td>${clientData.companyName || document.getElementById('company-name')?.value || 'Non spécifié'}</td>
                    </tr>
                    <tr>
                        <td><strong>Adresse :</strong></td>
                        <td>${clientData.companyAddress || document.getElementById('company-address')?.value || 'Non spécifié'}</td>
                    </tr>
                    <tr>
                        <td><strong>Site internet :</strong></td>
                        <td>${clientData.companyWebsite || document.getElementById('company-website')?.value || 'Non spécifié'}</td>
                    </tr>
                    <tr>
                        <td><strong>Taille de la structure :</strong></td>
                        <td>${clientData.companySize || document.getElementById('company-size')?.value || 'Non spécifié'}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="summary-section">
            <h3>Informations de contact</h3>
            <table class="summary-table">
                <tbody>
                    <tr>
                        <td><strong>Nom complet :</strong></td>
                        <td>${clientData.contactName || document.getElementById('contact-name')?.value || 'Non spécifié'}</td>
                    </tr>
                    <tr>
                        <td><strong>Fonction :</strong></td>
                        <td>${clientData.contactTitle || document.getElementById('contact-title')?.value || 'Non spécifié'}</td>
                    </tr>
                    <tr>
                        <td><strong>Email :</strong></td>
                        <td>${clientData.contactEmail || document.getElementById('contact-email')?.value || 'Non spécifié'}</td>
                    </tr>
                    <tr>
                        <td><strong>Téléphone :</strong></td>
                        <td>${clientData.contactPhone || document.getElementById('contact-phone')?.value || 'Non spécifié'}</td>
                    </tr>
                    <tr>
                        <td><strong>Mode de contact préféré :</strong></td>
                        <td>${clientData.contactPreferred || document.getElementById('contact-preferred')?.value || 'Non spécifié'}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
    
    // Récupérer les informations de recrutement
    const recruitmentNeeded = clientData.recruitmentNeeded || 
                             document.querySelector('input[name="recruitment-need"]:checked')?.value || 
                             'no';
    
    summaryHTML += `
        <div class="summary-section">
            <h3>Besoin en recrutement</h3>
            <table class="summary-table">
                <tbody>
                    <tr>
                        <td><strong>Besoin de recrutement :</strong></td>
                        <td>${recruitmentNeeded === 'yes' ? 'Oui' : 'Non'}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
    
    // Si un recrutement est nécessaire, ajouter les détails du poste
    if (recruitmentNeeded === 'yes') {
        // Récupérer les données du poste
        const jobData = clientData.jobData || {};
        
        // Ajouter les informations du poste
        summaryHTML += `
            <div class="summary-section">
                <h3>Détails du poste</h3>
                <table class="summary-table">
                    <tbody>
                        <tr>
                            <td><strong>Titre du poste :</strong></td>
                            <td>${jobData.title || document.getElementById('job-title-value')?.textContent || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Type de contrat :</strong></td>
                            <td>${jobData.contract_type || document.getElementById('job-contract-value')?.textContent || document.getElementById('contract-type')?.value || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Lieu :</strong></td>
                            <td>${jobData.location || document.getElementById('job-location-value')?.textContent || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Expérience requise :</strong></td>
                            <td>${getExperienceValue() || jobData.experience || document.getElementById('job-experience-value')?.textContent || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Délai de recrutement :</strong></td>
                            <td>${getRecruitmentDelays() || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Gestion de préavis :</strong></td>
                            <td>${getNoticeValue() || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Contexte de recrutement :</strong></td>
                            <td>${getRecruitmentContext() || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Environnement de travail :</strong></td>
                            <td>${getWorkEnvironment() || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Équipe et rattachement :</strong></td>
                            <td>${document.getElementById('team-composition')?.value || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Perspectives d'évolution :</strong></td>
                            <td>${document.getElementById('evolution-perspectives')?.value || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Rémunération :</strong></td>
                            <td>${document.getElementById('salary')?.value || jobData.salary || document.getElementById('job-salary-value')?.textContent || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Avantages :</strong></td>
                            <td>${document.getElementById('benefits')?.value || formatBenefits(jobData.benefits) || document.getElementById('job-benefits-value')?.textContent || 'Non spécifié'}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    }
    
    // Appliquer le HTML généré au conteneur
    summaryContainer.innerHTML = summaryHTML;
}

// Fonction pour récupérer la valeur d'expérience
function getExperienceValue() {
    const experienceRadio = document.querySelector('input[name="experience-required"]:checked');
    if (!experienceRadio) return '';
    
    const experienceValues = {
        'junior': 'Profil Junior',
        '2-3': '2 ans - 3 ans',
        '5-10': '5 ans - 10 ans',
        '10plus': '10 ans et plus'
    };
    
    return experienceValues[experienceRadio.value] || '';
}

// Fonction pour récupérer les délais de recrutement (checkboxes)
function getRecruitmentDelays() {
    const delayCheckboxes = document.querySelectorAll('input[name="recruitment-delay"]:checked');
    if (!delayCheckboxes || delayCheckboxes.length === 0) return '';
    
    const delayValues = {
        'immediate': 'Immédiat',
        '2weeks': '2 semaines',
        '1month': '1 mois',
        '2months': '2 mois',
        '3months': '3 mois'
    };
    
    const delays = Array.from(delayCheckboxes).map(checkbox => delayValues[checkbox.value] || checkbox.value);
    return delays.join(', ');
}

// Fonction pour récupérer les informations sur le préavis
function getNoticeValue() {
    const noticeRadio = document.querySelector('input[name="can-handle-notice"]:checked');
    if (!noticeRadio) return '';
    
    if (noticeRadio.value === 'no') {
        return 'Non';
    } else {
        const durationSelect = document.getElementById('notice-duration');
        const durationValue = durationSelect?.value || '';
        
        const durationValues = {
            '1month': '1 mois',
            '2months': '2 mois',
            '3months': '3 mois'
        };
        
        return `Oui (${durationValues[durationValue] || durationValue})`;
    }
}

// Fonction pour récupérer le contexte de recrutement
function getRecruitmentContext() {
    const contextRadio = document.querySelector('input[name="recruitment-context"]:checked');
    if (!contextRadio) return '';
    
    const contextValues = {
        'creation': 'Création de poste',
        'replacement': 'Remplacement',
        'growth': 'Accroissement d\'activité / Renfort',
        'confidential': 'Confidentiel'
    };
    
    return contextValues[contextRadio.value] || '';
}

// Fonction pour récupérer l'environnement de travail
function getWorkEnvironment() {
    const envRadio = document.querySelector('input[name="work-environment"]:checked');
    if (!envRadio) return '';
    
    const envValues = {
        'openspace': 'Open space',
        'office': 'Bureau'
    };
    
    return envValues[envRadio.value] || '';
}

// Fonction pour formater les avantages depuis les données du poste
function formatBenefits(benefits) {
    if (!benefits || !Array.isArray(benefits) || benefits.length === 0) return '';
    
    return benefits.join(', ');
}

// Fonction pour collecter toutes les données des formulaires
function collectFormData() {
    const formData = {
        // Structure
        companyName: document.getElementById('company-name')?.value || '',
        companyAddress: document.getElementById('company-address')?.value || '',
        companyWebsite: document.getElementById('company-website')?.value || '',
        companyDescription: document.getElementById('company-description')?.value || '',
        companySize: document.getElementById('company-size')?.value || '',
        
        // Contact
        contactName: document.getElementById('contact-name')?.value || '',
        contactTitle: document.getElementById('contact-title')?.value || '',
        contactEmail: document.getElementById('contact-email')?.value || '',
        contactPhone: document.getElementById('contact-phone')?.value || '',
        contactPreferred: document.getElementById('contact-preferred')?.value || '',
        
        // Recrutement
        recruitmentNeeded: document.querySelector('input[name="recruitment-need"]:checked')?.value || 'no'
    };
    
    // Sauvegarder les données collectées
    sessionStorage.setItem('clientFormData', JSON.stringify(formData));
    
    return formData;
}

// Initialisation - Générer le résumé lorsque la page est chargée
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si nous sommes sur la page de confirmation
    const confirmationSection = document.querySelector('.form-section[data-step="4"]');
    const isConfirmationActive = confirmationSection?.classList.contains('active');
    
    // Préparer les événements pour générer le résumé lors du changement d'étape
    const nextStepButtons = document.querySelectorAll('.next-step');
    nextStepButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetStep = parseInt(this.getAttribute('data-step'));
            if (targetStep === 4) {
                // Générer le résumé lorsqu'on passe à l'étape de confirmation
                setTimeout(generateSummary, 100);
            }
        });
    });
    
    // Si la page de confirmation est déjà active, générer le résumé
    if (isConfirmationActive) {
        generateSummary();
    }
});

// Ajouter des styles pour le résumé
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .summary-section {
            margin-bottom: 1.5rem;
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
        }
        
        .summary-section h3 {
            margin-top: 0;
            margin-bottom: 1rem;
            font-size: 1.1rem;
            color: #4b5563;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }
        
        .summary-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .summary-table td {
            padding: 0.5rem;
            vertical-align: top;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .summary-table tr:last-child td {
            border-bottom: none;
        }
        
        .summary-table td:first-child {
            width: 35%;
            color: #4b5563;
        }
        
        .summary-table td:last-child {
            width: 65%;
        }
    `;
    document.head.appendChild(style);
});
