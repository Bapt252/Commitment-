// ========================================
// NEXTEN V2.0 - SYSTÈME DE CONTRATS HYBRIDE
// Système interactif de ranking des types de contrats
// ========================================

console.log('🔥 Chargement système de contrats NEXTEN V2.0...');

class ContractSystem {
    constructor() {
        this.selectedContracts = [];
        this.ranking = [];
        this.init();
    }

    init() {
        console.log('🚀 Initialisation ContractSystem...');
        this.setupEventListeners();
        this.updateDisplay();
        console.log('✅ ContractSystem initialisé');
    }

    setupEventListeners() {
        // Les boutons ont déjà leurs onclick dans le HTML, on les remplace par nos méthodes
        const addButtons = document.querySelectorAll('.add-contract-button');
        addButtons.forEach(button => {
            const card = button.closest('.contract-card');
            if (card) {
                const contractType = card.dataset.type;
                button.onclick = () => this.addToRanking(contractType);
            }
        });
    }

    addToRanking(contractType) {
        console.log(`➕ Ajout du contrat: ${contractType}`);
        
        // Vérifier si déjà ajouté
        if (this.ranking.includes(contractType)) {
            this.showNotification('Ce type de contrat est déjà dans votre classement', 'warning');
            return;
        }

        // Ajouter au ranking
        this.ranking.push(contractType);
        this.updateDisplay();
        this.updateHiddenFields();
        this.showNotification(`${this.getContractName(contractType)} ajouté à votre classement`, 'success');
    }

    removeFromRanking(contractType) {
        console.log(`➖ Suppression du contrat: ${contractType}`);
        
        const index = this.ranking.indexOf(contractType);
        if (index > -1) {
            this.ranking.splice(index, 1);
            this.updateDisplay();
            this.updateHiddenFields();
            this.showNotification(`${this.getContractName(contractType)} retiré de votre classement`, 'info');
        }
    }

    moveUp(contractType) {
        const index = this.ranking.indexOf(contractType);
        if (index > 0) {
            [this.ranking[index], this.ranking[index - 1]] = [this.ranking[index - 1], this.ranking[index]];
            this.updateDisplay();
            this.updateHiddenFields();
        }
    }

    moveDown(contractType) {
        const index = this.ranking.indexOf(contractType);
        if (index < this.ranking.length - 1) {
            [this.ranking[index], this.ranking[index + 1]] = [this.ranking[index + 1], this.ranking[index]];
            this.updateDisplay();
            this.updateHiddenFields();
        }
    }

    updateDisplay() {
        const rankingList = document.getElementById('ranking-list');
        if (!rankingList) return;

        if (this.ranking.length === 0) {
            rankingList.innerHTML = `
                <div class="ranking-empty">
                    <div class="ranking-empty-icon">
                        <i class="fas fa-hand-pointer"></i>
                    </div>
                    <h5 class="ranking-empty-title">Commencez votre sélection</h5>
                    <p class="ranking-empty-text">
                        Ajoutez les types de contrats qui vous intéressent pour créer votre classement personnalisé
                    </p>
                </div>
            `;
        } else {
            rankingList.innerHTML = this.ranking.map((contractType, index) => {
                return this.createRankingItem(contractType, index);
            }).join('');
        }

        // Mettre à jour les boutons d'ajout
        this.updateAddButtons();
        
        // Mettre à jour le résumé
        this.updateSummary();
    }

