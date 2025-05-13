// Script amélioré pour l'affichage des résultats de matching

/**
 * Script amélioré pour l'affichage des résultats de matching
 */

// Fonction pour mettre à jour les cartes d'offres avec les données de matching améliorées
const updateJobCardsWithDetails = async (jobs) => {
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
        
        // Construire le HTML des badges de compétences
        let skillBadgesHTML = '';
        if (job.competences && job.competences.length > 0) {
            skillBadgesHTML = job.competences.map(skill => 
                `<span class="skill-badge">${skill}</span>`
            ).join('');
        }
        
        // Construire le HTML des explications de matching
        let matchingExplanationsHTML = '';
        if (job.matching_explanations) {
            const explanations = job.matching_explanations;
            matchingExplanationsHTML = `
                <div class="matching-explanations">
                    <h4>Pourquoi ce matching ?</h4>
                    <ul>
                        ${explanations.skills ? `<li>${explanations.skills}</li>` : ''}
                        ${explanations.contract ? `<li>${explanations.contract}</li>` : ''}
                        ${explanations.location ? `<li>${explanations.location}</li>` : ''}
                        ${explanations.salary ? `<li>${explanations.salary}</li>` : ''}
                        ${explanations.date ? `<li>${explanations.date}</li>` : ''}
                        ${explanations.experience ? `<li>${explanations.experience}</li>` : ''}
                        ${explanations.soft_skills ? `<li>${explanations.soft_skills}</li>` : ''}
                        ${explanations.culture ? `<li>${explanations.culture}</li>` : ''}
                    </ul>
                </div>
            `;
        }
        
        // Construire le HTML des scores détaillés
        let detailedScoresHTML = '';
        if (job.matching_details) {
            const details = job.matching_details;
            detailedScoresHTML = `
                <div class="detailed-scores">
                    <h4>Scores par critère</h4>
                    <div class="score-bars">
                        <div class="score-bar-item">
                            <span class="score-label">Compétences</span>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: ${details.skills}%"></div>
                            </div>
                            <span class="score-value">${details.skills}%</span>
                        </div>
                        <div class="score-bar-item">
                            <span class="score-label">Contrat</span>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: ${details.contract}%"></div>
                            </div>
                            <span class="score-value">${details.contract}%</span>
                        </div>
                        <div class="score-bar-item">
                            <span class="score-label">Localisation</span>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: ${details.location}%"></div>
                            </div>
                            <span class="score-value">${details.location}%</span>
                        </div>
                        <div class="score-bar-item">
                            <span class="score-label">Salaire</span>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: ${details.salary}%"></div>
                            </div>
                            <span class="score-value">${details.salary}%</span>
                        </div>
                        <div class="score-bar-item">
                            <span class="score-label">Date</span>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: ${details.date}%"></div>
                            </div>
                            <span class="score-value">${details.date}%</span>
                        </div>
                        <div class="score-bar-item">
                            <span class="score-label">Expérience</span>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: ${details.experience}%"></div>
                            </div>
                            <span class="score-value">${details.experience}%</span>
                        </div>
                        ${details.soft_skills ? `
                        <div class="score-bar-item">
                            <span class="score-label">Soft Skills</span>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: ${details.soft_skills}%"></div>
                            </div>
                            <span class="score-value">${details.soft_skills}%</span>
                        </div>
                        ` : ''}
                        ${details.culture ? `
                        <div class="score-bar-item">
                            <span class="score-label">Culture</span>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: ${details.culture}%"></div>
                            </div>
                            <span class="score-value">${details.culture}%</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        // Formatage des avantages (s'ils existent)
        let avantagesHTML = '';
        if (job.avantages && job.avantages.length > 0) {
            avantagesHTML = `
                <div class="job-info-item">
                    <span class="info-label"><i class="fas fa-gift"></i> Avantages</span>
                    <div class="avantages-list">
                        ${job.avantages.map(avantage => `<span class="avantage-badge">${avantage}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        // Formatage des soft skills (s'ils existent)
        let softSkillsHTML = '';
        if (job.soft_skills && job.soft_skills.length > 0) {
            softSkillsHTML = `
                <div class="job-info-item">
                    <span class="info-label"><i class="fas fa-users"></i> Soft Skills</span>
                    <div class="soft-skills-list">
                        ${job.soft_skills.map(skill => `<span class="soft-skill-badge">${skill}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        // Formatage de la culture d'entreprise (si elle existe)
        let cultureHTML = '';
        if (job.culture_entreprise) {
            const culture = job.culture_entreprise;
            let valeursHTML = '';
            if (culture.valeurs && culture.valeurs.length > 0) {
                valeursHTML = `
                    <div class="culture-values">
                        ${culture.valeurs.map(valeur => `<span class="culture-value-badge">${valeur}</span>`).join('')}
                    </div>
                `;
            }
            
            cultureHTML = `
                <div class="job-info-item culture-item">
                    <span class="info-label"><i class="fas fa-building"></i> Culture d'entreprise</span>
                    <span class="info-value">${culture.environnement || ''}</span>
                    ${valeursHTML}
                    ${culture.methodologie ? `<div class="culture-methodology">Méthodologie: ${culture.methodologie}</div>` : ''}
                    ${culture.taille_equipe ? `<div class="team-size">Équipe: ${culture.taille_equipe} personnes</div>` : ''}
                </div>
            `;
        }
        
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
                    <button class="btn-details" data-job-id="${job.id}">
                        <i class="fas fa-chart-bar"></i> Détails
                    </button>
                </div>
            </div>
            
            <!-- Conteneur des détails du matching (caché par défaut) -->
            <div class="matching-details-container" id="details-${job.id}" style="display: none;">
                ${detailedScoresHTML}
                ${matchingExplanationsHTML}
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
                <div class="job-info-item">
                    <span class="info-label"><i class="fas fa-code"></i> Compétences clés</span>
                    <div class="skills-badges">
                        ${skillBadgesHTML}
                    </div>
                </div>
                ${softSkillsHTML}
                ${cultureHTML}
                ${avantagesHTML}
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
    
    // Attacher les événements aux boutons de détail
    const detailsButtons = document.querySelectorAll('.btn-details');
    detailsButtons.forEach(button => {
        button.addEventListener('click', function() {
            const jobId = this.getAttribute('data-job-id');
            const detailsContainer = document.getElementById(`details-${jobId}`);
            
            if (detailsContainer) {
                // Toggle l'affichage des détails
                if (detailsContainer.style.display === 'none') {
                    detailsContainer.style.display = 'block';
                    this.innerHTML = '<i class="fas fa-times"></i> Fermer';
                } else {
                    detailsContainer.style.display = 'none';
                    this.innerHTML = '<i class="fas fa-chart-bar"></i> Détails';
                }
            }
        });
    });
    
    // Attacher les autres événements
    attachJobCardEvents();
    
    // Calculer les temps de trajet
    calculateAllTravelTimes();
};

// Ajouter ces styles CSS à la page

/*
.matching-details-container {
    padding: 1.5rem;
    background-color: #f8f9fa;
    border-top: 1px solid var(--cream-dark);
    border-bottom: 1px solid var(--cream-dark);
}

.detailed-scores, .matching-explanations {
    margin-bottom: 1.5rem;
}

.detailed-scores h4, .matching-explanations h4 {
    font-size: 1.1rem;
    margin-bottom: 1rem;
    color: var(--purple);
}

.score-bars {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
}

.score-bar-item {
    display: flex;
    align-items: center;
    margin-bottom: 0.8rem;
}

.score-label {
    width: 100px;
    font-size: 0.9rem;
    color: var(--gray);
}

.score-bar-container {
    flex-grow: 1;
    height: 8px;
    background-color: #eaeaea;
    border-radius: 4px;
    overflow: hidden;
    margin: 0 10px;
}

.score-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--purple) 0%, var(--purple-light) 100%);
    border-radius: 4px;
}

.score-value {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--black);
    width: 40px;
    text-align: right;
}

.matching-explanations ul {
    padding-left: 1.5rem;
}

.matching-explanations li {
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
    color: var(--gray);
}

.btn-details {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid var(--purple);
    background-color: white;
    color: var(--purple);
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s;
    margin-top: 0.8rem;
}

.btn-details:hover {
    background-color: var(--purple-glass);
    transform: translateY(-2px);
}

.skills-badges, .soft-skills-list, .avantages-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.skill-badge, .soft-skill-badge, .avantage-badge, .culture-value-badge {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}

.skill-badge {
    background-color: var(--purple-glass);
    color: var(--purple);
}

.soft-skill-badge {
    background-color: rgba(16, 185, 129, 0.1);
    color: #10B981;
}

.avantage-badge {
    background-color: rgba(245, 158, 11, 0.1);
    color: #F59E0B;
}

.culture-value-badge {
    background-color: rgba(79, 70, 229, 0.1);
    color: #4F46E5;
}

.culture-item {
    display: flex;
    flex-direction: column;
}

.culture-values {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.culture-methodology, .team-size {
    font-size: 0.85rem;
    color: var(--gray);
    margin-top: 0.5rem;
}
*/