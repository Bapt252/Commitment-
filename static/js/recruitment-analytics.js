/**
 * Module d'analyse et statistiques pour le recrutement
 * Ce script gère les fonctionnalités de dashboard, statistiques et timeline
 */

document.addEventListener('DOMContentLoaded', function() {
    initAdvancedFilters();
    initRecruitmentDashboard();
    initTimelines();
    initStatistics();
    initNotifications();
    initJobStatsTabs();
});

/**
 * Initialise les filtres avancés
 */
function initAdvancedFilters() {
    const toggleFiltersBtn = document.getElementById('toggle-advanced-filters');
    const filtersContainer = document.getElementById('advanced-filters');
    const filterDateSelect = document.getElementById('filter-date');
    const customDateRange = document.getElementById('custom-date-range');
    const applyFiltersBtn = document.getElementById('apply-filters');
    const resetFiltersBtn = document.getElementById('reset-filters');
    
    // Afficher/masquer les filtres avancés
    if (toggleFiltersBtn && filtersContainer) {
        toggleFiltersBtn.addEventListener('click', () => {
            filtersContainer.classList.toggle('show');
            
            // Mettre à jour l'icône du bouton
            const icon = toggleFiltersBtn.querySelector('i');
            if (filtersContainer.classList.contains('show')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-filter';
            }
        });
    }
    
    // Afficher/masquer le sélecteur de dates personnalisées
    if (filterDateSelect && customDateRange) {
        filterDateSelect.addEventListener('change', () => {
            if (filterDateSelect.value === 'custom') {
                customDateRange.style.display = 'flex';
            } else {
                customDateRange.style.display = 'none';
            }
        });
    }
    
    // Appliquer les filtres
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', () => {
            const stageFilter = document.getElementById('filter-stage').value;
            const matchingFilter = document.getElementById('filter-matching').value;
            const dateFilter = filterDateSelect.value;
            
            // Récupérer les valeurs de dates personnalisées si nécessaire
            const dateFrom = document.getElementById('date-from').value;
            const dateTo = document.getElementById('date-to').value;
            
            // Appliquer les filtres aux cartes de candidats
            applyAdvancedFilters(stageFilter, matchingFilter, dateFilter, dateFrom, dateTo);
            
            // Afficher une notification
            showNotification('Filtres appliqués avec succès', 'info');
        });
    }
    
    // Réinitialiser les filtres
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', () => {
            // Réinitialiser tous les sélecteurs
            document.getElementById('filter-stage').value = 'all';
            document.getElementById('filter-matching').value = 'all';
            document.getElementById('filter-date').value = 'all';
            document.getElementById('date-from').value = '';
            document.getElementById('date-to').value = '';
            
            // Masquer le sélecteur de dates personnalisées
            customDateRange.style.display = 'none';
            
            // Réinitialiser l'affichage
            resetAllFilters();
            
            // Afficher une notification
            showNotification('Filtres réinitialisés', 'info');
        });
    }
}

/**
 * Applique les filtres avancés aux cartes de candidats
 */
function applyAdvancedFilters(stageFilter, matchingFilter, dateFilter, dateFrom, dateTo) {
    const candidateCards = document.querySelectorAll('.candidate-card');
    
    candidateCards.forEach(card => {
        let showCard = true;
        
        // Filtre par étape
        if (stageFilter !== 'all') {
            const column = card.closest('.kanban-cards');
            if (column && column.getAttribute('data-column') !== stageFilter) {
                showCard = false;
            }
        }
        
        // Filtre par niveau de correspondance
        if (showCard && matchingFilter !== 'all') {
            const indicator = card.querySelector('.candidate-card-indicator');
            const hasMatchingClass = indicator.classList.contains(`indicator-${matchingFilter}`);
            if (!hasMatchingClass) {
                showCard = false;
            }
        }
        
        // Filtre par date
        if (showCard && dateFilter !== 'all') {
            const dateElement = card.querySelector('.candidate-date');
            if (dateElement) {
                const cardDate = parseDate(dateElement.textContent);
                const today = new Date();
                
                switch (dateFilter) {
                    case 'today':
                        showCard = isSameDay(cardDate, today);
                        break;
                    case 'week':
                        showCard = isThisWeek(cardDate, today);
                        break;
                    case 'month':
                        showCard = isSameMonth(cardDate, today);
                        break;
                    case 'custom':
                        if (dateFrom && dateTo) {
                            const fromDate = new Date(dateFrom);
                            const toDate = new Date(dateTo);
                            showCard = isDateInRange(cardDate, fromDate, toDate);
                        }
                        break;
                }
            }
        }
        
        // Afficher ou masquer la carte
        card.style.display = showCard ? '' : 'none';
    });
    
    // Mettre à jour les compteurs
    updateColumnCounts();
}

