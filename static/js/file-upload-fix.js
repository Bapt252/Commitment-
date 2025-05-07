/**
 * Script de correction pour le sélecteur de fichiers
 * Ce script garantit le bon fonctionnement de l'upload de fichiers
 */
document.addEventListener('DOMContentLoaded', function() {
    // Récupération des éléments importants
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const analyseButton = document.getElementById('analyse-button');
    const textInput = document.getElementById('text-input');

    // S'assurer que les éléments existent
    if (!dropZone || !fileInput || !analyseButton) {
        console.error("Éléments de l'interface introuvables");
        return;
    }

    // 1. Corriger le problème de clic sur la zone de dépôt
    dropZone.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click(); // Ceci devrait déclencher la boîte de dialogue de fichiers
    });

    // 2. Ajouter un gestionnaire d'événements pour la sélection de fichier
    fileInput.addEventListener('change', function(e) {
        if (fileInput.files && fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            dropZone.querySelector('.drop-text').textContent = `Fichier sélectionné: ${fileName}`;
            dropZone.classList.add('file-selected');
        }
    });

    // 3. Assurer le bon fonctionnement du glisser-déposer
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('highlight');
    }

    function unhighlight() {
        dropZone.classList.remove('highlight');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files && files.length > 0) {
            fileInput.files = files; // Ceci connecte les fichiers déposés à l'input file
            const fileName = files[0].name;
            dropZone.querySelector('.drop-text').textContent = `Fichier sélectionné: ${fileName}`;
            dropZone.classList.add('file-selected');
        }
    }

    // 4. Gérer le bouton d'analyse
    analyseButton.addEventListener('click', function() {
        if (fileInput.files && fileInput.files.length > 0) {
            // Utiliser le fichier sélectionné
            const file = fileInput.files[0];
            processFile(file);
        } else if (textInput.value.trim() !== '') {
            // Utiliser le texte saisi
            processText(textInput.value);
        } else {
            alert("Veuillez sélectionner un fichier ou saisir du texte avant d'analyser.");
        }
    });

    // Fonction pour traiter un fichier
    function processFile(file) {
        console.log('Traitement du fichier:', file.name);
        
        // Création d'une notification de chargement
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-indicator';
        loadingDiv.innerHTML = '<div class="spinner"></div><p>Analyse en cours...</p>';
        document.body.appendChild(loadingDiv);
        
        // Simulation de l'envoi au service (à remplacer par l'appel réel à l'API)
        setTimeout(function() {
            // Supprimer la notification de chargement
            document.body.removeChild(loadingDiv);
            
            // Afficher une fausse réponse pour le test
            const resultSection = document.getElementById('result-section');
            resultSection.innerHTML = `
                <div class="results-container">
                    <h2>Informations extraites</h2>
                    <div class="result-item"><strong>Titre du poste:</strong> Développeur Full Stack</div>
                    <div class="result-item"><strong>Entreprise:</strong> Tech Solutions</div>
                    <div class="result-item"><strong>Localisation:</strong> Paris</div>
                    <div class="result-item"><strong>Type de contrat:</strong> CDI</div>
                    <div class="result-item">
                        <strong>Compétences requises:</strong>
                        <ul class="skill-list">
                            <li>JavaScript</li>
                            <li>React</li>
                            <li>Node.js</li>
                            <li>Python</li>
                        </ul>
                    </div>
                    <div class="result-item">
                        <strong>Responsabilités:</strong>
                        <ul class="responsibility-list">
                            <li>Développer des applications web</li>
                            <li>Collaborer avec l'équipe de design</li>
                            <li>Maintenir les services existants</li>
                        </ul>
                    </div>
                </div>
            `;
            resultSection.style.display = 'block';
        }, 2000);
    }

    // Fonction pour traiter du texte
    function processText(text) {
        console.log('Traitement du texte:', text.substring(0, 50) + '...');
        
        // Création d'une notification de chargement
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-indicator';
        loadingDiv.innerHTML = '<div class="spinner"></div><p>Analyse en cours...</p>';
        document.body.appendChild(loadingDiv);
        
        // Simulation de l'envoi au service (à remplacer par l'appel réel à l'API)
        setTimeout(function() {
            // Supprimer la notification de chargement
            document.body.removeChild(loadingDiv);
            
            // Afficher une fausse réponse pour le test
            const resultSection = document.getElementById('result-section');
            resultSection.innerHTML = `
                <div class="results-container">
                    <h2>Informations extraites</h2>
                    <div class="result-item"><strong>Titre du poste:</strong> Chef de Projet</div>
                    <div class="result-item"><strong>Entreprise:</strong> Innovate Inc.</div>
                    <div class="result-item"><strong>Localisation:</strong> Lyon</div>
                    <div class="result-item"><strong>Type de contrat:</strong> CDI</div>
                    <div class="result-item">
                        <strong>Compétences requises:</strong>
                        <ul class="skill-list">
                            <li>Gestion de projet</li>
                            <li>Agilité</li>
                            <li>Leadership</li>
                        </ul>
                    </div>
                    <div class="result-item">
                        <strong>Responsabilités:</strong>
                        <ul class="responsibility-list">
                            <li>Piloter des projets digitaux</li>
                            <li>Gérer une équipe de développeurs</li>
                            <li>Assurer la communication avec les clients</li>
                        </ul>
                    </div>
                </div>
            `;
            resultSection.style.display = 'block';
        }, 2000);
    }

    // Ajouter un style pour la mise en forme "fichier sélectionné"
    const style = document.createElement('style');
    style.textContent = `
        .drop-zone.file-selected {
            border-color: #7C3AED;
            background-color: rgba(124, 58, 237, 0.05);
        }
        .drop-zone.file-selected .drop-icon {
            color: #7C3AED;
        }
    `;
    document.head.appendChild(style);

    // Ajouter un message dans la console pour confirmer que le script est chargé
    console.log('Script file-upload-fix.js chargé et initialisé');
});
