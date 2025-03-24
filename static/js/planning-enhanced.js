/**
 * planning-enhanced.js
 * Script pour améliorer l'interactivité et l'expérience utilisateur de la page planning
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialisation de toutes les fonctionnalités
  initSidebar();
  initDropdowns();
  initKanbanDragAndDrop();
  enhancedSearch();
  initToasts();
  initMobileCompactView();
  initThemeToggle();
  initUserMenu();
  initHelpTooltips();
  initFilterChips();
});

/**
 * Gestion améliorée de la sidebar pour mobile
 */
function initSidebar() {
  const sidebarToggle = document.querySelector('.sidebar-toggle-mobile');
  const sidebar = document.querySelector('.app-sidebar');
  const appLayout = document.querySelector('.app-layout');
  
  // Création d'un overlay pour fermer la sidebar sur mobile
  if (!document.querySelector('.sidebar-overlay')) {
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    appLayout.appendChild(overlay);
    
    overlay.addEventListener('click', () => {
      appLayout.classList.remove('sidebar-open');
      sidebar.classList.remove('open');
    });
  }
  
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      appLayout.classList.toggle('sidebar-open');
    });
  }
}

/**
 * Initialisation des dropdowns améliorés
 */
function initDropdowns() {
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle, [data-bs-toggle="dropdown"]');
  
  dropdownToggles.forEach(toggle => {
    // Si nous n'utilisons pas Bootstrap, nous devons ajouter manuellement le comportement
    if (!window.bootstrap) {
      toggle.addEventListener('click', (e) => {
        e.preventDefault();
        const target = toggle.nextElementSibling;
        if (target && target.classList.contains('dropdown-menu')) {
          target.classList.toggle('show');
          toggle.setAttribute('aria-expanded', target.classList.contains('show'));
          
          // Fermer le dropdown si on clique ailleurs
          const closeDropdown = (event) => {
            if (!toggle.contains(event.target) && !target.contains(event.target)) {
              target.classList.remove('show');
              toggle.setAttribute('aria-expanded', 'false');
              document.removeEventListener('click', closeDropdown);
            }
          };
          
          document.addEventListener('click', closeDropdown);
        }
      });
    }
  });
}

/**
 * Initialisation du glisser-déposer pour les cartes Kanban
 */
function initKanbanDragAndDrop() {
  const cards = document.querySelectorAll('.kanban-card');
  const columns = document.querySelectorAll('.kanban-column');
  
  cards.forEach(card => {
    // Rendre les cartes draggable
    card.setAttribute('draggable', 'true');
    
    card.addEventListener('dragstart', (e) => {
      // Mémoriser l'ID de la carte en cours de déplacement
      e.dataTransfer.setData('text/plain', card.dataset.candidateId);
      
      // Ajouter la classe pour le style de déplacement
      card.classList.add('dragging');
      
      // Retour haptique sur mobile si disponible
      if (navigator.vibrate) {
        navigator.vibrate(50);
      }
      
      // Délai pour que l'animation soit visible
      setTimeout(() => {
        card.style.opacity = '0.4';
      }, 10);
    });
    
    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
      card.style.opacity = '1';
    });
  });
  
  columns.forEach(column => {
    column.addEventListener('dragover', (e) => {
      e.preventDefault();
      column.classList.add('drop-target');
    });
    
    column.addEventListener('dragleave', () => {
      column.classList.remove('drop-target');
    });
    
    column.addEventListener('drop', (e) => {
      e.preventDefault();
      column.classList.remove('drop-target');
      
      const candidateId = e.dataTransfer.getData('text/plain');
      const card = document.querySelector(`.kanban-card[data-candidate-id="${candidateId}"]`);
      
      if (card) {
        // Empêcher le drop si la carte est déjà dans cette colonne
        const sourceColumn = card.closest('.kanban-column');
        if (sourceColumn === column) return;
        
        // Ajouter la carte à la nouvelle colonne
        const columnContent = column.querySelector('.kanban-column-content');
        const addCardButton = column.querySelector('.kanban-add-card');
        
        if (columnContent && addCardButton) {
          // Insérer la carte avant le bouton d'ajout
          columnContent.insertBefore(card, addCardButton);
          
          // Mettre à jour les compteurs
          updateColumnCounts();
          
          // Afficher une notification de succès
          const sourceStage = sourceColumn.dataset.stage;
          const targetStage = column.dataset.stage;
          
          showToast(
            'success',
            'Candidat déplacé',
            `Le candidat a été déplacé de "${getStageLabel(sourceStage)}" vers "${getStageLabel(targetStage)}"`
          );
        }
      }
    });
  });
}