/**
 * Réinitialise tous les filtres et affiche toutes les cartes
 */
function resetAllFilters() {
    const candidateCards = document.querySelectorAll('.candidate-card');
    
    candidateCards.forEach(card => {
        card.style.display = '';
    });
    
    // Mettre à jour les compteurs
    updateColumnCounts();
}

/**
 * Parse une date au format "JJ/MM/AAAA"
 */
function parseDate(dateStr) {
    const parts = dateStr.trim().split('/');
    if (parts.length === 3) {
        // Format JJ/MM/AAAA
        return new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
    }
    return new Date();
}

/**
 * Vérifie si deux dates sont le même jour
 */
function isSameDay(date1, date2) {
    return date1.getDate() === date2.getDate() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getFullYear() === date2.getFullYear();
}

/**
 * Vérifie si une date est dans la semaine courante
 */
function isThisWeek(date, currentDate) {
    // Calculer le début de la semaine courante (lundi)
    const startOfWeek = new Date(currentDate);
    const day = startOfWeek.getDay() || 7; // Transformer dimanche (0) en 7
    if (day !== 1) {
        startOfWeek.setHours(-24 * (day - 1));
    }
    startOfWeek.setHours(0, 0, 0, 0);
    
    // Calculer la fin de la semaine (dimanche)
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(endOfWeek.getDate() + 6);
    endOfWeek.setHours(23, 59, 59, 999);
    
    return date >= startOfWeek && date <= endOfWeek;
}

/**
 * Vérifie si deux dates sont dans le même mois
 */
function isSameMonth(date1, date2) {
    return date1.getMonth() === date2.getMonth() &&
           date1.getFullYear() === date2.getFullYear();
}

/**
 * Vérifie si une date est comprise dans un intervalle
 */
function isDateInRange(date, fromDate, toDate) {
    fromDate.setHours(0, 0, 0, 0);
    toDate.setHours(23, 59, 59, 999);
    return date >= fromDate && date <= toDate;
}

/**
 * Initialise le tableau de bord de recrutement
 */
function initRecruitmentDashboard() {
    const dashboardContainer = document.getElementById('recruitment-dashboard');
    const toggleDashboardBtn = document.getElementById('toggle-dashboard');
    
    if (dashboardContainer && toggleDashboardBtn) {
        toggleDashboardBtn.addEventListener('click', () => {
            const dashboardContent = dashboardContainer.querySelector('.dashboard-content');
            if (dashboardContent) {
                dashboardContent.style.display = dashboardContent.style.display === 'none' ? 'block' : 'none';
                
                // Mettre à jour l'icône
                const icon = toggleDashboardBtn.querySelector('i');
                if (dashboardContent.style.display === 'none') {
                    icon.className = 'fas fa-chevron-down';
                } else {
                    icon.className = 'fas fa-chevron-up';
                }
            }
        });
    }
    
    // Initialiser les données du tableau de bord
    updateDashboardStats();
}

/**
 * Met à jour les statistiques du tableau de bord
 */
function updateDashboardStats() {
    // Dans une application réelle, ces données viendraient d'une API
    // Ici, nous utilisons des données simulées
    
    // Total des candidats
    const totalCandidates = document.querySelectorAll('.candidate-card').length;
    document.getElementById('stat-total-candidates').textContent = totalCandidates;
    
    // Nombre d'entretiens planifiés
    const interviewsCount = document.querySelectorAll('.kanban-cards[data-column="entretiens"] .candidate-card').length;
    document.getElementById('stat-interviews').textContent = interviewsCount;
    
    // Nombre d'embauches
    const hiredCount = document.querySelectorAll('.kanban-cards[data-column="embauche"] .candidate-card').length;
    document.getElementById('stat-hired').textContent = hiredCount;
    
    // Taux de conversion
    const conversionRate = totalCandidates > 0 ? Math.round((hiredCount / totalCandidates) * 100) : 0;
    document.getElementById('stat-conversion-rate').textContent = conversionRate + '%';
    
    // Répartition par étape
    updateStageDistributionChart();
    
    // Activité récente
    updateRecentActivityChart();
}

