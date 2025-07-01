// ====== NEXTEN V2.0 - JAVASCRIPT ÉTAPES 3 & 4 ======
// Système d'interactions pour les motivations, secteurs et disponibilité

(function() {
    'use strict';

    console.log('🚀 Chargement script NEXTEN Steps 3 & 4...');

    // Variables globales
    let isInitialized = false;
    let formData = {
        step3: {
            motivations: [],
            secteurs: [],
            salaire: 45000,
            aspirations: ''
        },
        step4: {
            situation: null,
            disponibilite: null,
            modesTravail: [],
            typesEntreprise: [],
            contraintes: ''
        }
    };

    // ====== INITIALISATION PRINCIPALE ======
    function initializeSteps34() {
        if (isInitialized) {
            console.log('⚠️ Scripts étapes 3 & 4 déjà initialisés');
            return;
        }

        console.log('🔧 Initialisation des étapes 3 & 4...');

        try {
            // Attendre que le DOM soit complètement chargé
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    setTimeout(performInitialization, 100);
                });
            } else {
                setTimeout(performInitialization, 100);
            }
        } catch (error) {
            console.error('❌ Erreur initialisation étapes 3 & 4:', error);
        }
    }

    function performInitialization() {
        try {
            // Initialiser les interactions
            initializeFormInteractions();
            initializeSalarySlider();
            setupValidation();
            setupDataCollection();
            enhanceNavigationForSteps34();

            isInitialized = true;
            console.log('✅ Étapes 3 & 4 initialisées avec succès');

            // Exposer les fonctions globalement
            window.NEXTEN_Steps34 = {
                collectData: collectAllData,
                validateStep3: validateStep3,
                validateStep4: validateStep4,
                resetStep: resetStep,
                getFormData: () => formData
            };

        } catch (error) {
            console.error('❌ Erreur lors de l\'initialisation:', error);
        }
    }

    // ====== GESTION DES INTERACTIONS CHECKBOX/RADIO ======
    function initializeFormInteractions() {
        console.log('🎯 Initialisation des interactions formulaire...');

        // Sélectionner tous les éléments checkbox et radio des nouvelles étapes
        const checkboxItems = document.querySelectorAll('.checkbox-item');
        const radioItems = document.querySelectorAll('.radio-item');

        // Gestion des checkbox-item (étapes 3 & 4)
        checkboxItems.forEach(item => {
            item.addEventListener('click', function(e) {
                handleCheckboxItemClick(this, e);
            });

            // Empêcher la propagation sur l'input lui-même
            const input = item.querySelector('input[type="checkbox"]');
            if (input) {
                input.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
        });

        // Gestion des radio-item (étapes 3 & 4)
        radioItems.forEach(item => {
            item.addEventListener('click', function(e) {
                handleRadioItemClick(this, e);
            });

            // Empêcher la propagation sur l'input lui-même
            const input = item.querySelector('input[type="radio"]');
            if (input) {
                input.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
        });

        console.log(`✅ ${checkboxItems.length} checkbox-items et ${radioItems.length} radio-items configurés`);
    }

    function handleCheckboxItemClick(item, event) {
        const input = item.querySelector('input[type="checkbox"]');
        if (!input) return;

        // Toggle l'état
        input.checked = !input.checked;
        
        // Mettre à jour l'apparence visuelle
        item.classList.toggle('selected', input.checked);
        
        // Mettre à jour les données
        updateFormData();
        
        // Log pour debugging
        console.log(`Checkbox ${input.name}=${input.value}: ${input.checked ? 'sélectionné' : 'désélectionné'}`);
        
        // Empêcher la propagation
        event.preventDefault();
        event.stopPropagation();

        // Animation subtile
        if (input.checked) {
            item.style.transform = 'scale(1.02)';
            setTimeout(() => {
                item.style.transform = '';
            }, 150);
        }
    }

    function handleRadioItemClick(item, event) {
        const input = item.querySelector('input[type="radio"]');
        if (!input) return;

        // Déselectionner tous les autres radios du même groupe
        const groupName = input.name;
        document.querySelectorAll(`input[name="${groupName}"]`).forEach(radio => {
            const parentItem = radio.closest('.radio-item');
            if (parentItem) {
                parentItem.classList.remove('selected');
                radio.checked = false;
            }
        });

        // Sélectionner le radio cliqué
        input.checked = true;
        item.classList.add('selected');
        
        // Mettre à jour les données
        updateFormData();
        
        // Log pour debugging
        console.log(`Radio ${groupName}: ${input.value} sélectionné`);
        
        // Empêcher la propagation
        event.preventDefault();
        event.stopPropagation();

        // Animation subtile
        item.style.transform = 'scale(1.02)';
        setTimeout(() => {
            item.style.transform = '';
        }, 150);
    }

    // ====== GESTION DU SLIDER DE SALAIRE ======
    function initializeSalarySlider() {
        const salarySlider = document.getElementById('salary-range');
        const salaryDisplay = document.getElementById('salary-display');
        
        if (!salarySlider || !salaryDisplay) {
            console.log('ℹ️ Slider de salaire non trouvé (normal si pas sur étape 3)');
            return;
        }

        console.log('💰 Initialisation du slider de salaire...');

        // Fonction de mise à jour de l'affichage
        function updateSalaryDisplay() {
            const value = parseInt(salarySlider.value);
            let formattedValue;
            
            if (value >= 120000) {
                formattedValue = '120K+ €';
            } else {
                formattedValue = `${(value / 1000).toFixed(0)} 000 €`;
            }
            
            salaryDisplay.textContent = formattedValue;
            
            // Mettre à jour les données
            formData.step3.salaire = value;
            
            console.log(`💰 Salaire sélectionné: ${formattedValue} (${value})`);
        }
        
        // Event listeners
        salarySlider.addEventListener('input', updateSalaryDisplay);
        salarySlider.addEventListener('change', updateSalaryDisplay);
        
        // Initialisation de l'affichage
        updateSalaryDisplay();
        
        console.log('✅ Slider de salaire configuré');
    }

    // ====== MISE À JOUR DES DONNÉES ======
    function updateFormData() {
        try {
            // Étape 3 - Motivations
            const motivations = Array.from(document.querySelectorAll('input[name="motivations"]:checked'))
                .map(input => input.value);
            formData.step3.motivations = motivations;

            // Étape 3 - Secteurs
            const secteurs = Array.from(document.querySelectorAll('input[name="secteurs"]:checked'))
                .map(input => input.value);
            formData.step3.secteurs = secteurs;

            // Étape 3 - Aspirations
            const aspirationsField = document.getElementById('aspirations');
            if (aspirationsField) {
                formData.step3.aspirations = aspirationsField.value.trim();
            }

            // Étape 4 - Situation professionnelle
            const situationRadio = document.querySelector('input[name="situation"]:checked');
            formData.step4.situation = situationRadio ? situationRadio.value : null;

            // Étape 4 - Disponibilité
            const disponibiliteRadio = document.querySelector('input[name="disponibilite"]:checked');
            formData.step4.disponibilite = disponibiliteRadio ? disponibiliteRadio.value : null;

            // Étape 4 - Modes de travail
            const modesTravail = Array.from(document.querySelectorAll('input[name="modes-travail"]:checked'))
                .map(input => input.value);
            formData.step4.modesTravail = modesTravail;

            // Étape 4 - Types d'entreprise
            const typesEntreprise = Array.from(document.querySelectorAll('input[name="types-entreprise"]:checked'))
                .map(input => input.value);
            formData.step4.typesEntreprise = typesEntreprise;

            // Étape 4 - Contraintes
            const contraintesField = document.getElementById('contraintes');
            if (contraintesField) {
                formData.step4.contraintes = contraintesField.value.trim();
            }

        } catch (error) {
            console.error('❌ Erreur mise à jour données:', error);
        }
    }

    // ====== COLLECTE DE DONNÉES ======
    function collectAllData() {
        updateFormData();
        
        const completeData = {
            ...formData.step3,
            ...formData.step4,
            timestamp: new Date().toISOString()
        };
        
        console.log('📊 Données collectées étapes 3 & 4:', completeData);
        return completeData;
    }

    // ====== VALIDATION DES ÉTAPES ======
    function validateStep3() {
        console.log('🔍 Validation étape 3...');
        
        updateFormData();
        
        const motivations = formData.step3.motivations;
        const secteurs = formData.step3.secteurs;
        
        if (motivations.length === 0) {
            showNotification('Veuillez sélectionner au moins une motivation professionnelle.', 'error');
            return false;
        }
        
        if (secteurs.length === 0) {
            showNotification('Veuillez sélectionner au moins un secteur d\'activité.', 'error');
            return false;
        }
        
        console.log('✅ Étape 3 validée');
        return true;
    }

    function validateStep4() {
        console.log('🔍 Validation étape 4...');
        
        updateFormData();
        
        const situation = formData.step4.situation;
        const disponibilite = formData.step4.disponibilite;
        const modesTravail = formData.step4.modesTravail;
        
        if (!situation) {
            showNotification('Veuillez indiquer votre situation professionnelle actuelle.', 'error');
            return false;
        }
        
        if (!disponibilite) {
            showNotification('Veuillez indiquer votre disponibilité.', 'error');
            return false;
        }
        
        if (modesTravail.length === 0) {
            showNotification('Veuillez sélectionner au moins un mode de travail.', 'error');
            return false;
        }
        
        console.log('✅ Étape 4 validée');
        return true;
    }

    // ====== CONFIGURATION DE LA VALIDATION ======
    function setupValidation() {
        // Ajouter des event listeners pour la validation en temps réel
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('blur', updateFormData);
            textarea.addEventListener('input', updateFormData);
        });
    }

    // ====== CONFIGURATION DE LA COLLECTE DE DONNÉES ======
    function setupDataCollection() {
        // Exposer la fonction de collecte globalement
        window.collectSteps34Data = collectAllData;
        
        // Auto-collecte périodique pour backup
        setInterval(() => {
            if (getCurrentStep() >= 3) {
                updateFormData();
            }
        }, 5000); // Toutes les 5 secondes
    }

    // ====== INTÉGRATION AVEC LA NAVIGATION EXISTANTE ======
    function enhanceNavigationForSteps34() {
        // Intercepter la navigation pour ajouter la validation
        const originalNextStep = window.nextStep;
        
        if (typeof originalNextStep === 'function') {
            window.nextStep = function() {
                const currentStepNum = getCurrentStep();
                
                // Validation spécifique pour l'étape 3
                if (currentStepNum === 3 && !validateStep3()) {
                    return false;
                }
                
                // Validation spécifique pour l'étape 4
                if (currentStepNum === 4 && !validateStep4()) {
                    return false;
                }
                
                // Si validation OK, collecter les données
                if (currentStepNum >= 3) {
                    collectAllData();
                }
                
                // Appeler la fonction originale
                return originalNextStep();
            };
            
            console.log('🔗 Navigation étendue pour validation étapes 3 & 4');
        }

        // Intercepter la soumission finale
        const originalSubmitForm = window.submitForm;
        if (typeof originalSubmitForm === 'function') {
            window.submitForm = function() {
                // Validation finale
                if (!validateStep4()) {
                    return false;
                }
                
                // Collecte finale des données
                const finalData = collectAllData();
                console.log('📋 Données finales collectées:', finalData);
                
                // Appeler la fonction originale
                return originalSubmitForm();
            };
        }
    }

    // ====== UTILITAIRES ======
    function getCurrentStep() {
        const activeStep = document.querySelector('.form-step.active');
        if (activeStep) {
            const stepId = activeStep.id;
            const match = stepId.match(/step(\d+)/);
            return match ? parseInt(match[1]) : 1;
        }
        return 1;
    }

    function resetStep(stepNumber) {
        if (stepNumber === 3) {
            formData.step3 = {
                motivations: [],
                secteurs: [],
                salaire: 45000,
                aspirations: ''
            };
            // Réinitialiser l'interface
            document.querySelectorAll('input[name="motivations"]').forEach(input => {
                input.checked = false;
                input.closest('.checkbox-item')?.classList.remove('selected');
            });
            document.querySelectorAll('input[name="secteurs"]').forEach(input => {
                input.checked = false;
                input.closest('.checkbox-item')?.classList.remove('selected');
            });
        } else if (stepNumber === 4) {
            formData.step4 = {
                situation: null,
                disponibilite: null,
                modesTravail: [],
                typesEntreprise: [],
                contraintes: ''
            };
            // Réinitialiser l'interface
            document.querySelectorAll('#form-step4 input').forEach(input => {
                input.checked = false;
                input.closest('.checkbox-item, .radio-item')?.classList.remove('selected');
            });
        }
        
        console.log(`🔄 Étape ${stepNumber} réinitialisée`);
    }

    function showNotification(message, type = 'info') {
        // Utiliser le système de notification existant si disponible
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            // Fallback simple
            alert(message);
        }
    }

    // ====== AUTO-INITIALISATION ======
    
    // Initialisation immédiate si le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeSteps34);
    } else {
        // DOM déjà prêt, attendre un peu pour les autres scripts
        setTimeout(initializeSteps34, 200);
    }

    // Export pour compatibilité
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = {
            initializeSteps34,
            collectAllData,
            validateStep3,
            validateStep4
        };
    }

    console.log('📦 Script NEXTEN Steps 3 & 4 chargé');

})();
