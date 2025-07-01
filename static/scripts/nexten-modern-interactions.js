/**
 * NEXTEN V3.0 - JavaScript Interactions CORRIGÉ
 * 🔧 Corrections pour l'étape 2 : Temps de trajet + Contrats
 */

class NextenQuestionnaire {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.contractRanking = [];
        this.selectedSecteurs = [];
        this.selectedRedhibitoires = [];
        this.selectedMotivations = [];
        
        // 🆕 Données étape 4
        this.step4Data = {
            timing: '',
            employmentStatus: '',
            currentSalaryMin: '',
            currentSalaryMax: '',
            listeningReasons: [],
            noticePeriod: '',
            noticeNegotiable: '',
            contractEndReasons: [],
            recruitmentStatus: ''
        };
        
        // 🆕 Liste étendue des secteurs
        this.secteursList = [
            { id: 'tech', name: 'Technologie / Informatique', icon: 'fas fa-laptop-code' },
            { id: 'finance', name: 'Finance / Banque / Assurance', icon: 'fas fa-chart-line' },
            { id: 'sante', name: 'Santé / Pharmaceutique', icon: 'fas fa-heartbeat' },
            { id: 'education', name: 'Éducation / Formation', icon: 'fas fa-graduation-cap' },
            { id: 'industrie', name: 'Industrie / Manufacturing', icon: 'fas fa-industry' },
            { id: 'commerce', name: 'Commerce / Retail', icon: 'fas fa-shopping-cart' },
            { id: 'automobile', name: 'Automobile', icon: 'fas fa-car' },
            { id: 'energie', name: 'Énergie / Utilities', icon: 'fas fa-bolt' },
            { id: 'medias', name: 'Médias / Communication', icon: 'fas fa-broadcast-tower' },
            { id: 'telecoms', name: 'Télécommunications', icon: 'fas fa-wifi' },
            { id: 'immobilier', name: 'Immobilier', icon: 'fas fa-building' },
            { id: 'tourisme', name: 'Tourisme / Hôtellerie', icon: 'fas fa-plane' },
            { id: 'agriculture', name: 'Agriculture / Agroalimentaire', icon: 'fas fa-seedling' },
            { id: 'btp', name: 'BTP / Construction', icon: 'fas fa-hard-hat' },
            { id: 'logistique', name: 'Logistique / Transport', icon: 'fas fa-truck' },
            { id: 'consulting', name: 'Consulting / Services professionnels', icon: 'fas fa-briefcase' },
            { id: 'ecommerce', name: 'E-commerce / Digital', icon: 'fas fa-shopping-bag' },
            { id: 'biotech', name: 'Biotechnologie', icon: 'fas fa-dna' },
            { id: 'aeronautique', name: 'Aéronautique / Spatial', icon: 'fas fa-rocket' },
            { id: 'mode', name: 'Mode / Luxe', icon: 'fas fa-gem' },
            { id: 'sports', name: 'Sports / Loisirs', icon: 'fas fa-futbol' },
            { id: 'juridique', name: 'Juridique', icon: 'fas fa-gavel' },
            { id: 'culture', name: 'Art / Culture', icon: 'fas fa-palette' },
            { id: 'environnement', name: 'Environnement / Développement durable', icon: 'fas fa-leaf' },
            { id: 'recherche', name: 'Recherche & Développement', icon: 'fas fa-microscope' },
            { id: 'securite', name: 'Sécurité', icon: 'fas fa-shield-alt' },
            { id: 'public', name: 'Administration publique', icon: 'fas fa-landmark' },
            { id: 'ong', name: 'ONG / Associations', icon: 'fas fa-hands-helping' }
        ];
        