/**
 * Met à jour le graphique de répartition par étape
 */
function updateStageDistributionChart() {
    const chartContainer = document.getElementById('stage-distribution-chart');
    const progressChart = chartContainer.querySelector('.progress-chart');
    
    // Vider le conteneur
    progressChart.innerHTML = '';
    
    // Récupérer les données par colonne
    const columns = [
        { id: 'candidatures', name: 'Candidatures', icon: 'fas fa-file-alt' },
        { id: 'pre-selection', name: 'Pré-sélection', icon: 'fas fa-check' },
        { id: 'entretiens', name: 'Entretiens', icon: 'fas fa-calendar-check' },
        { id: 'tests', name: 'Tests techniques', icon: 'fas fa-tasks' },
        { id: 'decision', name: 'Décision finale', icon: 'fas fa-gavel' },
        { id: 'embauche', name: 'Embauche', icon: 'fas fa-handshake' }
    ];
    
    // Calculer le total
    const totalCandidates = document.querySelectorAll('.candidate-card').length;
    
    // Créer les barres de progression
    columns.forEach(column => {
        const count = document.querySelectorAll(`.kanban-cards[data-column="${column.id}"] .candidate-card`).length;
        const percentage = totalCandidates > 0 ? Math.round((count / totalCandidates) * 100) : 0;
        
        const progressItem = document.createElement('div');
        progressItem.className = 'progress-item';
        progressItem.innerHTML = `
            <div class="progress-label"><i class="${column.icon}"></i> ${column.name}</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${percentage}%"></div>
            </div>
            <div class="progress-value">${count}</div>
        `;
        
        progressChart.appendChild(progressItem);
    });
}

/**
 * Met à jour le graphique d'activité récente
 */
function updateRecentActivityChart() {
    const chartContainer = document.getElementById('recent-activity-chart');
    const activityTimeline = chartContainer.querySelector('.activity-timeline');
    
    // Dans une application réelle, ces données viendraient d'une API
    // Ici, nous utilisons des données simulées
    const recentActivities = [
        {
            time: 'Aujourd\'hui, 14:32',
            type: 'candidature',
            content: '<span class="activity-name">Marie Dupont</span> a été ajoutée comme candidate pour <span class="activity-name">Développeur Full-Stack</span>'
        },
        {
            time: 'Aujourd\'hui, 11:15',
            type: 'entretien',
            content: 'Entretien planifié avec <span class="activity-name">Pierre Moreau</span> pour le 28/03/2025'
        },
        {
            time: 'Hier, 16:45',
            type: 'deplacement',
            content: '<span class="activity-name">David Bernard</span> a été déplacé vers l\'étape <span class="activity-name">Pré-sélection</span>'
        },
        {
            time: 'Hier, 09:20',
            type: 'offre',
            content: 'Nouvelle offre d\'emploi créée : <span class="activity-name">Développeur Full-Stack</span>'
        },
        {
            time: '22/03/2025, 15:30',
            type: 'candidature',
            content: '3 nouveaux candidats ont postulé pour <span class="activity-name">Développeur Full-Stack</span>'
        }
    ];
    
    // Vider le conteneur
    activityTimeline.innerHTML = '';
    
    // Créer les éléments d'activité
    recentActivities.forEach(activity => {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        
        activityItem.innerHTML = `
            <div class="activity-icon"></div>
            <div class="activity-time">${activity.time}</div>
            <div class="activity-content">${activity.content}</div>
        `;
        
        activityTimeline.appendChild(activityItem);
    });
}

/**
 * Initialise les timelines de recrutement
 */
