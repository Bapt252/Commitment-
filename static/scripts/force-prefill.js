/**
 * Script forcé pour le pré-remplissage du formulaire
 * Ce script s'exécute indépendamment des autres et force le pré-remplissage
 */

(function() {
    console.log("Force-prefill: Script de pré-remplissage forcé lancé");
    
    // Données d'exemple pour le formulaire
    const sampleData = {
        "personal_info": {
            "name": "Thomas Dupont",
            "email": "thomas.dupont@email.com",
            "phone": "06 12 34 56 78",
            "address": "15 Rue de la République, 75001 Paris"
        },
        "position": "Développeur Full Stack JavaScript"
    };
    
    // Fonction pour remplir le formulaire
    function forceFillForm() {
        console.log("Force-prefill: Tentative de pré-remplissage forcé");
        
        try {
            // Informations personnelles
            fillField('full-name', sampleData.personal_info.name);
            fillField('job-title', sampleData.position);
            
            // Adresse
            fillField('address', sampleData.personal_info.address);
            
            // Cocher transport en commun par défaut
            checkOption('transport-method', 'public-transport');
            
            // Préférence de bureau sans préférence
            selectRadio('office-preference', 'no-preference');
            
            // Définir une fourchette de salaire
            fillField('salary-range', '40K€ - 60K€ brut annuel');
            
            // Disponibilité à 1 mois
            selectRadio('availability', '1month');
            
            // Actuellement en poste
            selectRadio('currently-employed', 'yes');
            selectRadio('listening-reason', 'no-evolution');
            setSelectOption('notice-period', '1month');
            selectRadio('notice-negotiable', 'yes');
            
            // Status de recrutement
            selectRadio('recruitment-status', 'no-leads');
            
            console.log("Force-prefill: Pré-remplissage forcé terminé avec succès");
            showSuccessMessage();
        } catch (error) {
            console.error("Force-prefill: Erreur lors du pré-remplissage forcé", error);
        }
    }
    
    // Fonction pour remplir un champ
    function fillField(id, value) {
        const field = document.getElementById(id);
        if (field) {
            field.value = value;
            // Déclencher un événement pour activer les validations
            triggerEvent(field, 'input');
            console.log(`Force-prefill: Champ ${id} rempli avec ${value}`);
        } else {
            console.warn(`Force-prefill: Champ ${id} non trouvé`);
        }
    }
    
    // Fonction pour cocher une option
    function checkOption(name, value) {
        const option = document.querySelector(`input[name="${name}"][value="${value}"]`);
        if (option) {
            option.checked = true;
            triggerEvent(option, 'change');
            console.log(`Force-prefill: Option ${name}=${value} cochée`);
            
            // Si c'est un moyen de transport, créer et remplir les questions de durée
            if (name === 'transport-method') {
                setTimeout(() => {
                    const container = document.getElementById('transport-time-questions');
                    if (container && container.style.display !== 'block') {
                        console.log(`Force-prefill: Forçage d'affichage des questions de temps de trajet`);
                        container.style.display = 'block';
                        
                        // Créer une question de durée si elle n'existe pas
                        if (!document.getElementById(`commute-time-${value}`)) {
                            const transportLabels = {
                                'public-transport': 'transports en commun',
                                'vehicle': 'véhicule personnel',
                                'bike': 'vélo',
                                'walking': 'à pied'
                            };
                            
                            const subQuestionDiv = document.createElement('div');
                            subQuestionDiv.className = 'form-group';
                            
                            subQuestionDiv.innerHTML = `
                                <label for="commute-time-${value}" class="form-label required">
                                    Combien de temps de trajet êtes-vous prêt à faire en ${transportLabels[value] || value} ?
                                </label>
                                <select id="commute-time-${value}" name="commute-time-${value}" class="form-control" required>
                                    <option value="">Sélectionnez une durée</option>
                                    <option value="10">10 minutes</option>
                                    <option value="20">20 minutes</option>
                                    <option value="30">30 minutes</option>
                                    <option value="45">45 minutes</option>
                                    <option value="60">1 heure</option>
                                    <option value="90">1 heure 30</option>
                                    <option value="120">2 heures</option>
                                </select>
                            `;
                            
                            container.appendChild(subQuestionDiv);
                        }
                        
                        // Définir la durée
                        setTimeout(() => {
                            setSelectOption(`commute-time-${value}`, '30');
                        }, 100);
                    }
                }, 100);
            }
        } else {
            console.warn(`Force-prefill: Option ${name}=${value} non trouvée`);
        }
    }
    
    // Fonction pour sélectionner un bouton radio
    function selectRadio(name, value) {
        const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
        if (radio) {
            radio.checked = true;
            triggerEvent(radio, 'change');
            console.log(`Force-prefill: Radio ${name}=${value} sélectionné`);
            
            // Si c'est le statut d'emploi, déclencher l'affichage des sections appropriées
            if (name === 'currently-employed') {
                const employedSection = document.getElementById('employed-section');
                const unemployedSection = document.getElementById('unemployed-section');
                
                if (employedSection && unemployedSection) {
                    employedSection.style.display = value === 'yes' ? 'block' : 'none';
                    unemployedSection.style.display = value === 'yes' ? 'none' : 'block';
                }
            }
            
            // Si c'est la préférence de secteur, déclencher l'affichage des options
            if (name === 'has-sector-preference') {
                const container = document.getElementById('sector-preference-container');
                if (container) {
                    container.style.display = value === 'yes' ? 'block' : 'none';
                }
            }
            
            // Si c'est le secteur prohibé, déclencher l'affichage des options
            if (name === 'has-prohibited-sector') {
                const container = document.getElementById('prohibited-sector-selection');
                if (container) {
                    container.style.display = value === 'yes' ? 'block' : 'none';
                }
            }
        } else {
            console.warn(`Force-prefill: Radio ${name}=${value} non trouvé`);
        }
    }
    
    // Fonction pour définir une option dans un select
    function setSelectOption(id, value) {
        const select = document.getElementById(id);
        if (select) {
            select.value = value;
            triggerEvent(select, 'change');
            console.log(`Force-prefill: Select ${id}=${value} défini`);
        } else {
            console.warn(`Force-prefill: Select ${id} non trouvé`);
        }
    }
    
    // Fonction pour déclencher un événement
    function triggerEvent(element, eventType) {
        const event = new Event(eventType, { bubbles: true });
        element.dispatchEvent(event);
    }
    
    // Fonction pour afficher un message de succès
    function showSuccessMessage() {
        if (typeof window.showNotification === 'function') {
            window.showNotification("Formulaire pré-rempli avec succès", "success");
        } else {
            // Si la fonction showNotification n'est pas disponible, créer manuellement une notification
            const notification = document.createElement('div');
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.backgroundColor = '#ffffff';
            notification.style.border = '1px solid #10B981';
            notification.style.borderLeft = '4px solid #10B981';
            notification.style.borderRadius = '5px';
            notification.style.padding = '15px 20px';
            notification.style.boxShadow = '0 3px 10px rgba(0,0,0,0.1)';
            notification.style.zIndex = '9999';
            notification.innerHTML = '<div style="color: #10B981; font-weight: bold;">✅ Succès</div><div>Formulaire pré-rempli avec succès</div>';
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transition = 'opacity 0.5s ease';
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 500);
            }, 5000);
        }
    }
    
    // Attendre que le DOM soit complètement chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(forceFillForm, 500);
        });
    } else {
        // Le DOM est déjà chargé, mais attendons un peu pour s'assurer que tout est prêt
        setTimeout(forceFillForm, 500);
    }
    
    // Ajouter un gestionnaire pour l'événement load de la fenêtre
    window.addEventListener('load', () => {
        // Vérifier si le formulaire est déjà rempli
        const fullNameField = document.getElementById('full-name');
        if (fullNameField && !fullNameField.value) {
            console.log("Force-prefill: Dernière tentative après chargement complet");
            setTimeout(forceFillForm, 1000);
        }
    });
    
    // Si après 3 secondes, le champ nom n'est toujours pas rempli, faire une ultime tentative
    setTimeout(() => {
        const fullNameField = document.getElementById('full-name');
        if (fullNameField && !fullNameField.value) {
            console.log("Force-prefill: Tentative ultime après 3 secondes");
            forceFillForm();
        }
    }, 3000);
})();