// ===== 🎯 PARCOURS CONDITIONNEL AVANCÉ ÉTAPE 4 - QUESTION EMPLOI =====
// 🚨 MODIFICATION CIBLÉE : Remplace UNIQUEMENT la question "Êtes-vous actuellement en poste ?"
// 🔒 PROTECTION ABSOLUE : Préserve tout le code existant et les autres questions
// 🎨 NEXTEN V3.0 : Maintient l'interface moderne et l'expérience utilisateur
// Version: 1.0 - Parcours conditionnel complexe
// Auteur: Système Nexten - Respect strict des contraintes

console.log('🎯 Chargement du parcours conditionnel avancé étape 4...');

// ===== SYSTÈME DE PARCOURS CONDITIONNEL AVANCÉ =====
window.advancedEmploymentQuestionnaire = {
    // 📊 Structure de données pour le parcours conditionnel
    formData: {
        currentlyEmployed: null,
        // Parcours EMPLOYÉ
        listeningReasons: [],
        noticeTime: null,
        noticeNegotiable: null,
        recruitmentStatus: null,
        // Parcours DEMANDEUR D'EMPLOI
        unemployedRecruitmentStatus: null,
        lastContractEndReasons: []
    },

    // 🔧 Initialisation du système
    init() {
        console.log('🔧 Initialisation du parcours conditionnel avancé...');
        
        // Attendre que l'étape 4 soit prête
        this.waitForStep4Ready(() => {
            this.replaceEmploymentQuestion();
            this.setupEventListeners();
            this.preserveExistingFunctionality();
            
            // 📊 Rapport de sécurité final
            this.generateSecurityReport();
            
            console.log('✅ Parcours conditionnel avancé initialisé avec succès');
        });
    },

    // ⏱️ Attendre que l'étape 4 soit prête
    waitForStep4Ready(callback) {
        const checkStep4 = () => {
            const step4Container = document.getElementById('form-step4');
            const employmentSection = document.querySelector('[data-question="employment-status"]');
            
            // 🛡️ PROTECTION CRITIQUE : Vérifier que la question "Quand cherchez-vous..." est présente et intacte
            const timingQuestion = this.validateTimingQuestionIntegrity();
            
            if (step4Container && employmentSection && timingQuestion) {
                console.log('✅ Étape 4 prête et question timing préservée');
                callback();
            } else {
                setTimeout(checkStep4, 200);
            }
        };
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(checkStep4, 300);
            });
        } else {
            setTimeout(checkStep4, 100);
        }
    },

    // 🛡️ Vérifier l'intégrité de la question "Quand cherchez-vous à prendre un poste ?"
    validateTimingQuestionIntegrity() {
        const timingQuestions = document.querySelectorAll('#form-step4 .step4-question-title, #form-step4 h3');
        
        for (const question of timingQuestions) {
            const questionText = question.textContent.toLowerCase();
            if (questionText.includes('quand cherchez-vous') || 
                questionText.includes('quand cherchez-vous à prendre un poste')) {
                console.log('✅ Question timing trouvée et préservée:', question.textContent);
                return true;
            }
        }
        
        // Si pas trouvée, vérifier les options timing
        const timingOptions = document.querySelector('[data-question="timing"]');
        if (timingOptions) {
            console.log('✅ Options timing trouvées, question probablement présente');
            return true;
        }
        
        console.warn('⚠️ Question timing non trouvée, attente...');
        return false;
    },

    // 🔄 Remplacer la question d'emploi par le parcours conditionnel
    replaceEmploymentQuestion() {
        console.log('🔄 Remplacement de la question d\'emploi par le parcours conditionnel...');
        
        // 🎯 CIBLAGE ULTRA-PRÉCIS : Localiser UNIQUEMENT la question "Êtes-vous actuellement en poste ?"
        // en s'assurant qu'on ne touche PAS à la question "Quand cherchez-vous à prendre un poste ?"
        
        // Méthode 1: Cibler par le texte exact de la question
        const employmentQuestionContainer = this.findEmploymentQuestionContainer();
        
        if (!employmentQuestionContainer) {
            console.error('❌ Question d\'emploi spécifique non trouvée pour remplacement');
            return;
        }

        // Vérifier qu'on a bien la bonne question avant de la remplacer
        const questionTitle = employmentQuestionContainer.querySelector('.step4-question-title, h3');
        if (!questionTitle || !questionTitle.textContent.includes('Êtes-vous actuellement en poste')) {
            console.error('❌ Mauvaise question détectée, abandon pour éviter les dégâts');
            return;
        }

        // Créer le nouveau contenu avec parcours conditionnel
        const newEmploymentHTML = this.createAdvancedEmploymentHTML();
        
        // Remplacer le contenu existant
        employmentQuestionContainer.innerHTML = newEmploymentHTML;
        
        // 🔍 VÉRIFICATION POST-MODIFICATION : S'assurer que la question timing est toujours là
        setTimeout(() => {
            const timingStillThere = this.validateTimingQuestionIntegrity();
            if (!timingStillThere) {
                console.error('❌ ERREUR CRITIQUE : Question timing disparue après modification !');
                // En cas d'erreur, on pourrait restaurer ou alerter
            } else {
                console.log('✅ Modification réussie, question timing préservée');
            }
        }, 100);
        
        console.log('✅ Question d\'emploi remplacée par le parcours conditionnel avancé');
    },

    // 🔍 Méthode sécurisée pour trouver la question d'emploi
    findEmploymentQuestionContainer() {
        // Rechercher toutes les questions possibles dans l'étape 4
        const allQuestionContainers = document.querySelectorAll('#form-step4 .step4-container');
        
        for (const container of allQuestionContainers) {
            const questionTitle = container.querySelector('.step4-question-title, h3');
            const employmentOptions = container.querySelector('[data-question="employment-status"]');
            
            // Vérifier par le texte ET par la présence des options d'emploi
            if (questionTitle && employmentOptions) {
                const titleText = questionTitle.textContent.toLowerCase();
                if (titleText.includes('êtes-vous actuellement en poste') || 
                    titleText.includes('actuellement en poste')) {
                    console.log('✅ Question d\'emploi trouvée via analyse textuelle');
                    return container;
                }
            }
        }
        
        // Méthode de secours: chercher par les options d'emploi
        const employmentOption = document.querySelector('[data-question="employment-status"]');
        if (employmentOption) {
            const container = employmentOption.closest('.step4-container');
            if (container) {
                console.log('✅ Question d\'emploi trouvée via options');
                return container;
            }
        }
        
        return null;
    },

    // 🎨 Créer le HTML du parcours conditionnel avancé
    createAdvancedEmploymentHTML() {
        return `
            <div class="step4-question">
                <h3 class="step4-question-title">
                    <i class="fas fa-briefcase"></i>
                    2) Êtes-vous actuellement en poste ?
                </h3>
                
                <div class="step4-options" id="employment-status-options">
                    <div class="step4-option" data-value="oui" data-question="employment-status">
                        <div class="step4-option-content">
                            <div class="step4-option-radio"></div>
                            <div class="step4-option-text">OUI</div>
                        </div>
                    </div>
                    
                    <div class="step4-option" data-value="non" data-question="employment-status">
                        <div class="step4-option-content">
                            <div class="step4-option-radio"></div>
                            <div class="step4-option-text">NON</div>
                        </div>
                    </div>
                </div>

                <!-- 🟢 PARCOURS EMPLOYÉ - Questions conditionnelles -->
                <div class="conditional-section" id="employment-yes-section">
                    <div class="conditional-section-title">
                        <i class="fas fa-user-tie"></i>
                        Parcours pour les personnes en poste
                    </div>
                    
                    <!-- Question 1: Pourquoi êtes-vous de nouveau à l'écoute ? -->
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-question-circle"></i>
                            Pourquoi êtes-vous de nouveau à l'écoute ? (plusieurs choix possibles)
                        </label>
                        <div class="step4-checkbox-group" id="listening-reasons-employed">
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
                                <div class="step4-checkbox-text">Manque de flexibilité (pas de TT, RTT)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="problemes-internes">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Problème en interne (organisation, management)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="ne-souhaite-pas">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Je ne souhaite pas communiquer</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="poste-different">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Le poste ne coïncide pas avec le poste proposé initialement</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="pse">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">PSE</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="epanouissement">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Je ne m'épanouis plus, je souhaite découvrir de nouvelles choses</div>
                            </div>
                        </div>
                    </div>

                    <!-- Question 2: Préavis -->
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-calendar-alt"></i>
                            De combien de temps est votre préavis ?
                        </label>
                        <div class="step4-options" id="notice-time-options">
                            <div class="step4-option" data-value="aucun" data-question="notice-time">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je n'en ai pas, encore en PE</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="1mois" data-question="notice-time">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">1 mois</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="2mois" data-question="notice-time">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">2 mois</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="3mois" data-question="notice-time">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">3 mois</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Question 3: Négociabilité du préavis -->
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-handshake"></i>
                            Est-il négociable ?
                        </label>
                        <div class="step4-options" id="notice-negotiable-options">
                            <div class="step4-option" data-value="oui" data-question="notice-negotiable">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">OUI</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="non" data-question="notice-negotiable">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">NON</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="ne-sais-pas" data-question="notice-negotiable">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je ne sais pas</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Question 4: Processus de recrutement (employé) -->
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-search"></i>
                            Où en êtes-vous dans vos processus de recrutement ?
                        </label>
                        <div class="step4-options" id="recruitment-status-employed-options">
                            <div class="step4-option" data-value="aucune-piste" data-question="recruitment-status-employed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je n'ai pas encore de piste</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="entretiens" data-question="recruitment-status-employed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">J'avance sur différents entretiens</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="processus-final" data-question="recruitment-status-employed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je suis en processus final</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="propositions" data-question="recruitment-status-employed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">On m'a fait des propositions</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 🔴 PARCOURS DEMANDEUR D'EMPLOI - Questions conditionnelles -->
                <div class="conditional-section" id="employment-no-section">
                    <div class="conditional-section-title">
                        <i class="fas fa-user-plus"></i>
                        Parcours pour les demandeurs d'emploi
                    </div>
                    
                    <!-- Question 1: Processus de recrutement (demandeur) -->
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-search"></i>
                            Où en êtes-vous dans vos processus de recrutement ?
                        </label>
                        <div class="step4-options" id="recruitment-status-unemployed-options">
                            <div class="step4-option" data-value="aucune-piste" data-question="recruitment-status-unemployed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je n'ai pas encore de piste</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="entretiens" data-question="recruitment-status-unemployed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">J'avance sur différents entretiens</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="processus-final" data-question="recruitment-status-unemployed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je suis en processus final</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="propositions" data-question="recruitment-status-unemployed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">On m'a fait des propositions</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Question 2: Pourquoi le dernier contrat s'est arrêté -->
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-question-circle"></i>
                            Pourquoi votre dernier contrat s'est-il arrêté ? (plusieurs choix possibles)
                        </label>
                        <div class="step4-checkbox-group" id="last-contract-end-reasons">
                            <div class="step4-checkbox-option" data-value="epanouissement">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Je ne m'épanouissais plus, je souhaite découvrir de nouvelles choses</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="evolution">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Manque de perspectives d'évolution</div>
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
                                <div class="step4-checkbox-text">Manque de flexibilité (pas de TT, RTT)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="problemes-internes">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Problème en interne (organisation, management)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="poste-different">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Poste ne coïncide pas avec le poste proposé initialement</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="pse">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">PSE</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="ne-souhaite-pas">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Je ne souhaite pas communiquer</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="remuneration">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Rémunération trop faible</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Champs cachés pour sauvegarder les données -->
                <input type="hidden" id="hidden-employment-status-advanced" name="employment-status-advanced">
                <input type="hidden" id="hidden-listening-reasons-employed" name="listening-reasons-employed">
                <input type="hidden" id="hidden-notice-time" name="notice-time">
                <input type="hidden" id="hidden-notice-negotiable" name="notice-negotiable">
                <input type="hidden" id="hidden-recruitment-status-employed" name="recruitment-status-employed">
                <input type="hidden" id="hidden-recruitment-status-unemployed" name="recruitment-status-unemployed">
                <input type="hidden" id="hidden-last-contract-end-reasons" name="last-contract-end-reasons">
            </div>
        `;
    },

    // 🎛️ Configuration des événements
    setupEventListeners() {
        console.log('🎛️ Configuration des événements du parcours conditionnel...');

        // Gestion des options radio principales
        document.addEventListener('click', (e) => {
            const option = e.target.closest('.step4-option[data-question]');
            if (option && this.isAdvancedEmploymentOption(option)) {
                this.handleRadioOption(option);
            }
        });

        // Gestion des checkboxes
        document.addEventListener('click', (e) => {
            const checkbox = e.target.closest('.step4-checkbox-option');
            if (checkbox && this.isAdvancedEmploymentCheckbox(checkbox)) {
                this.handleCheckboxOption(checkbox);
            }
        });

        console.log('✅ Événements du parcours conditionnel configurés');
    },

    // 🔍 Vérifier si l'option appartient au parcours conditionnel avancé
    isAdvancedEmploymentOption(option) {
        const question = option.dataset.question;
        return ['employment-status', 'notice-time', 'notice-negotiable', 
                'recruitment-status-employed', 'recruitment-status-unemployed'].includes(question);
    },

    // 🔍 Vérifier si la checkbox appartient au parcours conditionnel avancé
    isAdvancedEmploymentCheckbox(checkbox) {
        const container = checkbox.closest('.step4-checkbox-group');
        return container && ['listening-reasons-employed', 'last-contract-end-reasons'].includes(container.id);
    },

    // 🎯 Gestion des options radio
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
        this.updateFormData(question, value);
        
        // Gérer l'affichage conditionnel
        this.handleConditionalDisplay(question, value);
        
        // Sauvegarder dans les champs cachés
        this.saveToHiddenFields();
    },

    // ☑️ Gestion des checkboxes
    handleCheckboxOption(checkbox) {
        const value = checkbox.dataset.value;
        const container = checkbox.closest('.step4-checkbox-group');
        const groupId = container.id;
        
        // Basculer la sélection
        checkbox.classList.toggle('selected');
        
        // Mettre à jour le tableau correspondant
        if (groupId === 'listening-reasons-employed') {
            this.toggleArrayValue(this.formData.listeningReasons, value);
        } else if (groupId === 'last-contract-end-reasons') {
            this.toggleArrayValue(this.formData.lastContractEndReasons, value);
        }
        
        // Sauvegarder dans les champs cachés
        this.saveToHiddenFields();
    },

    // 🔄 Basculer une valeur dans un tableau
    toggleArrayValue(array, value) {
        const index = array.indexOf(value);
        if (index === -1) {
            array.push(value);
        } else {
            array.splice(index, 1);
        }
    },

    // 💾 Mettre à jour les données du formulaire
    updateFormData(question, value) {
        switch (question) {
            case 'employment-status':
                this.formData.currentlyEmployed = value;
                break;
            case 'notice-time':
                this.formData.noticeTime = value;
                break;
            case 'notice-negotiable':
                this.formData.noticeNegotiable = value;
                break;
            case 'recruitment-status-employed':
                this.formData.recruitmentStatus = value;
                break;
            case 'recruitment-status-unemployed':
                this.formData.unemployedRecruitmentStatus = value;
                break;
        }
    },

    // 👁️ Gérer l'affichage conditionnel
    handleConditionalDisplay(question, value) {
        if (question === 'employment-status') {
            const employedSection = document.getElementById('employment-yes-section');
            const unemployedSection = document.getElementById('employment-no-section');
            
            if (employedSection && unemployedSection) {
                if (value === 'oui') {
                    employedSection.classList.add('active');
                    unemployedSection.classList.remove('active');
                } else if (value === 'non') {
                    employedSection.classList.remove('active');
                    unemployedSection.classList.add('active');
                }
            }
        }
    },

    // 💾 Sauvegarder dans les champs cachés
    saveToHiddenFields() {
        const hiddenFields = {
            'hidden-employment-status-advanced': this.formData.currentlyEmployed,
            'hidden-listening-reasons-employed': this.formData.listeningReasons.join(','),
            'hidden-notice-time': this.formData.noticeTime,
            'hidden-notice-negotiable': this.formData.noticeNegotiable,
            'hidden-recruitment-status-employed': this.formData.recruitmentStatus,
            'hidden-recruitment-status-unemployed': this.formData.unemployedRecruitmentStatus,
            'hidden-last-contract-end-reasons': this.formData.lastContractEndReasons.join(',')
        };
        
        Object.entries(hiddenFields).forEach(([id, value]) => {
            const field = document.getElementById(id);
            if (field) {
                field.value = value || '';
            }
        });

        // Mettre à jour également les anciens champs cachés pour la compatibilité
        const oldEmploymentField = document.getElementById('hidden-employment-status');
        if (oldEmploymentField) {
            oldEmploymentField.value = this.formData.currentlyEmployed || '';
        }
    },

    // 🛡️ Préserver les fonctionnalités existantes
    preserveExistingFunctionality() {
        console.log('🛡️ Préservation des fonctionnalités existantes...');
        
        // S'assurer que les autres questions de l'étape 4 fonctionnent toujours
        const existingSystem = window.step4System;
        if (existingSystem && existingSystem.updateFormData) {
            // Étendre la fonction existante pour inclure nos nouvelles données
            const originalUpdateFormData = existingSystem.updateFormData.bind(existingSystem);
            existingSystem.updateFormData = function() {
                originalUpdateFormData();
                // Ajouter nos données à la structure existante
                if (window.advancedEmploymentQuestionnaire) {
                    Object.assign(this.formData, window.advancedEmploymentQuestionnaire.formData);
                }
            };
        }

        // Préserver la collecte de données pour le localStorage
        this.integrateWithLocalStorage();
        
        console.log('✅ Fonctionnalités existantes préservées');
    },

    // 🗃️ Intégration avec le localStorage existant
    integrateWithLocalStorage() {
        // Étendre la fonction de collecte de données existante
        const originalForm = document.getElementById('questionnaire-form');
        if (originalForm) {
            originalForm.addEventListener('submit', (e) => {
                // Ajouter nos données au localStorage
                const currentData = JSON.parse(localStorage.getItem('questionnaire_data') || '{}');
                currentData.availability_situation = {
                    ...currentData.availability_situation,
                    advanced_employment: this.formData
                };
                localStorage.setItem('questionnaire_data', JSON.stringify(currentData));
            });
        }
    },

    // 📊 Générer un rapport de sécurité pour confirmer l'intégrité
    generateSecurityReport() {
        console.log('📊 === RAPPORT DE SÉCURITÉ NEXTEN ===');
        
        // Vérifier la question 1 (timing)
        const timingIntact = this.validateTimingQuestionIntegrity();
        console.log(`🎯 Question 1 "Quand cherchez-vous..." : ${timingIntact ? '✅ PRÉSERVÉE' : '❌ MANQUANTE'}`);
        
        // Vérifier la question 2 modifiée (emploi)
        const employmentModified = document.querySelector('#employment-yes-section, #employment-no-section');
        console.log(`🎯 Question 2 "Êtes-vous en poste..." : ${employmentModified ? '✅ MODIFIÉE' : '❌ NON MODIFIÉE'}`);
        
        // Vérifier les autres questions de l'étape 4
        const allQuestions = document.querySelectorAll('#form-step4 .step4-question-title, #form-step4 h3');
        console.log(`🎯 Nombre total de questions étape 4 : ${allQuestions.length}`);
        
        // Vérifier les scripts existants
        const existingScripts = [
            'step4System',
            'questionnaire-redirect.js'
        ];
        
        existingScripts.forEach(script => {
            const exists = typeof window[script] !== 'undefined' || 
                          document.querySelector(`script[src*="${script}"]`);
            console.log(`🎯 Script "${script}" : ${exists ? '✅ ACTIF' : '⚠️ NON DÉTECTÉ'}`);
        });
        
        // Vérifier localStorage
        const localStorageWorking = typeof localStorage !== 'undefined';
        console.log(`🎯 LocalStorage : ${localStorageWorking ? '✅ FONCTIONNEL' : '❌ INDISPONIBLE'}`);
        
        console.log('📊 === FIN RAPPORT DE SÉCURITÉ ===');
    },

    // 🔍 Obtenir les données du parcours conditionnel
    getFormData() {
        return {
            ...this.formData,
            isComplete: this.isComplete()
        };
    },

    // ✅ Vérifier si le parcours est complet
    isComplete() {
        if (!this.formData.currentlyEmployed) {
            return false;
        }
        
        if (this.formData.currentlyEmployed === 'oui') {
            return this.formData.listeningReasons.length > 0 &&
                   this.formData.noticeTime &&
                   this.formData.noticeNegotiable &&
                   this.formData.recruitmentStatus;
        } else {
            return this.formData.unemployedRecruitmentStatus &&
                   this.formData.lastContractEndReasons.length > 0;
        }
    }
};

// ===== 🚀 INITIALISATION AUTOMATIQUE =====
function initializeAdvancedEmploymentQuestionnaire() {
    console.log('🚀 Initialisation du parcours conditionnel avancé...');
    
    // Vérifier que nous sommes dans l'environnement correct
    if (typeof window !== 'undefined' && document) {
        window.advancedEmploymentQuestionnaire.init();
    } else {
        console.error('❌ Environnement non compatible pour le parcours conditionnel');
    }
}

// Lancer l'initialisation
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAdvancedEmploymentQuestionnaire);
} else {
    // Si le DOM est déjà chargé, initialiser avec un délai pour laisser les autres scripts se charger
    setTimeout(initializeAdvancedEmploymentQuestionnaire, 500);
}

console.log('✅ Script de parcours conditionnel avancé chargé avec succès');
