/**
 * backend-config-helper.js
 * Ajoute une interface pour aider à configurer et tester la connexion au backend
 */

document.addEventListener('DOMContentLoaded', function() {
    // Créer et ajouter le CSS pour le panneau de configuration
    const style = document.createElement('style');
    style.textContent = `
        #backend-config-panel {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            width: 300px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        #backend-config-panel.collapsed {
            width: 50px;
            height: 50px;
            overflow: hidden;
        }
        
        .backend-config-header {
            background: linear-gradient(135deg, #7c3aed, #6d28d9);
            color: white;
            padding: 10px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        
        .backend-config-header h3 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
        }
        
        .backend-config-content {
            padding: 15px;
        }
        
        .backend-config-form {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .backend-config-form label {
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 3px;
        }
        
        .backend-config-form input {
            padding: 8px 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .backend-config-form button {
            background-color: #7c3aed;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .backend-config-form button:hover {
            background-color: #6d28d9;
        }
        
        .backend-status {
            display: flex;
            align-items: center;
            gap: 5px;
            margin-top: 10px;
            font-size: 13px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #ccc;
        }
        
        .status-indicator.connected {
            background-color: #10b981;
        }
        
        .status-indicator.disconnected {
            background-color: #ef4444;
        }
        
        .toggle-button {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
            padding: 0;
        }
        
        .config-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: #7c3aed;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            z-index: 999;
            border: none;
            font-size: 20px;
        }
    `;
    document.head.appendChild(style);
    
    // Créer le bouton d'accès rapide
    const configButton = document.createElement('button');
    configButton.id = 'backend-config-button';
    configButton.className = 'config-button';
    configButton.innerHTML = '<i class="fas fa-cog"></i>';
    configButton.title = 'Configurer le backend';
    document.body.appendChild(configButton);
    
    // Créer le panneau de configuration
    const panel = document.createElement('div');
    panel.id = 'backend-config-panel';
    panel.className = 'collapsed';
    panel.innerHTML = `
        <div class="backend-config-header">
            <h3>Configuration du Backend</h3>
            <button class="toggle-button"><i class="fas fa-times"></i></button>
        </div>
        <div class="backend-config-content">
            <div class="backend-config-form">
                <div>
                    <label for="backend-url">URL du Backend</label>
                    <input type="text" id="backend-url" placeholder="http://localhost:5055">
                </div>
                <div>
                    <label for="openai-key">Clé API OpenAI (optionnel)</label>
                    <input type="password" id="openai-key" placeholder="sk-...">
                </div>
                <button id="test-connection">Tester la connexion</button>
                <button id="apply-config">Appliquer la configuration</button>
                <div class="backend-status">
                    <div class="status-indicator" id="status-indicator"></div>
                    <span id="status-text">Non connecté</span>
                </div>
            </div>
        </div>
    `;
    
    // Ajouter le panneau à la page (initialement caché)
    document.body.appendChild(panel);
    
    // Gestion des événements
    const toggleButton = panel.querySelector('.toggle-button');
    const header = panel.querySelector('.backend-config-header');
    const testConnectionButton = document.getElementById('test-connection');
    const applyConfigButton = document.getElementById('apply-config');
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    // Ouvrir/fermer le panneau avec le bouton d'accès rapide
    configButton.addEventListener('click', function() {
        panel.classList.remove('collapsed');
        configButton.style.display = 'none';
    });
    
    // Fermer le panneau
    toggleButton.addEventListener('click', function() {
        panel.classList.add('collapsed');
        configButton.style.display = 'flex';
    });
    
    // Cacher le panneau au chargement
    panel.classList.add('collapsed');
    
    // Restaurer les valeurs depuis localStorage
    const urlInput = document.getElementById('backend-url');
    const apiKeyInput = document.getElementById('openai-key');
    
    // Charger les valeurs sauvegardées
    urlInput.value = localStorage.getItem('backendUrl') || 'http://localhost:5055';
    apiKeyInput.value = localStorage.getItem('openaiKey') || '';
    
    // Tester la connexion au backend
    testConnectionButton.addEventListener('click', async function() {
        const url = urlInput.value.trim();
        if (!url) {
            showNotification('Veuillez entrer une URL de backend valide', 'error');
            return;
        }
        
        // Mettre à jour l'UI
        statusIndicator.className = 'status-indicator';
        statusText.textContent = 'Test en cours...';
        testConnectionButton.disabled = true;
        
        try {
            // Tester la connexion
            const response = await fetch(`${url}/api/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(5000) // 5 secondes timeout
            });
            
            if (response.ok) {
                // Connexion réussie
                statusIndicator.className = 'status-indicator connected';
                statusText.textContent = 'Connecté';
                showNotification('Connexion au backend réussie !', 'success');
            } else {
                // Réponse reçue mais avec erreur
                statusIndicator.className = 'status-indicator disconnected';
                statusText.textContent = `Erreur: ${response.status}`;
                showNotification(`Le backend a répondu avec une erreur: ${response.status}`, 'error');
            }
        } catch (error) {
            // Erreur de connexion
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Non connecté';
            
            if (error.name === 'TimeoutError' || error.name === 'AbortError') {
                showNotification('La connexion au backend a expiré. Le serveur est-il démarré ?', 'error');
            } else {
                showNotification(`Erreur de connexion: ${error.message}`, 'error');
            }
        } finally {
            testConnectionButton.disabled = false;
        }
    });
    
    // Appliquer la configuration
    applyConfigButton.addEventListener('click', function() {
        const url = urlInput.value.trim();
        const apiKey = apiKeyInput.value.trim();
        
        if (!url) {
            showNotification('Veuillez entrer une URL de backend valide', 'error');
            return;
        }
        
        // Sauvegarder dans localStorage
        localStorage.setItem('backendUrl', url);
        if (apiKey) {
            localStorage.setItem('openaiKey', apiKey);
        }
        
        // Construire la nouvelle URL avec les paramètres
        let newUrl = `${window.location.pathname}?apiUrl=${encodeURIComponent(url)}`;
        
        // Ajouter d'autres paramètres d'URL existants (sauf apiUrl)
        const currentParams = new URLSearchParams(window.location.search);
        for (const [key, value] of currentParams.entries()) {
            if (key !== 'apiUrl') {
                newUrl += `&${key}=${encodeURIComponent(value)}`;
            }
        }
        
        // Demander confirmation avant de recharger la page
        if (confirm('La page va être rechargée pour appliquer la nouvelle configuration. Continuer ?')) {
            window.location.href = newUrl;
        }
    });
    
    // Tester automatiquement la connexion au démarrage
    setTimeout(async function() {
        try {
            const url = urlInput.value.trim();
            if (!url) return;
            
            const response = await fetch(`${url}/api/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(2000) // 2 secondes timeout
            });
            
            if (response.ok) {
                statusIndicator.className = 'status-indicator connected';
                statusText.textContent = 'Connecté';
            }
        } catch (error) {
            // Ignorer les erreurs
        }
    }, 1000);
});