function initTimelines() {
    // Gérer l'affichage/masquage des timelines
    document.querySelectorAll('.toggle-timeline').forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-target');
            const timelineElement = document.getElementById(targetId);
            
            if (timelineElement) {
                timelineElement.style.display = timelineElement.style.display === 'none' ? 'block' : 'none';
                
                // Changer le texte du bouton
                if (timelineElement.style.display === 'none') {
                    button.innerHTML = '<i class="fas fa-stream"></i> Afficher la timeline du recrutement';
                } else {
                    button.innerHTML = '<i class="fas fa-stream"></i> Masquer la timeline du recrutement';
                }
            }
        });
    });
    
    // Gérer l'ajout d'événements à la timeline
    document.querySelectorAll('.add-timeline-event').forEach(button => {
        button.addEventListener('click', () => {
            const jobId = button.getAttribute('data-job-id');
            document.getElementById('timeline-job-id').value = jobId;
            
            // Remplir avec la date du jour
            const today = new Date();
            document.getElementById('event-date').value = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
            
            // Afficher la modale
            document.getElementById('timeline-event-modal').classList.add('show');
        });
    });
    
    // Gérer le formulaire d'ajout d'événement
    const timelineEventForm = document.getElementById('timeline-event-form');
    const closeTimelineModal = document.getElementById('close-timeline-modal');
    const cancelTimelineBtn = document.getElementById('cancel-timeline-btn');
    
    if (timelineEventForm) {
        timelineEventForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const jobId = document.getElementById('timeline-job-id').value;
            const title = document.getElementById('event-title').value;
            const date = document.getElementById('event-date').value;
            const type = document.getElementById('event-type').value;
            const description = document.getElementById('event-description').value;
            
            // Ajouter l'événement à la timeline
            addTimelineEvent(jobId, title, date, type, description);
            
            // Fermer la modale
            document.getElementById('timeline-event-modal').classList.remove('show');
            
            // Afficher une notification
            showNotification('Événement ajouté à la timeline', 'success');
        });
    }
    
    if (closeTimelineModal) {
        closeTimelineModal.addEventListener('click', () => {
            document.getElementById('timeline-event-modal').classList.remove('show');
        });
    }
    
    if (cancelTimelineBtn) {
        cancelTimelineBtn.addEventListener('click', () => {
            document.getElementById('timeline-event-modal').classList.remove('show');
        });
    }
}

/**
 * Ajoute un événement à la timeline
 */
function addTimelineEvent(jobId, title, date, type, description) {
    const timelineContainer = document.getElementById(`${jobId}-timeline`);
    if (!timelineContainer) return;
    
    const timelineElement = timelineContainer.querySelector('.timeline');
    if (!timelineElement) return;
    
    // Formater la date
    const eventDate = new Date(date);
    const formattedDate = `${String(eventDate.getDate()).padStart(2, '0')}/${String(eventDate.getMonth() + 1).padStart(2, '0')}/${eventDate.getFullYear()}`;
    
    // Déterminer l'icône en fonction du type
    let icon = 'fas fa-info-circle';
    switch (type) {
        case 'publication':
            icon = 'fas fa-bullhorn';
            break;
        case 'candidature':
            icon = 'fas fa-user-plus';
            break;
        case 'entretien':
            icon = 'fas fa-calendar-check';
            break;
        case 'decision':
            icon = 'fas fa-gavel';
            break;
    }
    
    // Créer l'élément HTML
    const timelineItem = document.createElement('div');
    timelineItem.className = 'timeline-item';
    timelineItem.innerHTML = `
        <div class="timeline-date">${formattedDate}</div>
        <div class="timeline-content">
            <div class="timeline-icon"><i class="${icon}"></i></div>
            <div class="timeline-text">
                <span class="timeline-title">${title}</span>
                <p>${description}</p>
            </div>
        </div>
    `;
    
    // Ajouter au début de la timeline
    const firstItem = timelineElement.querySelector('.timeline-item');
    if (firstItem) {
        timelineElement.insertBefore(timelineItem, firstItem);
    } else {
        timelineElement.appendChild(timelineItem);
    }
}

/**
 * Initialise les statistiques de recrutement
 */