    createRankingItem(contractType, index) {
        const contractData = this.getContractData(contractType);
        const isFirst = index === 0;
        const isLast = index === this.ranking.length - 1;

        return `
            <div class="ranking-item" data-type="${contractType}">
                <div class="ranking-position">
                    <span class="ranking-number">${index + 1}</span>
                    <div class="ranking-badge ${index === 0 ? 'preferred' : ''}">${index === 0 ? 'PRÉFÉRÉ' : ''}</div>
                </div>
                
                <div class="ranking-content">
                    <div class="ranking-icon ${contractType}">
                        <i class="${contractData.icon}"></i>
                    </div>
                    <div class="ranking-info">
                        <h6 class="ranking-contract-name">${contractData.name}</h6>
                        <p class="ranking-contract-desc">${contractData.shortDesc}</p>
                    </div>
                </div>
                
                <div class="ranking-actions">
                    <button type="button" class="ranking-btn ranking-btn-up" 
                            onclick="contractSystem.moveUp('${contractType}')" 
                            ${isFirst ? 'disabled' : ''}>
                        <i class="fas fa-chevron-up"></i>
                    </button>
                    <button type="button" class="ranking-btn ranking-btn-down" 
                            onclick="contractSystem.moveDown('${contractType}')" 
                            ${isLast ? 'disabled' : ''}>
                        <i class="fas fa-chevron-down"></i>
                    </button>
                    <button type="button" class="ranking-btn ranking-btn-remove" 
                            onclick="contractSystem.removeFromRanking('${contractType}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
    }

    updateAddButtons() {
        const addButtons = document.querySelectorAll('.add-contract-button');
        addButtons.forEach(button => {
            const card = button.closest('.contract-card');
            if (card) {
                const contractType = card.dataset.type;
                const isAdded = this.ranking.includes(contractType);
                
                if (isAdded) {
                    button.innerHTML = '<i class="fas fa-check"></i> Ajouté';
                    button.disabled = true;
                    button.style.opacity = '0.6';
                } else {
                    button.innerHTML = '<i class="fas fa-plus"></i> Ajouter';
                    button.disabled = false;
                    button.style.opacity = '1';
                }
            }
        });
    }

    updateSummary() {
        const summaryContent = document.getElementById('summary-content');
        if (!summaryContent) return;

        if (this.ranking.length === 0) {
            summaryContent.innerHTML = `
                <p class="summary-empty">Aucun type de contrat sélectionné pour le moment.</p>
            `;
        } else {
            const primaryChoice = this.getContractName(this.ranking[0]);
            const totalChoices = this.ranking.length;
            
            summaryContent.innerHTML = `
                <div class="summary-stats">
                    <div class="summary-stat">
                        <span class="summary-stat-label">Choix prioritaire :</span>
                        <span class="summary-stat-value">${primaryChoice}</span>
                    </div>
                    <div class="summary-stat">
                        <span class="summary-stat-label">Types sélectionnés :</span>
                        <span class="summary-stat-value">${totalChoices}/4</span>
                    </div>
                </div>
                <div class="summary-list">
                    ${this.ranking.map((type, index) => 
                        `<span class="summary-item">${index + 1}. ${this.getContractName(type)}</span>`
                    ).join('')}
                </div>
            `;
        }
    }

    updateHiddenFields() {
        // Mettre à jour les champs cachés pour l'intégration
        const orderField = document.getElementById('contract-ranking-order');
        const selectedField = document.getElementById('contract-types-selected');
        const primaryField = document.getElementById('contract-primary-choice');
        const levelField = document.getElementById('contract-preference-level');

        if (orderField) orderField.value = this.ranking.join(',');
        if (selectedField) selectedField.value = this.ranking.join(',');
        if (primaryField) primaryField.value = this.ranking[0] || '';
        if (levelField) levelField.value = this.ranking.length;
    }

    getContractData(contractType) {
        const contracts = {
            'cdi': {
                name: 'CDI (Contrat à Durée Indéterminée)',
                shortDesc: 'Stabilité et sécurité d\'emploi',
                icon: 'fas fa-shield-alt'
            },
            'cdd': {
                name: 'CDD (Contrat à Durée Déterminée)',
                shortDesc: 'Missions courtes et flexibilité',
                icon: 'fas fa-calendar-alt'
            },
            'freelance': {
                name: 'Freelance / Consulting',
                shortDesc: 'Indépendance et autonomie',
                icon: 'fas fa-laptop-code'
            },
            'interim': {
                name: 'Intérim',
                shortDesc: 'Missions temporaires variées',
                icon: 'fas fa-users-cog'
            }
        };
        return contracts[contractType] || {};
    }

    getContractName(contractType) {
        return this.getContractData(contractType).name || contractType;
    }

    validateSelection() {
        if (this.ranking.length === 0) {
            this.showNotification('Veuillez sélectionner au moins un type de contrat', 'error');
            return false;
        }
        return true;
    }

    getContractData() {
        return {
            ranking: this.ranking,
            primaryChoice: this.ranking[0] || null,
            totalSelected: this.ranking.length,
            preferences: this.ranking.map((type, index) => ({
                type,
                position: index + 1,
                isPrimary: index === 0
            }))
        };
    }

    showNotification(message, type = 'info') {
        // Utiliser la fonction de notification existante si disponible
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
}

// Styles CSS pour les éléments de ranking
const rankingStyles = `
<style>
.ranking-item {
    background: white;
    border: 2px solid #E5E7EB;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.3s ease;
    position: relative;
}

.ranking-item:hover {
    border-color: #7C3AED;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ranking-position {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 60px;
}

.ranking-number {
    width: 32px;
    height: 32px;
    background: #7C3AED;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
}

.ranking-badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 8px;
    margin-top: 4px;
    background: #F3F4F6;
    color: #6B7280;
}

.ranking-badge.preferred {
    background: #10B981;
    color: white;
}

.ranking-content {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
}

.ranking-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.1rem;
}

