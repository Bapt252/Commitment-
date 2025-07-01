/**
 * NEXTEN V3.0 - SYSTÈME SECTEURS AMÉLIORÉ
 * Script JavaScript complet pour l'intégration du multi-select secteurs
 */

// ===== DONNÉES DES SECTEURS (25+ SECTEURS) =====
const NEXTEN_SECTORS_DATA = [
    { id: 'tech', name: 'Technologie & IT', icon: 'fas fa-laptop-code', description: 'Informatique, digital, IA, cybersécurité' },
    { id: 'finance', name: 'Finance & Banque', icon: 'fas fa-university', description: 'Services financiers, assurance, investissement' },
    { id: 'sante', name: 'Santé & Médical', icon: 'fas fa-heartbeat', description: 'Soins, pharmaceutique, biotechnologies' },
    { id: 'education', name: 'Éducation & Formation', icon: 'fas fa-graduation-cap', description: 'Enseignement, e-learning, formation' },
    { id: 'industrie', name: 'Industrie & Manufacturing', icon: 'fas fa-cogs', description: 'Production, logistique, ingénierie' },
    { id: 'commerce', name: 'Commerce & Retail', icon: 'fas fa-shopping-cart', description: 'Vente, marketing, e-commerce' },
    { id: 'automobile', name: 'Automobile', icon: 'fas fa-car', description: 'Construction automobile, mobilité' },
    { id: 'energie', name: 'Énergie & Environnement', icon: 'fas fa-bolt', description: 'Énergies renouvelables, développement durable' },
    { id: 'medias', name: 'Médias & Communication', icon: 'fas fa-broadcast-tower', description: 'Presse, télévision, digital media' },
    { id: 'telecoms', name: 'Télécommunications', icon: 'fas fa-satellite-dish', description: 'Opérateurs, équipements télécom' },
    { id: 'immobilier', name: 'Immobilier & Construction', icon: 'fas fa-building', description: 'Promotion, gestion immobilière' },
    { id: 'tourisme', name: 'Tourisme & Hôtellerie', icon: 'fas fa-plane', description: 'Voyage, restauration, loisirs' },
    { id: 'agriculture', name: 'Agriculture & Agroalimentaire', icon: 'fas fa-leaf', description: 'Production agricole, alimentation' },
    { id: 'btp', name: 'BTP & Travaux Publics', icon: 'fas fa-hard-hat', description: 'Construction, infrastructure' },
    { id: 'logistique', name: 'Logistique & Transport', icon: 'fas fa-truck', description: 'Supply chain, distribution' },
    { id: 'consulting', name: 'Conseil & Services', icon: 'fas fa-handshake', description: 'Conseil en management, audit' },
    { id: 'luxe', name: 'Luxe & Mode', icon: 'fas fa-gem', description: 'Maroquinerie, joaillerie, cosmétique' },
    { id: 'sport', name: 'Sport & Fitness', icon: 'fas fa-running', description: 'Équipementier sportif, coaching' },
    { id: 'culture', name: 'Culture & Divertissement', icon: 'fas fa-theater-masks', description: 'Spectacle, gaming, arts' },
    { id: 'juridique', name: 'Juridique & Droit', icon: 'fas fa-balance-scale', description: 'Cabinets d\'avocats, juridique' },
    { id: 'rh', name: 'Ressources Humaines', icon: 'fas fa-users', description: 'Recrutement, formation, SIRH' },
    { id: 'recherche', name: 'Recherche & Développement', icon: 'fas fa-flask', description: 'Innovation, laboratoires, R&D' },
    { id: 'securite', name: 'Sécurité & Défense', icon: 'fas fa-shield-alt', description: 'Sécurité privée, défense' },
    { id: 'ong', name: 'ONG & Associations', icon: 'fas fa-heart', description: 'Organisations humanitaires, bénévolat' },
    { id: 'public', name: 'Secteur Public', icon: 'fas fa-landmark', description: 'Administration, collectivités' },
    { id: 'startup', name: 'Startups & Innovation', icon: 'fas fa-rocket', description: 'Écosystème startup, innovation' }
];

