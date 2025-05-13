// Fonction pour générer le récapitulatif des informations
function generateSummary() {
    console.log("Génération du récapitulatif...");
    const summaryContainer = document.getElementById('summary-content');
    if (!summaryContainer) return;
    
    // Récupérer les données de sessionStorage ou localStorage
    let clientData = {};
    let parsedJobData = null;
    
    try {
        // Essayer de récupérer les données du formulaire client
        const storedData = sessionStorage.getItem('clientFormData');
        if (storedData) {
            clientData = JSON.parse(storedData);
            console.log("Données client récupérées:", clientData);
        }
        
        // Récupérer aussi les données de parsing de poste si disponibles
        const jobData = sessionStorage.getItem('parsedJobData');
        if (jobData) {
            parsedJobData = JSON.parse(jobData);
            console.log("Données de poste récupérées:", parsedJobData);
            clientData.jobData = parsedJobData;
        }
    } catch (error) {
        console.error('Erreur lors de la récupération des données :', error);
    }
    
    // Si aucune donnée n'est disponible, récupérer directement depuis les formulaires
    if (Object.keys(clientData).length === 0) {
        clientData = collectFormData();
    }
    
    // Déterminer si un recrutement est nécessaire en vérifiant plusieurs sources
    const recruitmentNeeded = determineRecruitmentNeeded();
    console.log("Besoin de recrutement détecté:", recruitmentNeeded);
    
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
                        <td>${getCompanySizeLabel(clientData.companySize) || getCompanySizeLabel(document.getElementById('company-size')?.value) || 'Non spécifié'}</td>
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
                        <td>${getContactMethodLabel(clientData.contactPreferred) || getContactMethodLabel(document.getElementById('contact-preferred')?.value) || 'Non spécifié'}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
    
    summaryHTML += `
        <div class="summary-section">
            <h3>Besoin en recrutement</h3>
            <table class="summary-table">
                <tbody>
                    <tr>
                        <td><strong>Besoin de recrutement :</strong></td>
                        <td>${recruitmentNeeded ? 'Oui' : 'Non'}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
    
    // Si un recrutement est nécessaire, ajouter les détails du poste
    if (recruitmentNeeded) {
        console.log("Ajout des détails du poste au récapitulatif");
        
        // Récupérer les données du poste
        const jobData = clientData.jobData || parsedJobData || {};
        
        // Vérifier si des données de poste ont été extraites par le parser
        const hasJobInfo = jobData && (jobData.title || document.getElementById('job-title-value')?.textContent !== 'Non spécifié');
        
        if (hasJobInfo) {
            summaryHTML += `
                <div class="summary-section">
                    <h3>Informations sur le poste (extraites)</h3>
                    <table class="summary-table">
                        <tbody>
                            <tr>
                                <td><strong>Titre du poste :</strong></td>
                                <td>${jobData.title || document.getElementById('job-title-value')?.textContent || 'Non spécifié'}</td>
                            </tr>
                            <tr>
                                <td><strong>Type de contrat :</strong></td>
                                <td>${jobData.contract_type || document.getElementById('job-contract-value')?.textContent || 'Non spécifié'}</td>
                            </tr>
                            <tr>
                                <td><strong>Lieu :</strong></td>
                                <td>${jobData.location || document.getElementById('job-location-value')?.textContent || 'Non spécifié'}</td>
                            </tr>
                            <tr>
                                <td><strong>Expérience requise :</strong></td>
                                <td>${jobData.experience || document.getElementById('job-experience-value')?.textContent || 'Non spécifié'}</td>
                            </tr>
                            <tr>
                                <td><strong>Formation :</strong></td>
                                <td>${jobData.education || document.getElementById('job-education-value')?.textContent || 'Non spécifié'}</td>
                            </tr>
                            <tr>
                                <td><strong>Salaire :</strong></td>
                                <td>${jobData.salary || document.getElementById('job-salary-value')?.textContent || 'Non spécifié'}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="summary-section">
                    <h3>Compétences et responsabilités (extraites)</h3>
                    <table class="summary-table">
                        <tbody>
                            <tr>
                                <td><strong>Compétences requises :</strong></td>
                                <td>${formatSkills(jobData.skills) || document.getElementById('job-skills-value')?.innerHTML || 'Non spécifié'}</td>
                            </tr>
                            <tr>
                                <td><strong>Responsabilités :</strong></td>
                                <td>${formatList(jobData.responsibilities) || document.getElementById('job-responsibilities-value')?.innerHTML || 'Non spécifié'}</td>
                            </tr>
                            <tr>
                                <td><strong>Avantages :</strong></td>
                                <td>${formatList(jobData.benefits) || document.getElementById('job-benefits-value')?.innerHTML || 'Non spécifié'}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
        }
        
        // Ajouter les informations du poste renseignées manuellement
        summaryHTML += `
            <div class="summary-section">
                <h3>Détails du recrutement (renseignés)</h3>
                <table class="summary-table">
                    <tbody>
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
                            <td><strong>Expérience requise :</strong></td>
                            <td>${getExperienceValue() || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Connaissance du secteur :</strong></td>
                            <td>${getSectorKnowledge() || 'Non spécifié'}</td>
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
                            <td>${document.getElementById('salary')?.value || jobData?.salary || document.getElementById('job-salary-value')?.textContent || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Avantages :</strong></td>
                            <td>${document.getElementById('benefits')?.value || formatBenefits(jobData?.benefits) || document.getElementById('job-benefits-value')?.textContent || 'Non spécifié'}</td>
                        </tr>
                        <tr>
                            <td><strong>Type de contrat :</strong></td>
                            <td>${getContractTypeLabel() || jobData?.contract_type || document.getElementById('job-contract-value')?.textContent || 'Non spécifié'}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    }
    
    // Appliquer le HTML généré au conteneur
    summaryContainer.innerHTML = summaryHTML;
}

// Fonction pour déterminer si l'utilisateur a besoin d'un recrutement
function determineRecruitmentNeeded() {
    // Vérifier plusieurs sources pour déterminer si un recrutement est nécessaire
    
    // 1. Vérifier dans sessionStorage
    const storedValue = sessionStorage.getItem('recruitmentNeeded');
    if (storedValue === 'yes') {
        return true;
    }
    
    // 2. Vérifier le bouton radio
    const recruitmentYes = document.getElementById('recruitment-yes');
    if (recruitmentYes && recruitmentYes.checked) {
        return true;
    }
    
    // 3. Vérifier si des informations de poste ont été parsées
    const parsedJobData = sessionStorage.getItem('parsedJobData');
    if (parsedJobData) {
        return true;
    }
    
    // 4. Vérifier si le conteneur d'informations de poste est visible
    const jobInfoContainer = document.getElementById('job-info-container');
    if (jobInfoContainer && jobInfoContainer.style.display !== 'none') {
        return true;
    }
    
    // 5. Vérifier si la section de parsing est active
    const jobParsingSection = document.getElementById('job-parsing-section');
    if (jobParsingSection && jobParsingSection.classList.contains('active')) {
        return true;
    }
    
    // Par défaut, retourner false
    return false;
}

// Fonction pour obtenir le libellé de la taille de l'entreprise
function getCompanySizeLabel(value) {
    if (!value) return '';
    
    const sizeLabels = {
        'tpe': 'TPE',
        'pme': 'PME',
        'eti': 'ETI',
        'groupe': 'Groupe',
        'startup': 'Startup'
    };
    
    return sizeLabels[value] || value;
}

// Fonction pour obtenir le libellé de la méthode de contact
function getContactMethodLabel(value) {
    if (!value) return '';
    
    const methodLabels = {
        'email': 'Email',
        'phone': 'Téléphone',
        'video': 'Visioconférence'
    };
    
    return methodLabels[value] || value;
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

// Fonction pour récupérer les informations sur la connaissance du secteur
function getSectorKnowledge() {
    const sectorRadio = document.querySelector('input[name="sector-knowledge"]:checked');
    if (!sectorRadio) return '';
    
    if (sectorRadio.value === 'no') {
        return 'Non';
    } else {
        const sectorSelect = document.getElementById('sector-list');
        const sectorValue = sectorSelect?.value || '';
        
        const sectorValues = {
            'tech': 'Informatique / Tech',
            'finance': 'Finance / Banque / Assurance',
            'health': 'Santé / Médical',
            'industry': 'Industrie / Production',
            'services': 'Services',
            'retail': 'Commerce / Distribution',
            'construction': 'Construction / BTP',
            'transport': 'Transport / Logistique',
            'hospitality': 'Hôtellerie / Restauration',
            'education': 'Éducation / Formation',
            'other': 'Autre'
        };
        
        return `Oui (${sectorValues[sectorValue] || sectorValue})`;
    }
}

// Fonction pour récupérer le type de contrat
function getContractTypeLabel() {
    const contractType = document.getElementById('contract-type')?.value;
    if (!contractType) return '';
    
    const contractValues = {
        '35h': '35h',
        '39h': '39h',
        'cadre': 'Cadre',
        'non-cadre': 'Non-cadre'
    };
    
    return contractValues[contractType] || contractType;
}

// Fonction pour formater les compétences depuis les données du poste
function formatSkills(skills) {
    if (!skills || !Array.isArray(skills) || skills.length === 0) return '';
    
    // Récupérer l'élément HTML des compétences pour vérifier son format
    const skillsElement = document.getElementById('job-skills-value');
    if (skillsElement && skillsElement.innerHTML.includes('tag')) {
        // Si l'élément utilise des tags, formater de la même façon
        return skills.map(skill => `<span class="tag">${skill}</span>`).join(' ');
    }
    
    // Sinon, retourner une liste simple
    return skills.join(', ');
}

// Fonction pour formater une liste
function formatList(items) {
    if (!items || !Array.isArray(items) || items.length === 0) return '';
    
    return `<ul>${items.map(item => `<li>${item}</li>`).join('')}</ul>`;
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
    console.log("Initialisation du générateur de récapitulatif");
    
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
        setTimeout(generateSummary, 100);
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
        
        /* Style spécifique pour les tags */
        .tag {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            background-color: #e5e7eb;
            color: #4b5563;
            margin: 0.25rem;
            font-size: 0.85rem;
        }
        
        /* Style pour les listes */
        .summary-table ul {
            margin: 0;
            padding-left: 1.5rem;
        }
        
        .summary-table li {
            margin-bottom: 0.25rem;
        }
    `;
    document.head.appendChild(style);
});

// Fonction pour forcer la génération du récapitulatif
window.forceGenerateSummary = function() {
    generateSummary();
};

// Ajouter un écouteur d'événements pour l'étape de confirmation
window.addEventListener('load', function() {
    // Si on est sur l'étape de confirmation, générer le récapitulatif
    const confirmationSection = document.querySelector('.form-section[data-step="4"]');
    if (confirmationSection && confirmationSection.classList.contains('active')) {
        console.log("Page de confirmation active au chargement de la page");
        setTimeout(generateSummary, 300);
    }
});
