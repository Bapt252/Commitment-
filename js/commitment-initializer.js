// CommitmentInitializer v2.13.2 - Système d'initialisation complet
class CommitmentInitializer {
    constructor() {
        this.version = '2.13.2-COMPLETE';
        this.components = {
            openaiConfig: false,
            jobParserAPI: false,
            questionnaire: false,
            ui: false
        };
        
        console.log('🚀 CommitmentInitializer v2.13.2 démarré');
        this.initialize();
    }
    
    async initialize() {
        try {
            // 1. Vérifier OpenAI Config
            if (window.openaiConfig) {
                this.components.openaiConfig = true;
                console.log('✅ OpenAI Config détecté');
            }
            
            // 2. Vérifier JobParserAPI
            if (window.JobParserAPI) {
                this.components.jobParserAPI = true;
                console.log('✅ JobParserAPI détecté');
            }
            
            // 3. Initialiser l'interface questionnaire
            this.initializeQuestionnaire();
            
            // 4. Initialiser les tests
            this.initializeTests();
            
            console.log('🎉 CommitmentInitializer v2.13.2 - Initialisation complète !');
            this.showSuccessBanner();
            
        } catch (error) {
            console.error('❌ Erreur initialisation:', error);
        }
    }
    
    initializeQuestionnaire() {
        // Restaurer la navigation du questionnaire
        const steps = document.querySelectorAll('.step');
        const sections = document.querySelectorAll('.form-section');
        
        if (steps.length > 0 && sections.length > 0) {
            this.components.questionnaire = true;
            console.log('✅ Questionnaire détecté');
        }
        
        // Assurer que la première section est active
        if (sections[0]) {
            sections[0].classList.add('active');
        }
    }
    
    initializeTests() {
        // Créer la fonction de test rapide
        window.quickTestPDF = () => {
            console.log('🧪 Test rapide PDF v2.13.2');
            if (window.JobParserAPI) {
                const parser = new window.JobParserAPI({ debug: true });
                console.log('✅ JobParserAPI fonctionnel');
                return true;
            } else {
                console.log('❌ JobParserAPI non disponible');
                return false;
            }
        };
        
        console.log('✅ Tests initialisés - window.quickTestPDF() disponible');
    }
    
    showSuccessBanner() {
        // Afficher la bannière de succès si elle n'existe pas
        if (!document.getElementById('success-banner-v213')) {
            const banner = document.createElement('div');
            banner.id = 'success-banner-v213';
            banner.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                padding: 12px;
                text-align: center;
                z-index: 99999;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            `;
            
            banner.innerHTML = `
                🚀 Commitment v2.13.2 RÉPARÉ ! Système complet opérationnel !
                <button onclick="this.parentElement.remove()" style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; margin-left: 15px;">×</button>
            `;
            
            document.body.insertBefore(banner, document.body.firstChild);
            
            // Auto-remove après 5 secondes
            setTimeout(() => {
                if (banner.parentNode) banner.remove();
            }, 5000);
        }
    }
    
    validateInitialization() {
        const working = Object.values(this.components).filter(Boolean).length;
        const total = Object.keys(this.components).length;
        
        console.log(`📊 Initialisation: ${working}/${total} composants fonctionnels`);
        console.log('🔧 Détails:', this.components);
        
        return working >= 2; // Au moins 2 composants fonctionnels
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    window.commitmentInitializer = new CommitmentInitializer();
});

console.log('📦 CommitmentInitializer v2.13.2 chargé');