/**
 * Mettre à jour les compteurs de cartes dans les colonnes
 */
function updateColumnCounts() {
  const columns = document.querySelectorAll('.kanban-column');
  
  columns.forEach(column => {
    const cards = column.querySelectorAll('.kanban-card').length;
    const countElement = column.querySelector('.kanban-column-count');
    
    if (countElement) {
      countElement.textContent = cards;
    }
    
    // Afficher/masquer le message "colonne vide"
    const emptyMessage = column.querySelector('.empty-column-message');
    const columnContent = column.querySelector('.kanban-column-content');
    
    if (cards === 0 && !emptyMessage) {
      // Créer le message si la colonne est vide
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'empty-column-message';
      emptyDiv.innerHTML = `
        <div class="empty-icon">
          <i class="ph-smiley"></i>
        </div>
        <p>Aucun candidat à cette étape</p>
        <button class="btn btn-sm btn-outline mt-2">
          <i class="ph-plus"></i> Ajouter un candidat
        </button>
      `;
      
      // Insérer avant le bouton d'ajout
      const addButton = column.querySelector('.kanban-add-card');
      if (columnContent && addButton) {
        columnContent.insertBefore(emptyDiv, addButton);
      }
    } else if (cards > 0 && emptyMessage) {
      // Supprimer le message si la colonne n'est plus vide
      emptyMessage.remove();
    }
  });
}

/**
 * Obtenir le libellé correspondant au code d'étape
 */
function getStageLabel(stageCode) {
  const stageLabels = {
    'validation': 'En cours de validation',
    'call': 'Premier contact',
    'visio': 'Visioconférence',
    'presentiel': 'Entretien',
    'acceptation': 'Acceptation'
  };
  
  return stageLabels[stageCode] || stageCode;
}

/**
 * Recherche améliorée avec suggestions
 */
function enhancedSearch() {
  const searchInputs = document.querySelectorAll('.search-box input, .search-global input');
  
  searchInputs.forEach(input => {
    const container = input.closest('.search-box, .search-global');
    
    // Ajouter le conteneur de suggestions s'il n'existe pas déjà
    if (!container.querySelector('.search-suggestions')) {
      const suggestionsDiv = document.createElement('div');
      suggestionsDiv.className = 'search-suggestions';
      suggestionsDiv.innerHTML = `
        <div class="suggestion-header">Suggestions récentes</div>
        <div class="suggestion-item">
          <i class="ph-user"></i>
          <span>Prénom N. (Comptabilité)</span>
        </div>
        <div class="suggestion-item">
          <i class="ph-briefcase"></i>
          <span>Développeur Full-Stack</span>
        </div>
        <div class="suggestion-header">Filtres rapides</div>
        <div class="suggestion-item">
          <i class="ph-funnel"></i>
          <span>Disponibles immédiatement</span>
        </div>
      `;
      
      // Insérer après l'icône de recherche
      container.appendChild(suggestionsDiv);
      
      // Fermer les suggestions au clic à l'extérieur
      document.addEventListener('click', (e) => {
        if (!container.contains(e.target)) {
          suggestionsDiv.style.display = 'none';
        }
      });
      
      // Gérer les clics sur les suggestions
      const suggestionItems = suggestionsDiv.querySelectorAll('.suggestion-item');
      suggestionItems.forEach(item => {
        item.addEventListener('click', () => {
          input.value = item.querySelector('span').textContent;
          suggestionsDiv.style.display = 'none';
          input.focus();
          
          // Déclencher la recherche
          triggerSearch(input.value);
        });
      });
    }
    
    // Logique de recherche en temps réel
    input.addEventListener('input', e => {
      const value = e.target.value.toLowerCase();
      const suggestions = container.querySelector('.search-suggestions');
      
      if (value.length > 2) {
        // Afficher les suggestions
        if (suggestions) {
          suggestions.style.display = 'block';
        }
        
        // Filtrer les cartes Kanban visibles
        filterKanbanCards(value);
      } else if (value.length === 0) {
        // Réinitialiser le filtre
        resetKanbanCards();
        
        if (suggestions) {
          suggestions.style.display = 'none';
        }
      }
    });
    
    // Bouton pour effacer la recherche
    const clearButton = container.querySelector('.search-clear');
    if (clearButton) {
      clearButton.addEventListener('click', () => {
        input.value = '';
        input.focus();
        resetKanbanCards();
        
        const suggestions = container.querySelector('.search-suggestions');
        if (suggestions) {
          suggestions.style.display = 'none';
        }
      });
    }
  });
}

