// Script pour le matching entre candidats et offres d'emploi
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script de matching chargé');
    
    // Configuration
    const API_BASE_URL = 'http://localhost:8000'; // URL de l'API de matching
    const EMAIL_KEY = 'user_email'; // Clé pour stocker l'email dans localStorage
    const JOBS_KEY = 'matching_jobs'; // Clé pour stocker les offres matchées
    
    // Référence au loader
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // Fonction pour afficher/masquer le loader
    const showLoader = () => {
        loadingOverlay.classList.add('show');
    };
    
    const hideLoader = () => {
        loadingOverlay.classList.remove('show');
    };
    
    // Fonction pour récupérer les offres matchées depuis l'API
    const fetchMatchingJobs = async () => {
        // Récupérer l'email de l'utilisateur
        const email = localStorage.getItem(EMAIL_KEY);
        
        if (!email) {
            console.error('Email de l\'utilisateur non trouvé');
            return null;
        }
        
        try {
            showLoader();
            
            // Appel à l'API
            const response = await fetch(`${API_BASE_URL}/api/get-matching-jobs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    limit: 10 // Top 10 offres
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Erreur API:', errorData);
                return null;
            }
            
            const data = await response.json();
            
            // Stocker les résultats dans localStorage pour accès hors ligne
            if (data.success && data.data) {
                localStorage.setItem(JOBS_KEY, JSON.stringify(data.data));
                return data.data;
            }
            
            return null;
        } catch (error) {
            console.error('Erreur lors de la récupération des offres:', error);
            return null;
        } finally {
            hideLoader();
        }
    };
    
    // Fonction pour charger des offres de démonstration si l'API n'est pas disponible
    const loadDemoJobs = () => {
        return [
            {
                id: 1,
                titre: "Développeur Front-End Senior",
                entreprise: "TechVision",
                localisation: "15 Rue de Rivoli, 75004 Paris",
                type_contrat: "CDI",
                competences: ["JavaScript", "React", "TypeScript", "HTML", "CSS"],
                experience: "3-5 ans",
                date_debut: "01/05/2025",
                salaire: "45K-55K€",
                description: "Nous recherchons un développeur Front-End expérimenté pour renforcer notre équipe technique en pleine croissance.",
                matching_score: 92,
                matching_details: {
                    skills: 85,
                    contract: 100,
                    location: 90,
                    date: 100,
                    salary: 95,
                    experience: 90
                }
            },
            {
                id: 2,
                titre: "Développeur Full-Stack",
                entreprise: "InnovateTech",
                localisation: "92 Avenue des Champs-Élysées, 75008 Paris",
                type_contrat: "CDI",
                competences: ["JavaScript", "React", "Node.js", "Express", "MongoDB"],
                experience: "2-4 ans",
                date_debut: "15/04/2025",
                salaire: "42K-48K€",
                description: "Notre entreprise cherche un développeur Full-Stack talentueux pour participer au développement de notre plateforme innovante.",
                matching_score: 88,
                matching_details: {
                    skills: 80,
                    contract: 100,
                    location: 85,
                    date: 90,
                    salary: 90,
                    experience: 85
                }
            },
            {
                id: 3,
                titre: "Développeur Back-End",
                entreprise: "Data Solutions",
                localisation: "56 Rue du Faubourg Saint-Honoré, 75008 Paris",
                type_contrat: "CDI",
                competences: ["Python", "Django", "SQL", "Docker", "AWS"],
                experience: "2-5 ans",
                date_debut: "01/06/2025",
                salaire: "40K-50K€",
                description: "Data Solutions recherche un développeur Back-End pour renforcer son équipe tech.",
                matching_score: 85,
                matching_details: {
                    skills: 75,
                    contract: 100,
                    location: 80,
                    date: 90,
                    salary: 85,
                    experience: 95
                }
            }
        ];
    };
    
    // Fonction pour calculer le temps de trajet en utilisant l'API Google Maps
    const calculateTravelTime = async (origin, destination) => {
        try {
            // Utiliser l'API Maps Distance Matrix
            const url = `https://maps.googleapis.com/maps/api/distancematrix/json?origins=${encodeURIComponent(origin)}&destinations=${encodeURIComponent(destination)}&mode=driving&key=YOUR_GOOGLE_MAPS_API_KEY`;
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.status === 'OK') {
                const duration = data.rows[0].elements[0].duration.text;
                return duration;
            } else {
                console.error('Erreur API Google Maps:', data.status);
                return 'Non disponible';
            }
        } catch (error) {
            console.error('Erreur lors du calcul du temps de trajet:', error);
            
            // Simulation pour le mode démo
            // Générer un temps entre 15 et 60 minutes
            const minutes = Math.floor(Math.random() * 45) + 15;
            return `${minutes} min`;
        }
    };
    
    // Fonction pour mettre à jour les cartes d'offres avec les données de matching
    const updateJobCards = async (jobs) => {
        // Conteneur des cartes d'offres
        const jobCardsContainer = document.querySelector('.job-cards-container');
        
        if (!jobCardsContainer) {
            console.error('Conteneur des cartes d\'offres non trouvé');
            return;
        }
        
        // Vider le conteneur
        jobCardsContainer.innerHTML = '';
        
        // Si aucune offre, afficher un message
        if (!jobs || jobs.length === 0) {
            jobCardsContainer.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search" style="font-size: 3rem; color: var(--purple-light); margin-bottom: 1rem;"></i>
                    <h3>Aucune offre correspondante trouvée</h3>
                    <p>Ajustez vos critères de recherche ou complétez votre profil pour obtenir plus de résultats.</p>
                </div>
            `;
            return;
        }
        
        // Mettre à jour le compteur de résultats
        const resultsCount = document.querySelector('.results-count span');
        if (resultsCount) {
            resultsCount.textContent = jobs.length;
        }
        
        // Fonction pour déterminer la classe de couleur en fonction du score
        const getScoreColorClass = (score) => {
            if (score >= 80) return 'match-high';
            if (score >= 60) return 'match-medium';
            return 'match-low';
        };
        
        // Créer les cartes d'offres
        for (let i = 0; i < jobs.length; i++) {
            const job = jobs[i];
            
            // Déterminer la classe de couleur pour le score
            const scoreColorClass = getScoreColorClass(job.matching_score);
            
            // Créer la carte
            const jobCard = document.createElement('div');
            jobCard.className = 'job-card';
            jobCard.style.animationDelay = `${0.7 + (i * 0.1)}s`;
            
            // Remplir la carte avec les données de l'offre
            jobCard.innerHTML = `
                <div class="job-select">
                    <input type="checkbox" id="job-${job.id}" data-job-id="${job.id}">
                    <label for="job-${job.id}" class="checkbox-custom"></label>
                </div>
                <div class="job-card-header">
                    <div class="job-title-company">
                        <div class="company-logo">
                            <span>${job.entreprise.charAt(0)}</span>
                        </div>
                        <div class="job-title-info">
                            <h3>${job.titre}</h3>
                            <p class="job-description">${job.description}</p>
                        </div>
                    </div>
                    <div class="job-match">
                        <div class="match-percentage">
                            <span class="${scoreColorClass}">${job.matching_score}%</span>
                        </div>
                    </div>
                </div>
                <div class="job-card-body">
                    <div class="job-info-item">
                        <span class="info-label"><i class="fas fa-building"></i> Entreprise</span>
                        <span class="info-value">${job.entreprise}</span>
                        <a href="#" class="link-style">Voir le profil <i class="fas fa-external-link-alt"></i></a>
                    </div>
                    <div class="job-info-item">
                        <span class="info-label"><i class="fas fa-file-contract"></i> Contrat</span>
                        <div class="contract-badges">
                            <span class="contract-badge">${job.type_contrat}</span>
                        </div>
                    </div>
                    <div class="job-info-item">
                        <span class="info-label"><i class="fas fa-map-marker-alt"></i> Temps de trajet</span>
                        <span class="info-value travel-time" data-location="${job.localisation}">Calcul en cours...</span>
                        <a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(job.localisation)}" class="link-style" target="_blank">Voir sur Maps <i class="fas fa-map"></i></a>
                    </div>
                    <div class="job-info-item">
                        <span class="info-label"><i class="fas fa-euro-sign"></i> Rémunération</span>
                        <span class="info-value">${job.salaire}</span>
                    </div>
                    <div class="job-info-item">
                        <span class="info-label"><i class="fas fa-calendar-alt"></i> Date de prise de poste</span>
                        <span class="info-value">${job.date_debut}</span>
                    </div>
                    <div class="job-info-item">
                        <span class="info-label"><i class="fas fa-briefcase"></i> Expérience requise</span>
                        <span class="info-value">${job.experience}</span>
                    </div>
                </div>
                <div class="job-actions">
                    <button class="save-job" data-job-id="${job.id}">
                        <i class="far fa-bookmark"></i>
                        <span>Sauvegarder</span>
                    </button>
                    <button class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i>
                        Voir les détails
                    </button>
                </div>
            `;
            
            // Ajouter la carte au conteneur
            jobCardsContainer.appendChild(jobCard);
        }
        
        // Attacher les événements
        attachJobCardEvents();
        
        // Calculer les temps de trajet
        calculateAllTravelTimes();
    };
    
    // Fonction pour calculer les temps de trajet pour toutes les offres
    const calculateAllTravelTimes = async () => {
        // Récupérer l'adresse du candidat depuis localStorage
        const candidateAddress = localStorage.getItem('candidate_address') || '123 Rue de Paris, 75001 Paris';
        
        // Récupérer tous les éléments de temps de trajet
        const travelTimeElements = document.querySelectorAll('.travel-time');
        
        // Pour chaque élément
        for (const element of travelTimeElements) {
            const jobAddress = element.getAttribute('data-location');
            
            // Calculer le temps de trajet
            const travelTime = await calculateTravelTime(candidateAddress, jobAddress);
            
            // Mettre à jour l'élément
            element.textContent = travelTime;
        }
    };
    
    // Fonction pour attacher les événements aux cartes d'offres
    const attachJobCardEvents = () => {
        // Expansion des descriptions
        const jobDescriptions = document.querySelectorAll('.job-description');
        jobDescriptions.forEach(desc => {
            desc.addEventListener('click', function() {
                this.classList.toggle('expanded');
            });
        });
        
        // Sauvegarder les offres
        const saveButtons = document.querySelectorAll('.save-job');
        saveButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const jobId = this.getAttribute('data-job-id');
                const icon = this.querySelector('i');
                const text = this.querySelector('span');
                
                if (this.classList.contains('saved')) {
                    this.classList.remove('saved');
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    text.textContent = 'Sauvegarder';
                } else {
                    this.classList.add('saved');
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    text.textContent = 'Sauvegardé';
                }
            });
        });
        
        // Boutons de détail
        const detailButtons = document.querySelectorAll('.btn-primary');
        detailButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const jobCard = this.closest('.job-card');
                const checkbox = jobCard.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                updateSelectedCount();
            });
        });
    };
    
    // Fonction pour mettre à jour le compteur de sélection
    const updateSelectedCount = () => {
        const selectedCount = document.getElementById('selected-count');
        const selectedText = document.getElementById('selected-text');
        const confirmButton = document.getElementById('confirm-selection');
        const clearButton = document.getElementById('clear-selection');
        
        const checked = document.querySelectorAll('.job-select input[type="checkbox"]:checked');
        
        if (selectedCount) selectedCount.textContent = checked.length;
        
        if (selectedText) {
            if (checked.length === 0) {
                selectedText.textContent = "Aucun poste";
            } else if (checked.length === 1) {
                selectedText.textContent = "1 poste";
            } else {
                selectedText.textContent = `${checked.length} postes`;
            }
        }
        
        if (confirmButton && clearButton) {
            if (checked.length > 0) {
                confirmButton.disabled = false;
                confirmButton.style.opacity = "1";
                clearButton.disabled = false;
                clearButton.style.opacity = "1";
            } else {
                confirmButton.disabled = true;
                confirmButton.style.opacity = "0.6";
                clearButton.disabled = true;
                clearButton.style.opacity = "0.6";
            }
        }
    };
    
    // Initialisation: charger les offres
    const initializeMatchingPage = async () => {
        try {
            // Tenter de récupérer les offres depuis l'API
            let jobs = await fetchMatchingJobs();
            
            // Si pas d'offres depuis l'API, utiliser les données de démo
            if (!jobs) {
                console.log('Utilisation des offres de démonstration');
                jobs = loadDemoJobs();
                
                // Simuler un délai pour l'expérience utilisateur
                showLoader();
                await new Promise(resolve => setTimeout(resolve, 1000));
                hideLoader();
            }
            
            // Mettre à jour l'interface avec les offres
            await updateJobCards(jobs);
            
            // Initialiser les boutons de filtrage et de tri
            initializeFiltersAndSorting();
            
            // Initialiser les boutons d'actions
            initializeActionButtons();
            
        } catch (error) {
            console.error('Erreur lors de l\'initialisation de la page:', error);
            
            // Afficher un message d'erreur convivial
            const container = document.querySelector('.container');
            if (container) {
                container.innerHTML += `
                    <div class="error-message" style="
                        background-color: #FFEBEE;
                        color: #C62828;
                        padding: 1rem;
                        border-radius: 8px;
                        margin-top: 2rem;
                        text-align: center;
                    ">
                        <i class="fas fa-exclamation-circle" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                        <h3>Une erreur est survenue</h3>
                        <p>Impossible de charger les propositions de postes. Veuillez réessayer ultérieurement.</p>
                    </div>
                `;
            }
            
            hideLoader();
        }
    };
    
    // Initialiser les filtres et le tri
    const initializeFiltersAndSorting = () => {
        // Filtrage par recherche
        const searchInput = document.getElementById('search-input');
        const contractFilter = document.getElementById('contract-filter');
        const matchingFilter = document.getElementById('matching-filter');
        const sortOptions = document.getElementById('sort-options');
        
        // Si les éléments existent
        if (searchInput && contractFilter && matchingFilter && sortOptions) {
            // Fonction de filtrage
            const applyFilters = () => {
                const searchTerm = searchInput.value.toLowerCase();
                const contractValue = contractFilter.value;
                const matchingValue = matchingFilter.value;
                
                showLoader();
                
                setTimeout(() => {
                    const jobCards = document.querySelectorAll('.job-card');
                    
                    jobCards.forEach(card => {
                        // Filtrage par texte
                        const title = card.querySelector('h3').textContent.toLowerCase();
                        const company = card.querySelector('.job-info-item:first-child .info-value').textContent.toLowerCase();
                        const description = card.querySelector('.job-description').textContent.toLowerCase();
                        const textMatch = title.includes(searchTerm) || company.includes(searchTerm) || description.includes(searchTerm);
                        
                        // Filtrage par contrat
                        let contractMatch = true;
                        if (contractValue !== 'all') {
                            const contracts = Array.from(card.querySelectorAll('.contract-badge')).map(badge => badge.textContent.toLowerCase());
                            contractMatch = contracts.includes(contractValue.toLowerCase());
                        }
                        
                        // Filtrage par niveau de matching
                        let matchingMatch = true;
                        const matchElement = card.querySelector('.match-percentage span');
                        if (matchElement) {
                            const matchPercentage = parseInt(matchElement.textContent);
                            if (matchingValue === 'high') {
                                matchingMatch = matchPercentage >= 80;
                            } else if (matchingValue === 'medium') {
                                matchingMatch = matchPercentage >= 60 && matchPercentage < 80;
                            } else if (matchingValue === 'low') {
                                matchingMatch = matchPercentage < 60;
                            }
                        }
                        
                        // Appliquer les filtres
                        if (textMatch && contractMatch && matchingMatch) {
                            card.style.display = 'block';
                        } else {
                            card.style.display = 'none';
                        }
                    });
                    
                    // Mettre à jour le compteur de résultats
                    const visibleCards = document.querySelectorAll('.job-card[style="display: block"]').length;
                    const resultsCount = document.querySelector('.results-count span');
                    if (resultsCount) {
                        resultsCount.textContent = visibleCards;
                    }
                    
                    hideLoader();
                }, 300);
            };
            
            // Attacher les événements
            searchInput.addEventListener('input', applyFilters);
            contractFilter.addEventListener('change', applyFilters);
            matchingFilter.addEventListener('change', applyFilters);
            
            // Filtres par puces
            const filterChips = document.querySelectorAll('.filter-chip');
            filterChips.forEach(chip => {
                chip.addEventListener('click', function() {
                    if (this.classList.contains('active')) {
                        this.classList.remove('active');
                    } else {
                        this.classList.add('active');
                    }
                    
                    setTimeout(applyFilters, 100);
                });
                
                const removeBtn = chip.querySelector('.remove');
                if (removeBtn) {
                    removeBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        chip.remove();
                        applyFilters();
                    });
                }
            });
            
            // Tri
            sortOptions.addEventListener('change', function() {
                const sortValue = this.value;
                const cardsContainer = document.querySelector('.job-cards-container');
                const cards = Array.from(document.querySelectorAll('.job-card'));
                
                showLoader();
                
                setTimeout(() => {
                    if (sortValue === 'matching') {
                        cards.sort((a, b) => {
                            const percentA = parseInt(a.querySelector('.match-percentage span').textContent);
                            const percentB = parseInt(b.querySelector('.match-percentage span').textContent);
                            return percentB - percentA;
                        });
                    } else if (sortValue === 'date') {
                        cards.sort((a, b) => {
                            const dateA = new Date(a.querySelector('.job-info-item:nth-child(5) .info-value').textContent.split('/').reverse().join('-'));
                            const dateB = new Date(b.querySelector('.job-info-item:nth-child(5) .info-value').textContent.split('/').reverse().join('-'));
                            return dateA - dateB;
                        });
                    } else if (sortValue === 'company') {
                        cards.sort((a, b) => {
                            const companyA = a.querySelector('.job-info-item:first-child .info-value').textContent;
                            const companyB = b.querySelector('.job-info-item:first-child .info-value').textContent;
                            return companyA.localeCompare(companyB);
                        });
                    }
                    
                    // Réorganiser les cartes
                    cards.forEach(card => cardsContainer.appendChild(card));
                    
                    hideLoader();
                }, 300);
            });
        }
    };
    
    // Initialiser les boutons d'action
    const initializeActionButtons = () => {
        const checkboxes = document.querySelectorAll('.job-select input[type="checkbox"]');
        const clearSelection = document.getElementById('clear-selection');
        const confirmSelection = document.getElementById('confirm-selection');
        
        // Gestion des sélections
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateSelectedCount);
        });
        
        // Bouton d'effacement
        if (clearSelection) {
            clearSelection.addEventListener('click', function() {
                checkboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
                updateSelectedCount();
            });
        }
        
        // Bouton de confirmation
        if (confirmSelection) {
            confirmSelection.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Collecter les offres sélectionnées
                const selectedJobs = [];
                
                checkboxes.forEach(checkbox => {
                    if (checkbox.checked) {
                        const jobId = checkbox.getAttribute('data-job-id');
                        const jobCard = checkbox.closest('.job-card');
                        
                        if (jobCard && jobId) {
                            // Extraire les données du job
                            const title = jobCard.querySelector('.job-title-info h3').textContent;
                            const company = jobCard.querySelector('.job-info-item:nth-child(1) .info-value').textContent;
                            const salary = jobCard.querySelector('.job-info-item:nth-child(4) .info-value').textContent;
                            const location = jobCard.querySelector('.job-info-item:nth-child(3) .info-value').textContent;
                            const contractElement = jobCard.querySelector('.contract-badge');
                            const contract = contractElement ? contractElement.textContent : 'Type de contrat non spécifié';
                            const date = jobCard.querySelector('.job-info-item:nth-child(5) .info-value').textContent;
                            const experience = jobCard.querySelector('.job-info-item:nth-child(6) .info-value').textContent;
                            const matchPercentage = jobCard.querySelector('.match-percentage span').textContent;
                            
                            console.log('Job sélectionné:', { title, company, matchPercentage });
                            
                            selectedJobs.push({
                                id: jobId,
                                title,
                                company,
                                salary,
                                location,
                                contract,
                                date,
                                experience,
                                matchPercentage,
                                saveDate: new Date().toISOString()
                            });
                        }
                    }
                });
                
                console.log('Opportunités sélectionnées:', selectedJobs);
                
                // Sauvegarder dans localStorage
                if (selectedJobs.length > 0) {
                    localStorage.setItem('selectedOpportunities', JSON.stringify(selectedJobs));
                    
                    // Afficher une notification
                    const notification = document.getElementById('selection-notification');
                    if (notification) {
                        notification.classList.add('show');
                        
                        setTimeout(() => {
                            notification.classList.remove('show');
                            
                            // Rediriger vers le tableau de bord
                            window.location.href = 'candidate-dashboard.html?email=demo.utilisateur%40nexten.fr&password=s';
                        }, 2000);
                    } else {
                        // Si pas de notification, rediriger directement
                        window.location.href = 'candidate-dashboard.html?email=demo.utilisateur%40nexten.fr&password=s';
                    }
                } else {
                    alert('Veuillez sélectionner au moins une opportunité.');
                }
            });
        }
    };
    
    // Pagination
    const initializePagination = () => {
        const paginationItems = document.querySelectorAll('.pagination-item');
        
        paginationItems.forEach(item => {
            item.addEventListener('click', function() {
                if (!this.classList.contains('active')) {
                    document.querySelector('.pagination-item.active').classList.remove('active');
                    this.classList.add('active');
                    
                    showLoader();
                    
                    // Simuler un changement de page
                    setTimeout(() => {
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        hideLoader();
                    }, 500);
                }
            });
        });
    };
    
    // Initialiser la page
    initializeMatchingPage();
    initializePagination();
    
    // Pour le menu mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
});
