// Script de connexion entre le frontend et le job-parser
document.addEventListener('DOMContentLoaded', function() {
    // Références aux éléments du DOM
    const dropZone = document.querySelector('.drop-zone') || document.querySelector('.upload-container');
    const fileInput = document.querySelector('input[type="file"]');
    const analyseButton = document.querySelector('.analyse-button') || document.querySelector('button[type="submit"]');
    let resultSection = document.querySelector('#result-section');
    const loadingIndicator = document.createElement('div');
    
    // Configuration du loading indicator
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<div class="spinner"></div><p>Analyse en cours...</p>';
    loadingIndicator.style.display = 'none';
    document.body.appendChild(loadingIndicator);
    
    // Si la section de résultats n'existe pas, la créer
    if (!resultSection) {
        resultSection = document.createElement('div');
        resultSection.id = 'result-section';
        
        // Trouver un bon emplacement pour insérer la section de résultats
        const container = document.querySelector('.container') || document.querySelector('main') || document.body;
        container.appendChild(resultSection);
    }
    
    // Gestionnaire pour le bouton d'analyse
    if (analyseButton) {
        analyseButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (fileInput && fileInput.files.length > 0) {
                analyseFile(fileInput.files[0]);
            } else {
                alert('Veuillez sélectionner un fichier à analyser.');
            }
        });
    }
    
    // Fonction principale d'analyse de fichier
    function analyseFile(file) {
        // Vérifier le type de fichier
        const validTypes = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                           'text/plain'];
        
        // Accepter les fichiers sans type MIME pour plus de flexibilité
        if (file.type && !validTypes.includes(file.type)) {
            const extension = file.name.split('.').pop().toLowerCase();
            if (!['pdf', 'docx', 'doc', 'txt'].includes(extension)) {
                alert('Format de fichier non supporté. Veuillez utiliser PDF, DOCX, DOC ou TXT.');
                return;
            }
        }
        
        // Préparation des données
        const formData = new FormData();
        formData.append('file', file);
        formData.append('force_refresh', 'true');
        
        // Afficher l'indicateur de chargement
        loadingIndicator.style.display = 'flex';
        
        // Appel à l'API du job-parser
        fetch('http://localhost:5053/api/parse-job', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Masquer l'indicateur de chargement
            loadingIndicator.style.display = 'none';
            
            // Afficher les résultats
            displayResults(data);
            
            // Enregistrer dans le localStorage pour la persistance
            localStorage.setItem('lastJobParseResult', JSON.stringify(data));
        })
        .catch(error => {
            console.error('Erreur lors de l\'analyse avec job-parser:', error);
            
            // En cas d'erreur, essayer le mode de secours avec le CV parser
            useBackupService(file);
        });
    }
    
    // Service de secours utilisant le CV parser
    function useBackupService(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('force_refresh', 'true');
        
        console.log('Tentative avec le service de secours (CV parser)...');
        
        fetch('http://localhost:5051/api/parse-cv/', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loadingIndicator.style.display = 'none';
            displayResults(data, true);
            
            // Enregistrer dans le localStorage
            localStorage.setItem('lastJobParseResult', JSON.stringify(data));
            localStorage.setItem('usedBackupService', 'true');
        })
        .catch(error => {
            console.error('Erreur avec le service de secours:', error);
            loadingIndicator.style.display = 'none';
            
            alert('Impossible de se connecter aux services d\'analyse. Veuillez vérifier que les services sont bien démarrés.');
            
            // Essayer de récupérer les derniers résultats du localStorage
            const lastResult = localStorage.getItem('lastJobParseResult');
            if (lastResult) {
                try {
                    const data = JSON.parse(lastResult);
                    displayResults(data, localStorage.getItem('usedBackupService') === 'true');
                    alert('Affichage des derniers résultats disponibles en cache.');
                } catch (e) {
                    console.error('Erreur lors de la récupération des résultats en cache:', e);
                }
            }
        });
    }
    
    // Affichage des résultats
    function displayResults(data, isBackupService = false) {
        // Données à afficher
        let parsedData = isBackupService ? data.data : data.data;
        
        // Si la structure n'est pas celle attendue, essayer d'adapter
        if (!parsedData) {
            parsedData = data;
        }
        
        // Construire le HTML pour l'affichage des résultats
        let resultHTML = '<div class="results-container">';
        resultHTML += '<h2>Informations extraites</h2>';
        
        if (isBackupService) {
            // Format pour le CV parser
            resultHTML += `<div class="result-item"><strong>Note:</strong> Résultats obtenus via le service CV parser (mode de secours)</div>`;
            
            // Mapper les données du CV au format de fiche de poste
            if (parsedData.skills && parsedData.skills.length > 0) {
                resultHTML += '<div class="result-item"><strong>Compétences détectées:</strong>';
                resultHTML += '<ul class="skill-list">';
                parsedData.skills.forEach(skill => {
                    resultHTML += `<li>${skill}</li>`;
                });
                resultHTML += '</ul></div>';
            }
            
            // Autres informations du CV qui pourraient être pertinentes
            if (parsedData.summary) {
                resultHTML += `<div class="result-item"><strong>Résumé:</strong> <p>${parsedData.summary}</p></div>`;
            }
            
            if (parsedData.experience && parsedData.experience.length > 0) {
                resultHTML += '<div class="result-item"><strong>Expériences professionnelles:</strong>';
                resultHTML += '<ul class="experience-list">';
                parsedData.experience.forEach(exp => {
                    const company = exp.company || 'Entreprise non spécifiée';
                    const title = exp.title || 'Poste non spécifié';
                    const description = exp.description || '';
                    
                    resultHTML += `<li><strong>${title}</strong> chez ${company}`;
                    if (description) {
                        resultHTML += `<p>${description}</p>`;
                    }
                    resultHTML += '</li>';
                });
                resultHTML += '</ul></div>';
            }
        } else {
            // Format pour le job parser
            if (parsedData.title) {
                resultHTML += `<div class="result-item"><strong>Titre du poste:</strong> ${parsedData.title}</div>`;
            }
            
            if (parsedData.company) {
                resultHTML += `<div class="result-item"><strong>Entreprise:</strong> ${parsedData.company}</div>`;
            }
            
            if (parsedData.location) {
                resultHTML += `<div class="result-item"><strong>Localisation:</strong> ${parsedData.location}</div>`;
            }
            
            if (parsedData.contract_type) {
                resultHTML += `<div class="result-item"><strong>Type de contrat:</strong> ${parsedData.contract_type}</div>`;
            }
            
            if (parsedData.required_skills && parsedData.required_skills.length > 0) {
                resultHTML += '<div class="result-item"><strong>Compétences requises:</strong>';
                resultHTML += '<ul class="skill-list">';
                parsedData.required_skills.forEach(skill => {
                    resultHTML += `<li>${skill}</li>`;
                });
                resultHTML += '</ul></div>';
            }
            
            if (parsedData.preferred_skills && parsedData.preferred_skills.length > 0) {
                resultHTML += '<div class="result-item"><strong>Compétences souhaitées:</strong>';
                resultHTML += '<ul class="skill-list">';
                parsedData.preferred_skills.forEach(skill => {
                    resultHTML += `<li>${skill}</li>`;
                });
                resultHTML += '</ul></div>';
            }
            
            if (parsedData.responsibilities && parsedData.responsibilities.length > 0) {
                resultHTML += '<div class="result-item"><strong>Responsabilités:</strong>';
                resultHTML += '<ul class="responsibility-list">';
                parsedData.responsibilities.forEach(resp => {
                    resultHTML += `<li>${resp}</li>`;
                });
                resultHTML += '</ul></div>';
            }
            
            if (parsedData.requirements && parsedData.requirements.length > 0) {
                resultHTML += '<div class="result-item"><strong>Prérequis:</strong>';
                resultHTML += '<ul class="requirements-list">';
                parsedData.requirements.forEach(req => {
                    resultHTML += `<li>${req}</li>`;
                });
                resultHTML += '</ul></div>';
            }
            
            if (parsedData.benefits && parsedData.benefits.length > 0) {
                resultHTML += '<div class="result-item"><strong>Avantages:</strong>';
                resultHTML += '<ul class="benefits-list">';
                parsedData.benefits.forEach(benefit => {
                    resultHTML += `<li>${benefit}</li>`;
                });
                resultHTML += '</ul></div>';
            }
        }
        
        // Ajouter un bouton pour générer un questionnaire
        resultHTML += `
            <div class="action-buttons">
                <button id="generate-questionnaire" class="btn btn-primary">Générer un questionnaire</button>
                <button id="save-results" class="btn btn-secondary">Sauvegarder les résultats</button>
            </div>
        `;
        
        resultHTML += '</div>';
        
        // Afficher les résultats
        resultSection.innerHTML = resultHTML;
        resultSection.style.display = 'block';
        
        // Scroll vers les résultats
        resultSection.scrollIntoView({ behavior: 'smooth' });
        
        // Ajouter les gestionnaires d'événements pour les boutons d'action
        document.getElementById('generate-questionnaire').addEventListener('click', function() {
            generateQuestionnaire(parsedData);
        });
        
        document.getElementById('save-results').addEventListener('click', function() {
            saveResults(parsedData);
        });
    }
    
    // Fonction pour générer un questionnaire basé sur les données extraites
    function generateQuestionnaire(data) {
        let questionnaireHTML = '<div class="questionnaire-container">';
        questionnaireHTML += '<h2>Questionnaire pour le candidat</h2>';
        
        // Questions basées sur les compétences requises
        if (data.required_skills && data.required_skills.length > 0) {
            questionnaireHTML += '<div class="questionnaire-section">';
            questionnaireHTML += '<h3>Compétences techniques</h3>';
            
            data.required_skills.forEach((skill, index) => {
                questionnaireHTML += `
                    <div class="question-item">
                        <p><strong>Q${index + 1}:</strong> Quel est votre niveau d'expertise en <strong>${skill}</strong> ?</p>
                        <div class="rating">
                            <label><input type="radio" name="skill_${index}" value="1"> Débutant</label>
                            <label><input type="radio" name="skill_${index}" value="2"> Intermédiaire</label>
                            <label><input type="radio" name="skill_${index}" value="3"> Avancé</label>
                            <label><input type="radio" name="skill_${index}" value="4"> Expert</label>
                        </div>
                        <textarea placeholder="Détaillez votre expérience avec cette compétence..."></textarea>
                    </div>
                `;
            });
            
            questionnaireHTML += '</div>';
        }
        
        // Questions sur les responsabilités
        if (data.responsibilities && data.responsibilities.length > 0) {
            questionnaireHTML += '<div class="questionnaire-section">';
            questionnaireHTML += '<h3>Expérience professionnelle</h3>';
            
            // Limiter à quelques responsabilités pour ne pas surcharger
            const selectedResponsibilities = data.responsibilities.slice(0, 3);
            
            selectedResponsibilities.forEach((resp, index) => {
                questionnaireHTML += `
                    <div class="question-item">
                        <p><strong>Q${index + 1}:</strong> Avez-vous déjà eu à "${resp}" dans vos précédents postes ?</p>
                        <div class="options">
                            <label><input type="radio" name="resp_${index}" value="yes"> Oui</label>
                            <label><input type="radio" name="resp_${index}" value="no"> Non</label>
                        </div>
                        <textarea placeholder="Si oui, pouvez-vous décrire cette expérience..."></textarea>
                    </div>
                `;
            });
            
            questionnaireHTML += '</div>';
        }
        
        // Question générale sur le poste
        questionnaireHTML += `
            <div class="questionnaire-section">
                <h3>Questions générales</h3>
                <div class="question-item">
                    <p><strong>Q:</strong> Pourquoi êtes-vous intéressé(e) par ce poste de "${data.title || 'ce poste'}" ?</p>
                    <textarea placeholder="Votre réponse..."></textarea>
                </div>
                <div class="question-item">
                    <p><strong>Q:</strong> Quelles sont vos attentes salariales ?</p>
                    <textarea placeholder="Votre réponse..."></textarea>
                </div>
            </div>
        `;
        
        // Bouton de soumission
        questionnaireHTML += `
            <div class="submit-section">
                <button class="btn btn-success">Soumettre le questionnaire</button>
            </div>
        `;
        
        questionnaireHTML += '</div>';
        
        // Créer une nouvelle section pour le questionnaire
        const questionnaireSection = document.createElement('div');
        questionnaireSection.id = 'questionnaire-section';
        questionnaireSection.innerHTML = questionnaireHTML;
        
        // Ajouter après la section de résultats
        resultSection.insertAdjacentElement('afterend', questionnaireSection);
        
        // Scroll vers le questionnaire
        questionnaireSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Fonction pour sauvegarder les résultats
    function saveResults(data) {
        // Convertir les données en chaîne JSON
        const jsonData = JSON.stringify(data, null, 2);
        
        // Créer un Blob avec les données
        const blob = new Blob([jsonData], { type: 'application/json' });
        
        // Créer un URL temporaire pour le téléchargement
        const url = URL.createObjectURL(blob);
        
        // Créer un élément d'ancrage pour le téléchargement
        const a = document.createElement('a');
        a.href = url;
        a.download = `job-analysis-${new Date().toISOString().slice(0, 10)}.json`;
        
        // Ajouter l'élément au DOM
        document.body.appendChild(a);
        
        // Simuler un clic sur l'élément
        a.click();
        
        // Supprimer l'élément du DOM
        document.body.removeChild(a);
        
        // Libérer l'URL temporaire
        URL.revokeObjectURL(url);
    }
    
    // Configuration du drag & drop
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropZone.classList.add('highlight');
        }
        
        function unhighlight() {
            dropZone.classList.remove('highlight');
        }
        
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                if (fileInput) {
                    fileInput.files = files;
                }
                // Déclencher l'analyse automatiquement après le drop
                analyseFile(files[0]);
            }
        }
    }
    
    // Initialiser la page - vérifier s'il y a des résultats en cache
    const lastResult = localStorage.getItem('lastJobParseResult');
    if (lastResult) {
        try {
            const data = JSON.parse(lastResult);
            const usedBackup = localStorage.getItem('usedBackupService') === 'true';
            
            // Ajouter un message pour indiquer que ce sont des résultats en cache
            const cacheMessage = document.createElement('div');
            cacheMessage.className = 'cache-message';
            cacheMessage.innerHTML = '<p>Résultats chargés depuis le cache. Analysez une nouvelle fiche de poste pour des résultats actualisés.</p>';
            document.body.insertBefore(cacheMessage, document.body.firstChild);
            
            // Afficher après un court délai pour laisser la page se charger
            setTimeout(() => {
                displayResults(data, usedBackup);
            }, 500);
        } catch (e) {
            console.error('Erreur lors de la récupération des résultats en cache:', e);
        }
    }
});