/**
 * Filtrer les cartes Kanban en fonction du terme de recherche
 */
function filterKanbanCards(searchTerm) {
  const cards = document.querySelectorAll('.kanban-card');
  let hasResults = false;
  
  cards.forEach(card => {
    const cardText = card.textContent.toLowerCase();
    if (cardText.includes(searchTerm)) {
      card.style.display = 'block';
      hasResults = true;
    } else {
      card.style.display = 'none';
    }
  });
  
  // Afficher un message si aucun résultat
  handleEmptySearchResults(hasResults);
}

/**
 * Réinitialiser l'affichage des cartes Kanban
 */
function resetKanbanCards() {
  const cards = document.querySelectorAll('.kanban-card');
  cards.forEach(card => {
    card.style.display = 'block';
  });
  
  // Supprimer le message de résultats vides
  const emptyState = document.querySelector('.empty-search-state');
  if (emptyState) {
    emptyState.remove();
  }
}

/**
 * Gérer l'affichage d'un message quand la recherche ne donne pas de résultats
 */
function handleEmptySearchResults(hasResults) {
  // Supprimer le message existant s'il y a des résultats
  const existingEmptyState = document.querySelector('.empty-search-state');
  if (existingEmptyState) {
    existingEmptyState.remove();
  }
  
  // Ajouter un message si aucun résultat
  if (!hasResults) {
    const container = document.querySelector('#kanban-view');
    if (container) {
      const emptyState = document.createElement('div');
      emptyState.className = 'empty-search-state';
      emptyState.innerHTML = `
        <div class="empty-search-icon">
          <i class="ph-magnifying-glass"></i>
        </div>
        <h4>Aucun résultat trouvé</h4>
        <p>Essayez avec d'autres termes ou filtres</p>
        <button class="btn btn-outline btn-sm reset-search">
          <i class="ph-x"></i> Effacer les filtres
        </button>
      `;
      
      container.appendChild(emptyState);
      
      // Ajouter l'action pour réinitialiser la recherche
      const resetButton = emptyState.querySelector('.reset-search');
      if (resetButton) {
        resetButton.addEventListener('click', () => {
          const searchInputs = document.querySelectorAll('.search-box input, .search-global input');
          searchInputs.forEach(input => {
            input.value = '';
          });
          resetKanbanCards();
        });
      }
    }
  }
}

/**
 * Déclencher une recherche
 */
function triggerSearch(searchTerm) {
  if (searchTerm) {
    filterKanbanCards(searchTerm.toLowerCase());
  } else {
    resetKanbanCards();
  }
}

/**
 * Système de notifications toast
 */
function initToasts() {
  // Créer le conteneur de toasts s'il n'existe pas
  if (!document.querySelector('.toast-container')) {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }
}

/**
 * Afficher une notification toast
 */
