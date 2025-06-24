// Questionnaire Navigation Script
// Gère la navigation entre les étapes du questionnaire client

class QuestionnaireNavigation {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.sections = document.querySelectorAll('.form-section');
        this.steps = document.querySelectorAll('.step');
        this.progressFill = document.getElementById('progress-fill');
        
        this.init();
    }
    
    init() {
        // Attacher les event listeners aux boutons de navigation
        this.attachEventListeners();
        
        // Initialiser l'affichage
        this.updateDisplay();
        
        console.log('✅ Navigation du questionnaire initialisée');
    }
    
    attachEventListeners() {
        // Boutons "Continuer" (next-step)
        const nextButtons = document.querySelectorAll('.next-step');
        nextButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const targetStep = parseInt(button.getAttribute('data-step'));
                
                // Valider l'étape actuelle avant de continuer
                if (this.validateCurrentStep()) {
                    this.goToStep(targetStep);
                }
            });
        });
        
        // Boutons "Précédent" (prev-step)  
        const prevButtons = document.querySelectorAll('.prev-step');
        prevButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const targetStep = parseInt(button.getAttribute('data-step'));
                this.goToStep(targetStep);
            });
        });
        
        // Navigation par clic sur les étapes (si autorisée)
        this.steps.forEach((step, index) => {
            step.addEventListener('click', () => {
                const stepNumber = index + 1;
                // Permettre seulement d'aller aux étapes déjà visitées ou suivante
                if (stepNumber <= this.currentStep + 1) {
                    this.goToStep(stepNumber);
                }
            });
        });
        
        // Gestion du formulaire de soumission
        const form = document.getElementById('client-questionnaire-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitForm();
            });
        }
    }
    
    goToStep(stepNumber) {
        if (stepNumber < 1 || stepNumber > this.totalSteps) {
            console.warn(`Étape ${stepNumber} invalide`);
            return;
        }
        
        console.log(`Navigation de l'étape ${this.currentStep} vers l'étape ${stepNumber}`);
        
        // Mettre à jour l'étape actuelle
        this.currentStep = stepNumber;
        
        // Mettre à jour l'affichage
        this.updateDisplay();
        
        // Animer la transition
        this.animateTransition();
        
        // Scroller vers le haut
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    updateDisplay() {
        // Mettre à jour les sections du formulaire
        this.sections.forEach(section => {
            const sectionStep = parseInt(section.getAttribute('data-step'));
            
            if (sectionStep === this.currentStep) {
                section.classList.add('active');
                section.style.display = 'block';
            } else {
                section.classList.remove('active');
                section.style.display = 'none';
            }
        });
        
        // Mettre à jour l'indicateur de progression
        this.updateStepIndicator();
        
        // Mettre à jour la barre de progression
        this.updateProgressBar();
        
        // Gérer les sections conditionnelles
        this.handleConditionalSections();
    }
    
    updateStepIndicator() {
        this.steps.forEach((step, index) => {
            const stepNumber = index + 1;
            
            // Supprimer toutes les classes
            step.classList.remove('active', 'completed');
            
            if (stepNumber < this.currentStep) {
                // Étapes complétées
                step.classList.add('completed');
                const bubble = step.querySelector('.step-bubble span');
                if (bubble) bubble.textContent = '✓';
            } else if (stepNumber === this.currentStep) {
                // Étape actuelle
                step.classList.add('active');
                const bubble = step.querySelector('.step-bubble span');
                if (bubble) bubble.textContent = stepNumber;
            } else {
                // Étapes futures
                const bubble = step.querySelector('.step-bubble span');
                if (bubble) bubble.textContent = stepNumber;
            }
        });
    }
    
    updateProgressBar() {
        if (this.progressFill) {
            const progress = ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
            this.progressFill.style.width = `${progress}%`;
        }
    }
    
    animateTransition() {
        const activeSection = document.querySelector('.form-section.active');
        if (activeSection) {
            activeSection.style.opacity = '0';
            activeSection.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                activeSection.style.opacity = '1';
                activeSection.style.transform = 'translateY(0)';
            }, 100);
        }
    }
    
    validateCurrentStep() {
        const currentSection = document.querySelector(`.form-section[data-step="${this.currentStep}"]`);
        if (!currentSection) return true;
        
        // Validation de l'étape 1 - Informations structure
        if (this.currentStep === 1) {
            const companyName = document.getElementById('company-name');
            const companyAddress = document.getElementById('company-address');
            
            if (companyName && !companyName.value.trim()) {
                this.showNotification('error', 'Nom de structure requis', 'Veuillez renseigner le nom de votre structure.');
                companyName.focus();
                return false;
            }
            
            if (companyAddress && !companyAddress.value.trim()) {
                this.showNotification('error', 'Adresse requise', 'Veuillez renseigner l\'adresse de votre structure.');
                companyAddress.focus();
                return false;
            }
        }
        
        // Validation de l'étape 2 - Contact (optionnel mais recommandé)
        if (this.currentStep === 2) {
            const contactEmail = document.getElementById('contact-email');
            
            if (contactEmail && contactEmail.value.trim()) {
                // Validation basique de l'email si renseigné
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(contactEmail.value.trim())) {
                    this.showNotification('error', 'Email invalide', 'Veuillez renseigner une adresse email valide.');
                    contactEmail.focus();
                    return false;
                }
            }
        }
        
        return true;
    }
    
    handleConditionalSections() {
        // Gérer l'affichage conditionnel des sections selon les réponses
        if (this.currentStep === 3) {
            const recruitmentYes = document.getElementById('recruitment-yes');
            const recruitmentNo = document.getElementById('recruitment-no');
            const jobParsingSection = document.getElementById('job-parsing-section');
            
            if (recruitmentYes && recruitmentNo && jobParsingSection) {
                // Écouter les changements sur les boutons radio
                [recruitmentYes, recruitmentNo].forEach(radio => {
                    radio.addEventListener('change', () => {
                        if (recruitmentYes.checked) {
                            jobParsingSection.classList.add('active');
                            jobParsingSection.style.display = 'block';
                        } else {
                            jobParsingSection.classList.remove('active');
                            jobParsingSection.style.display = 'none';
                        }
                    });
                });
                
                // Vérifier l'état initial
                if (recruitmentYes.checked) {
                    jobParsingSection.classList.add('active');
                    jobParsingSection.style.display = 'block';
                } else if (recruitmentNo.checked) {
                    jobParsingSection.classList.remove('active');
                    jobParsingSection.style.display = 'none';
                }
            }
        }
        
        // Générer le récapitulatif à l'étape 4
        if (this.currentStep === 4) {
            this.generateSummary();
        }
    }
    
    generateSummary() {
        const summaryContent = document.getElementById('summary-content');
        if (!summaryContent) return;
        
        let html = '';
        
        // Informations structure
        const companyName = document.getElementById('company-name')?.value || 'Non renseigné';
        const companyAddress = document.getElementById('company-address')?.value || 'Non renseigné';
        const companyWebsite = document.getElementById('company-website')?.value || 'Non renseigné';
        const companySize = document.getElementById('company-size')?.value || 'Non renseigné';
        
        html += `
            <div class="summary-section">
                <h4><i class="fas fa-building"></i> Structure</h4>
                <p><strong>Nom :</strong> ${companyName}</p>
                <p><strong>Adresse :</strong> ${companyAddress}</p>
                <p><strong>Site web :</strong> ${companyWebsite}</p>
                <p><strong>Taille :</strong> ${companySize}</p>
            </div>
        `;
        
        // Informations contact
        const contactName = document.getElementById('contact-name')?.value || 'Non renseigné';
        const contactEmail = document.getElementById('contact-email')?.value || 'Non renseigné';
        const contactPhone = document.getElementById('contact-phone')?.value || 'Non renseigné';
        
        html += `
            <div class="summary-section">
                <h4><i class="fas fa-user"></i> Contact</h4>
                <p><strong>Nom :</strong> ${contactName}</p>
                <p><strong>Email :</strong> ${contactEmail}</p>
                <p><strong>Téléphone :</strong> ${contactPhone}</p>
            </div>
        `;
        
        // Informations recrutement
        const recruitmentNeed = document.querySelector('input[name="recruitment-need"]:checked')?.value;
        if (recruitmentNeed === 'yes') {
            html += `
                <div class="summary-section">
                    <h4><i class="fas fa-user-plus"></i> Recrutement</h4>
                    <p><strong>Besoin de recrutement :</strong> Oui</p>
                </div>
            `;
        } else if (recruitmentNeed === 'no') {
            html += `
                <div class="summary-section">
                    <h4><i class="fas fa-user-plus"></i> Recrutement</h4>
                    <p><strong>Besoin de recrutement :</strong> Non</p>
                </div>
            `;
        }
        
        summaryContent.innerHTML = html;
    }
    
    submitForm() {
        console.log('Soumission du formulaire...');
        
        // Collecter toutes les données
        const formData = this.collectFormData();
        
        // Afficher une notification de succès
        this.showNotification('success', 'Formulaire envoyé !', 'Merci pour vos informations. Nous vous contacterons bientôt.');
        
        // Ici vous pouvez ajouter l'envoi vers votre backend
        // fetch('/api/submit-questionnaire', { method: 'POST', body: JSON.stringify(formData) })
        
        console.log('Données collectées:', formData);
    }
    
    collectFormData() {
        const data = {};
        
        // Collecter tous les champs du formulaire
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === 'radio') {
                if (input.checked) {
                    data[input.name] = input.value;
                }
            } else if (input.type === 'checkbox') {
                if (input.checked) {
                    data[input.id] = true;
                }
            } else {
                data[input.id] = input.value;
            }
        });
        
        return data;
    }
    
    showNotification(type, title, message) {
        // Créer ou réutiliser la notification
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.className = 'notification';
            document.body.appendChild(notification);
        }
        
        // Définir le contenu
        notification.className = `notification ${type}`;
        
        let icon = 'fas fa-info-circle';
        if (type === 'success') icon = 'fas fa-check-circle';
        if (type === 'error') icon = 'fas fa-exclamation-circle';
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="${icon}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <div class="notification-close">
                <i class="fas fa-times"></i>
            </div>
        `;
        
        // Afficher la notification
        notification.style.display = 'flex';
        
        // Gérer la fermeture
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.style.display = 'none';
        });
        
        // Auto-fermeture après 5 secondes
        setTimeout(() => {
            if (notification.style.display !== 'none') {
                notification.style.display = 'none';
            }
        }, 5000);
    }
}

// Initialiser la navigation quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    // Attendre un court délai pour s'assurer que tous les éléments sont chargés
    setTimeout(() => {
        window.questionnaireNav = new QuestionnaireNavigation();
    }, 100);
});

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuestionnaireNavigation;
}