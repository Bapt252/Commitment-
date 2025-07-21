// ===== CORRECTION COMPLÈTE ÉTAPE 4 - DISPONIBILITÉ & SITUATION =====
// Fichier de correction pour l'étape 4 du questionnaire candidat
// 🚀 Disponibilité | 💼 Situation | ✅ Finalisation
// Version: 1.0 - Correction complète et intégration

console.log('🚀 Chargement des corrections étape 4...');

// ===== SYSTÈME PRINCIPAL ÉTAPE 4 =====
window.step4System = {
    formData: {
        timing: null,
        employmentStatus: null,
        currentSalaryMin: null,
        currentSalaryMax: null,
        listeningReasons: [],
        unemploymentDuration: null,
        lastSalary: null,
        availabilityConstraints: [],
        workPreferences: [],
        relocationAccepted: null,
        additionalInfo: ''
    },

    init() {
        console.log('🔧 Initialisation système étape 4...');
        
        // Vérifier et compléter le HTML si nécessaire
        this.ensureStep4HTML();
        
        // Initialiser les événements
        this.setupEventListeners();
        
        // Préremplir avec des données de démo si en mode démo
        this.setupDemoData();
        
        console.log('✅ Système étape 4 initialisé');
    },

    ensureStep4HTML() {
        const step4Container = document.getElementById('form-step4');
        
        if (!step4Container) {
            console.error('❌ Container étape 4 non trouvé');
            return;
        }

        // Vérifier si le contenu de l'étape 4 est complet
        const existingContent = step4Container.innerHTML;
        if (!existingContent.includes('Quand cherchez-vous à prendre un poste')) {
            console.log('🔨 Reconstruction du HTML de l\'étape 4...');
            this.injectStep4HTML();
        } else {
            console.log('✅ HTML étape 4 déjà complet');
        }
    },

    injectStep4HTML() {
        const step4Container = document.getElementById('form-step4');
        if (!step4Container) return;

        const htmlContent = `
            <h2 class="form-section-title">🚀 Disponibilité & Situation</h2>
            <p class="step-description">
                Dernière étape ! Précisez votre situation actuelle et vos attentes pour finaliser votre profil candidat
            </p>

            <!-- Question 1: Quand cherchez-vous à prendre un poste ? -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-calendar-check"></i>
                        1) Quand cherchez-vous à prendre un poste ?
                    </h3>
                    
                    <div class="step4-options" id="timing-options">
                        <div class="step4-option" data-value="immediat" data-question="timing">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Immédiatement</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="1mois" data-question="timing">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Dans 1 mois</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="2mois" data-question="timing">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Dans 2 mois</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="3mois" data-question="timing">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Dans 3 mois ou plus</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 2: Êtes-vous actuellement en poste ? -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-briefcase"></i>
                        2) Êtes-vous actuellement en poste ?
                    </h3>
                    
                    <div class="step4-options" id="employment-status-options">
                        <div class="step4-option" data-value="oui" data-question="employment-status">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">OUI - Je suis actuellement en poste</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="non" data-question="employment-status">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">NON - Je recherche activement un emploi</div>
                            </div>
                        </div>
                    </div>

                    <!-- Section conditionnelle pour "OUI" -->
                    <div class="conditional-section" id="employment-yes-section">
                        <div class="conditional-section-title">
                            <i class="fas fa-arrow-right"></i>
                            Questions complémentaires pour les personnes en poste
                        </div>
                        
                        <!-- Salaire actuel -->
                        <div class="step4-input-group">
                            <label class="step4-input-label">
                                Votre salaire actuel (fourchette brute annuelle) :
                            </label>
                            <div class="salary-range-input">
                                <input type="number" class="salary-input-small" id="current-salary-min" 
                                       name="current-salary-min" placeholder="40" min="20" max="200">
                                <span class="salary-separator">K -</span>
                                <input type="number" class="salary-input-small" id="current-salary-max" 
                                       name="current-salary-max" placeholder="45" min="20" max="200">
                                <span class="salary-unit-small">K €</span>
                            </div>
                        </div>
                        
                        <!-- Pourquoi à l'écoute -->
                        <div class="step4-input-group">
                            <label class="step4-input-label">
                                Pourquoi êtes-vous de nouveau à l'écoute ? (plusieurs choix possibles)
                            </label>
                            <div class="step4-checkbox-group" id="listening-reasons">
                                <div class="step4-checkbox-option" data-value="evolution">
                                    <div class="step4-checkbox">
                                        <i class="fas fa-check"></i>
                                    </div>
                                    <div class="step4-checkbox-text">Manque de perspectives d'évolution</div>
                                </div>
                                <div class="step4-checkbox-option" data-value="remuneration">
                                    <div class="step4-checkbox">
                                        <i class="fas fa-check"></i>
                                    </div>
                                    <div class="step4-checkbox-text">Rémunération trop faible</div>
                                </div>
                                <div class="step4-checkbox-option" data-value="distance">
                                    <div class="step4-checkbox">
                                        <i class="fas fa-check"></i>
                                    </div>
                                    <div class="step4-checkbox-text">Poste trop loin de mon domicile</div>
                                </div>
                                <div class="step4-checkbox-option" data-value="flexibilite">
                                    <div class="step4-checkbox">
                                        <i class="fas fa-check"></i>
                                    </div>
                                    <div class="step4-checkbox-text">Manque de flexibilité (télétravail, horaires)</div>
                                </div>
                                <div class="step4-checkbox-option" data-value="ambiance">
                                    <div class="step4-checkbox">
                                        <i class="fas fa-check"></i>
                                    </div>
                                    <div class="step4-checkbox-text">Ambiance de travail difficile</div>
                                </div>
                                <div class="step4-checkbox-option" data-value="defis">
                                    <div class="step4-checkbox">
                                        <i class="fas fa-check"></i>
                                    </div>
                                    <div class="step4-checkbox-text">Manque de défis professionnels</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Section conditionnelle pour "NON" -->
                    <div class="conditional-section" id="employment-no-section">
                        <div class="conditional-section-title">
                            <i class="fas fa-arrow-right"></i>
                            Questions complémentaires pour les personnes en recherche d'emploi
                        </div>
                        
                        <!-- Durée sans emploi -->
                        <div class="step4-input-group">
                            <label class="step4-input-label">
                                Depuis combien de temps recherchez-vous ?
                            </label>
                            <div class="step4-options">
                                <div class="step4-option" data-value="moins1mois" data-question="unemployment-duration">
                                    <div class="step4-option-content">
                                        <div class="step4-option-radio"></div>
                                        <div class="step4-option-text">Moins d'1 mois</div>
                                    </div>
                                </div>
                                <div class="step4-option" data-value="1-3mois" data-question="unemployment-duration">
                                    <div class="step4-option-content">
                                        <div class="step4-option-radio"></div>
                                        <div class="step4-option-text">1 à 3 mois</div>
                                    </div>
                                </div>
                                <div class="step4-option" data-value="3-6mois" data-question="unemployment-duration">
                                    <div class="step4-option-content">
                                        <div class="step4-option-radio"></div>
                                        <div class="step4-option-text">3 à 6 mois</div>
                                    </div>
                                </div>
                                <div class="step4-option" data-value="plus6mois" data-question="unemployment-duration">
                                    <div class="step4-option-content">
                                        <div class="step4-option-radio"></div>
                                        <div class="step4-option-text">Plus de 6 mois</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dernier salaire -->
                        <div class="step4-input-group">
                            <label class="step4-input-label" for="last-salary">
                                Votre dernier salaire (K€ brut annuel) :
                            </label>
                            <div class="salary-range-input">
                                <input type="number" class="step4-input" id="last-salary" 
                                       name="last-salary" placeholder="42" min="20" max="200">
                                <span class="salary-unit-small">K €</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 3: Contraintes de disponibilité -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-clock"></i>
                        3) Avez-vous des contraintes de disponibilité ?
                    </h3>
                    
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            (Plusieurs choix possibles)
                        </label>
                        <div class="step4-checkbox-group" id="availability-constraints">
                            <div class="step4-checkbox-option" data-value="aucune">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Aucune contrainte particulière</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="enfants">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Garde d'enfants</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="formation">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Formation en cours</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="preavis">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Préavis à respecter</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="sante">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Contraintes de santé</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 4: Préférences de travail -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-laptop-house"></i>
                        4) Vos préférences de travail
                    </h3>
                    
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            Quel mode de travail préférez-vous ? (Plusieurs choix possibles)
                        </label>
                        <div class="step4-checkbox-group" id="work-preferences">
                            <div class="step4-checkbox-option" data-value="presentiel">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">100% présentiel sur site</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="hybride">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Travail hybride (mix présentiel/télétravail)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="remote">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">100% télétravail</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="flexible">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Horaires flexibles</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 5: Mobilité géographique -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-map-marked-alt"></i>
                        5) Accepteriez-vous de déménager pour un poste ?
                    </h3>
                    
                    <div class="step4-options" id="relocation-options">
                        <div class="step4-option" data-value="oui" data-question="relocation">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">OUI, je suis ouvert à la mobilité géographique</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="selon-poste" data-question="relocation">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Selon le poste et les conditions proposées</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="non" data-question="relocation">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">NON, je souhaite rester dans ma région actuelle</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 6: Informations complémentaires -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-comment-dots"></i>
                        6) Informations complémentaires (optionnel)
                    </h3>
                    
                    <div class="step4-input-group">
                        <label class="step4-input-label" for="additional-info">
                            Y a-t-il d'autres éléments importants que nous devrions connaître ?
                        </label>
                        <textarea class="step4-input" id="additional-info" name="additional-info" 
                                  rows="4" placeholder="Projets personnels, contraintes particulières, certifications en cours, souhaits spécifiques..."></textarea>
                    </div>
                </div>
            </div>

            <!-- Boutons d'Action -->
            <div class="modern-form-actions">
                <button type="button" class="modern-btn btn-secondary" id="back-step3">
                    <i class="fas fa-arrow-left"></i>
                    <span>Retour</span>
                </button>
                <button type="button" class="modern-btn btn-primary" id="submit-questionnaire">
                    <span>Finaliser mon profil</span>
                    <i class="fas fa-check-circle"></i>
                </button>
            </div>

            <!-- Champs cachés pour intégration -->
            <input type="hidden" id="hidden-timing" name="timing">
            <input type="hidden" id="hidden-employment-status" name="employment-status">
            <input type="hidden" id="hidden-current-salary" name="current-salary">
            <input type="hidden" id="hidden-listening-reasons" name="listening-reasons">
            <input type="hidden" id="hidden-unemployment-duration" name="unemployment-duration">
            <input type="hidden" id="hidden-last-salary" name="last-salary">
            <input type="hidden" id="hidden-availability-constraints" name="availability-constraints">
            <input type="hidden" id="hidden-work-preferences" name="work-preferences">
            <input type="hidden" id="hidden-relocation" name="relocation">
            <input type="hidden" id="hidden-additional-info" name="additional-info">
        `;

        step4Container.innerHTML = htmlContent;
        console.log('✅ HTML étape 4 injecté avec succès');
    },

    setupEventListeners() {
        console.log('🔧 Configuration des événements étape 4...');

        // Gestion des options radio (questions principales)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.step4-option[data-question]')) {
                this.handleRadioOption(e.target.closest('.step4-option'));
            }
        });

        // Gestion des checkboxes (questions multiples)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.step4-checkbox-option')) {
                this.handleCheckboxOption(e.target.closest('.step4-checkbox-option'));
            }
        });

        // Gestion des inputs
        ['current-salary-min', 'current-salary-max', 'last-salary', 'additional-info'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', () => this.updateFormData());
            }
        });

        // Bouton retour
        const backButton = document.getElementById('back-step3');
        if (backButton) {
            backButton.addEventListener('click', () => this.goBackToStep3());
        }

        // Bouton finalisation
        const submitButton = document.getElementById('submit-questionnaire');
        if (submitButton) {
            submitButton.addEventListener('click', () => this.finalizeQuestionnaire());
        }

        console.log('✅ Événements étape 4 configurés');
    },

    handleRadioOption(option) {
        const question = option.dataset.question;
        const value = option.dataset.value;
        
        // Désélectionner toutes les options du même groupe
        document.querySelectorAll(`[data-question="${question}"]`).forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Sélectionner l'option cliquée
        option.classList.add('selected');
        
        // Mettre à jour les données
        this.formData[question === 'employment-status' ? 'employmentStatus' : 
                      question === 'unemployment-duration' ? 'unemploymentDuration' :
                      question === 'relocation' ? 'relocationAccepted' : 'timing'] = value;
        
        // Gérer les sections conditionnelles
        this.handleConditionalSections(question, value);
        
        this.updateFormData();
    },

    handleCheckboxOption(option) {
        const value = option.dataset.value;
        option.classList.toggle('selected');
        
        // Identifier le groupe de checkboxes
        const container = option.parentElement;
        const groupId = container.id;
        
        // Mettre à jour le tableau correspondant
        let targetArray;
        if (groupId === 'listening-reasons') {
            targetArray = this.formData.listeningReasons;
        } else if (groupId === 'availability-constraints') {
            targetArray = this.formData.availabilityConstraints;
        } else if (groupId === 'work-preferences') {
            targetArray = this.formData.workPreferences;
        }
        
        if (targetArray) {
            const index = targetArray.indexOf(value);
            if (option.classList.contains('selected') && index === -1) {
                targetArray.push(value);
            } else if (!option.classList.contains('selected') && index > -1) {
                targetArray.splice(index, 1);
            }
        }
        
        this.updateFormData();
    },

    handleConditionalSections(question, value) {
        if (question === 'employment-status') {
            const yesSection = document.getElementById('employment-yes-section');
            const noSection = document.getElementById('employment-no-section');
            
            if (yesSection && noSection) {
                if (value === 'oui') {
                    yesSection.classList.add('active');
                    noSection.classList.remove('active');
                } else {
                    yesSection.classList.remove('active');
                    noSection.classList.add('active');
                }
            }
        }
    },

    updateFormData() {
        // Mettre à jour les salaires
        const currentSalaryMin = document.getElementById('current-salary-min');
        const currentSalaryMax = document.getElementById('current-salary-max');
        const lastSalary = document.getElementById('last-salary');
        const additionalInfo = document.getElementById('additional-info');
        
        if (currentSalaryMin && currentSalaryMax) {
            this.formData.currentSalaryMin = currentSalaryMin.value;
            this.formData.currentSalaryMax = currentSalaryMax.value;
        }
        
        if (lastSalary) {
            this.formData.lastSalary = lastSalary.value;
        }
        
        if (additionalInfo) {
            this.formData.additionalInfo = additionalInfo.value;
        }
        
        // Mettre à jour les champs cachés
        this.updateHiddenFields();
    },

    updateHiddenFields() {
        const hiddenFields = {
            'hidden-timing': this.formData.timing,
            'hidden-employment-status': this.formData.employmentStatus,
            'hidden-current-salary': `${this.formData.currentSalaryMin}-${this.formData.currentSalaryMax}`,
            'hidden-listening-reasons': this.formData.listeningReasons.join(','),
            'hidden-unemployment-duration': this.formData.unemploymentDuration,
            'hidden-last-salary': this.formData.lastSalary,
            'hidden-availability-constraints': this.formData.availabilityConstraints.join(','),
            'hidden-work-preferences': this.formData.workPreferences.join(','),
            'hidden-relocation': this.formData.relocationAccepted,
            'hidden-additional-info': this.formData.additionalInfo
        };
        
        Object.entries(hiddenFields).forEach(([id, value]) => {
            const field = document.getElementById(id);
            if (field) {
                field.value = value || '';
            }
        });
    },

    setupDemoData() {
        // Préremplir avec des données de démo si mode démo actif
        const isDemoMode = document.querySelector('.simulated-data-badge');
        if (isDemoMode) {
            console.log('📊 Mode démo détecté - préremplissage étape 4...');
            
            // Sélectionner automatiquement quelques options
            setTimeout(() => {
                // Timing: Dans 1 mois
                const timingOption = document.querySelector('[data-question="timing"][data-value="1mois"]');
                if (timingOption) {
                    this.handleRadioOption(timingOption);
                }
                
                // En poste: OUI
                const employmentOption = document.querySelector('[data-question="employment-status"][data-value="oui"]');
                if (employmentOption) {
                    this.handleRadioOption(employmentOption);
                }
                
                // Préremplir salaire actuel
                setTimeout(() => {
                    const currentSalaryMin = document.getElementById('current-salary-min');
                    const currentSalaryMax = document.getElementById('current-salary-max');
                    if (currentSalaryMin && currentSalaryMax) {
                        currentSalaryMin.value = '42';
                        currentSalaryMax.value = '47';
                        this.updateFormData();
                    }
                    
                    // Sélectionner quelques raisons
                    const reasonsToSelect = ['evolution', 'remuneration'];
                    reasonsToSelect.forEach(reason => {
                        const option = document.querySelector(`#listening-reasons [data-value="${reason}"]`);
                        if (option) {
                            this.handleCheckboxOption(option);
                        }
                    });
                    
                    // Préférences de travail
                    const workPrefsToSelect = ['hybride', 'flexible'];
                    workPrefsToSelect.forEach(pref => {
                        const option = document.querySelector(`#work-preferences [data-value="${pref}"]`);
                        if (option) {
                            this.handleCheckboxOption(option);
                        }
                    });
                    
                    // Mobilité
                    const relocationOption = document.querySelector('[data-question="relocation"][data-value="selon-poste"]');
                    if (relocationOption) {
                        this.handleRadioOption(relocationOption);
                    }
                    
                    console.log('✅ Données démo remplies pour étape 4');
                }, 500);
            }, 200);
        }
    },

    goBackToStep3() {
        console.log('⬅️ Retour vers étape 3');
        
        // Utiliser le système de navigation existant
        if (typeof showStep === 'function') {
            showStep(3);
        } else {
            // Fallback manuel
            document.querySelectorAll('.form-step').forEach(step => {
                step.style.display = 'none';
            });
            const step3 = document.getElementById('form-step3');
            if (step3) {
                step3.style.display = 'block';
            }
        }
    },

    validateStep4() {
        const errors = [];
        
        // Vérifier les questions obligatoires
        if (!this.formData.timing) {
            errors.push('Veuillez indiquer quand vous cherchez à prendre un poste');
        }
        
        if (!this.formData.employmentStatus) {
            errors.push('Veuillez indiquer si vous êtes actuellement en poste');
        }
        
        // Validations conditionnelles
        if (this.formData.employmentStatus === 'oui') {
            if (!this.formData.currentSalaryMin || !this.formData.currentSalaryMax) {
                errors.push('Veuillez indiquer votre salaire actuel');
            }
            if (this.formData.listeningReasons.length === 0) {
                errors.push('Veuillez indiquer pourquoi vous êtes à l\'écoute');
            }
        }
        
        if (this.formData.employmentStatus === 'non') {
            if (!this.formData.unemploymentDuration) {
                errors.push('Veuillez indiquer depuis combien de temps vous recherchez');
            }
        }
        
        return errors;
    },

    finalizeQuestionnaire() {
        console.log('🎯 Finalisation du questionnaire...');
        
        // Valider les données
        const errors = this.validateStep4();
        
        if (errors.length > 0) {
            this.showValidationErrors(errors);
            return;
        }
        
        // Préparer les données finales
        const allFormData = this.collectAllFormData();
        
        // Simulation de soumission
        this.simulateSubmission(allFormData);
    },

    showValidationErrors(errors) {
        // Supprimer les anciens messages d'erreur
        document.querySelectorAll('.step4-error-message').forEach(msg => msg.remove());
        
        // Créer le message d'erreur
        const errorContainer = document.createElement('div');
        errorContainer.className = 'step4-error-message';
        errorContainer.style.cssText = `
            background: #fee2e2; border: 2px solid #fecaca; color: #dc2626;
            padding: 16px; border-radius: 12px; margin: 20px 0;
            font-weight: 500;
        `;
        
        errorContainer.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Veuillez corriger les erreurs suivantes :</strong>
            </div>
            <ul style="margin: 0; padding-left: 20px;">
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        `;
        
        // Insérer au début de l'étape 4
        const step4Container = document.querySelector('#form-step4 .form-section-title');
        if (step4Container) {
            step4Container.parentNode.insertBefore(errorContainer, step4Container.nextSibling);
        }
        
        // Scroll vers le haut
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    },

    collectAllFormData() {
        // Collecter toutes les données du questionnaire
        const formData = new FormData(document.getElementById('questionnaire-form'));
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Ajouter les données de l'étape 4
        data.step4 = this.formData;
        
        return data;
    },

    simulateSubmission(data) {
        console.log('📤 Soumission simulée des données:', data);
        
        // Afficher un message de succès
        this.showSuccessMessage();
        
        // Optionnel: redirection ou autre action
        setTimeout(() => {
            // Ici vous pouvez rediriger vers une page de confirmation
            // window.location.href = '/confirmation';
            console.log('✅ Questionnaire complété avec succès');
        }, 3000);
    },

    showSuccessMessage() {
        // Créer le message de succès
        const successContainer = document.createElement('div');
        successContainer.className = 'step4-success-message';
        successContainer.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            padding: 32px; border-radius: 16px; text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3); z-index: 10000;
            max-width: 400px; width: 90%;
        `;
        
        successContainer.innerHTML = `
            <div style="font-size: 48px; margin-bottom: 16px;">
                <i class="fas fa-check-circle"></i>
            </div>
            <h3 style="margin: 0 0 8px 0; font-size: 24px;">Questionnaire complété !</h3>
            <p style="margin: 0; opacity: 0.9;">
                Merci ! Nous analyons votre profil et reviendrons vers vous très prochainement avec des opportunités personnalisées.
            </p>
        `;
        
        document.body.appendChild(successContainer);
        
        // Animation d'entrée
        successContainer.style.opacity = '0';
        successContainer.style.transform = 'translate(-50%, -50%) scale(0.8)';
        
        setTimeout(() => {
            successContainer.style.transition = 'all 0.3s ease-out';
            successContainer.style.opacity = '1';
            successContainer.style.transform = 'translate(-50%, -50%) scale(1)';
        }, 100);
        
        // Supprimer après 3 secondes
        setTimeout(() => {
            successContainer.remove();
        }, 3000);
    }
};