function initStatistics() {
    // Gérer l'affichage des statistiques d'une offre d'emploi
    document.querySelectorAll('.view-job-stats').forEach(button => {
        button.addEventListener('click', () => {
            const jobId = button.getAttribute('data-job-id');
            const jobTitle = button.closest('.job-offer-container').querySelector('.job-offer-title h3').textContent;
            
            // Mettre à jour le titre de la modale
            document.getElementById('job-stats-title').textContent = `Statistiques : ${jobTitle}`;
            
            // Afficher la modale
            document.getElementById('job-stats-modal').classList.add('show');
            
            // Charger les données (simulées)
            loadJobStats(jobId);
        });
    });
    
    // Fermer la modale de statistiques
    document.getElementById('close-job-stats-modal').addEventListener('click', () => {
        document.getElementById('job-stats-modal').classList.remove('show');
    });
}

/**
 * Charge les statistiques d'une offre d'emploi
 */
function loadJobStats(jobId) {
    // Dans une application réelle, ces données viendraient d'une API
    // Ici, nous utilisons des données simulées
    
    // Mettre à jour les statistiques générales
    document.getElementById('job-stat-candidates').textContent = '6';
    document.getElementById('job-stat-time').textContent = '15j';
    document.getElementById('job-stat-conversion').textContent = '17%';
    
    // Remplir la timeline des statistiques
    const timelineContainer = document.querySelector('#tab-timeline .timeline');
    timelineContainer.innerHTML = `
        <div class="timeline-item">
            <div class="timeline-date">20/03/2025</div>
            <div class="timeline-content">
                <div class="timeline-icon"><i class="fas fa-bullhorn"></i></div>
                <div class="timeline-text">
                    <span class="timeline-title">Publication de l'offre d'emploi</span>
                    <p>Offre de ${jobId === 'job1' ? 'Développeur Full-Stack' : 'Poste'} publiée sur 3 plateformes</p>
                </div>
            </div>
        </div>
        <div class="timeline-item">
            <div class="timeline-date">22/03/2025</div>
            <div class="timeline-content">
                <div class="timeline-icon"><i class="fas fa-user-plus"></i></div>
                <div class="timeline-text">
                    <span class="timeline-title">3 candidatures reçues</span>
                    <p>Marie Dupont, Thomas Martin et Julie Lefebvre</p>
                </div>
            </div>
        </div>
        <div class="timeline-item">
            <div class="timeline-date">25/03/2025</div>
            <div class="timeline-content">
                <div class="timeline-icon"><i class="fas fa-check"></i></div>
                <div class="timeline-text">
                    <span class="timeline-title">2 candidats présélectionnés</span>
                    <p>David Bernard et Sophie Dubois</p>
                </div>
            </div>
        </div>
    `;
    
    // Remplir le tableau des candidats
    const candidatesTableBody = document.querySelector('#tab-candidates tbody');
    candidatesTableBody.innerHTML = `
        <tr>
            <td>Marie Dupont</td>
            <td>Candidatures</td>
            <td><span class="badge badge-success">Élevé</span></td>
            <td>20/03/2025</td>
            <td>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-comment"></i>
                </button>
            </td>
        </tr>
        <tr>
            <td>Thomas Martin</td>
            <td>Candidatures</td>
            <td><span class="badge badge-warning">Moyen</span></td>
            <td>18/03/2025</td>
            <td>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-comment"></i>
                </button>
            </td>
        </tr>
        <tr>
            <td>Julie Lefebvre</td>
            <td>Candidatures</td>
            <td><span class="badge badge-success">Élevé</span></td>
            <td>15/03/2025</td>
            <td>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-comment"></i>
                </button>
            </td>
        </tr>
        <tr>
            <td>David Bernard</td>
            <td>Pré-sélection</td>
            <td><span class="badge badge-success">Élevé</span></td>
            <td>10/03/2025</td>
            <td>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-comment"></i>
                </button>
            </td>
        </tr>
        <tr>
            <td>Sophie Dubois</td>
            <td>Pré-sélection</td>
            <td><span class="badge badge-warning">Moyen</span></td>
            <td>08/03/2025</td>
            <td>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-comment"></i>
                </button>
            </td>
        </tr>
        <tr>
            <td>Pierre Moreau</td>
            <td>Entretiens</td>
            <td><span class="badge badge-success">Élevé</span></td>
            <td>05/03/2025</td>
            <td>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-text">
                    <i class="fas fa-comment"></i>
                </button>
            </td>
        </tr>
    `;
}

