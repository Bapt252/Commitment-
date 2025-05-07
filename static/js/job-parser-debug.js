/**
 * Script de débogage pour résoudre les problèmes de communication
 * entre l'iframe d'analyse de fiche de poste et la page principale.
 */
(function() {
    console.log('Initializing job parser debugging tools');
    
    // Vérifier si nous sommes dans une iframe ou dans la page principale
    const isIframe = window !== window.parent;
    
    // Fonction pour créer un bouton de débogage
    function createDebugButton() {
        // Créer un bouton flottant
        const button = document.createElement('button');
        button.textContent = 'Test Parser';
        button.style.cssText = `
            position: fixed;
            bottom: 10px;
            right: 10px;
            z-index: 9999;
            background: rgba(124, 58, 237, 0.9);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-family: 'Inter', sans-serif;
            cursor: pointer;
            font-weight: 500;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        `;
        document.body.appendChild(button);
        
        // Ajouter un gestionnaire d'événement
        button.addEventListener('click', function() {
            if (isIframe) {
                // Dans l'iframe, envoyez des données de test au parent
                console.log('Sending test data from iframe to parent');
                window.parent.postMessage({
                    type: 'jobParsingResult',
                    jobData: {
                        title: "Développeur Test",
                        skills: ["JavaScript", "Test", "Debug"],
                        experience: "3-5 ans d'expérience",
                        contract: "CDI"
                    },
                    messageId: new Date().getTime()
                }, '*');
                
                alert('Données de test envoyées à la page parente');
            } else {
                // Dans la page principale, affichez des données de test
                console.log('Testing job parser display in parent page');
                if (window.forceDisplayJobData) {
                    window.forceDisplayJobData({
                        title: "Développeur Test depuis le bouton de débogage",
                        skills: ["JavaScript", "Test", "Debug", "Interface"],
                        experience: "3-5 ans d'expérience en développement",
                        contract: "CDI"
                    });
                    alert('Données de test affichées dans le formulaire');
                } else {
                    alert('La fonction forceDisplayJobData n\'est pas disponible');
                }
            }
        });
        
        return button;
    }
    
    // Fonction pour afficher une zone de statut
    function createStatusPanel() {
        const panel = document.createElement('div');
        panel.style.cssText = `
            position: fixed;
            bottom: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: #ccc;
            padding: 10px;
            border-radius: 5px;
            max-width: 300px;
            max-height: 150px;
            overflow: auto;
            font-family: monospace;
            font-size: 12px;
            z-index: 9999;
            display: none;
        `;
        panel.innerHTML = `
            <div>Status: <span id="debug-status">Initializing...</span></div>
            <div>Context: ${isIframe ? 'iframe' : 'parent page'}</div>
            <div id="debug-message">Ready</div>
            <button id="debug-toggle-btn" style="margin-top: 5px; background: #333; color: #fff; border: none; padding: 3px 5px; cursor: pointer;">Hide</button>
        `;
        document.body.appendChild(panel);
        
        // Toggle button
        const toggleBtn = panel.querySelector('#debug-toggle-btn');
        toggleBtn.addEventListener('click', function() {
            if (panel.style.display === 'none') {
                panel.style.display = 'block';
                toggleBtn.textContent = 'Hide';
            } else {
                panel.style.display = 'none';
                toggleBtn.textContent = 'Show';
            }
        });
        
        // Function to update status
        window.updateDebugStatus = function(status, message) {
            const statusElem = document.getElementById('debug-status');
            const messageElem = document.getElementById('debug-message');
            
            if (statusElem) statusElem.textContent = status;
            if (messageElem) messageElem.textContent = message || '';
            
            panel.style.display = 'block';
        };
        
        return panel;
    }
    
    // Injecter des fonctions de débogage
    function injectDebugFunctions() {
        // Débogage pour la communication
        window.testJobParserCommunication = function() {
            console.log('Testing job parser communication');
            
            if (isIframe) {
                // Dans l'iframe
                if (window.parent) {
                    window.parent.postMessage({
                        type: 'testCommunication',
                        message: 'Test message from iframe',
                        timestamp: new Date().toISOString()
                    }, '*');
                    window.updateDebugStatus('Test sent', 'Message envoyé au parent');
                    return true;
                }
                window.updateDebugStatus('Error', 'Parent window not accessible');
                return false;
            } else {
                // Dans la page principale
                const iframe = document.getElementById('job-parser-iframe');
                if (iframe && iframe.contentWindow) {
                    iframe.contentWindow.postMessage({
                        type: 'testCommunication',
                        message: 'Test message from parent',
                        timestamp: new Date().toISOString()
                    }, '*');
                    window.updateDebugStatus('Test sent', 'Message envoyé à l\'iframe');
                    return true;
                }
                window.updateDebugStatus('Error', 'Iframe not accessible');
                return false;
            }
        };
        
        // Test des données simulées
        window.generateTestData = function() {
            return {
                title: "Développeur Fullstack",
                skills: ["JavaScript", "React", "Node.js", "MongoDB", "Git"],
                experience: "3-5 ans d'expérience",
                contract: "CDI"
            };
        };
        
        // Simulation de données
        if (!isIframe) {
            // Dans la page principale seulement
            window.simulateJobParsing = function() {
                // Récupérer les éléments
                const jobInfoContainer = document.getElementById('job-info-container');
                const jobTitleValue = document.getElementById('job-title-value');
                const jobSkillsValue = document.getElementById('job-skills-value');
                const jobExperienceValue = document.getElementById('job-experience-value');
                const jobContractValue = document.getElementById('job-contract-value');
                
                if (!jobInfoContainer || !jobTitleValue || !jobSkillsValue || !jobExperienceValue || !jobContractValue) {
                    window.updateDebugStatus('Error', 'DOM elements not found');
                    return false;
                }
                
                // Données de test
                const testData = window.generateTestData();
                
                // Mise à jour des valeurs
                jobTitleValue.textContent = testData.title;
                
                // Compétences avec formatage HTML
                const skillsHtml = testData.skills.map(skill => 
                    `<span class="skill-tag">${skill}</span>`
                ).join(' ');
                jobSkillsValue.innerHTML = skillsHtml;
                
                jobExperienceValue.textContent = testData.experience;
                jobContractValue.textContent = testData.contract;
                
                // Afficher le conteneur
                jobInfoContainer.style.display = 'block';
                jobInfoContainer.classList.add('visible');
                
                window.updateDebugStatus('Success', 'Simulation terminée');
                return true;
            };
        }
    }
    
    // Écouter les messages pour le débogage
    function setupMessageListeners() {
        window.addEventListener('message', function(event) {
            console.log('Debug: Received message:', event.data);
            
            if (event.data && event.data.type) {
                // Mettre à jour le statut de débogage
                window.updateDebugStatus('Message received', 
                    `Type: ${event.data.type} | ID: ${event.data.messageId || 'N/A'}`);
                
                // Si nous sommes dans la page principale et recevons des données de l'iframe
                if (!isIframe && event.data.type === 'jobParsingResult' && event.data.jobData) {
                    console.log('Debug: Job parsing data received:', event.data.jobData);
                    
                    // Essayer de mettre à jour l'affichage directement
                    if (window.forceDisplayJobData) {
                        window.forceDisplayJobData(event.data.jobData);
                        console.log('Debug: Display updated using forceDisplayJobData');
                    } else if (window.simulateJobParsing) {
                        window.simulateJobParsing();
                        console.log('Debug: Display updated using simulateJobParsing');
                    }
                }
            }
        });
    }
    
    // Fonction principale
    function initialize() {
        // Créer le panneau de statut
        createStatusPanel();
        
        // Injecter les fonctions de débogage
        injectDebugFunctions();
        
        // Configurer les écouteurs de messages
        setupMessageListeners();
        
        // Créer le bouton de débogage
        createDebugButton();
        
        // Initial status
        window.updateDebugStatus('Ready', 
            `Context: ${isIframe ? 'iframe' : 'parent page'} | Time: ${new Date().toLocaleTimeString()}`);
        
        console.log('Job parser debug tools initialized');
    }
    
    // Démarrer l'initialisation après que la page soit chargée
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
})();