function showToast(type, title, message) {
  const toastContainer = document.querySelector('.toast-container');
  
  if (!toastContainer) return;
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  toast.innerHTML = `
    <div class="toast-icon">
      <i class="ph-${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'warning-circle'}"></i>
    </div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
    <button class="toast-close">
      <i class="ph-x"></i>
    </button>
  `;
  
  toastContainer.appendChild(toast);
  
  // Auto-fermeture après 4 secondes
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 4000);
  
  // Fermeture manuelle
  toast.querySelector('.toast-close').addEventListener('click', () => {
    toast.style.opacity = '0';
    setTimeout(() => {
      toast.remove();
    }, 300);
  });
}

/**
 * Initialisation du mode compact pour mobile
 */
function initMobileCompactView() {
  const kanbanContainer = document.querySelector('.kanban-container');
  
  if (kanbanContainer && window.innerWidth <= 767) {
    // Créer les contrôles de vue compacte s'ils n'existent pas
    if (!document.querySelector('.view-toggle-compact')) {
      const toggleContainer = document.createElement('div');
      toggleContainer.className = 'view-toggle-compact';
      toggleContainer.innerHTML = `
        <button class="view-toggle-compact-btn active" data-view="normal">
          <i class="ph-layout"></i> Normal
        </button>
        <button class="view-toggle-compact-btn" data-view="compact">
          <i class="ph-layout-columns"></i> Compact
        </button>
      `;
      
      // Insérer avant le conteneur Kanban
      kanbanContainer.parentNode.insertBefore(toggleContainer, kanbanContainer);
      
      // Ajouter les événements
      const toggleButtons = toggleContainer.querySelectorAll('.view-toggle-compact-btn');
      toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
          toggleButtons.forEach(btn => btn.classList.remove('active'));
          button.classList.add('active');
          
          const cards = document.querySelectorAll('.kanban-card');
          
          if (button.dataset.view === 'compact') {
            cards.forEach(card => card.classList.add('kanban-card-compact'));
          } else {
            cards.forEach(card => card.classList.remove('kanban-card-compact'));
          }
        });
      });
    }
    
    // Ajouter des boutons de navigation pour le défilement mobile
    if (!document.querySelector('.kanban-scroll-buttons')) {
      const scrollButtons = document.createElement('div');
      scrollButtons.className = 'kanban-scroll-buttons';
      scrollButtons.innerHTML = `
        <button class="btn-scroll btn-scroll-left" aria-label="Défiler vers la gauche">
          <i class="ph-caret-left"></i>
        </button>
        <button class="btn-scroll btn-scroll-right" aria-label="Défiler vers la droite">
          <i class="ph-caret-right"></i>
        </button>
      `;
      
      kanbanContainer.parentNode.appendChild(scrollButtons);
      
      // Ajouter les événements de défilement
      const leftButton = scrollButtons.querySelector('.btn-scroll-left');
      const rightButton = scrollButtons.querySelector('.btn-scroll-right');
      
      leftButton.addEventListener('click', () => {
        kanbanContainer.scrollBy({ left: -300, behavior: 'smooth' });
      });
      
      rightButton.addEventListener('click', () => {
        kanbanContainer.scrollBy({ left: 300, behavior: 'smooth' });
      });
    }
  }
}

/**
 * Initialisation du basculement de thème (clair/sombre)
 */
function initThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  
  if (themeToggle) {
    // Vérifier si un thème est déjà enregistré
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      document.body.classList.add('dark-mode');
      themeToggle.innerHTML = '<i class="ph-moon"></i>';
    }
    
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
      
      if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
        themeToggle.innerHTML = '<i class="ph-moon"></i>';
      } else {
        localStorage.setItem('theme', 'light');
        themeToggle.innerHTML = '<i class="ph-sun"></i>';
      }
    });
  }
}

/**
 * Initialisation du menu utilisateur amélioré
 */
