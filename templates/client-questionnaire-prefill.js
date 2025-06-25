        async function analyzeJobDescription(text) {
            const apiKey = localStorage.getItem('openai_api_key');
            if (!apiKey) {
                showNotification('Veuillez configurer votre clé API OpenAI d\'abord.', 'error');
                return;
            }
            
            console.log('🤖 Début analyse ChatGPT...');
            showLoader(true);
            
            try {
                const response = await fetch('https://api.openai.com/v1/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`
                    },
                    body: JSON.stringify({
                        model: 'gpt-4o-mini',
                        messages: [{
                            role: 'user',
                            content: `Analysez cette fiche de poste et extrayez les informations suivantes au format JSON strict :
                            {
                                "titre": "titre du poste",
                                "contrat": "type de contrat",
                                "lieu": "lieu de travail",
                                "experience": "expérience requise",
                                "formation": "formation requise",
                                "remuneration": "rémunération",
                                "competences": ["compétence1", "compétence2"],
                                "responsabilites": "responsabilités principales",
                                "avantages": "avantages proposés",
                                "entreprise": "nom de l'entreprise"
                            }

                            Fiche de poste :
                            ${text}`
                        }],
                        max_tokens: 1000,
                        temperature: 0.1
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`API Error: ${response.status} ${response.statusText}`);
                }
                
                const data = await response.json();
                
                if (data.choices && data.choices[0] && data.choices[0].message) {
                    const content = data.choices[0].message.content;
                    console.log('🤖 Réponse ChatGPT:', content);
                    
                    try {
                        // Nettoyer la réponse pour extraire le JSON
                        let jsonContent = content;
                        if (content.includes('```json')) {
                            jsonContent = content.split('```json')[1].split('```')[0];
                        } else if (content.includes('```')) {
                            jsonContent = content.split('```')[1].split('```')[0];
                        }
                        
                        const jobInfo = JSON.parse(jsonContent.trim());
                        
                        // Afficher les informations extraites
                        displayJobInfo(jobInfo);
                        
                        // ✨ NOUVEAU: Pré-remplir automatiquement les champs du questionnaire
                        prefillFormWithJobInfo(jobInfo);
                        
                        showNotification('Analyse réalisée avec succès ! Champs pré-remplis automatiquement.', 'success');
                        console.log('✅ Analyse terminée avec succès');
                    } catch (e) {
                        console.error('❌ Erreur parsing JSON:', e);
                        console.log('Contenu reçu:', content);
                        showNotification('Erreur lors de l\'analyse. Format de réponse inattendu.', 'error');
                    }
                } else {
                    throw new Error('Réponse API invalide');
                }
                
            } catch (error) {
                console.error('❌ Erreur ChatGPT:', error);
                if (error.message.includes('API Error: 401')) {
                    showNotification('Clé API invalide. Vérifiez votre clé OpenAI.', 'error');
                } else if (error.message.includes('API Error: 429')) {
                    showNotification('Limite de taux atteinte. Attendez un moment.', 'error');
                } else {
                    showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
                }
            } finally {
                showLoader(false);
            }
        }

        // ✨ NOUVELLE FONCTION: Pré-remplir automatiquement les champs du questionnaire
        function prefillFormWithJobInfo(jobInfo) {
            console.log('🎯 Début du pré-remplissage automatique des champs...', jobInfo);
            
            let filledCount = 0;
            
            // Mapping intelligent des informations vers les champs correspondants
            
            // 1. Type de contrat (Nature du contrat)
            if (jobInfo.contrat) {
                const contractValue = normalizeContractType(jobInfo.contrat);
                if (contractValue) {
                    const contractRadio = document.querySelector(`input[name="contract-nature"][value="${contractValue}"]`);
                    if (contractRadio) {
                        contractRadio.checked = true;
                        markFieldAsPrefilled(contractRadio.closest('.form-group'));
                        filledCount++;
                        console.log('✅ Contrat pré-rempli:', contractValue);
                    }
                }
            }
            
            // 2. Rémunération
            if (jobInfo.remuneration && jobInfo.remuneration !== 'Non spécifié') {
                const salaryField = document.getElementById('salary-range');
                if (salaryField) {
                    salaryField.value = jobInfo.remuneration;
                    markFieldAsPrefilled(salaryField.closest('.form-group'));
                    filledCount++;
                    console.log('✅ Rémunération pré-remplie:', jobInfo.remuneration);
                }
            }
            
            // 3. Avantages
            if (jobInfo.avantages && jobInfo.avantages !== 'Non spécifié') {
                const benefitsField = document.getElementById('job-benefits');
                if (benefitsField) {
                    benefitsField.value = jobInfo.avantages;
                    markFieldAsPrefilled(benefitsField.closest('.form-group'));
                    filledCount++;
                    console.log('✅ Avantages pré-remplis:', jobInfo.avantages);
                }
            }
            
            // 4. Années d'expérience
            if (jobInfo.experience) {
                const experienceValue = normalizeExperience(jobInfo.experience);
                if (experienceValue) {
                    const experienceField = document.getElementById('experience-required');
                    if (experienceField) {
                        experienceField.value = experienceValue;
                        markFieldAsPrefilled(experienceField.closest('.form-group'));
                        filledCount++;
                        console.log('✅ Expérience pré-remplie:', experienceValue);
                    }
                }
            }
            
            // 5. Responsabilités dans les perspectives d'évolution (si pas d'autre champ disponible)
            if (jobInfo.responsabilites && jobInfo.responsabilites !== 'Non spécifié') {
                const evolutionField = document.getElementById('career-evolution');
                if (evolutionField && !evolutionField.value) {
                    // Utiliser les responsabilités comme base pour les perspectives d'évolution
                    evolutionField.value = `Missions principales: ${jobInfo.responsabilites}`;
                    markFieldAsPrefilled(evolutionField.closest('.form-group'));
                    filledCount++;
                    console.log('✅ Perspectives d\'évolution pré-remplies avec responsabilités');
                }
            }
            
            // 6. Nom de l'entreprise dans la structure (étape 1)
            if (jobInfo.entreprise && jobInfo.entreprise !== 'Non spécifié') {
                const companyField = document.getElementById('company-name');
                if (companyField && !companyField.value) {
                    companyField.value = jobInfo.entreprise;
                    markFieldAsPrefilled(companyField.closest('.form-group'));
                    filledCount++;
                    console.log('✅ Nom entreprise pré-rempli:', jobInfo.entreprise);
                }
            }
            
            // Notification de succès du pré-remplissage
            if (filledCount > 0) {
                setTimeout(() => {
                    showNotification(
                        `${filledCount} champ${filledCount > 1 ? 's' : ''} pré-rempli${filledCount > 1 ? 's' : ''} automatiquement !`, 
                        'success'
                    );
                }, 1000);
                
                console.log(`🎉 Pré-remplissage terminé: ${filledCount} champs remplis`);
            }
        }
        
        // Fonction utilitaire pour normaliser les types de contrat
        function normalizeContractType(contract) {
            const contractLower = contract.toLowerCase();
            if (contractLower.includes('cdi')) return 'cdi';
            if (contractLower.includes('cdd')) return 'cdd';
            if (contractLower.includes('interim') || contractLower.includes('intérim')) return 'interim';
            if (contractLower.includes('freelance') || contractLower.includes('indépendant')) return 'freelance';
            return null;
        }
        
        // Fonction utilitaire pour normaliser l'expérience
        function normalizeExperience(experience) {
            const expLower = experience.toLowerCase();
            if (expLower.includes('junior') || expLower.includes('débutant') || expLower.includes('0') || expLower.includes('sans')) {
                return 'junior';
            }
            if (expLower.includes('2') && expLower.includes('3')) return '2-3years';
            if (expLower.includes('5') || expLower.includes('10')) return '5-10years';
            if (expLower.includes('10') || expLower.includes('plus')) return '10plus';
            return null;
        }
        
        // Fonction pour marquer visuellement un champ comme pré-rempli
        function markFieldAsPrefilled(formGroup) {
            if (!formGroup) return;
            
            // Ajouter la classe de style pré-rempli
            const field = formGroup.querySelector('.form-control, input[type="radio"]:checked');
            if (field) {
                field.classList.add('prefilled-field');
                
                // Ajouter un indicateur visuel
                const indicator = document.createElement('div');
                indicator.className = 'prefill-indicator';
                indicator.innerHTML = '✨ Auto';
                indicator.title = 'Champ pré-rempli automatiquement par ChatGPT';
                
                // Positionner l'indicateur
                formGroup.style.position = 'relative';
                formGroup.appendChild(indicator);
                
                // Retirer l'indicateur après quelques secondes
                setTimeout(() => {
                    if (indicator.parentNode) {
                        indicator.remove();
                    }
                    if (field.classList.contains('prefilled-field')) {
                        field.classList.remove('prefilled-field');
                    }
                }, 5000);
            }
        }

        function displayJobInfo(jobInfo) {
            document.getElementById('job-title-value').textContent = jobInfo.titre || 'Non spécifié';
            document.getElementById('job-contract-value').textContent = jobInfo.contrat || 'Non spécifié';
            document.getElementById('job-location-value').textContent = jobInfo.lieu || 'Non spécifié';
            document.getElementById('job-experience-value').textContent = jobInfo.experience || 'Non spécifié';
            document.getElementById('job-education-value').textContent = jobInfo.formation || 'Non spécifié';
            document.getElementById('job-salary-value').textContent = jobInfo.remuneration || 'Non spécifié';
            document.getElementById('job-responsibilities-value').textContent = jobInfo.responsabilites || 'Non spécifié';
            document.getElementById('job-benefits-value').textContent = jobInfo.avantages || 'Non spécifié';
            
            // Affichage des compétences
            const skillsContainer = document.getElementById('job-skills-value');
            if (jobInfo.competences && jobInfo.competences.length > 0) {
                skillsContainer.innerHTML = '';
                jobInfo.competences.forEach(skill => {
                    const tag = document.createElement('span');
                    tag.className = 'tag';
                    tag.textContent = skill;
                    skillsContainer.appendChild(tag);
                });
            } else {
                skillsContainer.textContent = 'Non spécifié';
            }
            
            document.getElementById('job-info-container').style.display = 'block';
        }

        function showLoader(show) {
            const loader = document.getElementById('analysis-loader');
            loader.style.display = show ? 'flex' : 'none';
        }

        // FONCTION NOUVELLE: Génération du récapitulatif avec les nouvelles données (REMPLACE L'ANCIENNE)
        function generateSummary() {
            console.log('🎨 Génération du récapitulatif amélioré...');
            
            generateStructureCard();
            generateContactCard();
            generateRecruitmentCard();
            
            // Vérifier si il y a un besoin de recrutement pour afficher les détails
            const hasRecruitment = document.querySelector('input[name="recruitment-need"]:checked');
            if (hasRecruitment && hasRecruitment.value === 'yes') {
                generateJobDetailsCard();
                document.getElementById('jobDetailsCard').style.display = 'block';
            } else {
                document.getElementById('jobDetailsCard').style.display = 'none';
            }
            
            console.log('✅ Récapitulatif amélioré généré avec succès');
        }

        function generateStructureCard() {
            const content = document.getElementById('structureContent');
            const items = [
                { 
                    label: '🏢 Nom', 
                    value: document.getElementById('company-name').value || 'Non renseigné',
                    icon: 'fas fa-building'
                },
                { 
                    label: '📍 Adresse', 
                    value: document.getElementById('company-address').value || 'Non renseignée',
                    icon: 'fas fa-map-marker-alt'
                },
                { 
                    label: '🌐 Site web', 
                    value: document.getElementById('company-website').value || 'Non renseigné',
                    icon: 'fas fa-globe'
                },
                { 
                    label: '📏 Taille', 
                    value: formatCompanySize(document.getElementById('company-size').value) || 'Non renseignée',
                    icon: 'fas fa-chart-bar'
                }
            ];

            content.innerHTML = items.map(item => `
                <div class="info-item">
                    <span class="info-label"><i class="${item.icon}"></i> ${item.label}:</span>
                    <span class="info-value ${item.value === 'Non renseigné' || item.value === 'Non renseignée' ? 'empty-value' : ''}">${item.value}</span>
                </div>
            `).join('');

            // Ajouter la description si elle existe
            const description = document.getElementById('company-description').value;
            if (description) {
                content.innerHTML += `
                    <div class="info-item" style="grid-column: 1 / -1;">
                        <span class="info-label"><i class="fas fa-file-text"></i> Description:</span>
                        <span class="info-value">${description}</span>
                    </div>
                `;
            }
        }

        function generateContactCard() {
            const content = document.getElementById('contactContent');
            const items = [
                { 
                    label: '👤 Nom', 
                    value: document.getElementById('contact-name').value || 'Non renseigné',
                    icon: 'fas fa-user'
                },
                { 
                    label: '💼 Fonction', 
                    value: document.getElementById('contact-title').value || 'Non renseignée',
                    icon: 'fas fa-briefcase'
                },
                { 
                    label: '📧 Email', 
                    value: document.getElementById('contact-email').value || 'Non renseigné',
                    icon: 'fas fa-envelope'
                },
                { 
                    label: '📞 Téléphone', 
                    value: document.getElementById('contact-phone').value || 'Non renseigné',
                    icon: 'fas fa-phone'
                },
                { 
                    label: '📞 Méthode préférée', 
                    value: formatContactMethod(document.getElementById('contact-preferred').value) || 'Non renseignée',
                    icon: 'fas fa-comments'
                }
            ];

            content.innerHTML = items.map(item => `
                <div class="info-item">
                    <span class="info-label"><i class="${item.icon}"></i> ${item.label}:</span>
                    <span class="info-value ${item.value === 'Non renseigné' || item.value === 'Non renseignée' ? 'empty-value' : ''}">${item.value}</span>
                </div>
            `).join('');
        }

        function generateRecruitmentCard() {
            const content = document.getElementById('recruitmentContent');
            const hasNeed = document.querySelector('input[name="recruitment-need"]:checked');
            
            if (!hasNeed) {
                content.innerHTML = `
                    <div class="info-item">
                        <span class="info-label"><i class="fas fa-question-circle"></i> Besoin:</span>
                        <span class="info-value empty-value">Non renseigné</span>
                    </div>
                `;
                return;
            }

            if (hasNeed.value === 'no') {
                content.innerHTML = `
                    <div class="info-item">
                        <span class="info-label"><i class="fas fa-times-circle"></i> Besoin actuel:</span>
                        <span class="info-value">Aucun besoin immédiat</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label"><i class="fas fa-info-circle"></i> Statut:</span>
                        <span class="info-value">Redirection vers le dashboard entreprise</span>
                    </div>
                `;
                return;
            }

            // Si oui, afficher les informations de la fiche de poste
            const jobInfoContainer = document.getElementById('job-info-container');
            const hasJobInfo = jobInfoContainer && jobInfoContainer.style.display !== 'none';
            
            if (hasJobInfo) {
                const items = [
                    { 
                        label: '✅ Besoin', 
                        value: 'Oui, un poste à pourvoir',
                        icon: 'fas fa-check-circle'
                    },
                    { 
                        label: '💼 Poste', 
                        value: document.getElementById('job-title-value').textContent || 'Non spécifié',
                        icon: 'fas fa-briefcase'
                    },
                    { 
                        label: '📄 Contrat', 
                        value: document.getElementById('job-contract-value').textContent || 'Non spécifié',
                        icon: 'fas fa-file-contract'
                    },
                    { 
                        label: '📍 Lieu', 
                        value: document.getElementById('job-location-value').textContent || 'Non spécifié',
                        icon: 'fas fa-map-marker-alt'
                    }
                ];

                content.innerHTML = items.map(item => `
                    <div class="info-item">
                        <span class="info-label"><i class="${item.icon}"></i> ${item.label}:</span>
                        <span class="info-value ${item.value === 'Non spécifié' ? 'empty-value' : ''}">${item.value}</span>
                    </div>
                `).join('');

                // Ajouter les compétences si elles existent
                const skillsContainer = document.getElementById('job-skills-value');
                if (skillsContainer && skillsContainer.children.length > 0) {
                    const skills = Array.from(skillsContainer.children).map(tag => tag.textContent).join(', ');
                    content.innerHTML += `
                        <div class="info-item" style="grid-column: 1 / -1;">
                            <span class="info-label"><i class="fas fa-cogs"></i> Compétences:</span>
                            <span class="info-value">${skills}</span>
                        </div>
                    `;
                }
            } else {
                content.innerHTML = `
                    <div class="info-item">
                        <span class="info-label"><i class="fas fa-check-circle"></i> Besoin:</span>
                        <span class="info-value">Oui, un poste à pourvoir</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label"><i class="fas fa-info-circle"></i> Fiche de poste:</span>
                        <span class="info-value empty-value">Non analysée</span>
                    </div>
                `;
            }
        }

        function generateJobDetailsCard() {
            const content = document.getElementById('jobDetailsContent');
            
            // Section Délais et timing
            const delaysSection = generateJobSection('⏰ Délais et timing', [
                {
                    label: 'Délai souhaité',
                    value: getSelectedCheckboxes('recruitment-delay').join(', ') || 'Non renseigné'
                },
                {
                    label: 'Gestion préavis',
                    value: getRadioValue('notice-management') ? 
                        (getRadioValue('notice-management') === 'yes' ? 
                            `Oui (${getRadioValue('notice-duration') || 'durée non précisée'})` : 'Non') 
                        : 'Non renseigné'
                }
            ]);

            // Section Contexte et profil
            const contextSection = generateJobSection('👥 Contexte et profil', [
                {
                    label: 'Contexte',
                    value: formatRecruitmentContext(getRadioValue('recruitment-context')) || 'Non renseigné'
                },
                {
                    label: 'Expérience',
                    value: formatExperience(document.getElementById('experience-required').value) || 'Non renseignée'
                },
                {
                    label: 'Secteur requis',
                    value: getRadioValue('sector-knowledge') === 'yes' ? 
                        (document.getElementById('activity-sector').value || 'Oui, secteur non précisé') : 
                        (getRadioValue('sector-knowledge') === 'no' ? 'Non requis' : 'Non renseigné')
                }
            ]);

            // Section Environnement
            const environmentSection = generateJobSection('🏢 Environnement', [
                {
                    label: 'Type de bureau',
                    value: formatWorkEnvironment(getRadioValue('work-environment')) || 'Non renseigné'
                },
                {
                    label: 'Équipe',
                    value: document.getElementById('team-composition').value || 'Non renseignée'
                },
                {
                    label: 'Évolution',
                    value: document.getElementById('career-evolution').value || 'Non renseignée'
                }
            ]);

            // Section Rémunération
            const salarySection = generateJobSection('💰 Rémunération', [
                {
                    label: 'Nature contrat',
                    value: formatContractNature(getRadioValue('contract-nature')) || 'Non renseignée'
                },
                {
                    label: 'Rémunération',
                    value: document.getElementById('salary-range').value || 'Non renseignée'
                },
                {
                    label: 'Avantages',
                    value: document.getElementById('job-benefits').value || 'Non renseignés'
                },
                {
                    label: 'Temps de travail',
                    value: formatContractType(document.getElementById('contract-type').value) || 'Non renseigné'
                }
            ]);

            content.innerHTML = delaysSection + contextSection + environmentSection + salarySection;
        }

        function generateJobSection(title, items) {
            const itemsHtml = items.map(item => `
                <div class="info-item">
                    <span class="info-label">${item.label}:</span>
                    <span class="info-value ${item.value === 'Non renseigné' || item.value === 'Non renseignée' || item.value === 'Non renseignés' ? 'empty-value' : ''}">${item.value}</span>
                </div>
            `).join('');

            return `
                <div class="job-section">
                    <h4 class="job-section-title">${title}</h4>
                    ${itemsHtml}
                </div>
            `;
        }

        // Fonctions utilitaires pour le formatage
        function formatCompanySize(value) {
            const sizes = {
                'tpe': 'TPE (Très Petite Entreprise)',
                'pme': 'PME (Petite et Moyenne Entreprise)',
                'eti': 'ETI (Entreprise de Taille Intermédiaire)',
                'groupe': 'Groupe',
                'startup': 'Startup'
            };
            return sizes[value] || value;
        }

        function formatContactMethod(value) {
            const methods = {
                'email': 'Email',
                'phone': 'Téléphone',
                'video': 'Visioconférence'
            };
            return methods[value] || value;
        }

        function formatRecruitmentContext(value) {
            const contexts = {
                'creation': 'Création de poste',
                'replacement': 'Remplacement',
                'growth': 'Accroissement d\'activité/Renfort',
                'private': 'Confidentiel'
            };
            return contexts[value] || value;
        }

        function formatExperience(value) {
            const experiences = {
                'junior': 'Profil Junior',
                '2-3years': '2 à 3 ans',
                '5-10years': '5 à 10 ans',
                '10plus': '10 ans et plus'
            };
            return experiences[value] || value;
        }

        function formatWorkEnvironment(value) {
            const environments = {
                'openspace': 'Open space',
                'office': 'Bureau individuel'
            };
            return environments[value] || value;
        }

        function formatContractNature(value) {
            const natures = {
                'cdi': 'CDI',
                'cdd': 'CDD',
                'interim': 'Intérim',
                'freelance': 'Freelance'
            };
            return natures[value] || value;
        }

        function formatContractType(value) {
            const types = {
                '35h': '35 heures',
                '39h': '39 heures',
                'cadre': 'Cadre',
                'non-cadre': 'Non-cadre'
            };
            return types[value] || value;
        }

        function getRadioValue(name) {
            const radio = document.querySelector(`input[name="${name}"]:checked`);
            return radio ? radio.value : null;
        }

        function getSelectedCheckboxes(name) {
            const checkboxes = document.querySelectorAll(`input[name="${name}"]:checked`);
            return Array.from(checkboxes).map(cb => {
                const label = document.querySelector(`label[for="${cb.id}"]`);
                return label ? label.textContent.trim() : cb.value;
            });
        }

        // Système de notifications amélioré
        function showNotification(message, type = 'info') {
            const notification = document.getElementById('notification');
            const icon = notification.querySelector('.notification-icon i');
            const title = notification.querySelector('.notification-title');
            const messageEl = notification.querySelector('.notification-message');
            
            // Configurer l'icône et la classe selon le type
            notification.className = `notification ${type}`;
            
            const configs = {
                'success': { icon: 'fas fa-check-circle', title: 'Succès' },
                'error': { icon: 'fas fa-exclamation-circle', title: 'Erreur' },
                'info': { icon: 'fas fa-info-circle', title: 'Information' },
                'warning': { icon: 'fas fa-exclamation-triangle', title: 'Attention' }
            };
            
            const config = configs[type] || configs['info'];
            icon.className = config.icon;
            title.textContent = config.title;
            messageEl.textContent = message;
            
            // Afficher la notification
            notification.style.display = 'flex';
            
            // Masquer automatiquement après 5 secondes
            setTimeout(() => {
                notification.style.display = 'none';
            }, 5000);
            
            // Gérer le clic sur la croix de fermeture
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.onclick = () => {
                notification.style.display = 'none';
            };
        }

        // Initialisation au chargement de la page
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Initialisation du questionnaire client amélioré...');
            
            // Initialiser la configuration API
            initializeAPIConfig();
            
            // Gérer la navigation entre les étapes
            document.querySelectorAll('.next-step').forEach(button => {
                button.addEventListener('click', function() {
                    const nextStep = parseInt(this.dataset.step);
                    showStep(nextStep);
                });
            });
            
            document.querySelectorAll('.prev-step').forEach(button => {
                button.addEventListener('click', function() {
                    const prevStep = parseInt(this.dataset.step);
                    showStep(prevStep);
                });
            });
            
            // Gérer la logique conditionnelle de l'étape 3 (recrutement)
            document.querySelectorAll('input[name="recruitment-need"]').forEach(radio => {
                radio.addEventListener('change', function() {
                    const jobParsingSection = document.getElementById('job-parsing-section');
                    const noRecruitmentSection = document.getElementById('no-recruitment-section');
                    
                    if (this.value === 'yes') {
                        jobParsingSection.classList.add('active');
                        noRecruitmentSection.classList.remove('active');
                        stopRedirectCountdown();
                    } else if (this.value === 'no') {
                        jobParsingSection.classList.remove('active');
                        noRecruitmentSection.classList.add('active');
                        startRedirectCountdown();
                    }
                });
            });
            
            // Gérer les boutons de redirection
            document.getElementById('go-to-dashboard')?.addEventListener('click', function() {
                stopRedirectCountdown();
                redirectToDashboard();
            });
            
            document.getElementById('stay-here')?.addEventListener('click', function() {
                stopRedirectCountdown();
                document.getElementById('no-recruitment-section').classList.remove('active');
                showNotification('Vous pouvez continuer à explorer le questionnaire.', 'info');
            });
            
            // Soumettre le formulaire
            document.getElementById('submit-form').addEventListener('click', function(e) {
                e.preventDefault();
                showNotification('Demande soumise avec succès ! Nous vous contacterons bientôt.', 'success');
                
                // Optionnel: rediriger vers une page de confirmation
                setTimeout(() => {
                    window.location.href = RECOMMENDATION_URL;
                }, 2000);
            });
            
            console.log('✅ Questionnaire client initialisé avec succès !');
        });
    </script>
</body>
</html>