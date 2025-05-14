/**
 * Correctif pour le problème d'analyse bloquée
 * Ce script remplace ou étend le module auto-chargeur GPT
 */

// Fonction immédiatement exécutée pour corriger le problème d'analyse
(function() {
    console.log('🔧 GPT-FixLoader: Initialisation du correctif pour le problème d\'analyse...');
    
    // Attendre que la page soit complètement chargée
    window.addEventListener('load', function() {
        // Timeout court pour s'assurer que tous les autres scripts sont chargés
        setTimeout(applyFix, 500);
    });
    
    // Appliquer le correctif
    function applyFix() {
        console.log('🔧 GPT-FixLoader: Application du correctif...');
        
        // 1. Mettre en place un gestionnaire d'analyse avec timeout
        const originalHandleGptAnalysis = window.handleGptAnalysis;
        
        // Remplacer la fonction d'analyse par une version avec timeout
        window.handleGptAnalysis = function(apiUrl) {
            console.log('🔧 GPT-FixLoader: Gestion de l\'analyse avec protection timeout');
            
            // Afficher le statut initial
            const statusElements = document.querySelectorAll('#gpt-analyze-status');
            updateStatus('Démarrage de l\'analyse...', '#7C3AED');
            
            // Mettre en place un timeout
            const analysisTimeout = setTimeout(function() {
                console.log('🔧 GPT-FixLoader: Timeout déclenché! L\'analyse prend trop de temps.');
                clearLoader();
                updateStatus('Timeout - L\'analyse prend trop de temps', 'red');
                showNotification("L'analyse a pris trop de temps. Fallback sur l'analyse locale.", "error");
                
                // Tenter une analyse locale
                tryLocalAnalysis();
                
                // Réactiver les boutons
                document.querySelectorAll('[id^="analyze-with-gpt"]').forEach(btn => {
                    if (btn) btn.disabled = false;
                });
            }, 15000); // 15 secondes de timeout
            
            try {
                // Rechercher le fichier ou le texte à analyser
                const fileInput = document.getElementById('job-file-input');
                const textArea = document.getElementById('job-description-text');
                
                // Désactiver tous les boutons pendant l'analyse
                document.querySelectorAll('[id^="analyze-with-gpt"]').forEach(btn => {
                    if (btn) btn.disabled = true;
                });
                
                // Afficher le loader
                const loader = document.getElementById('analysis-loader');
                if (loader) {
                    loader.style.display = 'flex';
                }
                
                // Cas 1: Fichier sélectionné
                if (fileInput && fileInput.files && fileInput.files.length > 0) {
                    const file = fileInput.files[0];
                    updateStatus('Analyse du fichier en cours...', '#7C3AED');
                    
                    // Lire le fichier localement d'abord
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Garder le contenu du fichier en mémoire pour l'analyse locale si besoin
                        window._fileContent = e.target.result;
                        
                        // Tenter l'analyse via API
                        tryApiAnalysis(file, apiUrl, analysisTimeout);
                    };
                    reader.onerror = function() {
                        clearTimeout(analysisTimeout);
                        clearLoader();
                        updateStatus('Erreur de lecture du fichier', 'red');
                        showNotification("Impossible de lire le fichier. Veuillez réessayer.", "error");
                        enableButtons();
                    };
                    
                    // Lire le fichier comme texte ou binaire selon le type
                    if (file.type === 'application/pdf' || file.type.includes('word')) {
                        reader.readAsArrayBuffer(file);
                    } else {
                        reader.readAsText(file);
                    }
                }
                // Cas 2: Texte saisi
                else if (textArea && textArea.value.trim()) {
                    updateStatus('Analyse du texte en cours...', '#7C3AED');
                    
                    // Garder le texte en mémoire pour l'analyse locale si besoin
                    window._textContent = textArea.value.trim();
                    
                    // Tenter l'analyse via API
                    tryApiAnalysisText(textArea.value.trim(), apiUrl, analysisTimeout);
                }
                // Aucune donnée à analyser
                else {
                    clearTimeout(analysisTimeout);
                    clearLoader();
                    updateStatus('Aucun contenu à analyser', 'red');
                    showNotification("Veuillez d'abord sélectionner un fichier ou saisir le texte de la fiche de poste.", "error");
                    enableButtons();
                }
            } catch (error) {
                clearTimeout(analysisTimeout);
                clearLoader();
                console.error('🔧 GPT-FixLoader: Erreur lors de l\'analyse:', error);
                updateStatus(`Erreur: ${error.message}`, 'red');
                showNotification(error.message, 'error');
                enableButtons();
            }
        };
        
        // Fonction pour tenter l'analyse via API
        function tryApiAnalysis(file, apiUrl, timeout) {
            console.log('🔧 GPT-FixLoader: Tentative d\'analyse API pour le fichier');
            
            // Préparer les données
            const formData = new FormData();
            formData.append('file', file);
            
            // Détecter l'URL de l'API
            const api = apiUrl || getApiUrl();
            
            // Appeler l'API
            console.log('🔧 GPT-FixLoader: Appel API sur', api);
            updateStatus('Envoi à l\'API...', '#7C3AED');
            
            fetch(`${api}/api/parse-job-posting`, {
                method: 'POST',
                body: formData,
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(result => {
                // Annuler le timeout car l'analyse a réussi
                clearTimeout(timeout);
                
                if (result.success && result.data) {
                    // Remplir le formulaire avec les données
                    fillFormWithJobData(result.data);
                    clearLoader();
                    updateStatus('Analyse réussie!', 'green');
                    showNotification('Fiche de poste analysée avec succès!', 'success');
                } else {
                    throw new Error(result.error || 'Données invalides reçues du serveur');
                }
            })
            .catch(error => {
                console.error('🔧 GPT-FixLoader: Erreur API:', error);
                // Si l'API échoue, tenter l'analyse locale
                console.log('🔧 GPT-FixLoader: Fallback sur analyse locale');
                updateStatus('API indisponible, analyse locale...', 'orange');
                
                // Annuler le timeout car nous gérons l'erreur
                clearTimeout(timeout);
                
                // Tenter l'analyse locale
                tryLocalAnalysis();
            })
            .finally(() => {
                enableButtons();
            });
        }
        
        // Fonction pour tenter l'analyse de texte via API
        function tryApiAnalysisText(text, apiUrl, timeout) {
            console.log('🔧 GPT-FixLoader: Tentative d\'analyse API pour le texte');
            
            // Préparer les données
            const formData = new FormData();
            formData.append('text', text);
            
            // Détecter l'URL de l'API
            const api = apiUrl || getApiUrl();
            
            // Appeler l'API
            console.log('🔧 GPT-FixLoader: Appel API sur', api);
            updateStatus('Envoi à l\'API...', '#7C3AED');
            
            fetch(`${api}/api/parse-job-posting`, {
                method: 'POST',
                body: formData,
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(result => {
                // Annuler le timeout car l'analyse a réussi
                clearTimeout(timeout);
                
                if (result.success && result.data) {
                    // Remplir le formulaire avec les données
                    fillFormWithJobData(result.data);
                    clearLoader();
                    updateStatus('Analyse réussie!', 'green');
                    showNotification('Fiche de poste analysée avec succès!', 'success');
                } else {
                    throw new Error(result.error || 'Données invalides reçues du serveur');
                }
            })
            .catch(error => {
                console.error('🔧 GPT-FixLoader: Erreur API:', error);
                // Si l'API échoue, tenter l'analyse locale
                console.log('🔧 GPT-FixLoader: Fallback sur analyse locale');
                updateStatus('API indisponible, analyse locale...', 'orange');
                
                // Annuler le timeout car nous gérons l'erreur
                clearTimeout(timeout);
                
                // Tenter l'analyse locale
                tryLocalAnalysis();
            })
            .finally(() => {
                enableButtons();
            });
        }
        
        // Effectuer une analyse locale
        function tryLocalAnalysis() {
            console.log('🔧 GPT-FixLoader: Analyse locale en cours...');
            updateStatus('Analyse locale en cours...', 'orange');
            
            let content = window._textContent || window._fileContent || '';
            let jobData = null;
            
            try {
                // Essayer d'abord d'utiliser l'API locale
                if (window.JobParserAPI) {
                    const localApi = new JobParserAPI({debug: true});
                    jobData = localApi.analyzeJobLocally(content);
                    console.log('🔧 GPT-FixLoader: Résultat de l\'analyse locale:', jobData);
                } 
                
                // Si ça ne marche pas, utiliser une analyse basique
                if (!jobData) {
                    jobData = basicJobAnalysis(content);
                }
                
                // Afficher les résultats
                if (jobData) {
                    fillFormWithJobData(jobData);
                    clearLoader();
                    updateStatus('Analyse locale réussie', '#10b981');
                    showNotification('Analyse effectuée localement avec succès', 'info');
                } else {
                    throw new Error('Échec de l\'analyse locale');
                }
            } catch (error) {
                console.error('🔧 GPT-FixLoader: Erreur analyse locale:', error);
                clearLoader();
                updateStatus('Échec de l\'analyse', 'red');
                showNotification('Impossible d\'analyser la fiche de poste. Veuillez réessayer ou saisir les informations manuellement.', 'error');
            }
        }
        
        // Analyse basique de secours
        function basicJobAnalysis(text) {
            console.log('🔧 GPT-FixLoader: Analyse basique de secours');
            
            if (!text || typeof text !== 'string') {
                if (window._fileContent instanceof ArrayBuffer) {
                    text = String.fromCharCode.apply(null, new Uint8Array(window._fileContent));
                } else {
                    text = "Contenu non analysable";
                }
            }
            
            // Extraire le titre (première ligne non vide)
            const lines = text.split('\n').filter(line => line.trim());
            const title = lines.length > 0 ? lines[0].trim() : "Non spécifié";
            
            // Recherche de mots-clés
            const hasWordNear = (text, word1, word2, maxDistance = 50) => {
                const pos1 = text.toLowerCase().indexOf(word1.toLowerCase());
                if (pos1 === -1) return false;
                
                const pos2 = text.toLowerCase().indexOf(word2.toLowerCase());
                if (pos2 === -1) return false;
                
                return Math.abs(pos1 - pos2) < maxDistance;
            };
            
            // Extraire le lieu
            let location = "Paris";
            const locationKeywords = ['lieu', 'location', 'localis', 'site', 'région', 'ville'];
            for (const keyword of locationKeywords) {
                const idx = text.toLowerCase().indexOf(keyword);
                if (idx !== -1) {
                    const segment = text.substring(idx, idx + 50);
                    const match = segment.match(/:\s*([^,.;()\n]+)/);
                    if (match && match[1].trim()) {
                        location = match[1].trim();
                        break;
                    }
                }
            }
            
            // Extraire le type de contrat
            let contractType = "CDI";
            if (text.toLowerCase().includes('cdd')) contractType = "CDD";
            if (text.toLowerCase().includes('stage')) contractType = "Stage";
            if (text.toLowerCase().includes('alternance') || text.toLowerCase().includes('apprentissage')) contractType = "Alternance";
            if (text.toLowerCase().includes('freelance') || text.toLowerCase().includes('indépendant')) contractType = "Freelance";
            
            // Extraire l'expérience
            let experience = "3-5 ans";
            if (hasWordNear(text, 'expérience', 'junior') || hasWordNear(text, 'expérience', '1 an')) {
                experience = "1-2 ans";
            } else if (hasWordNear(text, 'expérience', 'confirmé') || hasWordNear(text, 'expérience', '3 ans')) {
                experience = "3-5 ans";
            } else if (hasWordNear(text, 'expérience', 'senior') || hasWordNear(text, 'expérience', '5 ans')) {
                experience = "5+ ans";
            }
            
            // Extraire le salaire
            let salary = "Selon profil";
            const salaryMatch = text.match(/(\d+[kK€]|\d+\s*000\s*€|\d+\s*[kK]€)/);
            if (salaryMatch) {
                salary = salaryMatch[0];
            }
            
            // Extraire les compétences (recherche basique)
            const skills = [];
            const skillsKeywords = ['compétences', 'skills', 'profil', 'maîtrise', 'connaissances'];
            const techKeywords = ['java', 'python', 'javascript', 'react', 'angular', 'vue', 'node', 'php', 'c#', '.net', 'sql', 'nosql', 'mongodb', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'devops', 'agile', 'scrum'];
            
            techKeywords.forEach(tech => {
                if (text.toLowerCase().includes(tech.toLowerCase())) {
                    skills.push(tech);
                }
            });
            
            // Si pas assez de compétences détectées, ajouter quelques génériques
            if (skills.length < 3) {
                if (text.toLowerCase().includes('développeur') || text.toLowerCase().includes('developer')) {
                    skills.push('Programmation');
                    skills.push('Git');
                    skills.push('Travail en équipe');
                } else if (text.toLowerCase().includes('manager') || text.toLowerCase().includes('directeur')) {
                    skills.push('Management');
                    skills.push('Leadership');
                    skills.push('Communication');
                } else {
                    skills.push('Autonomie');
                    skills.push('Travail en équipe');
                    skills.push('Communication');
                }
            }
            
            // Résultat de l'analyse
            return {
                title: title,
                location: location,
                contract_type: contractType,
                experience: experience,
                salary: salary,
                skills: skills,
                responsibilities: ["Responsabilités à définir selon le poste"],
                benefits: ["Avantages à préciser"]
            };
        }
        
        // Masquer le loader
        function clearLoader() {
            const loader = document.getElementById('analysis-loader');
            if (loader) {
                loader.style.display = 'none';
            }
        }
        
        // Activer tous les boutons d'analyse
        function enableButtons() {
            document.querySelectorAll('[id^="analyze-with-gpt"]').forEach(btn => {
                if (btn) btn.disabled = false;
            });
        }
        
        // Mettre à jour le statut
        function updateStatus(message, color) {
            const statusElements = document.querySelectorAll('#gpt-analyze-status');
            statusElements.forEach(element => {
                if (element) {
                    element.textContent = message;
                    element.style.color = color;
                }
            });
        }
        
        // Récupérer l'URL de l'API
        function getApiUrl() {
            // Essayer d'abord le paramètre URL
            const urlParams = new URLSearchParams(window.location.search);
            const apiParam = urlParams.get('apiUrl');
            
            if (apiParam) {
                return apiParam;
            }
            
            // Ensuite la variable globale
            if (window.gptApiUrl) {
                return window.gptApiUrl;
            }
            
            // Fallback sur les URLs par défaut
            const DEFAULT_API_ENDPOINTS = [
                'http://localhost:5055',
                'https://api.commitment-analyzer.com',
                'https://gpt-parser-api.onrender.com'
            ];
            
            return DEFAULT_API_ENDPOINTS[0];
        }
        
        // Fonction pour afficher une notification (si disponible)
        function showNotification(message, type) {
            if (typeof window.showNotification === 'function') {
                window.showNotification(message, type);
                return;
            }
            
            // Fallback si la fonction n'existe pas
            console.log(`Notification (${type}): ${message}`);
            alert(message);
        }
        
        // Fonction pour remplir le formulaire avec les données analysées
        function fillFormWithJobData(jobData) {
            console.log('🔧 GPT-FixLoader: Remplissage du formulaire avec les données:', jobData);
            
            // Mapping des champs
            const fieldMapping = {
                'title': { selector: '#job-title-value' },
                'titre': { selector: '#job-title-value' },
                'company': { selector: '#job-contract-value' },
                'entreprise': { selector: '#job-contract-value' },
                'location': { selector: '#job-location-value' },
                'localisation': { selector: '#job-location-value' },
                'contract_type': { selector: '#job-contract-value' },
                'type_contrat': { selector: '#job-contract-value' },
                'experience': { selector: '#job-experience-value' },
                'education': { selector: '#job-education-value' },
                'formation': { selector: '#job-education-value' },
                'salary': { selector: '#job-salary-value' },
                'salaire': { selector: '#job-salary-value' },
                'skills': { selector: '#job-skills-value', type: 'skills' },
                'competences': { selector: '#job-skills-value', type: 'skills' },
                'responsibilities': { selector: '#job-responsibilities-value', type: 'list' },
                'missions': { selector: '#job-responsibilities-value', type: 'list' },
                'benefits': { selector: '#job-benefits-value', type: 'list' },
                'avantages': { selector: '#job-benefits-value', type: 'list' }
            };
            
            // Pour chaque champ dans le mapping
            for (const [dataKey, fieldInfo] of Object.entries(fieldMapping)) {
                if (jobData[dataKey]) {
                    const value = jobData[dataKey];
                    const element = document.querySelector(fieldInfo.selector);
                    
                    if (element) {
                        if (fieldInfo.type === 'skills' && Array.isArray(value)) {
                            element.innerHTML = value.map(skill => 
                                `<span class="tag">${skill}</span>`
                            ).join('');
                        } else if (fieldInfo.type === 'list' && Array.isArray(value)) {
                            element.innerHTML = '<ul>' + 
                                value.map(item => `<li>${item}</li>`).join('') + 
                                '</ul>';
                        } else {
                            element.textContent = Array.isArray(value) ? value.join(', ') : value;
                        }
                    }
                }
            }
            
            // Rendre visible le conteneur de résultats
            const jobInfoContainer = document.getElementById('job-info-container');
            if (jobInfoContainer) {
                jobInfoContainer.style.display = 'block';
            }
        }
        
        // Ajouter un bouton d'urgence pour l'analyse locale
        function addEmergencyButton() {
            // Vérifier si le bouton existe déjà
            if (document.getElementById('emergency-local-analysis')) {
                return;
            }
            
            // Créer un bouton d'urgence pour lancer l'analyse locale
            const emergencyButton = document.createElement('button');
            emergencyButton.id = 'emergency-local-analysis';
            emergencyButton.className = 'btn btn-danger';
            emergencyButton.style.position = 'fixed';
            emergencyButton.style.bottom = '20px';
            emergencyButton.style.right = '20px';
            emergencyButton.style.zIndex = '9999';
            emergencyButton.style.backgroundColor = '#dc3545';
            emergencyButton.style.color = 'white';
            emergencyButton.style.border = 'none';
            emergencyButton.style.borderRadius = '8px';
            emergencyButton.style.padding = '10px 15px';
            emergencyButton.style.fontSize = '14px';
            emergencyButton.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
            emergencyButton.innerHTML = '<i class="fas fa-bolt"></i> Analyse locale d\'urgence';
            
            // Ajouter un événement au clic
            emergencyButton.addEventListener('click', function() {
                clearLoader();
                tryLocalAnalysis();
            });
            
            // Ajouter à la page
            document.body.appendChild(emergencyButton);
        }
        
        // Ajouter le bouton d'urgence après un délai
        setTimeout(addEmergencyButton, 5000);
        
        console.log('🔧 GPT-FixLoader: Correctif appliqué avec succès!');
    }
})();
