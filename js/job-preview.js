/**
 * job-preview.js
 * Script pour prévisualiser la fiche de poste extraite dans une fenêtre modale
 */

class JobPreview {
    constructor() {
        this.initElements();
        this.addEventListeners();
        console.log('JobPreview initialisé');
    }

    // Initialisation des éléments du DOM
    initElements() {
        // Créer la fenêtre modale s'il elle n'existe pas déjà
        if (!document.getElementById('job-preview-modal')) {
            this.createModal();
        }

        this.modal = document.getElementById('job-preview-modal');
        this.modalContent = document.getElementById('job-preview-content');
        this.closeButton = document.getElementById('job-preview-close');
        this.previewButton = document.getElementById('preview-job-info');
    }

    // Création de la fenêtre modale de prévisualisation
    createModal() {
        const modal = document.createElement('div');
        modal.id = 'job-preview-modal';
        modal.className = 'preview-modal';
        modal.innerHTML = `
            <div class="preview-modal-content">
                <div class="preview-modal-header">
                    <h2>Aperçu de la fiche de poste</h2>
                    <button id="job-preview-close" class="preview-modal-close">&times;</button>
                </div>
                <div id="job-preview-content" class="preview-modal-body">
                    <!-- Le contenu sera généré dynamiquement -->
                </div>
                <div class="preview-modal-footer">
                    <p>Ces informations seront utilisées pour trouver des candidats correspondant à vos critères.</p>
                </div>
            </div>
        `;

        // Ajouter le style CSS pour la modale
        const style = document.createElement('style');
        style.textContent = `
            .preview-modal {
                display: none;
                position: fixed;
                z-index: 9999;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0, 0, 0, 0.6);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .preview-modal.show {
                display: block;
                opacity: 1;
            }

            .preview-modal-content {
                position: relative;
                background: white;
                margin: 3% auto;
                padding: 0;
                width: 85%;
                max-width: 900px;
                box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
                border-radius: 16px;
                animation: modalFadeIn 0.5s;
                max-height: 90vh;
                display: flex;
                flex-direction: column;
            }

            @keyframes modalFadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .preview-modal-header {
                padding: 20px 25px;
                background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
                color: white;
                border-radius: 16px 16px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .preview-modal-header h2 {
                margin: 0;
                font-size: 1.5rem;
                font-weight: 600;
            }

            .preview-modal-close {
                color: white;
                background: none;
                border: none;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.2s;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
            }

            .preview-modal-close:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: rotate(90deg);
            }

            .preview-modal-body {
                padding: 25px;
                overflow-y: auto;
                max-height: calc(90vh - 140px);
            }

            .preview-modal-footer {
                padding: 15px 25px;
                background-color: #f5f5f5;
                border-top: 1px solid #e0e0e0;
                border-radius: 0 0 16px 16px;
            }

            .preview-modal-footer p {
                margin: 0;
                color: #666;
                font-size: 0.9rem;
                text-align: center;
            }

            /* Styles pour le contenu de prévisualisation */
            .job-preview-section {
                margin-bottom: 25px;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 20px;
            }

            .job-preview-section:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }

            .job-preview-header {
                display: flex;
                align-items: center;
                margin-bottom: 25px;
            }

            .job-preview-company-info {
                flex: 1;
            }

            .job-preview-title {
                font-size: 1.8rem;
                font-weight: 700;
                margin: 0;
                color: #333;
                margin-bottom: 5px;
            }

            .job-preview-company {
                font-size: 1.2rem;
                color: #666;
                margin: 0;
            }

            .job-preview-location {
                display: flex;
                align-items: center;
                margin-top: 10px;
                color: #666;
            }

            .job-preview-location i {
                color: #7C3AED;
                margin-right: 8px;
            }

            .job-preview-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-top: 20px;
            }

            .job-preview-meta-item {
                display: flex;
                align-items: center;
                background: rgba(124, 58, 237, 0.1);
                padding: 8px 15px;
                border-radius: 30px;
                font-size: 0.9rem;
            }

            .job-preview-meta-item i {
                color: #7C3AED;
                margin-right: 8px;
            }

            .job-preview-section-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
                position: relative;
                padding-left: 15px;
                border-left: 3px solid #7C3AED;
            }

            .job-preview-skills {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 15px;
            }

            .job-preview-skill {
                background: rgba(124, 58, 237, 0.1);
                color: #5B21B6;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 500;
            }

            .job-preview-list {
                list-style: none;
                padding: 0;
                margin: 15px 0 0;
            }

            .job-preview-list li {
                position: relative;
                padding-left: 25px;
                margin-bottom: 10px;
                line-height: 1.5;
            }

            .job-preview-list li:before {
                content: "•";
                color: #7C3AED;
                position: absolute;
                left: 0;
                font-weight: bold;
                font-size: 1.2em;
            }

            @media (max-width: 768px) {
                .preview-modal-content {
                    width: 95%;
                    margin: 5% auto;
                }

                .job-preview-header {
                    flex-direction: column;
                    align-items: flex-start;
                }

                .job-preview-meta {
                    gap: 10px;
                }

                .job-preview-meta-item {
                    padding: 6px 12px;
                    font-size: 0.8rem;
                }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(modal);

        // Ajouter le bouton d'aperçu s'il n'existe pas déjà
        const jobInfoContainer = document.getElementById('job-info-container');
        if (jobInfoContainer) {
            const jobActions = jobInfoContainer.querySelector('.job-actions');
            if (jobActions) {
                const exportButtonsContainer = jobActions.querySelector('.job-export-buttons');
                if (exportButtonsContainer) {
                    // Vérifier si le bouton existe déjà
                    if (!document.getElementById('preview-job-info')) {
                        const previewButton = document.createElement('button');
                        previewButton.id = 'preview-job-info';
                        previewButton.className = 'btn btn-outline';
                        previewButton.innerHTML = '<i class="fas fa-eye"></i> Aperçu';
                        
                        // Ajouter en première position
                        if (exportButtonsContainer.firstChild) {
                            exportButtonsContainer.insertBefore(previewButton, exportButtonsContainer.firstChild);
                        } else {
                            exportButtonsContainer.appendChild(previewButton);
                        }
                    }
                }
            }
        }
    }

    // Ajout des écouteurs d'événements
    addEventListeners() {
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.hideModal());
        }

        if (this.previewButton) {
            this.previewButton.addEventListener('click', () => this.showPreview());
        } else {
            // Observer pour attendre que le bouton soit ajouté au DOM
            const observer = new MutationObserver((mutations) => {
                for (let mutation of mutations) {
                    if (mutation.type === 'childList') {
                        const button = document.getElementById('preview-job-info');
                        if (button) {
                            button.addEventListener('click', () => this.showPreview());
                            observer.disconnect();
                            break;
                        }
                    }
                }
            });

            // Observer les changements dans le document
            observer.observe(document.body, { childList: true, subtree: true });
        }

        // Ajouter un gestionnaire pour fermer la modale si on clique en dehors
        window.addEventListener('click', (event) => {
            if (event.target === this.modal) {
                this.hideModal();
            }
        });
    }

    // Afficher la prévisualisation
    showPreview() {
        console.log('Tentative d\'affichage de la prévisualisation');
        
        if (!window.JobParserConnector || !window.JobParserConnector.cachedJobData) {
            console.log('Aucune donnée disponible pour la prévisualisation');
            if (window.showNotification) {
                window.showNotification('Aucune donnée de poste disponible pour la prévisualisation.', 'error');
            }
            return;
        }

        // Générer le contenu de la prévisualisation
        this.generatePreviewContent();

        // Afficher la modale
        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Empêcher le scroll de la page
    }

    // Masquer la modale
    hideModal() {
        this.modal.classList.remove('show');
        document.body.style.overflow = ''; // Restaurer le scroll
    }

    // Générer le contenu de la prévisualisation
    generatePreviewContent() {
        // Récupérer les données du poste
        const jobData = window.JobParserConnector ? 
                        (window.JobParserConnector.cachedJobData.data || window.JobParserConnector.cachedJobData) : null;
        
        console.log('Données du poste pour prévisualisation:', jobData);

        if (!jobData) {
            this.modalContent.innerHTML = '<p>Aucune donnée disponible</p>';
            return;
        }

        // Construire le contenu HTML
        let html = `
            <div class="job-preview-header">
                <div class="job-preview-company-info">
                    <h1 class="job-preview-title">${jobData.title || 'Poste non spécifié'}</h1>
                    <p class="job-preview-company">${jobData.company || document.getElementById('company-name')?.value || 'Entreprise'}</p>
                    <div class="job-preview-location">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${jobData.location || 'Lieu non spécifié'}</span>
                    </div>
                </div>
            </div>
            
            <div class="job-preview-meta">
                <div class="job-preview-meta-item">
                    <i class="fas fa-briefcase"></i>
                    <span>${jobData.contract_type || 'Type de contrat non spécifié'}</span>
                </div>
                <div class="job-preview-meta-item">
                    <i class="fas fa-user-clock"></i>
                    <span>${this.extractExperience(jobData) || 'Expérience non spécifiée'}</span>
                </div>
                <div class="job-preview-meta-item">
                    <i class="fas fa-money-bill-wave"></i>
                    <span>${jobData.salary || 'Salaire non spécifié'}</span>
                </div>
            </div>
        `;

        // Section des responsabilités
        if (jobData.responsibilities && jobData.responsibilities.length > 0) {
            html += `
                <div class="job-preview-section">
                    <h3 class="job-preview-section-title">Missions / Responsabilités</h3>
                    <ul class="job-preview-list">
                        ${jobData.responsibilities.map(resp => `<li>${resp}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Section des compétences
        const skills = [];
        if (jobData.required_skills && jobData.required_skills.length > 0) {
            skills.push(...jobData.required_skills);
        }
        if (jobData.preferred_skills && jobData.preferred_skills.length > 0) {
            skills.push(...jobData.preferred_skills);
        }

        if (skills.length > 0) {
            html += `
                <div class="job-preview-section">
                    <h3 class="job-preview-section-title">Compétences</h3>
                    <div class="job-preview-skills">
                        ${skills.map(skill => `<span class="job-preview-skill">${skill}</span>`).join('')}
                    </div>
                </div>
            `;
        }

        // Section des prérequis
        if (jobData.requirements && jobData.requirements.length > 0) {
            html += `
                <div class="job-preview-section">
                    <h3 class="job-preview-section-title">Prérequis</h3>
                    <ul class="job-preview-list">
                        ${jobData.requirements.map(req => `<li>${req}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Section des avantages
        if (jobData.benefits && jobData.benefits.length > 0) {
            html += `
                <div class="job-preview-section">
                    <h3 class="job-preview-section-title">Avantages</h3>
                    <ul class="job-preview-list">
                        ${jobData.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        // Mettre à jour le contenu de la modale
        this.modalContent.innerHTML = html;
    }

    // Extraire les informations sur l'expérience requise
    extractExperience(jobData) {
        if (jobData.experience) {
            return jobData.experience;
        }

        // Chercher dans les prérequis
        if (jobData.requirements && jobData.requirements.length > 0) {
            const expReq = jobData.requirements.find(req => 
                req.toLowerCase().includes('expérience') || 
                req.toLowerCase().includes('ans') ||
                req.toLowerCase().includes('experience')
            );

            if (expReq) {
                return expReq;
            }
        }

        return null;
    }
}

// Rendre la classe accessible globalement
window.JobPreview = JobPreview;

// Initialiser la prévisualisation lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    const jobPreview = new JobPreview();
});

// Initialiser immédiatement si le DOM est déjà chargé
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    const jobPreview = new JobPreview();
}