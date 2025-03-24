/**
 * planning-interactive.js
 * Script amélioré pour les fonctionnalités interactives du planning
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialisation de toutes les fonctionnalités
  initKanban();
  initNotifications();
  initFilters();
  initMobileSupport();
  initOnboarding();
  initThemeToggle();
  initSearchEnhancements();
  initAccessibilityFeatures();
  
  // Animation d'entrée des éléments
  animateElements();
});

/**
 * Fonctionnalité de Kanban améliorée avec animation et retour haptique
 */
function initKanban() {
  const kanbanCards = document.querySelectorAll('.kanban-card');
  const kanbanColumns = document.querySelectorAll('.kanban-column');
  const kanbanContainer = document.querySelector('.kanban-container');
  
  // Comptage initial des cartes par colonne et mise à jour des compteurs
  updateColumnCounts();
  
  // Gestion du glisser-déposer avec animations fluides
  kanbanCards.forEach(card => {
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);
    
    // Ajouter un événement de clic pour ouvrir le panneau de détails
    card.addEventListener('click', function(e) {
      // Ne pas ouvrir le panneau si on clique sur un bouton d'action
      if (!e.target.closest('.kanban-card-actions')) {
        const candidateId = this.dataset.candidateId;
        openCandidatePanel(candidateId);
      }
    });
  });
  
  kanbanColumns.forEach(column => {
    column.addEventListener('dragover', handleDragOver);
    column.addEventListener('dragenter', handleDragEnter);
    column.addEventListener('dragleave', handleDragLeave);
    column.addEventListener('drop', handleDrop);
  });
  
  // Fonctions de gestion des événements de drag-and-drop
  function handleDragStart(e) {
    this.classList.add('dragging');
    e.dataTransfer.setData('text/plain', this.dataset.candidateId);
    
    // Effet de rotation pour un retour visuel amélioré
    this.style.transform = 'rotate(3deg) scale(1.05)';
    
    // Ajouter un effet fantôme plus esthétique
    const dragImage = this.cloneNode(true);
    dragImage.style.opacity = '0.7';
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-1000px';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 20, 20);
    
    // Supprimer le clone après utilisation
    setTimeout(() => {
      document.body.removeChild(dragImage);
    }, 0);
  }
  
  function handleDragEnd(e) {
    this.classList.remove('dragging');
    this.style.transform = '';
    
    // Réinitialiser les colonnes
    kanbanColumns.forEach(col => {
      col.classList.remove('drop-target');
    });
  }
  
  function handleDragOver(e) {
    e.preventDefault();
    this.classList.add('drop-target');
  }
  
  function handleDragEnter(e) {
    e.preventDefault();
    this.classList.add('drop-target');
  }
  
  function handleDragLeave(e) {
    this.classList.remove('drop-target');
  }
  
  function handleDrop(e) {
    e.preventDefault();
    this.classList.remove('drop-target');
    
    const candidateId = e.dataTransfer.getData('text/plain');
    const card = document.querySelector(`.kanban-card[data-candidate-id="${candidateId}"]`);
    const fromColumn = card.closest('.kanban-column');
    const toColumn = this;
    
    if (fromColumn !== toColumn) {
      // Ajouter une animation de transition
      card.style.opacity = '0';
      card.style.transform = 'translateY(-20px)';
      
      // Ajouter un délai pour l'animation
      setTimeout(() => {
        const columnContent = toColumn.querySelector('.kanban-column-content');
        const addCardButton = columnContent.querySelector('.kanban-add-card');
        
        // Insérer avant le bouton "Ajouter un candidat"
        columnContent.insertBefore(card, addCardButton);
        
        // Animer l'apparition dans la nouvelle colonne
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
        
        // Vibration subtile pour le retour haptique sur mobile
        if (window.navigator.vibrate) {
          window.navigator.vibrate(50);
        }
        
        // Mettre à jour les compteurs
        updateColumnCounts();
        
        // Afficher une notification de déplacement
        showToast(`Candidat déplacé vers ${toColumn.querySelector('.kanban-column-title').textContent}`, 'success');
      }, 200);
    }
  }
  
  // Fonction pour mettre à jour les compteurs de colonnes
  function updateColumnCounts() {
    kanbanColumns.forEach(column => {
      const cards = column.querySelectorAll('.kanban-card').length;
      const countElement = column.querySelector('.kanban-column-count');
      
      if (countElement) {
        // Animer le changement de compteur
        const currentValue = parseInt(countElement.textContent);
        if (currentValue !== cards) {
          animateCounter(countElement, currentValue, cards);
        }
      }
    });
  }
  
  // Animation du compteur
  function animateCounter(element, start, end) {
    let current = start;
    const increment = end > start ? 1 : -1;
    const duration = 300; // ms
    const steps = Math.abs(end - start);
    const stepTime = steps ? duration / steps : duration;
    
    function updateCounter() {
      element.textContent = current;
      
      if (current !== end) {
        current += increment;
        setTimeout(updateCounter, stepTime);
      }
    }
    
    updateCounter();
  }
  
  // Ajouter le défilement horizontal tactile pour mobile
  let isDragging = false;
  let startX, scrollLeft;
  
  kanbanContainer.addEventListener('mousedown', (e) => {
    if (window.innerWidth <= 1023) {
      isDragging = true;
      startX = e.pageX - kanbanContainer.offsetLeft;
      scrollLeft = kanbanContainer.scrollLeft;
    }
  });
  
  kanbanContainer.addEventListener('mouseleave', () => {
    isDragging = false;
  });
  
  kanbanContainer.addEventListener('mouseup', () => {
    isDragging = false;
  });
  
  kanbanContainer.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const x = e.pageX - kanbanContainer.offsetLeft;
    const walk = (x - startX) * 2; // Vitesse de défilement
    kanbanContainer.scrollLeft = scrollLeft - walk;
  });
  
  // Boutons de défilement pour mobile
  const btnScrollLeft = document.querySelector('.btn-scroll-left');
  const btnScrollRight = document.querySelector('.btn-scroll-right');
  
  if (btnScrollLeft && btnScrollRight) {
    btnScrollLeft.addEventListener('click', () => {
      kanbanContainer.scrollBy({ left: -300, behavior: 'smooth' });
      updateColumnIndicators();
    });
    
    btnScrollRight.addEventListener('click', () => {
      kanbanContainer.scrollBy({ left: 300, behavior: 'smooth' });
      updateColumnIndicators();
    });
    
    // Mise à jour des indicateurs de colonne
    kanbanContainer.addEventListener('scroll', updateColumnIndicators);
  }
  
  function updateColumnIndicators() {
    const indicators = document.querySelectorAll('.column-indicator');
    const containerWidth = kanbanContainer.clientWidth;
    const scrollPosition = kanbanContainer.scrollLeft;
    const columnWidth = 300; // Largeur approximative d'une colonne + gap
    
    const activeColumnIndex = Math.floor(scrollPosition / columnWidth);
    
    indicators.forEach((indicator, index) => {
      indicator.classList.toggle('active', index === activeColumnIndex);
    });
  }
  
  // Initialiser les indicateurs au chargement
  updateColumnIndicators();
}

