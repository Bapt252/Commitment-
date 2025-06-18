/**
 * CV Parser Integration - Script d'intégration pour le parsing de CV
 * Compatible avec la page candidate-upload.html
 * Gère l'intégration avec GPT Parser Client et le mode fallback
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('CV Parser Integration chargé');
    
    // Vérifier si GPTParserClient est disponible
    if (typeof window.GPTParserClient === 'undefined') {
        console.error('GPTParserClient non trouvé, chargement du script...');
        loadGPTParserClient();
        return;
    }
    
    initializeCVParser();
});

/**
 * Charge dynamiquement le script GPT Parser Client si nécessaire
 */
function loadGPTParserClient() {
    const script = document.createElement('script');
    script.src = '../static/js/gpt-parser-client.js';
    script.onload = function() {
        console.log('GPT Parser Client chargé dynamiquement');
        initializeCVParser();
    };
    script.onerror = function() {
        console.error('Erreur lors du chargement de GPT Parser Client');
        // Utiliser un parser de base en fallback
        initializeFallbackParser();
    };
    document.head.appendChild(script);
}

/**
 * Initialise le parser CV principal
 */
function initializeCVParser() {
    if (typeof window.CVParserIntegration === 'undefined') {
        console.error('CVParserIntegration non disponible');
        initializeFallbackParser();
        return;
    }
    
    // Configuration automatique selon l'environnement
    const isGitHubPages = window.location.hostname.includes('github.io');
    const apiKey = localStorage.getItem('openai_api_key');
    
    // Créer l'instance du parser
    const parserConfig = {
        apiKey: apiKey,
        useDirectOpenAI: isGitHubPages && apiKey,
        fallbackMode: isGitHubPages && !apiKey,
        onProgress: function(message) {
            console.log('Progress:', message);
            // Cette fonction sera utilisée par l'interface utilisateur
            if (typeof updateLoadingMessage === 'function') {
                updateLoadingMessage(message);
            }
        },
        onSuccess: function(message) {
            console.log('Success:', message);
        },
        onError: function(error) {
            console.error('Parser Error:', error);
        }
    };
    
    window.cvParserInstance = new window.CVParserIntegration(parserConfig);
    console.log('CV Parser configuré avec succès', parserConfig);
}

/**
 * Parser de fallback si GPT Parser Client n'est pas disponible
 */
function initializeFallbackParser() {
    console.log('Initialisation du parser de fallback');
    
    window.cvParserInstance = {
        parseCV: async function(file) {
            return new Promise((resolve, reject) => {
                try {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const content = e.target.result;
                        
                        // Analyse basique du contenu
                        const result = {
                            data: {
                                personal_info: {
                                    name: extractName(content) || 'À compléter',
                                    email: extractEmail(content) || 'À compléter',
                                    phone: extractPhone(content) || 'À compléter'
                                },
                                current_position: extractPosition(content) || 'À compléter',
                                skills: extractSkills(content),
                                software: ['À spécifier'],
                                languages: [
                                    { language: 'Français', level: 'Natif' },
                                    { language: 'Anglais', level: 'À évaluer' }
                                ],
                                work_experience: [
                                    {
                                        title: 'À compléter',
                                        company: 'À spécifier',
                                        start_date: 'À définir',
                                        end_date: 'À définir'
                                    }
                                ]
                            },
                            source: 'fallback',
                            timestamp: new Date().toISOString()
                        };
                        
                        resolve(result);
                    };
                    
                    reader.onerror = function() {
                        reject(new Error('Erreur lors de la lecture du fichier'));
                    };
                    
                    reader.readAsText(file);
                } catch (error) {
                    reject(error);
                }
            });
        }
    };
}

/**
 * Fonctions d'extraction pour le mode fallback
 */
function extractName(content) {
    const lines = content.split('\n').filter(line => line.trim().length > 0);
    return lines[0]?.trim() || null;
}

function extractEmail(content) {
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
    const match = content.match(emailRegex);
    return match ? match[0] : null;
}

function extractPhone(content) {
    const phoneRegex = /(\+33|0)[1-9](\d{8}|\s\d{2}\s\d{2}\s\d{2}\s\d{2})/;
    const match = content.match(phoneRegex);
    return match ? match[0] : null;
}

function extractPosition(content) {
    const positionKeywords = ['développeur', 'ingénieur', 'chef', 'manager', 'analyst', 'consultant'];
    const lines = content.toLowerCase().split('\n');
    
    for (const line of lines.slice(0, 10)) {
        if (positionKeywords.some(keyword => line.includes(keyword))) {
            return line.trim();
        }
    }
    
    return null;
}

function extractSkills(content) {
    const techKeywords = [
        'JavaScript', 'Python', 'Java', 'React', 'Angular', 'Vue',
        'Node.js', 'PHP', 'C#', 'C++', 'HTML', 'CSS', 'SQL'
    ];
    
    const foundSkills = [];
    const lowerContent = content.toLowerCase();
    
    for (const skill of techKeywords) {
        if (lowerContent.includes(skill.toLowerCase())) {
            foundSkills.push(skill);
        }
    }
    
    return foundSkills.length > 0 ? foundSkills : ['À spécifier'];
}

/**
 * Fonction utilitaire pour mettre à jour le message de chargement
 * (sera appelée depuis l'interface utilisateur)
 */
function updateLoadingMessage(message) {
    const loadingText = document.querySelector('.loading-text');
    if (loadingText) {
        loadingText.textContent = message;
    }
}

/**
 * Fonction d'exportation pour compatibilité
 */
window.CVParserIntegration = window.CVParserIntegration || {
    parseCV: async function(file) {
        if (window.cvParserInstance) {
            return await window.cvParserInstance.parseCV(file);
        } else {
            throw new Error('Parser CV non initialisé');
        }
    }
};

console.log('CV Parser Integration initialisé');