.ranking-icon.cdi {
    background: linear-gradient(135deg, #2563EB, #3B82F6);
}

.ranking-icon.cdd {
    background: linear-gradient(135deg, #DC2626, #EF4444);
}

.ranking-icon.freelance {
    background: linear-gradient(135deg, #7C2D12, #EA580C);
}

.ranking-icon.interim {
    background: linear-gradient(135deg, #059669, #10B981);
}

.ranking-info {
    flex: 1;
}

.ranking-contract-name {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 4px 0;
    line-height: 1.2;
}

.ranking-contract-desc {
    font-size: 0.875rem;
    color: #6B7280;
    margin: 0;
    line-height: 1.3;
}

.ranking-actions {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.ranking-btn {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.8rem;
}

.ranking-btn-up,
.ranking-btn-down {
    background: #F3F4F6;
    color: #6B7280;
}

.ranking-btn-up:hover:not(:disabled),
.ranking-btn-down:hover:not(:disabled) {
    background: #7C3AED;
    color: white;
}

.ranking-btn-remove {
    background: #FEE2E2;
    color: #DC2626;
}

.ranking-btn-remove:hover {
    background: #DC2626;
    color: white;
}

.ranking-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.summary-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
}

.summary-stat {
    text-align: center;
    padding: 12px;
    background: #F9FAFB;
    border-radius: 8px;
}

.summary-stat-label {
    display: block;
    font-size: 0.8rem;
    color: #6B7280;
    margin-bottom: 4px;
}

.summary-stat-value {
    display: block;
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
}

.summary-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.summary-item {
    background: #EDE9FE;
    color: #7C3AED;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
}

.summary-empty {
    text-align: center;
    color: #6B7280;
    font-style: italic;
    margin: 20px 0;
}

@media (max-width: 768px) {
    .ranking-item {
        flex-direction: column;
        text-align: center;
        gap: 12px;
    }
    
    .ranking-content {
        justify-content: center;
    }
    
    .ranking-actions {
        flex-direction: row;
        justify-content: center;
    }
    
    .summary-stats {
        grid-template-columns: 1fr;
    }
}
</style>
`;

// Injecter les styles
if (!document.getElementById('ranking-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'ranking-styles';
    styleElement.innerHTML = rankingStyles;
    document.head.appendChild(styleElement);
}

// Initialisation automatique
function initContractSystem() {
    if (!window.contractSystem) {
        console.log('🚀 Création de l\'instance ContractSystem...');
        window.contractSystem = new ContractSystem();
        
        // Exposer la classe pour utilisation globale
        window.ContractSystem = ContractSystem;
        
        console.log('✅ Système de contrats NEXTEN V2.0 opérationnel !');
    }
}

// Démarrage automatique
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initContractSystem);
} else {
    initContractSystem();
}

// Export pour utilisation externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContractSystem;
}
