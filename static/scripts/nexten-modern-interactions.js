/**
 * NEXTEN V3.0 - Modern JavaScript Interactions
 * Système d'interactions modernes pour les étapes 3 & 4
 * Focus: Animations fluides, UX premium, accessibilité
 */

class NextenModernUI {
    constructor() {
        this.currentStep = 3;
        this.formData = {
            motivations: [],
            secteurs: [],
            salaire: 45000,
            aspirations: '',
            situation: '',
            disponibilite: '',
            modesTravail: [],
            typesEntreprise: [],
            contraintes: ''
        };
        this.init();
    }

    init() {
        console.log('🚀 Initialisation NEXTEN V3.0 Modern UI');
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupSalarySlider();
        this.setupFormValidation();
        this.setupAccessibility();
        this.loadSavedData();
    }

    setupEventListeners() {
        // Cards interactives pour motivations
        this.setupInteractiveCards('motivations', this.formData.motivations);
        
        // Cards interactives pour secteurs
        this.setupInteractiveCards('secteurs', this.formData.secteurs);
        
        // Options modernes pour situation
        this.setupModernOptions('situation', 'radio');
        
        // Options modernes pour disponibilité
        this.setupModernOptions('disponibilite', 'radio');
        
        // Options modernes pour modes de travail
        this.setupModernOptions('modes-travail', 'checkbox', this.formData.modesTravail);
        
        // Options modernes pour types d'entreprise
        this.setupModernOptions('types-entreprise', 'checkbox', this.formData.typesEntreprise);
        
        // Textarea avec auto-resize
        this.setupModernTextareas();
        
        // Navigation entre étapes
        this.setupStepNavigation();
        
        // Auto-save
        this.setupAutoSave();
    }