function initUserMenu() {
  const userMenuToggle = document.querySelector('.user-menu-toggle');
  const userDropdown = document.querySelector('.user-dropdown');
  
  if (userMenuToggle && userDropdown) {
    userMenuToggle.addEventListener('click', () => {
      const expanded = userMenuToggle.getAttribute('aria-expanded') === 'true';
      userMenuToggle.setAttribute('aria-expanded', !expanded);
      
      if (!expanded) {
        userDropdown.style.display = 'block';
        
        // Fermer le menu si on clique ailleurs
        const closeMenu = (e) => {
          if (!userMenuToggle.contains(e.target) && !userDropdown.contains(e.target)) {
            userDropdown.style.display = 'none';
            userMenuToggle.setAttribute('aria-expanded', 'false');
            document.removeEventListener('click', closeMenu);
          }
        };
        
        setTimeout(() => {
          document.addEventListener('click', closeMenu);
        }, 0);
      } else {
        userDropdown.style.display = 'none';
      }
    });
  }
}

/**
 * Initialisation des tooltips d'aide
 */
function initHelpTooltips() {
  // Ajouter des tooltips d'aide aux endroits stratégiques
  const helpTargets = [
    { selector: '.priority-badge', title: "Qu'est-ce que le matching?", 
      content: "Le score de matching indique la compatibilité entre le candidat et le poste, basé sur les compétences, l'expérience et les préférences. Un score plus élevé indique une meilleure adéquation." },
    { selector: '.recruitment-progress', title: "Comprendre le processus", 
      content: "Ce diagramme montre les étapes du processus de recrutement et où en sont vos candidats. L'étape active est mise en évidence." }
  ];
  
  helpTargets.forEach(target => {
    const elements = document.querySelectorAll(target.selector);
    
    elements.forEach(element => {
      if (!element.querySelector('.feature-help')) {
        const helpDiv = document.createElement('div');
        helpDiv.className = 'feature-help';
        helpDiv.innerHTML = `
          <button class="help-trigger" aria-label="Aide contextuelle">
            <i class="ph-question"></i>
          </button>
          <div class="help-content">
            <h5>${target.title}</h5>
            <p>${target.content}</p>
            <a href="#" class="help-link">En savoir plus <i class="ph-arrow-right"></i></a>
          </div>
        `;
        
        // Positionner correctement en fonction de l'élément cible
        if (target.selector === '.priority-badge') {
          element.parentNode.style.position = 'relative';
          element.parentNode.appendChild(helpDiv);
        } else {
          // S'assurer que l'élément parent peut positionner correctement le tooltip
          if (window.getComputedStyle(element).position === 'static') {
            element.style.position = 'relative';
          }
          element.appendChild(helpDiv);
        }
      }
    });
  });
}

/**
 * Initialisation des puces de filtre
 */
function initFilterChips() {
  const filterChips = document.querySelectorAll('.filter-chip');
  
  filterChips.forEach(chip => {
    const removeButton = chip.querySelector('.remove-filter');
    
    if (removeButton) {
      removeButton.addEventListener('click', () => {
        // Animation de sortie
        chip.style.transform = 'translateY(-10px)';
        chip.style.opacity = '0';
        
        setTimeout(() => {
          chip.remove();
          
          // Mettre à jour le badge de filtre
          updateFilterBadge();
          
          // Afficher une notification
          showToast('success', 'Filtre supprimé', 'Le filtre a été supprimé avec succès');
        }, 300);
      });
    }
  });
  
  // Mette à jour le badge initial
  updateFilterBadge();
}

/**
 * Mettre à jour le badge du nombre de filtres actifs
 */
function updateFilterBadge() {
  const filterChips = document.querySelectorAll('.filter-chip');
  const filterButtons = document.querySelectorAll('.btn-filter');
  
  filterButtons.forEach(button => {
    // Supprimer les badges existants
    const existingBadge = button.querySelector('.filter-badge');
    if (existingBadge) {
      existingBadge.remove();
    }
    
    // Ajouter un nouveau badge si des filtres sont actifs
    if (filterChips.length > 0) {
      const badge = document.createElement('span');
      badge.className = 'filter-badge';
      badge.textContent = filterChips.length;
      button.appendChild(badge);
    }
  });
}