// ===== GESTIONNAIRE PRINCIPAL =====
class NEXTENSectorsIntegration {
    constructor() {
        this.selectedSectors = new Set();
        this.selectedDealbreakers = new Set();
        this.isDropdownOpen = false;
        this.isInitialized = false;
    }

    // Méthode d'intégration principale
    integrate() {
        if (this.isInitialized) {
            console.warn('NEXTEN Sectors déjà initialisé');
            return;
        }

        console.log('🚀 Intégration NEXTEN Sectors V3.0...');
        
        this.setupMultiSelect();
        this.setupDealbreakers();
        this.setupEventListeners();
        this.connectToForm();
        
        this.isInitialized = true;
        console.log('✅ NEXTEN Sectors V3.0 intégré avec succès');
    }

    setupMultiSelect() {
        const optionsList = document.getElementById('nexten-sectorsOptionsList');
        if (!optionsList) return;

        optionsList.innerHTML = '';

        NEXTEN_SECTORS_DATA.forEach(sector => {
            const option = document.createElement('div');
            option.className = 'nexten-multiselect-option';
            option.dataset.value = sector.id;
            option.innerHTML = `
                <div class="nexten-option-icon">
                    <i class="${sector.icon}"></i>
                </div>
                <div class="nexten-option-text">
                    <strong>${sector.name}</strong>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">${sector.description}</div>
                </div>
                <div class="nexten-option-check">
                    <i class="fas fa-check"></i>
                </div>
            `;
            
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleSector(sector.id);
            });
            
            optionsList.appendChild(option);
        });
    }

    setupDealbreakers() {
        const grid = document.getElementById('nexten-dealbreakersGrid');
        if (!grid) return;

        grid.innerHTML = '';

        NEXTEN_SECTORS_DATA.forEach(sector => {
            const option = document.createElement('div');
            option.className = 'nexten-dealbreaker-option';
            option.dataset.value = sector.id;
            option.innerHTML = `
                <div class="nexten-dealbreaker-checkbox">
                    <i class="fas fa-times" style="font-size: 10px; opacity: 0;"></i>
                </div>
                <div class="nexten-dealbreaker-text">${sector.name}</div>
            `;
            
            option.addEventListener('click', () => {
                this.toggleDealbreaker(sector.id);
            });
            
            grid.appendChild(option);
        });
    }

    setupEventListeners() {
        // Dropdown toggle
        const dropdown = document.getElementById('nexten-sectorsDropdown');
        if (!dropdown) return;

        const header = dropdown.querySelector('.nexten-multiselect-header');
        header.addEventListener('click', (e) => {
            if (!e.target.closest('.remove-tag')) {
                this.toggleDropdown();
            }
        });

        // Search functionality
        const searchInput = document.getElementById('nexten-sectorsSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterOptions(e.target.value);
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Prevent dropdown close when clicking inside options
        const options = dropdown.querySelector('.nexten-multiselect-options');
        if (options) {
            options.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
    }

    toggleDropdown() {
        const dropdown = document.getElementById('nexten-sectorsDropdown');
        this.isDropdownOpen = !this.isDropdownOpen;
        
        if (this.isDropdownOpen) {
            dropdown.classList.add('active');
            const searchInput = document.getElementById('nexten-sectorsSearch');
            if (searchInput) searchInput.focus();
        } else {
            dropdown.classList.remove('active');
        }
    }

    closeDropdown() {
        const dropdown = document.getElementById('nexten-sectorsDropdown');
        if (dropdown) {
            dropdown.classList.remove('active');
            this.isDropdownOpen = false;
        }
    }

    toggleSector(sectorId) {
        if (this.selectedSectors.has(sectorId)) {
            this.selectedSectors.delete(sectorId);
        } else {
            this.selectedSectors.add(sectorId);
        }
        
        this.updateSelectedDisplay();
        this.updateOptionStates();
        this.updateHiddenFields();
        this.notifyFormChange();
    }

    toggleDealbreaker(sectorId) {
        const option = document.querySelector(`.nexten-dealbreaker-option[data-value="${sectorId}"]`);
        const checkbox = option.querySelector('.nexten-dealbreaker-checkbox i');
        
        if (this.selectedDealbreakers.has(sectorId)) {
            this.selectedDealbreakers.delete(sectorId);
            option.classList.remove('selected');
            checkbox.style.opacity = '0';
        } else {
            this.selectedDealbreakers.add(sectorId);
            option.classList.add('selected');
            checkbox.style.opacity = '1';
        }
        
        this.updateHiddenFields();
        this.notifyFormChange();
    }

    updateSelectedDisplay() {
        const selectedContainer = document.getElementById('nexten-sectorsSelected');
        const placeholder = document.getElementById('nexten-sectorsPlaceholder');
        
        if (!selectedContainer || !placeholder) return;

        selectedContainer.innerHTML = '';
        
        if (this.selectedSectors.size === 0) {
            placeholder.style.display = 'block';
        } else {
            placeholder.style.display = 'none';
            
            Array.from(this.selectedSectors).forEach(sectorId => {
                const sector = NEXTEN_SECTORS_DATA.find(s => s.id === sectorId);
                if (sector) {
                    const tag = document.createElement('div');
                    tag.className = 'nexten-selected-tag';
                    tag.innerHTML = `
                        <i class="${sector.icon}"></i>
                        ${sector.name}
                        <i class="fas fa-times remove-tag" onclick="nextenSectors.removeSector('${sectorId}')"></i>
                    `;
                    selectedContainer.appendChild(tag);
                }
            });
        }
    }

    updateOptionStates() {
        document.querySelectorAll('.nexten-multiselect-option').forEach(option => {
            const sectorId = option.dataset.value;
            if (this.selectedSectors.has(sectorId)) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
    }

    removeSector(sectorId) {
        this.selectedSectors.delete(sectorId);
        this.updateSelectedDisplay();
        this.updateOptionStates();
        this.updateHiddenFields();
        this.notifyFormChange();
    }

    filterOptions(searchTerm) {
        const options = document.querySelectorAll('.nexten-multiselect-option');
        const normalizedSearch = searchTerm.toLowerCase().trim();
        
        options.forEach(option => {
            const text = option.textContent.toLowerCase();
            if (text.includes(normalizedSearch)) {
                option.style.display = 'flex';
            } else {
                option.style.display = 'none';
            }
        });
    }

    updateHiddenFields() {
        const sectorsField = document.getElementById('nexten-selected-sectors');
        const dealbreakersField = document.getElementById('nexten-dealbreaker-sectors');
        
        if (sectorsField) {
            sectorsField.value = Array.from(this.selectedSectors).join(',');
        }
        
        if (dealbreakersField) {
            dealbreakersField.value = Array.from(this.selectedDealbreakers).join(',');
        }

        // Mettre à jour aussi le champ secteurs original pour compatibilité
        const originalSectorsField = document.getElementById('hidden-secteurs');
        if (originalSectorsField) {
            originalSectorsField.value = Array.from(this.selectedSectors).join(',');
        }
    }

    connectToForm() {
        // Connecter aux événements du formulaire existant
        const form = document.getElementById('questionnaire-form');
        if (form) {
            // Ajouter la validation lors de la soumission
            form.addEventListener('submit', () => {
                this.updateHiddenFields();
            });
        }

        // Connecter aux scripts de navigation existants
        this.overrideFormNavigation();
    }

    overrideFormNavigation() {
        // Override du bouton "Suivant" de l'étape 3
        const nextStep3Btn = document.getElementById('next-step3');
        if (nextStep3Btn) {
            const originalHandler = nextStep3Btn.onclick;
            nextStep3Btn.onclick = () => {
                this.updateHiddenFields();
                if (originalHandler) originalHandler();
            };
        }
    }

    notifyFormChange() {
        // Déclencher un événement personnalisé pour notifier les changements
        const event = new CustomEvent('nextenSectorsChange', {
            detail: {
                selectedSectors: Array.from(this.selectedSectors),
                dealbreakers: Array.from(this.selectedDealbreakers)
            }
        });
        document.dispatchEvent(event);
    }

    // API publique pour intégration
    getSelectedSectors() {
        return Array.from(this.selectedSectors);
    }

    getSelectedDealbreakers() {
        return Array.from(this.selectedDealbreakers);
    }

    getFormData() {
        return {
            selectedSectors: this.getSelectedSectors(),
            dealbreakers: this.getSelectedDealbreakers(),
            conflicts: this.getSelectedSectors().filter(id => 
                this.selectedDealbreakers.has(id)
            ),
            timestamp: new Date().toISOString()
        };
    }

    setSelections(sectors = [], dealbreakers = []) {
        this.selectedSectors = new Set(sectors);
        this.selectedDealbreakers = new Set(dealbreakers);
        
        this.updateSelectedDisplay();
        this.updateOptionStates();
        
        // Mettre à jour les dealbreakers visuellement
        document.querySelectorAll('.nexten-dealbreaker-option').forEach(option => {
            const sectorId = option.dataset.value;
            const checkbox = option.querySelector('.nexten-dealbreaker-checkbox i');
            
            if (this.selectedDealbreakers.has(sectorId)) {
                option.classList.add('selected');
                checkbox.style.opacity = '1';
            } else {
                option.classList.remove('selected');
                checkbox.style.opacity = '0';
            }
        });
        
        this.updateHiddenFields();
    }

    validate() {
        const data = this.getFormData();
        const hasConflicts = data.conflicts.length > 0;
        
        return {
            isValid: !hasConflicts,
            hasInterests: data.selectedSectors.length > 0,
            hasDealbreakers: data.dealbreakers.length > 0,
            conflicts: data.conflicts,
            data: data
        };
    }

    reset() {
        this.selectedSectors.clear();
        this.selectedDealbreakers.clear();
        this.setSelections([], []);
        this.closeDropdown();
        
        const searchInput = document.getElementById('nexten-sectorsSearch');
        if (searchInput) {
            searchInput.value = '';
            this.filterOptions('');
        }
        
        console.log('🔄 Reset secteurs NEXTEN effectué');
    }
}

// ===== INITIALISATION AUTOMATIQUE =====
function initNEXTENSectors() {
    // Vérifier que nous sommes sur la bonne page
    if (!document.getElementById('form-step3')) {
        console.log('Page questionnaire non détectée, skip intégration secteurs');
        return;
    }

    // Attendre que le DOM soit complètement chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNEXTENSectors);
        return;
    }

    // Attendre un délai pour s'assurer que les autres scripts sont chargés
    setTimeout(() => {
        try {
            window.nextenSectors = new NEXTENSectorsIntegration();
            window.nextenSectors.integrate();
            
            // Exposer globalement pour debugging
            window.NEXTENSectorsIntegration = NEXTENSectorsIntegration;
            window.NEXTEN_SECTORS_DATA = NEXTEN_SECTORS_DATA;
            
            console.log('✅ NEXTEN Sectors V3.0 prêt');
            console.log('🛠️ Commandes debug disponibles:');
            console.log('   - nextenSectors.getFormData() - Voir les données');
            console.log('   - nextenSectors.validate() - Valider la sélection');
            console.log('   - nextenSectors.reset() - Reset complet');
            console.log('   - nextenSectors.setSelections([\'tech\', \'finance\'], [\'agriculture\']) - Test');
            
        } catch (error) {
            console.error('❌ Erreur initialisation NEXTEN Sectors:', error);
        }
    }, 1500);
}

// Démarrer l'initialisation
initNEXTENSectors();

// ===== FONCTIONS GLOBALES POUR COMPATIBILITÉ =====
function nextenSectorsRemove(sectorId) {
    if (window.nextenSectors) {
        window.nextenSectors.removeSector(sectorId);
    }
}

// Exposer pour les onclick dans le HTML
window.nextenSectorsRemove = nextenSectorsRemove;