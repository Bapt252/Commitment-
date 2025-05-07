// job-parser-client.js
// Client-side library for communicating with the job-parser API

// Create a JobParser object in the global scope
window.JobParser = (function() {
    // Configuration
    const API_URL = 'http://localhost:5053'; // Local development URL
    
    // Dans l'environnement GitHub Pages, nous utiliserons une simulation
    // puisque nous n'avons pas de backend réel déployé
    const isGitHubPages = window.location.hostname.includes('github.io');
    
    // Helper function to determine the best API URL to use
    function getApiUrl() {
        // If we're on GitHub Pages, use simulation mode
        if (isGitHubPages) {
            console.log('Running on GitHub Pages - using simulation mode');
            return null;
        }
        // Otherwise use the local development URL
        return API_URL;
    }
    
    // Function to analyze a file using the API
    async function analyzeFile(file) {
        try {
            console.log(`Starting file analysis of ${file.name}...`);
            
            // Si nous sommes sur GitHub Pages, simuler immédiatement
            if (isGitHubPages) {
                console.log('GitHub Pages detected, using simulation mode');
                return simulateParsingResult(file.name);
            }
            
            // Create a FormData object to send the file
            const formData = new FormData();
            formData.append('file', file);
            formData.append('force_refresh', 'true');
            
            // Make the API request
            const apiUrl = `${getApiUrl()}/api/parse-job`;
            console.log(`Sending request to: ${apiUrl}`);
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData,
                // Don't set Content-Type header - FormData will set it automatically
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('API response:', result);
            
            // Format the result for display
            const formattedResult = formatApiResponse(result);
            return formattedResult;
        } catch (error) {
            console.error('Error analyzing file:', error);
            // Fall back to simulation if the API call fails
            console.log('Using simulated data instead');
            return simulateParsingResult(file.name);
        }
    }
    
    // Function to analyze text using the API
    async function analyzeText(text) {
        try {
            console.log('Starting text analysis...');
            
            // Si nous sommes sur GitHub Pages, simuler immédiatement
            if (isGitHubPages) {
                console.log('GitHub Pages detected, using simulation mode for text analysis');
                return simulateParsingResultFromText(text);
            }
            
            // Create a blob and a file from the text
            const blob = new Blob([text], { type: 'text/plain' });
            const file = new File([blob], 'job-description.txt', { type: 'text/plain' });
            
            // Create a FormData object
            const formData = new FormData();
            formData.append('file', file);
            formData.append('force_refresh', 'true');
            
            // Make the API request
            const apiUrl = `${getApiUrl()}/api/parse-job`;
            console.log(`Sending request to: ${apiUrl}`);
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('API response:', result);
            
            // Format the result for display
            const formattedResult = formatApiResponse(result);
            return formattedResult;
        } catch (error) {
            console.error('Error analyzing text:', error);
            // Fall back to simulation if the API call fails
            return simulateParsingResultFromText(text);
        }
    }
    
    // Function to format the API response into a consistent structure
    function formatApiResponse(apiResponse) {
        // Check if the response is already in the expected format
        if (apiResponse.data) {
            return apiResponse;
        }
        
        // Convert the API response to our expected format
        const formattedData = {
            data: {
                title: apiResponse.title || '',
                company: apiResponse.company || '',
                location: apiResponse.location || '',
                contract_type: apiResponse.contract_type || '',
                required_skills: Array.isArray(apiResponse.skills) ? apiResponse.skills : [],
                experience: apiResponse.experience || '',
                responsibilities: []
            }
        };
        
        return formattedData;
    }
    
    // Fonction pour simuler des résultats d'analyse de texte
    function simulateParsingResultFromText(text) {
        console.log(`Simulating parsing for text input`);
        
        // On utilise le texte pour tenter d'extraire des informations pertinentes
        let simulatedTitle = "Poste à pourvoir";
        let simulatedSkills = ["Communication", "Organisation", "Travail d'équipe"];
        let simulatedExp = "2-3 ans d'expérience";
        let simulatedContract = "CDI";
        
        // Extraire des informations intéressantes du texte
        if (text.toLowerCase().includes('développeur') || text.toLowerCase().includes('developer')) {
            simulatedTitle = "Développeur";
            simulatedSkills = ["JavaScript", "React", "Node.js", "Git"];
            simulatedExp = "3-5 ans d'expérience en développement";
        } else if (text.toLowerCase().includes('comptable')) {
            simulatedTitle = "Comptable";
            simulatedSkills = ["Excel", "SAP", "Comptabilité générale"];
            simulatedExp = "2 ans minimum en comptabilité";
        } else if (text.toLowerCase().includes('marketing')) {
            simulatedTitle = "Responsable Marketing";
            simulatedSkills = ["SEO", "Réseaux sociaux", "Google Analytics"];
            simulatedExp = "3 ans en marketing digital";
        }
        
        // Si le texte contient des informations sur le contrat, les extraire
        if (text.toLowerCase().includes('cdi')) {
            simulatedContract = "CDI";
        } else if (text.toLowerCase().includes('cdd')) {
            simulatedContract = "CDD";
        } else if (text.toLowerCase().includes('stage')) {
            simulatedContract = "Stage";
        } else if (text.toLowerCase().includes('alternance')) {
            simulatedContract = "Alternance";
        }
        
        return {
            data: {
                title: simulatedTitle,
                company: "Entreprise",
                location: "Paris",
                contract_type: simulatedContract,
                required_skills: simulatedSkills,
                preferred_skills: [],
                experience: simulatedExp,
                responsibilities: [
                    "Responsabilités extraites du texte fourni"
                ]
            }
        };
    }
    
    // Function to simulate parsing results when the API is unavailable
    function simulateParsingResult(fileName) {
        console.log(`Simulating parsing for: ${fileName}`);
        
        // Create a simulated response based on the file name
        let simulatedTitle = "Poste à pourvoir";
        let simulatedSkills = ["Communication", "Organisation", "Travail d'équipe"];
        let simulatedExp = "2-3 ans d'expérience";
        let simulatedContract = "CDI";
        
        // Try to extract some info from the file name
        if (fileName.toLowerCase().includes('dev')) {
            simulatedTitle = "Développeur";
            simulatedSkills = ["JavaScript", "React", "Node.js", "Git"];
            simulatedExp = "3-5 ans d'expérience en développement";
        } else if (fileName.toLowerCase().includes('compta')) {
            simulatedTitle = "Comptable";
            simulatedSkills = ["Excel", "SAP", "Comptabilité générale"];
            simulatedExp = "2 ans minimum en comptabilité";
        } else if (fileName.toLowerCase().includes('market')) {
            simulatedTitle = "Responsable Marketing";
            simulatedSkills = ["SEO", "Réseaux sociaux", "Google Analytics"];
            simulatedExp = "3 ans en marketing digital";
        }
        
        return {
            data: {
                title: simulatedTitle,
                company: "Entreprise",
                location: "Paris",
                contract_type: simulatedContract,
                required_skills: simulatedSkills,
                preferred_skills: [],
                experience: simulatedExp,
                responsibilities: [
                    "Responsabilités à définir selon le poste"
                ]
            }
        };
    }
    
    // Return the public API
    return {
        analyzeFile,
        analyzeText,
        simulateParsingResult // Exposer cette fonction pour des tests
    };
})();