    setupInteractiveCards(name, dataArray) {
        const cards = document.querySelectorAll(`[data-card-group="${name}"]`);
        
        cards.forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleCard(card, name, dataArray);
            });
            
            // Animation au hover
            card.addEventListener('mouseenter', () => {
                if (!card.classList.contains('selected')) {
                    card.style.transform = 'translateY(-4px) scale(1.02)';
                }
            });
            
            card.addEventListener('mouseleave', () => {
                if (!card.classList.contains('selected')) {
                    card.style.transform = 'translateY(0) scale(1)';
                }
            });
            
            // Support clavier
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleCard(card, name, dataArray);
                }
            });
        });
    }

    toggleCard(card, groupName, dataArray) {
        const value = card.dataset.value;
        const isSelected = card.classList.contains('selected');
        
        if (isSelected) {
            // Déselectionner
            card.classList.remove('selected');
            const index = dataArray.indexOf(value);
            if (index > -1) {
                dataArray.splice(index, 1);
            }
            
            // Animation de déselection
            this.animateCardDeselection(card);
        } else {
            // Sélectionner
            card.classList.add('selected');
            dataArray.push(value);
            
            // Animation de sélection
            this.animateCardSelection(card);
        }
        
        // Mettre à jour les champs cachés
        this.updateHiddenFields(groupName, dataArray);
        
        // Valider le formulaire
        this.validateStep();
        
        // Auto-save
        this.saveFormData();
    }

    animateCardSelection(card) {
        // Animation de sélection avec spring effect
        card.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
        card.style.transform = 'translateY(-8px) scale(1.05)';
        
        // Ajouter l'icône de check avec animation
        const checkIcon = card.querySelector('.card-check');
        if (checkIcon) {
            checkIcon.style.opacity = '1';
            checkIcon.style.transform = 'scale(1.2)';
            
            setTimeout(() => {
                checkIcon.style.transform = 'scale(1)';
            }, 200);
        }
        
        // Retour à la normale après animation
        setTimeout(() => {
            card.style.transform = 'translateY(-2px) scale(1.02)';
        }, 300);
        
        // Effet de particules (optionnel)
        this.createSelectionParticles(card);
    }

    animateCardDeselection(card) {
        card.style.transition = 'all 0.2s ease-out';
        card.style.transform = 'translateY(0) scale(1)';
        
        const checkIcon = card.querySelector('.card-check');
        if (checkIcon) {
            checkIcon.style.opacity = '0';
            checkIcon.style.transform = 'scale(0.8)';
        }
    }

    createSelectionParticles(card) {
        // Effet de particules léger pour la sélection
        const rect = card.getBoundingClientRect();
        
        for (let i = 0; i < 6; i++) {
            const particle = document.createElement('div');
            particle.style.position = 'fixed';
            particle.style.width = '4px';
            particle.style.height = '4px';
            particle.style.background = '#7c3aed';
            particle.style.borderRadius = '50%';
            particle.style.pointerEvents = 'none';
            particle.style.zIndex = '9999';
            particle.style.left = (rect.left + rect.width/2) + 'px';
            particle.style.top = (rect.top + rect.height/2) + 'px';
            
            document.body.appendChild(particle);
            
            // Animation des particules
            const angle = (i / 6) * Math.PI * 2;
            const distance = 30 + Math.random() * 20;
            const duration = 500 + Math.random() * 300;
            
            particle.animate([
                { 
                    transform: 'translate(0, 0) scale(1)',
                    opacity: 1
                },
                { 
                    transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0)`,
                    opacity: 0
                }
            ], {
                duration: duration,
                easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
            }).onfinish = () => {
                particle.remove();
            };
        }
    }

    setupModernOptions(name, type, dataArray = null) {
        const options = document.querySelectorAll(`[data-option-group="${name}"]`);
        
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleOptionSelection(option, name, type, dataArray);
            });
            
            // Accessibilité clavier
            option.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleOptionSelection(option, name, type, dataArray);
                }
            });
        });
    }

    handleOptionSelection(option, groupName, type, dataArray) {
        const value = option.dataset.value;
        
        if (type === 'radio') {
            // Déselectionner toutes les autres options du groupe
            const allOptions = document.querySelectorAll(`[data-option-group="${groupName}"]`);
            allOptions.forEach(opt => {
                opt.classList.remove('selected');
                this.animateOptionDeselection(opt);
            });
            
            // Sélectionner l'option actuelle
            option.classList.add('selected');
            this.animateOptionSelection(option);
            this.formData[groupName] = value;
            
        } else if (type === 'checkbox' && dataArray) {
            const isSelected = option.classList.contains('selected');
            
            if (isSelected) {
                option.classList.remove('selected');
                this.animateOptionDeselection(option);
                const index = dataArray.indexOf(value);
                if (index > -1) {
                    dataArray.splice(index, 1);
                }
            } else {
                option.classList.add('selected');
                this.animateOptionSelection(option);
                dataArray.push(value);
            }
        }
        
        this.updateHiddenFields(groupName, dataArray || this.formData[groupName]);
        this.validateStep();
        this.saveFormData();
    }

    animateOptionSelection(option) {
        const input = option.querySelector('.option-input');
        if (input) {
            input.style.transform = 'scale(1.1)';
            input.style.borderColor = '#7c3aed';
            
            setTimeout(() => {
                input.style.transform = 'scale(1)';
            }, 150);
        }
        
        // Effet de ripple
        this.createRippleEffect(option);
    }

    animateOptionDeselection(option) {
        const input = option.querySelector('.option-input');
        if (input) {
            input.style.transform = 'scale(0.95)';
            input.style.borderColor = '#e2e8f0';
            
            setTimeout(() => {
                input.style.transform = 'scale(1)';
            }, 150);
        }
    }

    createRippleEffect(element) {
        const ripple = document.createElement('div');
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(124, 58, 237, 0.3)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s linear';
        ripple.style.left = '50%';
        ripple.style.top = '50%';
        ripple.style.width = '100px';
        ripple.style.height = '100px';
        ripple.style.marginLeft = '-50px';
        ripple.style.marginTop = '-50px';
        ripple.style.pointerEvents = 'none';
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    setupSalarySlider() {
        const slider = document.getElementById('salary-range');
        const display = document.getElementById('salary-display');
        
        if (slider && display) {
            // Mise à jour en temps réel
            slider.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                this.updateSalaryDisplay(value, display);
                this.formData.salaire = value;
                this.saveFormData();
            });
            
            // Animation au survol
            slider.addEventListener('mouseenter', () => {
                slider.style.transform = 'scaleY(1.2)';
            });
            
            slider.addEventListener('mouseleave', () => {
                slider.style.transform = 'scaleY(1)';
            });
            
            // Initialiser l'affichage
            this.updateSalaryDisplay(slider.value, display);
        }
    }

    updateSalaryDisplay(value, display) {
        const formatted = this.formatSalary(value);
        display.textContent = formatted;
        
        // Animation du changement de valeur
        display.style.transform = 'scale(1.1)';
        setTimeout(() => {
            display.style.transform = 'scale(1)';
        }, 150);
        
        // Mise à jour de la couleur selon la valeur
        const percentage = (value - 25000) / (120000 - 25000);
        const hue = percentage * 120; // De rouge (0) à vert (120)
        display.style.background = `hsl(${hue}, 70%, 50%)`;
    }

    formatSalary(value) {
        if (value >= 120000) {
            return '120K €+';
        }
        return `${(value / 1000).toFixed(0)}K €`;
    }

    setupModernTextareas() {
        const textareas = document.querySelectorAll('.modern-textarea');
        
        textareas.forEach(textarea => {
            // Auto-resize
            textarea.addEventListener('input', () => {
                this.autoResizeTextarea(textarea);
                
                // Sauvegarder dans formData
                if (textarea.id === 'aspirations') {
                    this.formData.aspirations = textarea.value;
                } else if (textarea.id === 'contraintes') {
                    this.formData.contraintes = textarea.value;
                }
                
                this.saveFormData();
            });
            
            // Animations focus/blur
            textarea.addEventListener('focus', () => {
                textarea.parentElement.classList.add('focused');
            });
            
            textarea.addEventListener('blur', () => {
                textarea.parentElement.classList.remove('focused');
            });
            
            // Initialiser la taille
            this.autoResizeTextarea(textarea);
        });
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.max(120, textarea.scrollHeight) + 'px';
    }

    setupStepNavigation() {
        // Bouton Retour Step 3
        const backBtn3 = document.getElementById('back-step2');
        if (backBtn3) {
            backBtn3.addEventListener('click', () => {
                this.navigateToStep(2);
            });
        }
        
        // Bouton Suivant Step 3
        const nextBtn3 = document.getElementById('next-step3');
        if (nextBtn3) {
            nextBtn3.addEventListener('click', () => {
                if (this.validateStep3()) {
                    this.navigateToStep(4);
                }
            });
        }
        
        // Bouton Retour Step 4
        const backBtn4 = document.getElementById('back-step3');
        if (backBtn4) {
            backBtn4.addEventListener('click', () => {
                this.navigateToStep(3);
            });
        }
        
        // Bouton Submit Step 4
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => {
                if (this.validateStep4()) {
                    this.submitForm();
                }
            });
        }
    }

    navigateToStep(stepNumber) {
        console.log(`🔄 Navigation vers étape ${stepNumber}`);
        
        // Animation de sortie de l'étape actuelle
        const currentStepEl = document.getElementById(`form-step${this.currentStep}`);
        if (currentStepEl) {
            currentStepEl.style.opacity = '0';
            currentStepEl.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                currentStepEl.style.display = 'none';
                this.showStep(stepNumber);
            }, 300);
        }
        
        this.currentStep = stepNumber;
        this.updateStepper();
        
        // Utiliser la fonction globale si disponible
        if (typeof window.goToStep === 'function') {
            window.goToStep(stepNumber);
        }
    }

    showStep(stepNumber) {
        const stepEl = document.getElementById(`form-step${stepNumber}`);
        if (stepEl) {
            stepEl.style.display = 'block';
            stepEl.style.opacity = '0';
            stepEl.style.transform = 'translateX(20px)';
            
            // Animation d'entrée
            setTimeout(() => {
                stepEl.style.opacity = '1';
                stepEl.style.transform = 'translateX(0)';
            }, 50);
        }
    }

    updateStepper() {
        // Mettre à jour l'indicateur de progression global
        const progressBar = document.querySelector('.stepper-progress, #stepper-progress');
        if (progressBar) {
            const percentage = ((this.currentStep - 1) / 3) * 100;
            progressBar.style.width = `${percentage}%`;
        }
        
        // Mettre à jour les étapes
        const steps = document.querySelectorAll('.step, .step-item');
        steps.forEach((step, index) => {
            const stepNum = index + 1;
            
            if (stepNum < this.currentStep) {
                step.classList.add('completed');
                step.classList.remove('active');
            } else if (stepNum === this.currentStep) {
                step.classList.add('active');
                step.classList.remove('completed');
            } else {
                step.classList.remove('active', 'completed');
            }
        });
    }

    validateStep3() {
        let isValid = true;
        
        // Vérifier qu'au moins une motivation est sélectionnée
        if (this.formData.motivations.length === 0) {
            this.showValidationError('Veuillez sélectionner au moins une motivation professionnelle');
            isValid = false;
        }
        
        // Vérifier qu'au moins un secteur est sélectionné
        if (this.formData.secteurs.length === 0) {
            this.showValidationError('Veuillez sélectionner au moins un secteur d\'intérêt');
            isValid = false;
        }
        
        return isValid;
    }

    validateStep4() {
        let isValid = true;
        
        // Vérifier que la situation est sélectionnée
        if (!this.formData.situation) {
            this.showValidationError('Veuillez indiquer votre situation professionnelle actuelle');
            isValid = false;
        }
        
        // Vérifier que la disponibilité est sélectionnée
        if (!this.formData.disponibilite) {
            this.showValidationError('Veuillez indiquer votre disponibilité');
            isValid = false;
        }
        
        return isValid;
    }

    showValidationError(message) {
        // Supprimer les messages précédents
        const existingError = document.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Créer le nouveau message d'erreur
        const errorEl = document.createElement('div');
        errorEl.className = 'validation-error';
        errorEl.style.cssText = `
            background: #fee2e2;
            border: 1px solid #fecaca;
            color: #dc2626;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 16px 0;
            display: flex;
            align-items: center;
            gap: 8px;
            animation: shake 0.5s ease-in-out;
        `;
        
        errorEl.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
        `;
        
        // Insérer le message avant les boutons d'action
        const actionsEl = document.querySelector('.modern-form-actions, .form-actions');
        if (actionsEl) {
            actionsEl.parentNode.insertBefore(errorEl, actionsEl);
            
            // Scroll vers l'erreur
            errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Supprimer après 5 secondes
            setTimeout(() => {
                errorEl.remove();
            }, 5000);
        }
    }

    setupAutoSave() {
        // Sauvegarder automatiquement toutes les 3 secondes
        setInterval(() => {
            this.saveFormData();
        }, 3000);
    }

    saveFormData() {
        try {
            const dataToSave = {
                ...this.formData,
                lastSaved: new Date().toISOString(),
                version: '3.0'
            };
            localStorage.setItem('nexten_form_step3_4_v3', JSON.stringify(dataToSave));
            console.log('💾 Données sauvegardées NEXTEN V3.0:', dataToSave);
        } catch (error) {
            console.error('❌ Erreur sauvegarde:', error);
        }
    }

    loadSavedData() {
        try {
            const saved = localStorage.getItem('nexten_form_step3_4_v3');
            if (saved) {
                const savedData = JSON.parse(saved);
                this.formData = { ...this.formData, ...savedData };
                
                // Attendre que le DOM soit prêt avant de restaurer
                setTimeout(() => {
                    this.restoreFormState();
                }, 500);
                
                console.log('📂 Données restaurées NEXTEN V3.0:', this.formData);
            }
        } catch (error) {
            console.error('❌ Erreur restauration:', error);
        }
    }

    restoreFormState() {
        // Restaurer les sélections de motivations
        this.formData.motivations.forEach(value => {
            const card = document.querySelector(`[data-card-group="motivations"][data-value="${value}"]`);
            if (card) {
                card.classList.add('selected');
            }
        });
        
        // Restaurer les sélections de secteurs
        this.formData.secteurs.forEach(value => {
            const card = document.querySelector(`[data-card-group="secteurs"][data-value="${value}"]`);
            if (card) {
                card.classList.add('selected');
            }
        });
        
        // Restaurer le slider de salaire
        const slider = document.getElementById('salary-range');
        const display = document.getElementById('salary-display');
        if (slider && this.formData.salaire) {
            slider.value = this.formData.salaire;
            if (display) {
                this.updateSalaryDisplay(this.formData.salaire, display);
            }
        }
        
        // Restaurer les textareas
        const aspirations = document.getElementById('aspirations');
        if (aspirations && this.formData.aspirations) {
            aspirations.value = this.formData.aspirations;
            this.autoResizeTextarea(aspirations);
        }
        
        const contraintes = document.getElementById('contraintes');
        if (contraintes && this.formData.contraintes) {
            contraintes.value = this.formData.contraintes;
            this.autoResizeTextarea(contraintes);
        }
        
        // Restaurer les options radio
        if (this.formData.situation) {
            const option = document.querySelector(`[data-option-group="situation"][data-value="${this.formData.situation}"]`);
            if (option) {
                option.classList.add('selected');
            }
        }
        
        if (this.formData.disponibilite) {
            const option = document.querySelector(`[data-option-group="disponibilite"][data-value="${this.formData.disponibilite}"]`);
            if (option) {
                option.classList.add('selected');
            }
        }
        
        // Restaurer les checkboxes
        this.formData.modesTravail.forEach(value => {
            const option = document.querySelector(`[data-option-group="modes-travail"][data-value="${value}"]`);
            if (option) {
                option.classList.add('selected');
            }
        });
        
        this.formData.typesEntreprise.forEach(value => {
            const option = document.querySelector(`[data-option-group="types-entreprise"][data-value="${value}"]`);
            if (option) {
                option.classList.add('selected');
            }
        });
    }

    updateHiddenFields(groupName, data) {
        // Mettre à jour les champs cachés pour l'intégration backend
        const hiddenField = document.getElementById(`hidden-${groupName}`);
        if (hiddenField) {
            hiddenField.value = Array.isArray(data) ? data.join(',') : data;
        }
        
        // Aussi mettre à jour les anciens champs si ils existent
        const legacyFields = document.querySelectorAll(`input[name="${groupName}"]`);
        legacyFields.forEach(field => {
            if (field.type === 'hidden') {
                field.value = Array.isArray(data) ? data.join(',') : data;
            }
        });
    }

    submitForm() {
        console.log('📤 Soumission du formulaire NEXTEN V3.0:', this.formData);
        
        // Animation de soumission
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Traitement en cours...</span>';
            submitBtn.disabled = true;
        }
        
        // Créer l'écran de chargement
        this.showLoadingOverlay();
        
        // Simuler l'envoi (remplacer par votre logique backend)
        setTimeout(() => {
            this.showSuccessMessage();
            localStorage.removeItem('nexten_form_step3_4_v3');
        }, 2000);
    }

    showLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'nexten-loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(124, 58, 237, 0.95);
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            color: white;
            font-family: Inter, sans-serif;
        `;
        
        overlay.innerHTML = `
            <div style="width: 60px; height: 60px; border: 4px solid rgba(255,255,255,0.3); border-top: 4px solid white; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 24px;"></div>
            <h3 style="margin: 0 0 12px 0; font-size: 1.5rem; font-weight: 600;">Finalisation de votre profil</h3>
            <p style="margin: 0; opacity: 0.8; text-align: center; max-width: 400px;">Nous analysons vos réponses pour créer votre profil candidat personnalisé...</p>
        `;
        
        document.body.appendChild(overlay);
        
        // Animation d'apparition
        overlay.style.opacity = '0';
        setTimeout(() => {
            overlay.style.opacity = '1';
        }, 10);
    }

    showSuccessMessage() {
        const overlay = document.querySelector('.nexten-loading-overlay');
        if (overlay) {
            overlay.remove();
        }
        
        const successEl = document.createElement('div');
        successEl.className = 'nexten-success-overlay';
        successEl.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, #10b981, #059669);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            color: white;
            text-align: center;
            padding: 20px;
            font-family: Inter, sans-serif;
        `;
        
        successEl.innerHTML = `
            <div style="width: 80px; height: 80px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 24px;">
                <i class="fas fa-check" style="font-size: 2.5rem;"></i>
            </div>
            <h2 style="margin: 0 0 16px 0; font-size: 2.5rem; font-weight: 700;">Questionnaire envoyé !</h2>
            <p style="margin: 0 0 24px 0; font-size: 1.25rem; opacity: 0.9; max-width: 500px; line-height: 1.6;">
                Merci pour votre temps ! Nous analysons votre profil et vous recontacterons très prochainement avec des opportunités personnalisées.
            </p>
            <div style="background: rgba(255,255,255,0.1); padding: 16px 24px; border-radius: 12px; margin-top: 20px;">
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">
                    <i class="fas fa-clock"></i> Temps de réponse moyen : 24-48h
                </p>
            </div>
        `;
        
        document.body.appendChild(successEl);
        
        // Redirection après 5 secondes
        setTimeout(() => {
            window.location.href = 'https://bapt252.github.io/Commitment-/templates/index.html';
        }, 5000);
    }

    initializeAnimations() {
        // Observer pour animer les éléments lors du scroll
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        }, { threshold: 0.1 });
        
        // Observer tous les éléments animables
        setTimeout(() => {
            document.querySelectorAll('.interactive-card, .modern-option, .modern-slider-container').forEach(el => {
                observer.observe(el);
            });
        }, 100);
    }

    setupAccessibility() {
        // Améliorer l'accessibilité clavier
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
        
        // Annoncer les changements pour les lecteurs d'écran
        this.setupAriaLiveRegion();
    }

    setupAriaLiveRegion() {
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.cssText = 'position: absolute; left: -10000px; width: 1px; height: 1px; overflow: hidden;';
        liveRegion.id = 'aria-live-region';
        document.body.appendChild(liveRegion);
    }

    announceForScreenReader(message) {
        const liveRegion = document.getElementById('aria-live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
        }
    }

    validateStep() {
        // Validation générale
        const currentStepEl = document.getElementById(`form-step${this.currentStep}`);
        if (currentStepEl) {
            currentStepEl.classList.add('validated');
        }
        
        // Mise à jour des compteurs
        this.updateSelectionCounters();
    }

    updateSelectionCounters() {
        // Afficher des compteurs de sélection si nécessaire
        const motivationCount = this.formData.motivations.length;
        const secteurCount = this.formData.secteurs.length;
        
        console.log(`📊 Sélections actuelles: ${motivationCount} motivations, ${secteurCount} secteurs`);
    }

    // Méthode pour exposer les données (debugging)
    getFormData() {
        return { ...this.formData };
    }

    // Méthode pour reset complet
    resetForm() {
        this.formData = {
            motivations: [],
            secteurs: [],
            salaire: 45000,
            aspirations: '',
            situation: '',
            disponibilite: '',
            modesTravail: [],
            typesEntreprise: [],
            contraintes: ''
        };
        
        localStorage.removeItem('nexten_form_step3_4_v3');
        location.reload();
    }
}

// CSS pour les animations supplémentaires
const modernAnimationStyles = `
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

.keyboard-navigation *:focus {
    outline: 2px solid #7c3aed !important;
    outline-offset: 2px !important;
}
`;

// Injecter les styles d'animation
const modernStyleEl = document.createElement('style');
modernStyleEl.textContent = modernAnimationStyles;
document.head.appendChild(modernStyleEl);

// Initialiser l'interface moderne quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    // Délai pour laisser le temps aux autres scripts de se charger
    setTimeout(() => {
        window.nextenModernUI = new NextenModernUI();
        
        // Exposer pour debugging
        window.NextenModernUI = NextenModernUI;
        
        console.log('✅ NEXTEN V3.0 Modern UI initialisé avec succès');
        console.log('🎛️ Commandes debug disponibles:');
        console.log('   - nextenModernUI.getFormData() - Voir les données');
        console.log('   - nextenModernUI.navigateToStep(4) - Aller à l\'étape 4');
        console.log('   - nextenModernUI.resetForm() - Reset complet');
    }, 1000);
});

// Exportation pour utilisation externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenModernUI;
}

console.log('🚀 NEXTEN V3.0 - Script d\'interactions modernes chargé');