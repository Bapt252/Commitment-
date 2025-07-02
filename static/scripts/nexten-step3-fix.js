/**
 * 🔧 CORRECTION COMPLÈTE ÉTAPE 3 - NEXTEN QUESTIONNAIRE
 * Répare les fonctionnalités manquantes : motivations, secteurs, fourchette salariale
 */

(function() {
    'use strict';

    console.log('🔧 Chargement correction étape 3...');

    // ===== VARIABLES GLOBALES =====
    let step3Data = {
        motivations: [],
        motivationRanking: [],
        selectedSecteurs: [],
        selectedRedhibitoires: [],
        salaryMin: 40,
        salaryMax: 45,
        aspirations: ''
    };

    // Liste complète des secteurs
    const secteursList = [
        { id: 'tech', name: 'Technologie / Informatique', icon: 'fas fa-laptop-code', description: 'Développement, data science, cybersécurité...' },
        { id: 'finance', name: 'Finance / Banque / Assurance', icon: 'fas fa-chart-line', description: 'Services financiers, trading, assurance...' },
        { id: 'sante', name: 'Santé / Pharmaceutique', icon: 'fas fa-heartbeat', description: 'Médical, recherche pharmaceutique, biotechs...' },
        { id: 'education', name: 'Éducation / Formation', icon: 'fas fa-graduation-cap', description: 'Enseignement, formation professionnelle...' },
        { id: 'industrie', name: 'Industrie / Manufacturing', icon: 'fas fa-industry', description: 'Production, automatisation, qualité...' },
        { id: 'commerce', name: 'Commerce / Retail', icon: 'fas fa-shopping-cart', description: 'Vente, distribution, e-commerce...' },
        { id: 'automobile', name: 'Automobile', icon: 'fas fa-car', description: 'Constructeurs, équipementiers, mobilité...' },
        { id: 'energie', name: 'Énergie / Utilities', icon: 'fas fa-bolt', description: 'Électricité, renouvelables, pétrole/gaz...' },
        { id: 'medias', name: 'Médias / Communication', icon: 'fas fa-broadcast-tower', description: 'Presse, TV, radio, marketing...' },
        { id: 'telecoms', name: 'Télécommunications', icon: 'fas fa-wifi', description: 'Réseaux, mobile, internet...' },
        { id: 'immobilier', name: 'Immobilier', icon: 'fas fa-building', description: 'Promotion, gestion, investissement...' },
        { id: 'tourisme', name: 'Tourisme / Hôtellerie', icon: 'fas fa-plane', description: 'Voyages, hôtels, restauration...' },
        { id: 'agriculture', name: 'Agriculture / Agroalimentaire', icon: 'fas fa-seedling', description: 'Production agricole, transformation...' },
        { id: 'btp', name: 'BTP / Construction', icon: 'fas fa-hard-hat', description: 'Bâtiment, travaux publics, génie civil...' },
        { id: 'logistique', name: 'Logistique / Transport', icon: 'fas fa-truck', description: 'Supply chain, fret, entreposage...' },
        { id: 'consulting', name: 'Consulting / Services professionnels', icon: 'fas fa-briefcase', description: 'Conseil en management, audit...' },
        { id: 'ecommerce', name: 'E-commerce / Digital', icon: 'fas fa-shopping-bag', description: 'Commerce en ligne, marketplaces...' },
        { id: 'biotech', name: 'Biotechnologie', icon: 'fas fa-dna', description: 'Recherche biologique, génomique...' },
        { id: 'aeronautique', name: 'Aéronautique / Spatial', icon: 'fas fa-rocket', description: 'Aviation, spatial, défense...' },
        { id: 'mode', name: 'Mode / Luxe', icon: 'fas fa-gem', description: 'Textile, cosmétiques, maroquinerie...' },
        { id: 'sports', name: 'Sports / Loisirs', icon: 'fas fa-futbol', description: 'Équipements sportifs, divertissement...' },
        { id: 'juridique', name: 'Juridique', icon: 'fas fa-gavel', description: 'Cabinets d\'avocats, services juridiques...' },
        { id: 'culture', name: 'Art / Culture', icon: 'fas fa-palette', description: 'Musées, spectacles, édition...' },
        { id: 'environnement', name: 'Environnement / Développement durable', icon: 'fas fa-leaf', description: 'Écologie, recyclage, énergies vertes...' },
        { id: 'recherche', name: 'Recherche & Développement', icon: 'fas fa-microscope', description: 'Innovation, laboratoires, R&D...' },
        { id: 'securite', name: 'Sécurité', icon: 'fas fa-shield-alt', description: 'Sécurité privée, surveillance...' },
        { id: 'public', name: 'Administration publique', icon: 'fas fa-landmark', description: 'Fonction publique, collectivités...' },
        { id: 'ong', name: 'ONG / Associations', icon: 'fas fa-hands-helping', description: 'Humanitaire, social, environnement...' }
    ];

    // ===== INITIALISATION PRINCIPALE =====
    function initStep3Fix() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', performStep3Fix);
        } else {
            setTimeout(performStep3Fix, 100);
        }
    }

    function performStep3Fix() {
        try {
            console.log('🔧 Démarrage réparation étape 3...');
            
            initializeMotivationRankingFixed();
            initializeSecteurSelectorsFixed();
            initializeSalaryControlsFixed();
            setupStep3Navigation();
            
            console.log('✅ Étape 3 réparée avec succès !');
        } catch (error) {
            console.error('❌ Erreur réparation étape 3:', error);
        }
    }

    // ===== 1. SYSTÈME DE CLASSEMENT DES MOTIVATIONS =====
    function initializeMotivationRankingFixed() {
        console.log('🎯 Initialisation classement motivations...');
        
        const motivationCards = document.querySelectorAll('.motivation-card');
        const motivationCounter = document.getElementById('motivation-counter');
        const motivationSummary = document.getElementById('motivation-summary');
        const summaryList = document.getElementById('summary-list');
        const autreField = document.getElementById('autre-field');
        const autreTextarea = document.getElementById('autre-motivation-text');

        if (!motivationCards.length) {
            console.warn('⚠️ Cartes de motivation non trouvées');
            return;
        }

        // Event listeners sur les cartes de motivation
        motivationCards.forEach(card => {
            card.addEventListener('click', function() {
                handleMotivationClick(this);
            });

            // Support clavier
            card.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleMotivationClick(this);
                }
            });
        });

        // Event listener sur le textarea "Autre"
        if (autreTextarea) {
            autreTextarea.addEventListener('input', function() {
                updateMotivationData();
            });
        }

        function handleMotivationClick(card) {
            const motivation = card.dataset.motivation;
            const isSelected = card.classList.contains('selected');
            
            if (isSelected) {
                // Déselectionner
                deselectMotivation(motivation, card);
            } else {
                // Sélectionner (max 3)
                if (step3Data.motivationRanking.length < 3) {
                    selectMotivation(motivation, card);
                } else {
                    showNotification('Vous pouvez sélectionner maximum 3 motivations', 'warning');
                    return;
                }
            }
            
            updateMotivationDisplay();
            updateMotivationData();
        }

        function selectMotivation(motivation, card) {
            const rank = step3Data.motivationRanking.length + 1;
            step3Data.motivationRanking.push({ motivation, rank });
            
            card.classList.add('selected');
            const badge = card.querySelector('.ranking-badge');
            if (badge) {
                badge.textContent = rank;
                badge.className = `ranking-badge rank-${rank}`;
            }

            // Montrer le champ "Autre" si nécessaire
            if (motivation === 'autre' && autreField) {
                autreField.classList.add('active');
                if (autreTextarea) {
                    setTimeout(() => autreTextarea.focus(), 300);
                }
            }

            // Animation
            card.style.transform = 'scale(1.05)';
            setTimeout(() => {
                card.style.transform = '';
            }, 200);
        }

        function deselectMotivation(motivation, card) {
            const index = step3Data.motivationRanking.findIndex(m => m.motivation === motivation);
            if (index !== -1) {
                step3Data.motivationRanking.splice(index, 1);
                // Réorganiser les rangs
                step3Data.motivationRanking.forEach((m, i) => m.rank = i + 1);
            }
            
            card.classList.remove('selected');
            
            // Masquer le champ "Autre" si nécessaire
            if (motivation === 'autre' && autreField) {
                autreField.classList.remove('active');
                if (autreTextarea) {
                    autreTextarea.value = '';
                }
            }

            // Mettre à jour tous les badges
            motivationCards.forEach(c => {
                const m = c.dataset.motivation;
                const found = step3Data.motivationRanking.find(mr => mr.motivation === m);
                const badge = c.querySelector('.ranking-badge');
                if (found && badge) {
                    badge.textContent = found.rank;
                    badge.className = `ranking-badge rank-${found.rank}`;
                }
            });
        }

        function updateMotivationDisplay() {
            // Compteur
            if (motivationCounter) {
                motivationCounter.textContent = `${step3Data.motivationRanking.length} / 3 sélectionnées`;
            }

            // Résumé
            if (step3Data.motivationRanking.length > 0) {
                if (motivationSummary) motivationSummary.classList.add('active');
                
                if (summaryList) {
                    const summaryHTML = step3Data.motivationRanking
                        .sort((a, b) => a.rank - b.rank)
                        .map(m => {
                            const card = document.querySelector(`[data-motivation="${m.motivation}"]`);
                            const title = card ? card.querySelector('.card-title')?.textContent || m.motivation : m.motivation;
                            return `
                                <div class="summary-item">
                                    <div class="summary-rank">${m.rank}</div>
                                    <span>${title}</span>
                                </div>
                            `;
                        })
                        .join('');
                    summaryList.innerHTML = summaryHTML;
                }
            } else {
                if (motivationSummary) motivationSummary.classList.remove('active');
            }

            // Désactiver les cartes non sélectionnées si on a atteint le max
            motivationCards.forEach(card => {
                if (step3Data.motivationRanking.length >= 3 && !card.classList.contains('selected')) {
                    card.classList.add('disabled');
                } else {
                    card.classList.remove('disabled');
                }
            });
        }

        function updateMotivationData() {
            // Mettre à jour les champs cachés
            const hiddenMotivations = document.getElementById('hidden-motivations');
            const hiddenRanking = document.getElementById('hidden-motivations-ranking');
            
            if (hiddenMotivations) {
                hiddenMotivations.value = step3Data.motivationRanking.map(m => m.motivation).join(',');
            }
            if (hiddenRanking) {
                hiddenRanking.value = JSON.stringify(step3Data.motivationRanking);
            }

            // Aspirations
            const aspirationsField = document.getElementById('aspirations');
            if (aspirationsField) {
                step3Data.aspirations = aspirationsField.value;
            }

            // Texte "Autre"
            if (autreTextarea) {
                step3Data.autreMotivationText = autreTextarea.value;
            }
        }

        console.log('✅ Système de motivation initialisé');
    }

    // ===== 2. SYSTÈME DE SÉLECTION DES SECTEURS =====
    function initializeSecteurSelectorsFixed() {
        console.log('🏭 Initialisation sélecteurs secteurs...');

        // Initialiser les dropdowns
        initializeSecteurDropdown('secteurs', false);
        initializeSecteurDropdown('redhibitoires', true);

        function initializeSecteurDropdown(type, isRedhibitoire) {
            const optionsContainer = document.getElementById(`${type}-options`);
            const searchInput = document.getElementById(`${type}-search`);
            const counter = document.getElementById(`${type}-counter`);
            const selectedContainer = document.getElementById(`${type}-selected`);
            const tagsContainer = document.getElementById(`${type}-tags`);

            if (!optionsContainer) {
                console.warn(`⚠️ Conteneur ${type} non trouvé`);
                return;
            }

            // Générer les options
            generateSecteurOptions(optionsContainer, type, isRedhibitoire);

            // Search functionality
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    filterSecteurOptions(this.value, optionsContainer);
                });
            }

            // Mettre à jour l'affichage initial
            updateSecteurDisplay(type, isRedhibitoire);
        }

        function generateSecteurOptions(container, type, isRedhibitoire) {
            const optionsHTML = secteursList.map(secteur => {
                const isSelected = isRedhibitoire ? 
                    step3Data.selectedRedhibitoires.includes(secteur.id) :
                    step3Data.selectedSecteurs.includes(secteur.id);
                
                return `
                    <div class="dropdown-option ${isSelected ? 'selected' : ''}" 
                         data-secteur="${secteur.id}" 
                         data-type="${type}">
                        <div class="option-checkbox">
                            ${isSelected ? '<i class="fas fa-check"></i>' : ''}
                        </div>
                        <div class="option-icon">
                            <i class="${secteur.icon}"></i>
                        </div>
                        <div class="option-content">
                            <div class="option-name">${secteur.name}</div>
                            <div class="option-description">${secteur.description}</div>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = optionsHTML;

            // Event listeners
            container.querySelectorAll('.dropdown-option').forEach(option => {
                option.addEventListener('click', function() {
                    handleSecteurClick(this, type, isRedhibitoire);
                });
            });
        }

        function handleSecteurClick(option, type, isRedhibitoire) {
            const secteurId = option.dataset.secteur;
            const isSelected = option.classList.contains('selected');
            const targetArray = isRedhibitoire ? step3Data.selectedRedhibitoires : step3Data.selectedSecteurs;
            const conflictArray = isRedhibitoire ? step3Data.selectedSecteurs : step3Data.selectedRedhibitoires;

            if (isSelected) {
                // Déselectionner
                const index = targetArray.indexOf(secteurId);
                if (index !== -1) {
                    targetArray.splice(index, 1);
                }
                option.classList.remove('selected');
                option.querySelector('.option-checkbox').innerHTML = '';
            } else {
                // Vérifier les conflits
                if (conflictArray.includes(secteurId)) {
                    const conflictWarning = document.getElementById('conflict-warning');
                    if (conflictWarning) {
                        conflictWarning.classList.add('active');
                        setTimeout(() => conflictWarning.classList.remove('active'), 5000);
                    }
                    showNotification('Ce secteur est déjà sélectionné dans l\'autre catégorie', 'warning');
                    return;
                }

                // Sélectionner
                targetArray.push(secteurId);
                option.classList.add('selected');
                option.querySelector('.option-checkbox').innerHTML = '<i class="fas fa-check"></i>';
            }

            updateSecteurDisplay(type, isRedhibitoire);
            updateSecteurData();
        }

        function filterSecteurOptions(searchTerm, container) {
            const options = container.querySelectorAll('.dropdown-option');
            const term = searchTerm.toLowerCase();

            options.forEach(option => {
                const name = option.querySelector('.option-name').textContent.toLowerCase();
                const description = option.querySelector('.option-description').textContent.toLowerCase();
                
                if (name.includes(term) || description.includes(term)) {
                    option.style.display = 'flex';
                } else {
                    option.style.display = 'none';
                }
            });
        }

        function updateSecteurDisplay(type, isRedhibitoire) {
            const targetArray = isRedhibitoire ? step3Data.selectedRedhibitoires : step3Data.selectedSecteurs;
            const counter = document.getElementById(`${type}-counter`);
            const selectedContainer = document.getElementById(`${type}-selected`);
            const tagsContainer = document.getElementById(`${type}-tags`);

            // Compteur
            if (counter) {
                const count = targetArray.length;
                if (isRedhibitoire) {
                    counter.textContent = `${count} exclus`;
                } else {
                    counter.textContent = `${count} sélectionnés`;
                }
            }

            // Tags
            if (tagsContainer) {
                const tagsHTML = targetArray.map(secteurId => {
                    const secteur = secteursList.find(s => s.id === secteurId);
                    if (!secteur) return '';
                    
                    return `
                        <div class="sector-tag" data-secteur="${secteurId}">
                            <span>${secteur.name}</span>
                            <i class="fas fa-times remove-tag" onclick="removeSecteurTag('${secteurId}', '${type}', ${isRedhibitoire})"></i>
                        </div>
                    `;
                }).join('');
                
                tagsContainer.innerHTML = tagsHTML;
            }

            // Affichage du conteneur
            if (selectedContainer) {
                if (targetArray.length > 0) {
                    selectedContainer.classList.add('active');
                } else {
                    selectedContainer.classList.remove('active');
                }
            }
        }

        // Fonction globale pour supprimer un tag
        window.removeSecteurTag = function(secteurId, type, isRedhibitoire) {
            const targetArray = isRedhibitoire ? step3Data.selectedRedhibitoires : step3Data.selectedSecteurs;
            const index = targetArray.indexOf(secteurId);
            if (index !== -1) {
                targetArray.splice(index, 1);
            }

            // Mettre à jour l'option correspondante
            const option = document.querySelector(`[data-secteur="${secteurId}"][data-type="${type}"]`);
            if (option) {
                option.classList.remove('selected');
                option.querySelector('.option-checkbox').innerHTML = '';
            }

            updateSecteurDisplay(type, isRedhibitoire);
            updateSecteurData();
        };

        function updateSecteurData() {
            const hiddenSecteurs = document.getElementById('hidden-secteurs');
            const hiddenRedhibitoires = document.getElementById('hidden-secteurs-redhibitoires');

            if (hiddenSecteurs) {
                hiddenSecteurs.value = step3Data.selectedSecteurs.join(',');
            }
            if (hiddenRedhibitoires) {
                hiddenRedhibitoires.value = step3Data.selectedRedhibitoires.join(',');
            }
        }

        console.log('✅ Sélecteurs secteurs initialisés');
    }

    // ===== 3. CONTRÔLES DE FOURCHETTE SALARIALE =====
    function initializeSalaryControlsFixed() {
        console.log('💰 Initialisation contrôles salaire...');

        const salaryMinInput = document.getElementById('salary-min');
        const salaryMaxInput = document.getElementById('salary-max');
        const salarySliderMin = document.getElementById('salary-slider-min');
        const salarySliderMax = document.getElementById('salary-slider-max');
        const salaryDisplay = document.getElementById('salary-display');
        const salaryValidation = document.getElementById('salary-validation');
        const salaryMinGroup = document.getElementById('salary-min-group');
        const salaryMaxGroup = document.getElementById('salary-max-group');

        if (!salaryMinInput || !salaryMaxInput) {
            console.warn('⚠️ Champs salaire non trouvés');
            return;
        }

        // Synchronisation inputs et sliders
        function syncValues() {
            const min = parseInt(salaryMinInput.value) || 20;
            const max = parseInt(salaryMaxInput.value) || 200;

            // Validation
            const isValid = min < max;
            
            if (isValid) {
                step3Data.salaryMin = min;
                step3Data.salaryMax = max;
                
                // Mettre à jour les sliders
                if (salarySliderMin) salarySliderMin.value = min;
                if (salarySliderMax) salarySliderMax.value = max;
                
                // Mettre à jour l'affichage
                if (salaryDisplay) {
                    salaryDisplay.textContent = `Entre ${min}K et ${max}K €`;
                }
                
                // Supprimer les erreurs
                if (salaryValidation) salaryValidation.classList.remove('active');
                if (salaryMinGroup) salaryMinGroup.classList.remove('error');
                if (salaryMaxGroup) salaryMaxGroup.classList.remove('error');
            } else {
                // Afficher l'erreur
                if (salaryValidation) salaryValidation.classList.add('active');
                if (salaryMinGroup) salaryMinGroup.classList.add('error');
                if (salaryMaxGroup) salaryMaxGroup.classList.add('error');
            }

            updateSalaryData();
        }

        // Event listeners
        [salaryMinInput, salaryMaxInput, salarySliderMin, salarySliderMax].forEach(element => {
            if (element) {
                element.addEventListener('input', function() {
                    if (this === salarySliderMin) {
                        salaryMinInput.value = this.value;
                    } else if (this === salarySliderMax) {
                        salaryMaxInput.value = this.value;
                    } else if (this === salaryMinInput) {
                        if (salarySliderMin) salarySliderMin.value = this.value;
                    } else if (this === salaryMaxInput) {
                        if (salarySliderMax) salarySliderMax.value = this.value;
                    }
                    syncValues();
                });
            }
        });

        // Focus management
        [salaryMinInput, salaryMaxInput].forEach(input => {
            if (input) {
                input.addEventListener('focus', function() {
                    this.closest('.salary-input-group')?.classList.add('focused');
                });
                input.addEventListener('blur', function() {
                    this.closest('.salary-input-group')?.classList.remove('focused');
                });
            }
        });

        // Suggestions de fourchettes
        document.querySelectorAll('.salary-suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', function() {
                const min = parseInt(this.dataset.min);
                const max = parseInt(this.dataset.max);
                
                salaryMinInput.value = min;
                salaryMaxInput.value = max;
                syncValues();
                
                showNotification(`Fourchette ${min}-${max}K € sélectionnée`, 'success');
            });
        });

        function updateSalaryData() {
            const hiddenSalaryMin = document.getElementById('hidden-salary-min');
            const hiddenSalaryMax = document.getElementById('hidden-salary-max');
            const hiddenSalaryRange = document.getElementById('hidden-salary-range');

            if (hiddenSalaryMin) hiddenSalaryMin.value = step3Data.salaryMin;
            if (hiddenSalaryMax) hiddenSalaryMax.value = step3Data.salaryMax;
            if (hiddenSalaryRange) {
                hiddenSalaryRange.value = `${step3Data.salaryMin}000-${step3Data.salaryMax}000`;
            }
        }

        // Initialisation
        syncValues();
        
        console.log('✅ Contrôles salaire initialisés');
    }

    // ===== 4. NAVIGATION ÉTAPE 3 =====
    function setupStep3Navigation() {
        const nextBtn = document.getElementById('next-step3');
        const backBtn = document.getElementById('back-step2');

        if (nextBtn) {
            nextBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (validateStep3()) {
                    // Navigation gérée par le système principal
                    if (typeof window.nextenQuestionnaire?.goToStep === 'function') {
                        window.nextenQuestionnaire.goToStep(4);
                    } else {
                        showNotification('Navigation vers l\'étape 4...', 'info');
                    }
                }
            });
        }

        if (backBtn) {
            backBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (typeof window.nextenQuestionnaire?.goToStep === 'function') {
                    window.nextenQuestionnaire.goToStep(2);
                }
            });
        }
    }

    // ===== 5. VALIDATION ÉTAPE 3 =====
    function validateStep3() {
        const errors = [];

        // Vérifier motivations
        if (step3Data.motivationRanking.length === 0) {
            errors.push('Veuillez sélectionner au moins une motivation professionnelle');
        }

        // Vérifier secteurs
        if (step3Data.selectedSecteurs.length === 0) {
            errors.push('Veuillez sélectionner au moins un secteur d\'activité');
        }

        // Vérifier fourchette salariale
        if (step3Data.salaryMin >= step3Data.salaryMax) {
            errors.push('Le salaire maximum doit être supérieur au salaire minimum');
        }

        // Afficher les erreurs
        if (errors.length > 0) {
            errors.forEach(error => showNotification(error, 'error'));
            return false;
        }

        console.log('✅ Étape 3 validée', step3Data);
        showNotification('Étape 3 complétée avec succès !', 'success');
        return true;
    }

    // ===== 6. UTILITAIRES =====
    function showNotification(message, type = 'info') {
        // Utiliser le système de notification existant si disponible
        if (typeof window.nextenQuestionnaire?.showNotification === 'function') {
            window.nextenQuestionnaire.showNotification(message, type);
        } else if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            // Fallback simple
            console.log(`${type.toUpperCase()}: ${message}`);
            
            // Notification visuelle simple
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed; top: 20px; right: 20px; z-index: 10000;
                background: ${type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : type === 'success' ? '#10b981' : '#3b82f6'};
                color: white; padding: 12px 20px; border-radius: 8px;
                font-size: 14px; font-weight: 500;
                transition: all 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
    }

    // ===== 7. EXPOSITION GLOBALE =====
    window.step3Fix = {
        init: initStep3Fix,
        validate: validateStep3,
        getData: () => step3Data,
        reset: () => {
            step3Data = {
                motivations: [],
                motivationRanking: [],
                selectedSecteurs: [],
                selectedRedhibitoires: [],
                salaryMin: 40,
                salaryMax: 45,
                aspirations: ''
            };
        }
    };

    // ===== 8. AUTO-INITIALISATION =====
    initStep3Fix();

    console.log('✅ Correction étape 3 chargée');

})();