// ===== INTÉGRATION AVEC LE SYSTÈME DE NAVIGATION EXISTANT =====
function enhanceStep4Navigation() {
    console.log('🔗 Amélioration de la navigation vers étape 4...');
    
    // Améliorer le bouton "Suivant" de l'étape 3
    const nextStep3Button = document.getElementById('next-step3');
    if (nextStep3Button) {
        // Supprimer les anciens événements et ajouter le nouveau
        const newButton = nextStep3Button.cloneNode(true);
        nextStep3Button.parentNode.replaceChild(newButton, nextStep3Button);
        
        newButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('🎯 Navigation vers étape 4...');
            
            // Masquer toutes les étapes
            document.querySelectorAll('.form-step').forEach(step => {
                step.style.display = 'none';
            });
            
            // Afficher l'étape 4
            const step4 = document.getElementById('form-step4');
            if (step4) {
                step4.style.display = 'block';
                
                // Mettre à jour la barre de progression
                document.querySelectorAll('.step').forEach((step, index) => {
                    step.classList.remove('active');
                    if (index < 3) {
                        step.classList.add('completed');
                    }
                    if (index === 3) {
                        step.classList.add('active');
                    }
                });
                
                // Scroll vers le haut
                window.scrollTo({ top: 0, behavior: 'smooth' });
                
                console.log('✅ Étape 4 affichée');
            }
        });
    }
    
    // S'assurer que l'étape 4 est cliquable dans la barre de progression
    const step4Progress = document.getElementById('step4');
    if (step4Progress) {
        step4Progress.style.cursor = 'pointer';
        step4Progress.addEventListener('click', () => {
            // Navigation directe vers étape 4
            document.querySelectorAll('.form-step').forEach(step => {
                step.style.display = 'none';
            });
            
            const step4Form = document.getElementById('form-step4');
            if (step4Form) {
                step4Form.style.display = 'block';
                
                // Mettre à jour la barre de progression
                document.querySelectorAll('.step').forEach((step, index) => {
                    step.classList.remove('active');
                    if (index < 3) {
                        step.classList.add('completed');
                    }
                    if (index === 3) {
                        step.classList.add('active');
                    }
                });
                
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }
}

// ===== INITIALISATION AUTOMATIQUE =====
function initializeStep4System() {
    console.log('🚀 Initialisation complète système étape 4...');
    
    const checkAndInit = () => {
        // Vérifier que les éléments de base existent
        const step4Container = document.getElementById('form-step4');
        
        if (step4Container) {
            // Initialiser le système principal
            window.step4System.init();
            
            // Améliorer la navigation
            enhanceStep4Navigation();
            
            console.log('✅ Système étape 4 complètement initialisé');
        } else {
            console.warn('⚠️ Container étape 4 non trouvé, nouvelle tentative...');
            setTimeout(checkAndInit, 500);
        }
    };
    
    // Initialiser après chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(checkAndInit, 300);
        });
    } else {
        setTimeout(checkAndInit, 200);
    }
}

// Lancer l'initialisation
initializeStep4System();

console.log('✅ Script de correction étape 4 chargé avec succès');
