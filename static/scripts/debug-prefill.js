/**
 * Script de débogage pour le pré-remplissage du formulaire
 * Ce script ajoute des fonctionnalités de débogage pour vérifier le fonctionnement du pré-remplissage
 */

// Fonction exécutée au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script de débogage du pré-remplissage chargé');
    
    // Vérifier s'il y a des données dans sessionStorage
    try {
        const storedData = sessionStorage.getItem('parsedCandidateData');
        if (storedData) {
            console.log('Données trouvées dans sessionStorage:', JSON.parse(storedData));
            // Afficher une notification pour indiquer que des données ont été trouvées
            if (window.showNotification) {
                window.showNotification('Données de CV trouvées dans le stockage', 'success');
            }
            
            // Tenter de pré-remplir le formulaire manuellement
            setTimeout(function() {
                forcePreFill(JSON.parse(storedData));
            }, 1000);
        } else {
            console.warn('Aucune donnée trouvée dans sessionStorage');
            // Ajouter des données de test pour tester le pré-remplissage
            createTestData();
        }
    } catch (error) {
        console.error('Erreur lors de la vérification des données:', error);
    }

    // Ajouter un bouton de débogage dans l'interface
    addDebugButton();
});

// Fonction pour forcer le pré-remplissage du formulaire avec des données
function forcePreFill(data) {
    console.log('Tentative de pré-remplissage forcé avec les données:', data);
    
    if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
        // S'assurer que les fonctions toggleSectorPreference et toggleProhibitedSector sont définies
        if (typeof window.toggleSectorPreference !== 'function') {
            window.toggleSectorPreference = function(radio) {
                const container = document.getElementById('sector-preference-container');
                if (container) {
                    container.style.display = radio.value === 'yes' ? 'block' : 'none';
                }
            };
        }
        
        if (typeof window.toggleProhibitedSector !== 'function') {
            window.toggleProhibitedSector = function(radio) {
                const container = document.getElementById('prohibited-sector-selection');
                if (container) {
                    container.style.display = radio.value === 'yes' ? 'block' : 'none';
                }
            };
        }
        
        if (typeof window.toggleEmploymentStatus !== 'function') {
            window.toggleEmploymentStatus = function(radio) {
                const employedSection = document.getElementById('employed-section');
                const unemployedSection = document.getElementById('unemployed-section');
                
                if (employedSection && unemployedSection) {
                    employedSection.style.display = radio.value === 'yes' ? 'block' : 'none';
                    unemployedSection.style.display = radio.value === 'yes' ? 'none' : 'block';
                }
            };
        }
        
        window.FormPrefiller.initialize(data);
        console.log('FormPrefiller.initialize appelé avec succès');
    } else {
        console.error('FormPrefiller n\'est pas disponible ou n\'est pas correctement initialisé');
        
        // Tentative de pré-remplissage manuel des champs basiques
        if (data.data) {
            // Format provenant directement du parsing
            if (data.data.personal_info && data.data.personal_info.name) {
                const fullNameField = document.getElementById('full-name');
                if (fullNameField) {
                    fullNameField.value = data.data.personal_info.name;
                    // Déclencher un événement input pour activer les validations
                    fullNameField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
            
            if (data.data.position) {
                const jobTitleField = document.getElementById('job-title');
                if (jobTitleField) {
                    jobTitleField.value = data.data.position;
                    // Déclencher un événement input
                    jobTitleField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
            
            if (data.data.personal_info && data.data.personal_info.address) {
                const addressField = document.getElementById('address');
                if (addressField) {
                    addressField.value = data.data.personal_info.address;
                    addressField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
        } else if (data.personalInfo) {
            // Format déjà transformé
            if (data.personalInfo.fullName) {
                const fullNameField = document.getElementById('full-name');
                if (fullNameField) {
                    fullNameField.value = data.personalInfo.fullName;
                    fullNameField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
            
            if (data.personalInfo.jobTitle) {
                const jobTitleField = document.getElementById('job-title');
                if (jobTitleField) {
                    jobTitleField.value = data.personalInfo.jobTitle;
                    jobTitleField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
        }
        
        console.log('Pré-remplissage manuel basique effectué');
    }
}

// Fonction pour créer des données de test
function createTestData() {
    console.log('Création de données de test pour le pré-remplissage');
    
    // Format que le système de transformation devrait produire
    const testData = {
        data: {
            personal_info: {
                name: "Jean Dupont",
                email: "jean.dupont@email.com",
                phone: "06 12 34 56 78",
                address: "15 Rue de la République, 75001 Paris"
            },
            position: "Développeur Full Stack",
            skills: [
                { name: "JavaScript" },
                { name: "React" },
                { name: "Node.js" }
            ],
            experience: [
                {
                    title: "Développeur Frontend",
                    company: "Tech Company",
                    start_date: "Janvier 2022",
                    end_date: "Présent",
                    description: "Développement d'applications web"
                }
            ],
            education: [
                {
                    degree: "Master en Informatique",
                    institution: "Université Paris-Saclay",
                    start_date: "2018",
                    end_date: "2020"
                }
            ],
            languages: [
                { language: "Français", level: "Natif" },
                { language: "Anglais", level: "Courant" }
            ],
            softwares: ["VS Code", "Git", "Docker"]
        }
    };
    
    sessionStorage.setItem('parsedCandidateData', JSON.stringify(testData));
    console.log('Données de test stockées dans sessionStorage');
    
    // Tenter le pré-remplissage après un court délai
    setTimeout(function() {
        forcePreFill(testData);
    }, 1000);
}

// Fonction pour ajouter un bouton de débogage à l'interface
function addDebugButton() {
    const debugButton = document.createElement('button');
    debugButton.textContent = 'Déboguer pré-remplissage';
    debugButton.style.position = 'fixed';
    debugButton.style.bottom = '10px';
    debugButton.style.left = '10px';
    debugButton.style.zIndex = '9999';
    debugButton.style.padding = '10px';
    debugButton.style.backgroundColor = '#FF5722';
    debugButton.style.color = 'white';
    debugButton.style.border = 'none';
    debugButton.style.borderRadius = '5px';
    debugButton.style.cursor = 'pointer';
    
    debugButton.addEventListener('click', function() {
        // Récupérer et afficher les données stockées
        const storedData = sessionStorage.getItem('parsedCandidateData');
        console.log('Données stockées:', storedData ? JSON.parse(storedData) : 'Aucune donnée');
        
        // Tenter de pré-remplir avec les données existantes ou des données de test
        if (storedData) {
            forcePreFill(JSON.parse(storedData));
        } else {
            createTestData();
        }
        
        // Afficher une notification
        if (window.showNotification) {
            window.showNotification('Tentative de pré-remplissage forcé', 'success');
        }
    });
    
    document.body.appendChild(debugButton);
}