/**
 * Initialise les onglets de statistiques d'une offre d'emploi
 */
function initJobStatsTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            
            // Désactiver tous les onglets et contenus
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Activer l'onglet et le contenu sélectionnés
            button.classList.add('active');
            document.getElementById(`tab-${tabName}`).classList.add('active');
        });
    });
}

/**
 * Initialise le système de notifications en temps réel
 */
function initNotifications() {
    const toggleNotificationsBtn = document.getElementById('toggle-notifications');
    const notificationsPanel = document.getElementById('notifications-panel');
    const closeNotificationsBtn = document.getElementById('close-notifications');
    const markAllReadBtn = document.getElementById('mark-all-read');
    
    if (toggleNotificationsBtn && notificationsPanel) {
        // Afficher/masquer le panneau de notifications
        toggleNotificationsBtn.addEventListener('click', () => {
            notificationsPanel.classList.toggle('show');
            
            // Remplir les notifications si le panneau est affiché
            if (notificationsPanel.classList.contains('show')) {
                loadNotifications();
            }
        });
    }
    
    if (closeNotificationsBtn) {
        closeNotificationsBtn.addEventListener('click', () => {
            notificationsPanel.classList.remove('show');
        });
    }
    
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', () => {
            document.querySelectorAll('.notification-item').forEach(item => {
                item.classList.add('read');
            });
            
            // Mettre à jour le compteur
            updateNotificationBadge(0);
            
            // Afficher une notification
            showNotification('Toutes les notifications ont été marquées comme lues', 'success');
        });
    }
}

/**
 * Charge les notifications (simulées)
 */
function loadNotifications() {
    const notificationsList = document.getElementById('notifications-list');
    
    // Dans une application réelle, ces données viendraient d'une API
    // Ici, nous utilisons des données simulées
    const notifications = [
        {
            title: 'Nouvel entretien planifié',
            time: 'Il y a 10 minutes',
            body: 'Un entretien a été planifié avec Pierre Moreau pour le 28/03/2025 à 14h00.',
            read: false
        },
        {
            title: 'Nouvelle candidature',
            time: 'Il y a 2 heures',
            body: 'Marie Dupont a postulé pour le poste de Développeur Full-Stack.',
            read: false
        },
        {
            title: 'Deadline approchant',
            time: 'Hier',
            body: 'La date limite de candidature pour le poste de Développeur Full-Stack est dans 1 semaine.',
            read: false
        },
        {
            title: 'Candidat déplacé',
            time: 'Il y a 2 jours',
            body: 'David Bernard a été déplacé vers l\'étape de pré-sélection.',
            read: true
        },
        {
            title: 'Nouvelle offre créée',
            time: 'Il y a 5 jours',
            body: 'Une nouvelle offre d\'emploi "Développeur Full-Stack" a été créée.',
            read: true
        }
    ];
    
    // Vider la liste
    notificationsList.innerHTML = '';
    
    // Remplir la liste
    notifications.forEach(notification => {
        const notificationItem = document.createElement('div');
        notificationItem.className = `notification-item ${notification.read ? 'read' : ''}`;
        
        notificationItem.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-time">${notification.time}</div>
            </div>
            <div class="notification-body">${notification.body}</div>
        `;
        
        notificationsList.appendChild(notificationItem);
    });
    
    // Mettre à jour le compteur
    const unreadCount = notifications.filter(n => !n.read).length;
    updateNotificationBadge(unreadCount);
}

/**
 * Met à jour le badge de notification
 */
function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// Ajouter des styles pour les badges
const styleElement = document.createElement('style');
styleElement.textContent = `
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-success {
        background-color: var(--success-light);
        color: var(--success);
    }
    
    .badge-warning {
        background-color: var(--warning-light);
        color: var(--warning);
    }
    
    .badge-danger {
        background-color: var(--danger-light);
        color: var(--danger);
    }
`;

document.head.appendChild(styleElement);