        this.init();
    }

    init() {
        console.log('🚀 Initialisation NEXTEN V3.0 - Version CORRIGÉE');
        
        // Attendre que le DOM soit prêt
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeAll();
            });
        } else {
            this.initializeAll();
        }
    }

    initializeAll() {
        try {
            this.initializeStepNavigation();
            this.initializeTransportAndTravelTime(); // 🔧 CORRECTION : Gestion temps de trajet
            this.initializeContractSystem(); // 🔧 CORRECTION : Système de contrats
            this.initializeMotivationRanking();
            this.initializeSecteurSelectors();
            this.initializeSalaryControls();
            this.initializeModernOptions();
            this.initializeStep4Logic();
            this.updateStepIndicator();
            this.handleDemoMode();
            
            console.log('✅ Toutes les fonctionnalités initialisées avec succès');
        } catch (error) {
            console.error('❌ Erreur lors de l\'initialisation:', error);
            this.handleInitializationError(error);
        }
    }

    // 🔧 CORRECTION MAJEURE : Système de transport et temps de trajet RÉPARÉ
    initializeTransportAndTravelTime() {
        console.log('🚗 Initialisation système de transport et temps de trajet...');
        
        try {
            const transportCheckboxes = document.querySelectorAll('input[name="transport-method"]');
            const travelTimeContainer = document.getElementById('travel-time-container');
            
            if (!transportCheckboxes.length) {
                console.warn('⚠️ Aucune checkbox de transport trouvée');
                return;
            }

            if (!travelTimeContainer) {
                console.warn('⚠️ Conteneur de temps de trajet non trouvé');
                return;
            }

            // 🔧 FIX : Supprimer les anciens event listeners pour éviter les doublons
            transportCheckboxes.forEach(checkbox => {
                // Cloner l'élément pour supprimer tous les event listeners
                const newCheckbox = checkbox.cloneNode(true);
                checkbox.parentNode.replaceChild(newCheckbox, checkbox);
            });

            // 🔧 FIX : Ajouter les nouveaux event listeners
            const freshCheckboxes = document.querySelectorAll('input[name="transport-method"]');
            freshCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', () => {
                    console.log(`🔄 Transport ${checkbox.value} ${checkbox.checked ? 'sélectionné' : 'désélectionné'}`);
                    this.updateTravelTimeDisplay();
                });
            });

            // Initialisation de l'affichage
            this.updateTravelTimeDisplay();
            
            console.log('✅ Système de transport initialisé avec succès');
        } catch (error) {
            console.error('❌ Erreur initialisation transport:', error);
        }
    }

    // 🔧 CORRECTION : Méthode de mise à jour des temps de trajet RÉPARÉE
    updateTravelTimeDisplay() {
        try {
            const selectedTransports = document.querySelectorAll('input[name="transport-method"]:checked');
            const travelTimeContainer = document.getElementById('travel-time-container');
            
            if (!travelTimeContainer) {
                console.warn('⚠️ Conteneur de temps de trajet non trouvé');
                return;
            }

            // Mapping des transports vers leurs champs correspondants
            const transportFieldMap = {
                'public-transport': 'travel-time-public-transport',
                'vehicle': 'travel-time-vehicle',
                'bike': 'travel-time-bike',
                'walking': 'travel-time-walking'
            };

            // 🔧 FIX : Masquer TOUS les champs de temps de trajet d'abord
            Object.values(transportFieldMap).forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.style.display = 'none';
                    field.style.opacity = '0';
                    field.style.transform = 'translateX(-20px)';
                }
            });

            // 🔧 FIX : Afficher les champs correspondants avec animation
            if (selectedTransports.length > 0) {
                travelTimeContainer.classList.add('active');
                travelTimeContainer.style.maxHeight = '500px';
                travelTimeContainer.style.opacity = '1';
                travelTimeContainer.style.transform = 'translateY(0)';
                
                selectedTransports.forEach((transport, index) => {
                    const fieldId = transportFieldMap[transport.value];
                    const field = document.getElementById(fieldId);
                    
                    if (field) {
                        setTimeout(() => {
                            field.style.display = 'flex';
                            field.style.opacity = '1';
                            field.style.transform = 'translateX(0)';
                        }, index * 150); // Animation en cascade
                    }
                });
                
                console.log(`✅ Champs de temps de trajet affichés pour: ${Array.from(selectedTransports).map(t => t.value).join(', ')}`);
            } else {
                travelTimeContainer.classList.remove('active');
                travelTimeContainer.style.maxHeight = '0px';
                travelTimeContainer.style.opacity = '0';
                travelTimeContainer.style.transform = 'translateY(-10px)';
                
                console.log('📝 Aucun transport sélectionné - champs masqués');
            }
        } catch (error) {
            console.error('❌ Erreur mise à jour temps de trajet:', error);
        }
    }

    // 🔧 CORRECTION MAJEURE : Système de contrats COMPLÈTEMENT RÉPARÉ
    initializeContractSystem() {
        console.log('📋 Initialisation système de contrats...');
        
        try {
            // 🔧 FIX : Créer l'objet contractSystem global avec protection contre les erreurs
            window.contractSystem = {
                addToRanking: (contractType) => {
                    try {
                        return this.addContractToRanking(contractType);
                    } catch (error) {
                        console.error('❌ Erreur ajout contrat:', error);
                        this.showNotification('Erreur lors de l\'ajout du contrat', 'error');
                    }
                },
                removeFromRanking: (contractType) => {
                    try {
                        return this.removeContractFromRanking(contractType);
                    } catch (error) {
                        console.error('❌ Erreur suppression contrat:', error);
                        this.showNotification('Erreur lors de la suppression du contrat', 'error');
                    }
                },
                moveContract: (contractType, direction) => {
                    try {
                        return this.moveContract(contractType, direction);
                    } catch (error) {
                        console.error('❌ Erreur déplacement contrat:', error);
                        this.showNotification('Erreur lors du déplacement du contrat', 'error');
                    }
                },
                updateRankingDisplay: () => {
                    try {
                        return this.updateContractRankingDisplay();
                    } catch (error) {
                        console.error('❌ Erreur mise à jour affichage:', error);
                    }
                }
            };

            // 🔧 FIX : Vérifier que les boutons existent avant d'ajouter les event listeners
            const addButtons = document.querySelectorAll('.add-contract-button');
            console.log(`📊 ${addButtons.length} boutons "Ajouter" trouvés`);

            // 🔧 FIX : Ajouter des event listeners de secours si onclick ne fonctionne pas
            addButtons.forEach((button, index) => {
                const contractCard = button.closest('.contract-card');
                if (contractCard) {
                    const contractType = contractCard.dataset.type;
                    
                    // Event listener de secours
                    button.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log(`🔄 Clic sur bouton contrat: ${contractType}`);
                        this.addContractToRanking(contractType);
                    });
                    
                    console.log(`✅ Event listener ajouté pour ${contractType}`);
                }
            });

            // Initialiser l'affichage
            this.updateContractRankingDisplay();
            
            console.log('✅ Système de contrats initialisé avec succès');
        } catch (error) {
            console.error('❌ Erreur initialisation contrats:', error);
        }
    }

    // 🔧 CORRECTION : Méthode d'ajout de contrat RÉPARÉE
    addContractToRanking(contractType) {
        try {
            console.log(`➕ Tentative d'ajout du contrat: ${contractType}`);

            // Vérifier si le contrat n'est pas déjà dans le ranking
            if (this.contractRanking.find(c => c.type === contractType)) {
                this.showNotification('Ce type de contrat est déjà dans votre sélection', 'warning');
                return false;
            }

            // Trouver les informations du contrat
            const contractCard = document.querySelector(`[data-type="${contractType}"]`);
            if (!contractCard) {
                console.error(`❌ Carte de contrat ${contractType} non trouvée`);
                this.showNotification('Erreur: type de contrat non trouvé', 'error');
                return false;
            }

            const contractName = contractCard.dataset.name || this.getContractNameFallback(contractType);
            const contractData = {
                type: contractType,
                name: contractName,
                rank: this.contractRanking.length + 1
            };

            // Ajouter au ranking
            this.contractRanking.push(contractData);
            
            // 🔧 FIX : Mise à jour sécurisée du bouton
            const addButton = contractCard.querySelector('.add-contract-button');
            if (addButton) {
                addButton.disabled = true;
                addButton.innerHTML = '<i class="fas fa-check"></i> Ajouté';
                addButton.classList.add('added');
                addButton.style.opacity = '0.6';
                addButton.style.cursor = 'not-allowed';
            }

            // Mettre à jour l'affichage
            this.updateContractRankingDisplay();
            
            console.log(`✅ Contrat ${contractName} ajouté au rang ${contractData.rank}`);
            this.showNotification(`${contractName} ajouté à votre sélection`, 'success');
            
            return true;
        } catch (error) {
            console.error('❌ Erreur lors de l\'ajout du contrat:', error);
            this.showNotification('Erreur lors de l\'ajout du contrat', 'error');
            return false;
        }
    }

    // 🔧 NOUVEAU : Fallback pour les noms de contrats
    getContractNameFallback(contractType) {
        const contractNames = {
            'cdi': 'CDI (Contrat à Durée Indéterminée)',
            'cdd': 'CDD (Contrat à Durée Déterminée)', 
            'freelance': 'Freelance / Consulting',
            'interim': 'Intérim'
        };
        return contractNames[contractType] || contractType;
    }

    // 🔧 CORRECTION : Méthode de suppression RÉPARÉE
    removeContractFromRanking(contractType) {
        try {
            console.log(`➖ Suppression du contrat: ${contractType}`);

            // Retirer du ranking
            this.contractRanking = this.contractRanking.filter(c => c.type !== contractType);
            
            // Réorganiser les rangs
            this.contractRanking.forEach((contract, index) => {
                contract.rank = index + 1;
            });

            // 🔧 FIX : Réactiver le bouton "Ajouter" de manière sécurisée
            const contractCard = document.querySelector(`[data-type="${contractType}"]`);
            if (contractCard) {
                const addButton = contractCard.querySelector('.add-contract-button');
                if (addButton) {
                    addButton.disabled = false;
                    addButton.innerHTML = '<i class="fas fa-plus"></i> Ajouter';
                    addButton.classList.remove('added');
                    addButton.style.opacity = '1';
                    addButton.style.cursor = 'pointer';
                }
            }

            // Mettre à jour l'affichage
            this.updateContractRankingDisplay();
            
            console.log(`🗑️ Contrat ${contractType} retiré du ranking`);
            this.showNotification('Contrat retiré de votre sélection', 'info');
            
            return true;
        } catch (error) {
            console.error('❌ Erreur lors de la suppression:', error);
            return false;
        }
    }

    // 🔧 CORRECTION : Méthode de déplacement RÉPARÉE
    moveContract(contractType, direction) {
        try {
            const contractIndex = this.contractRanking.findIndex(c => c.type === contractType);
            if (contractIndex === -1) {
                console.warn(`⚠️ Contrat ${contractType} non trouvé dans le ranking`);
                return false;
            }

            let newIndex;
            if (direction === 'up' && contractIndex > 0) {
                newIndex = contractIndex - 1;
            } else if (direction === 'down' && contractIndex < this.contractRanking.length - 1) {
                newIndex = contractIndex + 1;
            } else {
                console.log(`📍 Pas de mouvement possible pour ${contractType} vers ${direction}`);
                return false;
            }

            // Échanger les positions
            [this.contractRanking[contractIndex], this.contractRanking[newIndex]] = 
            [this.contractRanking[newIndex], this.contractRanking[contractIndex]];

            // Réorganiser les rangs
            this.contractRanking.forEach((contract, index) => {
                contract.rank = index + 1;
            });

            // Mettre à jour l'affichage
            this.updateContractRankingDisplay();
            
            console.log(`🔄 Contrat ${contractType} déplacé vers le ${direction}`);
            return true;
        } catch (error) {
            console.error('❌ Erreur lors du déplacement:', error);
            return false;
        }
    }

    // 🔧 CORRECTION : Mise à jour de l'affichage RÉPARÉE
    updateContractRankingDisplay() {
        try {
            const rankingList = document.getElementById('ranking-list');
            const contractSummary = document.getElementById('contract-summary');
            const summaryContent = document.getElementById('summary-content');
            
            if (!rankingList) {
                console.warn('⚠️ Element ranking-list non trouvé');
                return;
            }

            if (this.contractRanking.length === 0) {
                // 🔧 FIX : Affichage sécurisé du message vide
                rankingList.innerHTML = `
                    <div class="ranking-empty">
                        <div class="ranking-empty-icon">
                            <i class="fas fa-hand-pointer"></i>
                        </div>
                        <h5 class="ranking-empty-title">Commencez votre sélection</h5>
                        <p class="ranking-empty-text">
                            Ajoutez les types de contrats qui vous intéressent pour créer votre classement personnalisé
                        </p>
                    </div>
                `;
                
                if (contractSummary) {
                    contractSummary.style.display = 'none';
                }
                
                console.log('📝 Affichage du message vide pour les contrats');
            } else {
                // 🔧 FIX : Affichage sécurisé des contrats classés
                const contractItems = this.contractRanking.map(contract => `
                    <div class="ranking-item" data-type="${contract.type}">
                        <div class="ranking-position">
                            <div class="rank-number">${contract.rank}</div>
                            <div class="rank-controls">
                                <button class="rank-btn rank-up" 
                                        onclick="window.contractSystem.moveContract('${contract.type}', 'up')" 
                                        ${contract.rank === 1 ? 'disabled' : ''}>
                                    <i class="fas fa-chevron-up"></i>
                                </button>
                                <button class="rank-btn rank-down" 
                                        onclick="window.contractSystem.moveContract('${contract.type}', 'down')"
                                        ${contract.rank === this.contractRanking.length ? 'disabled' : ''}>
                                    <i class="fas fa-chevron-down"></i>
                                </button>
                            </div>
                        </div>
                        <div class="ranking-content">
                            <h6 class="ranking-title">${contract.name}</h6>
                            <p class="ranking-description">Position ${contract.rank} dans votre classement</p>
                        </div>
                        <button class="ranking-remove" 
                                onclick="window.contractSystem.removeFromRanking('${contract.type}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `).join('');

                rankingList.innerHTML = contractItems;

                // 🔧 FIX : Affichage sécurisé du résumé
                if (contractSummary && summaryContent) {
                    contractSummary.style.display = 'block';
                    summaryContent.innerHTML = `
                        <div class="summary-stats">
                            <div class="summary-stat">
                                <span class="stat-number">${this.contractRanking.length}</span>
                                <span class="stat-label">type(s) sélectionné(s)</span>
                            </div>
                        </div>
                        <div class="summary-ranking">
                            ${this.contractRanking.map(contract => `
                                <div class="summary-rank-item">
                                    <span class="summary-rank">${contract.rank}</span>
                                    <span class="summary-name">${contract.name}</span>
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
                
                console.log(`📊 Affichage de ${this.contractRanking.length} contrats dans le ranking`);
            }

            // Mettre à jour les champs cachés
            this.updateContractHiddenFields();
        } catch (error) {
            console.error('❌ Erreur mise à jour affichage contrats:', error);
        }
    }

    // 🔧 CORRECTION : Mise à jour des champs cachés RÉPARÉE
    updateContractHiddenFields() {
        try {
            const fields = {
                'contract-ranking-order': this.contractRanking.map(c => c.type).join(','),
                'contract-types-selected': this.contractRanking.map(c => c.name).join(','),
                'contract-preference-level': this.contractRanking.length > 0 ? 'high' : 'none',
                'contract-primary-choice': this.contractRanking.length > 0 ? this.contractRanking[0].type : ''
            };

            Object.entries(fields).forEach(([fieldId, value]) => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.value = value;
                } else {
                    console.warn(`⚠️ Champ caché ${fieldId} non trouvé`);
                }
            });
            
            console.log('✅ Champs cachés mis à jour:', fields);
        } catch (error) {
            console.error('❌ Erreur mise à jour champs cachés:', error);
        }
    }

    // 🔧 CORRECTION : Gestion d'erreurs d'initialisation
    handleInitializationError(error) {
        console.error('❌ Erreur d\'initialisation détectée:', error);
        
        // Réessayer certaines initialisations critiques
        setTimeout(() => {
            console.log('🔄 Tentative de récupération...');
            try {
                if (!window.contractSystem) {
                    this.initializeContractSystem();
                }
                this.initializeTransportAndTravelTime();
            } catch (retryError) {
                console.error('❌ Échec de la récupération:', retryError);
            }
        }, 1000);
    }

    // Navigation entre étapes (inchangée mais sécurisée)
    initializeStepNavigation() {
        console.log('🔄 Initialisation navigation étapes...');
        
        try {
            // Boutons Next
            const nextButtons = [
                { id: 'next-step1', targetStep: 2 },
                { id: 'next-step2', targetStep: 3 },
                { id: 'next-step3', targetStep: 4 }
            ];
            
            nextButtons.forEach(({ id, targetStep }) => {
                const btn = document.getElementById(id);
                if (btn) {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        console.log(`⚡ Clic sur ${id} → Étape ${targetStep}`);
                        if (this.validateStep(targetStep - 1)) {
                            this.goToStep(targetStep);
                        }
                    });
                } else {
                    console.warn(`⚠️ Bouton ${id} non trouvé`);
                }
            });

            // Boutons Back
            const backButtons = [
                { id: 'back-step1', targetStep: 1 },
                { id: 'back-step2', targetStep: 2 },
                { id: 'back-step3', targetStep: 3 }
            ];
            
            backButtons.forEach(({ id, targetStep }) => {
                const btn = document.getElementById(id);
                if (btn) {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        console.log(`⚡ Retour ${id} → Étape ${targetStep}`);
                        this.goToStep(targetStep);
                    });
                }
            });

            console.log('✅ Navigation initialisée');
        } catch (error) {
            console.error('❌ Erreur navigation:', error);
        }
    }

    goToStep(stepNumber) {
        if (stepNumber < 1 || stepNumber > this.totalSteps) {
            console.warn(`⚠️ Étape ${stepNumber} invalide`);
            return;
        }
        
        console.log(`🎯 Navigation: ${this.currentStep} → ${stepNumber}`);
        
        // Masquer toutes les étapes
        for (let i = 1; i <= this.totalSteps; i++) {
            const step = document.getElementById(`form-step${i}`);
            if (step) {
                step.style.display = 'none';
                step.classList.remove('active');
            }
        }
        
        // Afficher l'étape cible
        const targetStep = document.getElementById(`form-step${stepNumber}`);
        if (targetStep) {
            targetStep.style.display = 'block';
            targetStep.classList.add('active');
            
            // Scroll vers l'étape
            setTimeout(() => {
                targetStep.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);
            
            console.log(`✅ Étape ${stepNumber} affichée`);
        } else {
            console.error(`❌ Impossible de trouver l'étape ${stepNumber}`);
        }
        
        this.currentStep = stepNumber;
        this.updateStepIndicator();
    }

    validateStep(step) {
        try {
            switch(step) {
                case 1:
                    const name = document.getElementById('full-name')?.value;
                    const job = document.getElementById('job-title')?.value;
                    
                    if (!name || !job) {
                        this.showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
                        return false;
                    }
                    return true;
                    
                case 2:
                    const transport = document.querySelector('input[name="transport-method"]:checked');
                    const office = document.querySelector('input[name="office-preference"]:checked');
                    
                    if (!transport) {
                        this.showNotification('Veuillez sélectionner au moins un mode de transport', 'warning');
                        return false;
                    }
                    if (!office) {
                        this.showNotification('Veuillez sélectionner votre préférence d\'environnement', 'warning');
                        return false;
                    }
                    return true;
                    
                case 3:
                    if (this.selectedMotivations.length === 0) {
                        this.showNotification('Veuillez sélectionner au moins une motivation', 'warning');
                        return false;
                    }
                    return true;
                    
                case 4:
                    if (!this.step4Data.timing || !this.step4Data.employmentStatus) {
                        this.showNotification('Veuillez répondre à toutes les questions obligatoires', 'warning');
                        return false;
                    }
                    return true;
                    
                default:
                    return true;
            }
        } catch (error) {
            console.error('❌ Erreur validation:', error);
            return false;
        }
    }

    updateStepIndicator() {
        try {
            document.querySelectorAll('.step').forEach((step, index) => {
                const stepNum = index + 1;
                step.classList.remove('active', 'completed');
                
                if (stepNum < this.currentStep) {
                    step.classList.add('completed');
                } else if (stepNum === this.currentStep) {
                    step.classList.add('active');
                }
            });

            // Mise à jour de la barre de progression
            const progress = ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
            const progressBar = document.getElementById('stepper-progress');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
        } catch (error) {
            console.error('❌ Erreur mise à jour indicateur:', error);
        }
    }

    // Notifications améliorées
    showNotification(message, type = 'info') {
        try {
            // Supprimer les anciennes notifications
            document.querySelectorAll('.nexten-v3-notification').forEach(n => n.remove());
            
            const notification = document.createElement('div');
            notification.className = `nexten-v3-notification ${type}`;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${this.getNotificationColor(type)};
                color: white;
                padding: 16px 24px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                z-index: 10000;
                font-weight: 500;
                font-size: 14px;
                max-width: 400px;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
            `;
            notification.innerHTML = `
                <i class="fas fa-${this.getNotificationIcon(type)}" style="margin-right: 8px;"></i>
                <span>${message}</span>
            `;
            
            document.body.appendChild(notification);
            
            // Animation d'entrée
            setTimeout(() => {
                notification.style.opacity = '1';
                notification.style.transform = 'translateX(0)';
            }, 100);
            
            // Animation de sortie
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }, 4000);
        } catch (error) {
            console.error('❌ Erreur notification:', error);
            // Fallback
            alert(message);
        }
    }

    getNotificationColor(type) {
        const colors = {
            'success': 'linear-gradient(135deg, #10b981, #059669)',
            'warning': 'linear-gradient(135deg, #f59e0b, #d97706)',
            'error': 'linear-gradient(135deg, #ef4444, #dc2626)',
            'info': 'linear-gradient(135deg, #3b82f6, #2563eb)'
        };
        return colors[type] || colors.info;
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Stubs pour les autres méthodes (pour éviter les erreurs)
    initializeMotivationRanking() { console.log('🎯 Motivation ranking - stub'); }
    initializeSecteurSelectors() { console.log('🏭 Secteur selectors - stub'); }
    initializeSalaryControls() { console.log('💰 Salary controls - stub'); }
    initializeModernOptions() { console.log('⚙️ Modern options - stub'); }
    initializeStep4Logic() { console.log('🚀 Step 4 logic - stub'); }
    handleDemoMode() { console.log('🎭 Demo mode - stub'); }
}

// 🚀 Initialisation globale SÉCURISÉE
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Démarrage NEXTEN V3.0 - VERSION CORRIGÉE');
    
    try {
        // Nettoyer les anciennes instances
        if (window.nextenQuestionnaire) {
            console.log('🧹 Nettoyage ancienne instance');
            delete window.nextenQuestionnaire;
        }
        if (window.contractSystem) {
            console.log('🧹 Nettoyage ancien contractSystem');
            delete window.contractSystem;
        }
        
        // Attendre que tous les scripts soient chargés
        setTimeout(() => {
            window.nextenQuestionnaire = new NextenQuestionnaire();
            console.log('✅ NEXTEN V3.0 CORRIGÉ initialisé avec succès');
        }, 500);
    } catch (error) {
        console.error('❌ Erreur lors de l\'initialisation globale:', error);
        
        // Fallback d'urgence
        setTimeout(() => {
            try {
                window.nextenQuestionnaire = new NextenQuestionnaire();
            } catch (fallbackError) {
                console.error('❌ Échec du fallback:', fallbackError);
            }
        }, 2000);
    }
});

// Export pour utilisation externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenQuestionnaire;
}