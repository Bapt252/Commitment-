/**
 * Script pour ajouter un toggle de mode sombre
 * Amélioration UI/UX pour Commitment-
 */

document.addEventListener('DOMContentLoaded', function() {
    // Créer le bouton de toggle
    const darkModeToggle = document.createElement('button');
    darkModeToggle.className = 'dark-mode-toggle';
    darkModeToggle.setAttribute('aria-label', 'Basculer le mode sombre');
    darkModeToggle.innerHTML = `
        <i class="fas fa-moon moon-icon"></i>
        <i class="fas fa-sun sun-icon"></i>
        <span class="toggle-slider"></span>
    `;
    
    // Ajouter le bouton au header
    const header = document.querySelector('header .container');
    if (header) {
        header.insertBefore(darkModeToggle, header.querySelector('nav'));
    }
    
    // Ajouter la classe support au body
    document.body.classList.add('dark-mode-support');
    
    // Vérifier les préférences de l'utilisateur
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedMode = localStorage.getItem('darkMode');
    
    // Appliquer le mode sombre si nécessaire
    if (savedMode === 'true' || (savedMode === null && prefersDarkMode)) {
        document.body.classList.add('dark-mode');
        darkModeToggle.classList.add('active');
    }
    
    // Gérer le basculement du mode sombre
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        darkModeToggle.classList.toggle('active');
        
        // Enregistrer la préférence
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        
        // Animation de transition
        document.body.classList.add('theme-transition');
        setTimeout(() => {
            document.body.classList.remove('theme-transition');
        }, 1000);
    });
    
    // Ajouter des styles pour le bouton de toggle et les transitions
    const style = document.createElement('style');
    style.textContent = `
        .dark-mode-toggle {
            position: relative;
            width: 60px;
            height: 30px;
            border-radius: 15px;
            background: #e0e0e0;
            border: none;
            padding: 0;
            margin-right: 15px;
            cursor: pointer;
            overflow: hidden;
            transition: background-color 0.3s ease;
        }
        
        .dark-mode-toggle.active {
            background: var(--primary);
        }
        
        .toggle-slider {
            position: absolute;
            top: 3px;
            left: 3px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: white;
            transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55), box-shadow 0.3s ease;
            z-index: 2;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .dark-mode-toggle.active .toggle-slider {
            transform: translateX(30px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
        }
        
        .moon-icon, .sun-icon {
            position: absolute;
            top: 6px;
            font-size: 18px;
            transition: opacity 0.3s ease, transform 0.5s ease;
        }
        
        .moon-icon {
            right: 8px;
            color: #555;
            opacity: 1;
        }
        
        .sun-icon {
            left: 8px;
            color: #f1c40f;
            opacity: 0;
            transform: rotate(-45deg);
        }
        
        .dark-mode-toggle.active .moon-icon {
            opacity: 0;
            transform: rotate(45deg);
        }
        
        .dark-mode-toggle.active .sun-icon {
            opacity: 1;
            transform: rotate(0);
        }
        
        /* Styles pour le mode sombre */
        body.dark-mode {
            background-color: var(--gray-900);
            color: var(--gray-200);
        }
        
        body.dark-mode header {
            background-color: var(--gray-800);
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        body.dark-mode header nav a {
            color: var(--gray-300);
        }
        
        body.dark-mode .logo {
            color: white;
        }
        
        body.dark-mode .candidate-dashboard-section {
            background-color: var(--gray-800);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        
        body.dark-mode .section-heading {
            color: var(--primary-light);
        }
        
        body.dark-mode .form-control {
            background-color: var(--gray-700);
            border-color: var(--gray-600);
            color: white;
        }
        
        body.dark-mode .filter-badge:not(.active) {
            background-color: var(--gray-700);
            color: var(--gray-300);
        }
        
        body.dark-mode .opportunity-card {
            background-color: var(--gray-800);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        body.dark-mode .company-details h3,
        body.dark-mode .company-details h4 {
            color: white;
        }
        
        body.dark-mode .status-label, 
        body.dark-mode .travel-time {
            color: var(--gray-400);
        }
        
        body.dark-mode .progress-bar-container {
            background-color: var(--gray-700);
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        }
        
        body.dark-mode .stages-line {
            background-color: var(--gray-700);
        }
        
        body.dark-mode .stage-icon {
            background-color: var(--gray-800);
            border-color: var(--gray-700);
        }
        
        body.dark-mode .stage-label {
            color: var(--gray-400);
        }
        
        body.dark-mode .interviewer-card {
            background-color: var(--gray-800);
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }
        
        body.dark-mode .interviewer-name {
            color: white;
        }
        
        body.dark-mode .btn-outline {
            border-color: var(--gray-600);
            color: var(--gray-300);
        }
        
        body.dark-mode .btn-outline:hover {
            border-color: var(--primary);
            color: var(--primary-light);
            background-color: rgba(124, 58, 237, 0.15);
        }
        
        body.dark-mode .secondary-actions {
            border-top-color: var(--gray-700);
        }
        
        body.dark-mode .note-input-container input {
            background-color: var(--gray-700);
            border-color: var(--gray-600);
            color: white;
        }
        
        body.dark-mode footer {
            background-color: var(--gray-800);
            color: var(--gray-300);
        }
        
        body.dark-mode .footer-heading {
            color: white;
        }
        
        body.theme-transition * {
            transition: background-color 0.5s ease, color 0.5s ease, border-color 0.5s ease, box-shadow 0.5s ease !important;
        }
        
        @media (max-width: 768px) {
            .dark-mode-toggle {
                width: 50px;
                height: 26px;
                margin-right: 10px;
            }
            
            .toggle-slider {
                width: 20px;
                height: 20px;
            }
            
            .dark-mode-toggle.active .toggle-slider {
                transform: translateX(24px);
            }
            
            .moon-icon, .sun-icon {
                font-size: 16px;
            }
        }
    `;
    
    document.head.appendChild(style);
});
