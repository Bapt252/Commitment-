// OpenAI/Claude Configuration v2.13.2 - Mode local avec fallback
class OpenAIConfig {
    constructor() {
        this.apiKey = null; // Mode local par défaut
        this.endpoint = null;
        this.model = 'gpt-3.5-turbo';
        this.localMode = true;
        this.version = '2.13.2-LOCAL';
        
        console.log('🔧 OpenAI Config v2.13.2 - Mode local activé');
        this.initializeLocalMode();
    }
    
    initializeLocalMode() {
        // Mode local - pas d'API externe nécessaire
        window.gptServiceAvailable = false;
        window.localParsingMode = true;
        
        console.log('✅ Mode local configuré - Parsing local activé');
    }
    
    isAvailable() {
        return this.localMode; // Toujours disponible en mode local
    }
    
    getConfig() {
        return {
            localMode: this.localMode,
            version: this.version,
            available: true
        };
    }
}

// Initialisation globale
window.openaiConfig = new OpenAIConfig();
console.log('🚀 OpenAI Config chargé et prêt');