/**
 * Gestion des notifications et toasts
 */
function initNotifications() {
  const toastContainer = document.querySelector('.toast-container');
  
  // Fonction pour afficher un toast
  window.showToast = function(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'x-circle';
    if (type === 'warning') icon = 'warning';
    
    toast.innerHTML = `
      <div class="toast-icon">
        <i class="ph-${icon}"></i>
      </div>
      <div class="toast-content">
        <div class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" aria-label="Fermer">
        <i class="ph-x"></i>
      </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Animation d'entrée
    setTimeout(() => {
      toast.style.transform = 'translateX(0)';
      toast.style.opacity = '1';
    }, 10);
    
    // Fermeture automatique
    const timeout = setTimeout(() => {
      closeToast(toast);
    }, duration);
    
    // Bouton de fermeture
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
      clearTimeout(timeout);
      closeToast(toast);
    });
    
    function closeToast(toast) {
      toast.style.transform = 'translateX(100%)';
      toast.style.opacity = '0';
      
      setTimeout(() => {
        toastContainer.removeChild(toast);
      }, 300);
    }
  };
  
  // Simuler une notification au chargement (à enlever en production)
  setTimeout(() => {
    showToast('5 candidats sont en attente de traitement', 'info');
  }, 2000);
}

/**
 * Gestion des filtres et de la recherche améliorée
 */
function initFilters() {
  const jobFilterTabs = document.querySelectorAll('.job-filter-tab');
  const filterChips = document.querySelectorAll('.filter-chip');
  const searchBoxes = document.querySelectorAll('.search-box, .search-global');
  
  // Gestion des onglets de filtrage par poste
  jobFilterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      jobFilterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      // Appliquer le filtre
      const jobId = tab.dataset.jobId;
      applyJobFilter(jobId);
    });
  });
  
  // Gestion des puces de filtre
  filterChips.forEach(chip => {
    const removeBtn = chip.querySelector('.remove-filter');
    
    if (removeBtn) {
      removeBtn.addEventListener('click', () => {
        // Animation de suppression
        chip.style.transform = 'translateX(10px)';
        chip.style.opacity = '0';
        
        setTimeout(() => {
          chip.remove();
          // Mettre à jour les filtres actifs
          updateActiveFilters();
        }, 300);
      });
    }
  });
  
  // Effacement de la recherche
  searchBoxes.forEach(searchBox => {
    const input = searchBox.querySelector('input');
    const clearBtn = searchBox.querySelector('.search-clear');
    
    if (input && clearBtn) {
      input.addEventListener('input', () => {
        clearBtn.style.display = input.value ? 'flex' : 'none';
        
        // Recherche en temps réel
        if (input.value.length > 2) {
          performSearch(input.value);
        }
      });
      
      clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        resetSearch();
      });
    }
  });
  
  // Fonction pour appliquer un filtre par poste
  function applyJobFilter(jobId) {
    const kanbanCards = document.querySelectorAll('.kanban-card');
    
    if (jobId === 'tous') {
      // Réinitialiser tous les filtres
      kanbanCards.forEach(card => {
        card.style.display = 'block';
        // Animation de réapparition
        setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        }, 10);
      });
    } else {
      kanbanCards.forEach(card => {
        const jobTag = card.querySelector('.job-tag');
        
        if (jobTag && jobTag.textContent.toLowerCase().includes(jobId.toLowerCase())) {
          card.style.display = 'block';
          // Animation de réapparition
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 10);
        } else {
          // Animation de disparition
          card.style.opacity = '0';
          card.style.transform = 'translateY(-10px)';
          
          setTimeout(() => {
            card.style.display = 'none';
          }, 300);
        }
      });
    }
    
    // Mettre à jour les compteurs après filtrage
    updateColumnCounts();
  }
  
  // Fonction de recherche
  function performSearch(query) {
    query = query.toLowerCase();
    const kanbanCards = document.querySelectorAll('.kanban-card');
    
    kanbanCards.forEach(card => {
      const title = card.querySelector('.kanban-card-title').textContent.toLowerCase();
      const job = card.querySelector('.job-tag').textContent.toLowerCase();
      const info = card.querySelector('.kanban-card-info').textContent.toLowerCase();
      
      if (title.includes(query) || job.includes(query) || info.includes(query)) {
        card.style.display = 'block';
        
        // Animation et surbrillance des résultats
        setTimeout(() => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
          // Ajouter une classe de surbrillance temporaire
          card.classList.add('search-highlight');
          setTimeout(() => {
            card.classList.remove('search-highlight');
          }, 1000);
        }, 10);
      } else {
        // Animation de disparition
        card.style.opacity = '0';
        card.style.transform = 'translateY(-10px)';
        
        setTimeout(() => {
          card.style.display = 'none';
        }, 300);
      }
    });
    
    // Vérifier s'il y a des résultats
    setTimeout(checkEmptySearchResults, 350);
  }
  
  // Vérifier s'il n'y a aucun résultat de recherche
  function checkEmptySearchResults() {
    const kanbanColumns = document.querySelectorAll('.kanban-column');
    
    kanbanColumns.forEach(column => {
      const visibleCards = column.querySelectorAll('.kanban-card[style*="display: block"]');
      const emptyMessage = column.querySelector('.empty-search-message');
      
      if (visibleCards.length === 0) {
        // Afficher un message si aucun résultat
        if (!emptyMessage) {
          const newEmptyMessage = document.createElement('div');
          newEmptyMessage.className = 'empty-search-message';
          newEmptyMessage.innerHTML = `
            <div class="empty-icon">
              <i class="ph-magnifying-glass"></i>
            </div>
            <p>Aucun candidat trouvé</p>
          `;
          
          const columnContent = column.querySelector('.kanban-column-content');
          columnContent.insertBefore(newEmptyMessage, columnContent.firstChild);
        }
      } else if (emptyMessage) {
        // Supprimer le message s'il y a des résultats
        emptyMessage.remove();
      }
    });
  }
  
  // Réinitialiser la recherche
  function resetSearch() {
    const kanbanCards = document.querySelectorAll('.kanban-card');
    
    kanbanCards.forEach(card => {
      card.style.display = 'block';
      
      setTimeout(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, 10);
    });
    
    // Supprimer les messages de recherche vide
    document.querySelectorAll('.empty-search-message').forEach(msg => msg.remove());
  }
  
  // Mettre à jour les compteurs de colonnes
  function updateColumnCounts() {
    const kanbanColumns = document.querySelectorAll('.kanban-column');
    
    kanbanColumns.forEach(column => {
      const visibleCards = column.querySelectorAll('.kanban-card[style*="display: block"]').length;
      const countElement = column.querySelector('.kanban-column-count');
      
      if (countElement) {
        countElement.textContent = visibleCards;
      }
    });
  }
  
  // Mettre à jour les indicateurs de filtres actifs
  function updateActiveFilters() {
    const filterChips = document.querySelectorAll('.filter-chip');
    const filterButtons = document.querySelectorAll('.btn-filter');
    
    // Mettre à jour les badges sur les boutons de filtre
    filterButtons.forEach(button => {
      const filterBadge = button.querySelector('.filter-badge');
      const relevantChips = document.querySelectorAll(`.filter-chip[data-type="${button.dataset.filterType}"]`);
      
      if (filterBadge) {
        if (relevantChips.length > 0) {
          filterBadge.textContent = relevantChips.length;
          filterBadge.style.display = 'flex';
        } else {
          filterBadge.style.display = 'none';
        }
      }
    });
  }
}

/**
 * Support mobile amélioré
 */
function initMobileSupport() {
  const sidebarToggle = document.querySelector('.sidebar-toggle-mobile');
  const sidebar = document.querySelector('.app-sidebar');
  const pageContent = document.querySelector('.app-content');
  const mobileFab = document.querySelector('.action-button');
  const mobileActionMenu = document.querySelector('.action-menu');
  
  // Gestion du menu latéral sur mobile
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      document.body.classList.toggle('sidebar-open');
      
      // Ajouter un overlay pour fermer la sidebar
      if (!document.querySelector('.sidebar-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
        
        overlay.addEventListener('click', () => {
          sidebar.classList.remove('open');
          document.body.classList.remove('sidebar-open');
          overlay.remove();
        });
      } else {
        document.querySelector('.sidebar-overlay').remove();
      }
    });
  }
  
  // Bouton d'action flottant sur mobile
  if (mobileFab && mobileActionMenu) {
    mobileFab.addEventListener('click', () => {
      mobileActionMenu.classList.toggle('show');
      
      if (mobileActionMenu.classList.contains('show')) {
        // Ajouter un overlay pour fermer le menu
        const overlay = document.createElement('div');
        overlay.className = 'fab-overlay';
        overlay.style.position = 'fixed';
        overlay.style.inset = '0';
        overlay.style.zIndex = '97';
        document.body.appendChild(overlay);
        
        overlay.addEventListener('click', () => {
          mobileActionMenu.classList.remove('show');
          overlay.remove();
        });
      } else {
        const overlay = document.querySelector('.fab-overlay');
        if (overlay) overlay.remove();
      }
    });
    
    // Fermer le menu au clic sur un élément
    const menuItems = mobileActionMenu.querySelectorAll('.action-menu-item');
    menuItems.forEach(item => {
      item.addEventListener('click', () => {
        mobileActionMenu.classList.remove('show');
        const overlay = document.querySelector('.fab-overlay');
        if (overlay) overlay.remove();
      });
    });
  }
  
  // Optimisation pour l'orientation de l'écran
  window.addEventListener('orientationchange', () => {
    // Recalculer les hauteurs et dimensions
    setTimeout(() => {
      const kanbanContainer = document.querySelector('.kanban-container');
      if (kanbanContainer) {
        if (window.innerWidth <= 767) {
          kanbanContainer.style.height = 'calc(100vh - 400px)';
        } else if (window.innerWidth <= 1023) {
          kanbanContainer.style.height = 'calc(100vh - 340px)';
        } else {
          kanbanContainer.style.height = 'calc(100vh - 320px)';
        }
      }
    }, 300);
  });
}

/**
 * Guide d'onboarding pour les nouveaux utilisateurs
 */
function initOnboarding() {
  const onboardingTips = document.getElementById('onboardingTips');
  
  if (onboardingTips) {
    // Vérifier si l'utilisateur a déjà fermé le guide
    const hideOnboarding = localStorage.getItem('hideOnboardingTips');
    
    if (hideOnboarding !== 'true') {
      setTimeout(() => {
        onboardingTips.style.display = 'block';
        
        setTimeout(() => {
          onboardingTips.style.transform = 'translateY(0)';
          onboardingTips.style.opacity = '1';
        }, 100);
      }, 1500);
    }
    
    // Bouton pour fermer le guide
    const closeBtn = onboardingTips.querySelector('.onboarding-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        onboardingTips.style.transform = 'translateY(20px)';
        onboardingTips.style.opacity = '0';
        
        setTimeout(() => {
          onboardingTips.style.display = 'none';
        }, 300);
      });
    }
    
    // Checkbox pour ne plus afficher
    const hideCheckbox = onboardingTips.querySelector('#hideOnboarding');
    if (hideCheckbox) {
      hideCheckbox.addEventListener('change', (e) => {
        if (e.target.checked) {
          localStorage.setItem('hideOnboardingTips', 'true');
        } else {
          localStorage.removeItem('hideOnboardingTips');
        }
      });
    }
  }
}

/**
 * Gestion du thème sombre/clair
 */
function initThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  
  if (themeToggle) {
    // Vérifier la préférence système et les paramètres sauvegardés
    const savedTheme = localStorage.getItem('theme');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Appliquer le thème initial
    if (savedTheme === 'dark' || (!savedTheme && prefersDarkScheme.matches)) {
      document.body.classList.add('dark-mode');
      themeToggle.innerHTML = '<i class="ph-moon"></i>';
    } else {
      themeToggle.innerHTML = '<i class="ph-sun"></i>';
    }
    
    // Toggle du thème au clic
    themeToggle.addEventListener('click', () => {
      if (document.body.classList.contains('dark-mode')) {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
        themeToggle.innerHTML = '<i class="ph-sun"></i>';
        
        // Animation de transition
        const sun = themeToggle.querySelector('i');
        sun.style.transform = 'rotate(180deg)';
        setTimeout(() => {
          sun.style.transform = 'rotate(0)';
        }, 10);
      } else {
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
        themeToggle.innerHTML = '<i class="ph-moon"></i>';
        
        // Animation de transition
        const moon = themeToggle.querySelector('i');
        moon.style.transform = 'rotate(-180deg)';
        setTimeout(() => {
          moon.style.transform = 'rotate(0)';
        }, 10);
      }
    });
  }
}

/**
 * Améliorations de la recherche
 */
function initSearchEnhancements() {
  const searchInputs = document.querySelectorAll('.search-box input, .search-global input');
  
  searchInputs.forEach(input => {
    // Suggestions intelligentes
    input.addEventListener('focus', () => {
      // Vérifier si les suggestions existent déjà
      if (!input.parentElement.querySelector('.search-suggestions')) {
        // Créer et ajouter le conteneur de suggestions
        const suggestions = document.createElement('div');
        suggestions.className = 'search-suggestions';
        
        // Ajouter des suggestions récentes et populaires
        suggestions.innerHTML = `
          <div class="suggestion-header">Recherches récentes</div>
          <div class="suggestion-item"><i class="ph-clock-counter-clockwise"></i> Développeur Paris</div>
          <div class="suggestion-item"><i class="ph-clock-counter-clockwise"></i> Comptable 5 ans d'expérience</div>
          
          <div class="suggestion-header">Suggestions populaires</div>
          <div class="suggestion-item"><i class="ph-trending-up"></i> Disponible immédiatement</div>
          <div class="suggestion-item"><i class="ph-trending-up"></i> Remote</div>
          <div class="suggestion-item"><i class="ph-trending-up"></i> Anglais courant</div>
        `;
        
        input.parentElement.appendChild(suggestions);
        
        // Ajouter des événements aux suggestions
        const suggestionItems = suggestions.querySelectorAll('.suggestion-item');
        suggestionItems.forEach(item => {
          item.addEventListener('click', () => {
            const text = item.textContent.trim();
            input.value = text;
            input.focus();
            
            // Déclencher la recherche
            const event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);
            
            // Fermer les suggestions
            suggestions.style.display = 'none';
          });
        });
      }
    });
  });
}

/**
 * Fonctionnalités d'accessibilité
 */
function initAccessibilityFeatures() {
  // Support pour la navigation au clavier
  document.querySelectorAll('.kanban-card, .btn, .btn-icon').forEach(element => {
    if (!element.hasAttribute('tabindex')) {
      element.setAttribute('tabindex', '0');
    }
    
    // Ajouter des événements clavier pour les éléments cliquables
    if (element.classList.contains('kanban-card')) {
      element.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          element.click();
        }
      });
    }
  });
  
  // Amélioration du contraste des couleurs
  const highContrastMediaQuery = window.matchMedia('(prefers-contrast: high)');
  if (highContrastMediaQuery.matches) {
    document.body.classList.add('high-contrast');
  }
  
  // Réduction des animations si nécessaire
  const reducedMotionMediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reducedMotionMediaQuery.matches) {
    document.body.classList.add('reduced-motion');
  }
}

/**
 * Animation des éléments lors du chargement
 */
function animateElements() {
  const elements = document.querySelectorAll('.animated-fade-in');
  
  elements.forEach((element, index) => {
    const delay = element.style.animationDelay || `${index * 0.1}s`;
    element.style.animationDelay = delay;
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    
    // Vérifier si les animations sont réduites
    if (document.body.classList.contains('reduced-motion')) {
      element.style.opacity = '1';
      element.style.transform = 'translateY(0)';
    } else {
      setTimeout(() => {
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
      }, index * 100); // Délai progressif
    }
  });
}

/**
 * Ouvrir le panneau de détails du candidat
 * @param {string} candidateId - ID du candidat à afficher
 */
function openCandidatePanel(candidateId) {
  const candidatePanel = document.getElementById('candidateDetailsPanel');
  const overlay = document.getElementById('panelOverlay');
  
  if (candidatePanel && overlay) {
    // Afficher le panneau et l'overlay
    overlay.style.display = 'block';
    candidatePanel.style.transform = 'translateX(0)';
    
    // Ajouter une classe au body pour empêcher le défilement
    document.body.classList.add('panel-open');
    
    // Animer les éléments à l'intérieur du panneau
    const animatedElements = candidatePanel.querySelectorAll('.panel-animate-in');
    animatedElements.forEach((element, index) => {
      element.style.opacity = '0';
      element.style.transform = 'translateY(20px)';
      
      setTimeout(() => {
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
      }, 300 + index * 100); // Délai progressif après l'ouverture du panneau
    });
    
    // Charger les données du candidat (simulé)
    updateCandidatePanelData(candidateId);
    
    // Événement pour fermer le panneau
    const closeBtn = document.getElementById('closePanelBtn');
    if (closeBtn) {
      closeBtn.addEventListener('click', closeCandidatePanel);
    }
    
    // Fermer le panneau en cliquant sur l'overlay
    overlay.addEventListener('click', closeCandidatePanel);
  }
}

/**
 * Fermer le panneau de détails
 */
function closeCandidatePanel() {
  const candidatePanel = document.getElementById('candidateDetailsPanel');
  const overlay = document.getElementById('panelOverlay');
  
  if (candidatePanel && overlay) {
    candidatePanel.style.transform = 'translateX(100%)';
    overlay.style.opacity = '0';
    
    setTimeout(() => {
      overlay.style.display = 'none';
      overlay.style.opacity = '1';
      document.body.classList.remove('panel-open');
    }, 300);
  }
}

/**
 * Mettre à jour les données du panneau (simulé)
 * @param {string} candidateId - ID du candidat
 */
function updateCandidatePanelData(candidateId) {
  // Simulation des données du candidat
  const candidateCard = document.querySelector(`.kanban-card[data-candidate-id="${candidateId}"]`);
  
  if (candidateCard) {
    const candidateName = candidateCard.querySelector('.kanban-card-title').textContent;
    const candidateJob = candidateCard.querySelector('.job-tag').textContent;
    const matchValue = candidateCard.querySelector('.priority-badge').textContent.trim();
    
    // Mettre à jour les éléments du panneau
    const panelName = document.querySelector('.candidate-name');
    const panelPosition = document.querySelector('.candidate-position');
    const panelMatch = document.querySelector('.candidate-match .match-bar');
    const panelMatchText = document.querySelector('.candidate-match span');
    
    if (panelName) panelName.textContent = candidateName;
    if (panelPosition) panelPosition.textContent = candidateJob;
    if (panelMatch) panelMatch.style.width = matchValue;
    if (panelMatchText) panelMatchText.textContent = `${matchValue} de compatibilité`;
    
    // Mettre à jour l'avatar
    const panelAvatar = document.querySelector('.profile-avatar');
    if (panelAvatar) {
      const initials = candidateName.split(' ').map(n => n[0]).join('');
      panelAvatar.textContent = initials;
    }
  }
}