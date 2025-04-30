/**
 * CV API TESTER
 * 
 * Script permettant de tester l'intégration du parsing de CV
 * en simulant l'envoi de données depuis le backend.
 * 
 * Ce script est uniquement destiné aux tests et au développement.
 */

// IIFE pour éviter la pollution du scope global
(function() {
    // Injecter un bouton de test dans l'interface
    function injectTestButton() {
        // Vérifier si nous sommes sur la page du questionnaire
        if (!window.location.pathname.includes('candidate-questionnaire.html')) {
            return;
        }
        
        console.log("CV-API-Tester: Injection du bouton de test");
        
        // Créer le bouton de test
        const testButton = document.createElement('button');
        testButton.id = 'cv-api-test-button';
        testButton.innerText = 'Test CV API';
        testButton.style.position = 'fixed';
        testButton.style.bottom = '20px';
        testButton.style.left = '20px';
        testButton.style.zIndex = '9999';
        testButton.style.backgroundColor = '#10B981';
        testButton.style.color = 'white';
        testButton.style.border = 'none';
        testButton.style.borderRadius = '4px';
        testButton.style.padding = '8px 12px';
        testButton.style.cursor = 'pointer';
        testButton.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        
        // Ajouter le bouton à la page
        document.body.appendChild(testButton);
        
        // Ajouter un gestionnaire d'événements
        testButton.addEventListener('click', function() {
            showTestDialog();
        });
    }
    
    // Créer et afficher une boîte de dialogue de test
    function showTestDialog() {
        console.log("CV-API-Tester: Affichage de la boîte de dialogue de test");
        
        // Vérifier si une boîte de dialogue existe déjà
        if (document.getElementById('cv-api-test-dialog')) {
            return;
        }
        
        // Créer la boîte de dialogue
        const dialog = document.createElement('div');
        dialog.id = 'cv-api-test-dialog';
        dialog.style.position = 'fixed';
        dialog.style.top = '50%';
        dialog.style.left = '50%';
        dialog.style.transform = 'translate(-50%, -50%)';
        dialog.style.backgroundColor = 'white';
        dialog.style.boxShadow = '0 0 20px rgba(0, 0, 0, 0.2)';
        dialog.style.borderRadius = '8px';
        dialog.style.padding = '20px';
        dialog.style.width = '90%';
        dialog.style.maxWidth = '600px';
        dialog.style.zIndex = '10000';
        dialog.style.maxHeight = '80vh';
        dialog.style.overflow = 'auto';
        
        // Contenu de la boîte de dialogue
        dialog.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #333;">Test d'intégration CV API</h3>
                <button id="close-dialog" style="background: none; border: none; cursor: pointer; font-size: 20px;">&times;</button>
            </div>
            <p style="margin-bottom: 15px;">Sélectionnez un exemple de CV à tester ou entrez des données personnalisées :</p>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold;">Exemples prédéfinis :</label>
                <select id="cv-example-selector" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                    <option value="" selected>-- Sélectionnez un exemple --</option>
                    <option value="cv1">Claire Dubois - Développeuse Frontend</option>
                    <option value="cv2">Nicolas Martin - Product Manager</option>
                    <option value="cv3">Sophie Leroy - Data Scientist</option>
                    <option value="cv4">Antoine Moreau - DevOps Engineer</option>
                    <option value="custom">Données personnalisées</option>
                </select>
            </div>
            
            <div id="custom-data-container" style="display: none; margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: bold;">Données personnalisées (JSON) :</label>
                <textarea id="custom-cv-data" style="width: 100%; height: 200px; padding: 8px; border-radius: 4px; border: 1px solid #ddd; font-family: monospace; resize: vertical;"></textarea>
            </div>
            
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button id="cancel-test" style="padding: 8px 15px; border-radius: 4px; border: 1px solid #ddd; background-color: #f5f5f5; cursor: pointer;">Annuler</button>
                <button id="run-test" style="padding: 8px 15px; border-radius: 4px; border: none; background-color: #10B981; color: white; cursor: pointer;">Exécuter le test</button>
            </div>
        `;
        
        // Ajouter la boîte de dialogue au document
        document.body.appendChild(dialog);
        
        // Ajouter une overlay semi-transparente
        const overlay = document.createElement('div');
        overlay.id = 'cv-api-test-overlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.zIndex = '9999';
        document.body.appendChild(overlay);
        
        // Gestionnaires d'événements
        document.getElementById('close-dialog').addEventListener('click', closeDialog);
        document.getElementById('cancel-test').addEventListener('click', closeDialog);
        document.getElementById('run-test').addEventListener('click', runTest);
        document.getElementById('cv-example-selector').addEventListener('change', function() {
            const customDataContainer = document.getElementById('custom-data-container');
            customDataContainer.style.display = this.value === 'custom' ? 'block' : 'none';
        });
        
        // Fermeture par clic sur l'overlay
        overlay.addEventListener('click', closeDialog);
    }
    
    // Fermer la boîte de dialogue
    function closeDialog() {
        const dialog = document.getElementById('cv-api-test-dialog');
        const overlay = document.getElementById('cv-api-test-overlay');
        
        if (dialog) {
            dialog.remove();
        }
        
        if (overlay) {
            overlay.remove();
        }
    }
    
    // Exécuter le test
    function runTest() {
        const exampleSelector = document.getElementById('cv-example-selector');
        const selectedExample = exampleSelector.value;
        
        if (!selectedExample) {
            alert('Veuillez sélectionner un exemple de CV ou choisir "Données personnalisées".');
            return;
        }
        
        let cvData;
        
        if (selectedExample === 'custom') {
            // Utiliser les données personnalisées
            const customDataText = document.getElementById('custom-cv-data').value;
            
            try {
                cvData = JSON.parse(customDataText);
            } catch (error) {
                alert('Erreur: Les données JSON personnalisées sont invalides.\n\n' + error.message);
                return;
            }
        } else {
            // Utiliser un exemple prédéfini
            cvData = getExampleCVData(selectedExample);
        }
        
        // Vérifier que les données sont valides
        if (!cvData) {
            alert('Erreur: Impossible de charger les données de CV.');
            return;
        }
        
        // Fermer la boîte de dialogue
        closeDialog();
        
        // Envoyer les données au système de parsing CV
        console.log("CV-API-Tester: Envoi des données de test au système de parsing CV", cvData);
        
        // Effacer les données précédentes
        sessionStorage.removeItem('REAL_CV_DATA');
        sessionStorage.removeItem('REAL_CV_DATA_RECEIVED');
        
        // Simuler un appel API réussi en appelant directement la fonction receiveCV
        if (window.receiveCV && typeof window.receiveCV === 'function') {
            window.receiveCV(cvData);
            
            // Afficher une notification de succès
            if (window.showNotification) {
                window.showNotification("Test CV API réussi - Données transmises au système", "success");
            } else {
                alert("Test CV API réussi - Données transmises au système");
            }
        } else {
            console.error("CV-API-Tester: La fonction receiveCV n'est pas disponible");
            alert("Erreur: La fonction receiveCV n'est pas disponible");
        }
    }
    
    // Obtenir les données d'exemple de CV
    function getExampleCVData(exampleId) {
        const examples = {
            'cv1': {
                "data": {
                    "personal_info": {
                        "name": "Claire Dubois",
                        "email": "claire.dubois@email.com",
                        "phone": "06 12 34 56 78",
                        "address": "25 Avenue des Champs-Élysées, 75008 Paris"
                    },
                    "position": "Développeuse Frontend React",
                    "skills": [
                        { "name": "React" },
                        { "name": "JavaScript" },
                        { "name": "HTML/CSS" },
                        { "name": "TypeScript" },
                        { "name": "Redux" }
                    ],
                    "experience": [
                        {
                            "title": "Développeuse Frontend Senior",
                            "company": "WebTech Solutions",
                            "start_date": "Janvier 2022",
                            "end_date": "Présent",
                            "description": "Développement d'applications SPA avec React et TypeScript"
                        },
                        {
                            "title": "Développeuse Frontend",
                            "company": "Digital Agency",
                            "start_date": "Mars 2019",
                            "end_date": "Décembre 2021",
                            "description": "Création d'interfaces utilisateur responsive"
                        }
                    ],
                    "education": [
                        {
                            "degree": "Master en Développement Web",
                            "institution": "École Supérieure du Digital",
                            "start_date": "2017",
                            "end_date": "2019"
                        }
                    ],
                    "salary_range": "55K€ - 65K€ brut annuel"
                }
            },
            'cv2': {
                "data": {
                    "personal_info": {
                        "name": "Nicolas Martin",
                        "email": "nicolas.martin@email.com",
                        "phone": "07 98 76 54 32",
                        "address": "48 Rue de Rivoli, 75004 Paris"
                    },
                    "position": "Product Manager",
                    "skills": [
                        { "name": "Gestion de produit" },
                        { "name": "Agile/Scrum" },
                        { "name": "Analyse de marché" },
                        { "name": "UX/UI" },
                        { "name": "Jira" }
                    ],
                    "experience": [
                        {
                            "title": "Senior Product Manager",
                            "company": "TechStart",
                            "start_date": "Juin 2020",
                            "end_date": "Présent",
                            "description": "Gestion de la roadmap produit et définition de la stratégie"
                        },
                        {
                            "title": "Product Owner",
                            "company": "InnovApp",
                            "start_date": "Janvier 2018",
                            "end_date": "Mai 2020",
                            "description": "Coordination des développements et priorisation des features"
                        }
                    ],
                    "education": [
                        {
                            "degree": "MBA Stratégie Digitale",
                            "institution": "HEC Paris",
                            "start_date": "2015",
                            "end_date": "2017"
                        }
                    ],
                    "salary_range": "70K€ - 85K€ brut annuel"
                }
            },
            'cv3': {
                "data": {
                    "personal_info": {
                        "name": "Sophie Leroy",
                        "email": "sophie.leroy@email.com",
                        "phone": "06 87 65 43 21",
                        "address": "12 Rue de la République, 69002 Lyon"
                    },
                    "position": "Data Scientist",
                    "skills": [
                        { "name": "Python" },
                        { "name": "Machine Learning" },
                        { "name": "SQL" },
                        { "name": "TensorFlow" },
                        { "name": "Data Visualization" }
                    ],
                    "experience": [
                        {
                            "title": "Data Scientist",
                            "company": "DataInsight",
                            "start_date": "Septembre 2021",
                            "end_date": "Présent",
                            "description": "Développement de modèles prédictifs et analyse de données"
                        },
                        {
                            "title": "Data Analyst",
                            "company": "E-Commerce Plus",
                            "start_date": "Avril 2019",
                            "end_date": "Août 2021",
                            "description": "Analyse des données clients et optimisation des parcours"
                        }
                    ],
                    "education": [
                        {
                            "degree": "Master en Science des Données",
                            "institution": "Université de Lyon",
                            "start_date": "2017",
                            "end_date": "2019"
                        }
                    ],
                    "salary_range": "60K€ - 70K€ brut annuel"
                }
            },
            'cv4': {
                "data": {
                    "personal_info": {
                        "name": "Antoine Moreau",
                        "email": "antoine.moreau@email.com",
                        "phone": "07 12 34 56 78",
                        "address": "5 Rue Nationale, 59000 Lille"
                    },
                    "position": "DevOps Engineer",
                    "skills": [
                        { "name": "Docker" },
                        { "name": "Kubernetes" },
                        { "name": "AWS" },
                        { "name": "Terraform" },
                        { "name": "CI/CD" }
                    ],
                    "experience": [
                        {
                            "title": "DevOps Engineer",
                            "company": "CloudSolutions",
                            "start_date": "Février 2021",
                            "end_date": "Présent",
                            "description": "Mise en place d'infrastructures cloud et automatisation"
                        },
                        {
                            "title": "Administrateur Système",
                            "company": "ITServices",
                            "start_date": "Juillet 2018",
                            "end_date": "Janvier 2021",
                            "description": "Gestion des serveurs et déploiement d'applications"
                        }
                    ],
                    "education": [
                        {
                            "degree": "Ingénieur en Informatique",
                            "institution": "École Centrale de Lille",
                            "start_date": "2015",
                            "end_date": "2018"
                        }
                    ],
                    "salary_range": "65K€ - 75K€ brut annuel"
                }
            }
        };
        
        return examples[exampleId] || null;
    }
    
    // Initialiser le testeur API
    function initialize() {
        console.log("CV-API-Tester: Initialisation du testeur d'API CV");
        
        // Injecter le bouton de test dans l'interface
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', injectTestButton);
        } else {
            injectTestButton();
        }
    }
    
    // Exécuter l'initialisation
    initialize();
})();