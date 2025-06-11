#!/usr/bin/env node

/**
 * 📄 Parser de documents réels - Extraction intelligente
 * Pour vos vrais PDF: fdp.pdf et DA SILVA christine manuelle_CV.pdf
 */

const fs = require('fs');

// Fonction de parsing intelligent pour CV
function parseCV(text) {
    console.log('🔍 Analyse du CV...');
    
    const cv = {
        personal_info: {},
        skills: [],
        experience: [],
        languages: [],
        education: []
    };

    // Extraction nom (patterns français)
    const namePatterns = [
        /^([A-Z\s\-']+)\s*$/m,
        /^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/m,
        /(DA\s+SILVA\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/i
    ];
    
    for (const pattern of namePatterns) {
        const match = text.match(pattern);
        if (match) {
            cv.personal_info.name = match[1].trim();
            break;
        }
    }

    // Extraction email
    const emailMatch = text.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
    if (emailMatch) {
        cv.personal_info.email = emailMatch[1];
    }

    // Extraction téléphone (formats français)
    const phonePatterns = [
        /(\+33\s?[1-9](?:\s?\d{2}){4})/,
        /(0[1-9](?:\s?\d{2}){4})/,
        /(\d{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2})/
    ];
    
    for (const pattern of phonePatterns) {
        const match = text.match(pattern);
        if (match) {
            cv.personal_info.phone = match[1].trim();
            break;
        }
    }

    // Extraction adresse
    const addressPatterns = [
        /(\d+[\s,]+[^,\n]+,\s*\d{5}\s+[A-Z][a-z\s]+)/,
        /([A-Z][a-z\s]+,\s*\d{5}\s+[A-Z][a-z\s]+)/,
        /(Paris|Lyon|Marseille|Toulouse|Nice|Nantes|Strasbourg|Montpellier|Bordeaux|Lille)/i
    ];
    
    for (const pattern of addressPatterns) {
        const match = text.match(pattern);
        if (match) {
            cv.personal_info.address = match[1].trim();
            break;
        }
    }

    // Extraction compétences techniques
    const skillPatterns = [
        /(?:compétences|skills|technologies|outils)[\s\S]*?(?:JavaScript|Python|Java|PHP|C\+\+|HTML|CSS|SQL|React|Vue|Angular|Node\.js|Laravel|Symfony|Django|Flask|MongoDB|PostgreSQL|MySQL|Git|Docker|Kubernetes|AWS|Azure|Linux|Windows|Excel|Word|PowerPoint)/gi,
        /(JavaScript|TypeScript|Python|Java|PHP|C\#|C\+\+|Ruby|HTML|CSS|SCSS|SASS|SQL|NoSQL|React|Vue\.js|Angular|Node\.js|Express|Laravel|Symfony|Django|Flask|MongoDB|PostgreSQL|MySQL|Redis|Git|GitHub|GitLab|Docker|Kubernetes|AWS|Azure|GCP|Linux|Ubuntu|Windows|Mac|Excel|Word|PowerPoint|Photoshop|Illustrator|InDesign|AutoCAD|SolidWorks)/gi
    ];
    
    skillPatterns.forEach(pattern => {
        const matches = text.match(pattern) || [];
        cv.skills.push(...matches.map(s => s.toLowerCase()));
    });
    
    // Déduplication
    cv.skills = [...new Set(cv.skills)];

    // Extraction langues
    const languagePatterns = [
        /(Français|Anglais|Espagnol|Allemand|Italien|Portugais|Chinois|Japonais|Arabe)[\s\-]*(?:\([^)]*\))?[\s\-]*(natif|native|courant|fluent|bilingue|bilingual|intermédiaire|intermediate|débutant|beginner|lu|écrit|parlé|spoken|written|read)?/gi,
        /(French|English|Spanish|German|Italian|Portuguese|Chinese|Japanese|Arabic)[\s\-]*(?:\([^)]*\))?[\s\-]*(native|fluent|bilingual|intermediate|beginner|spoken|written|read)?/gi
    ];
    
    languagePatterns.forEach(pattern => {
        const matches = text.match(pattern) || [];
        matches.forEach(match => {
            cv.languages.push(match.trim().toLowerCase());
        });
    });
    
    cv.languages = [...new Set(cv.languages)];

    // Extraction expérience (années)
    const expPatterns = [
        /(\d+)\s*(?:ans?|années?)\s*(?:d'|de\s)?(?:expérience|exp)/i,
        /expérience[\s:]*(\d+)\s*(?:ans?|années?)/i,
        /(\d+)\+?\s*(?:years?)\s*(?:of\s)?experience/i
    ];
    
    for (const pattern of expPatterns) {
        const match = text.match(pattern);
        if (match) {
            cv.experience_years = parseInt(match[1]);
            break;
        }
    }

    // Calcul expérience depuis les dates
    if (!cv.experience_years) {
        const yearMatches = text.match(/20\d{2}/g) || [];
        if (yearMatches.length >= 2) {
            const years = yearMatches.map(y => parseInt(y)).sort();
            const minYear = Math.min(...years);
            const maxYear = Math.max(...years);
            cv.experience_years = Math.max(0, maxYear - minYear);
        }
    }

    // Extraction formation/éducation
    const educationPatterns = [
        /(Master|Licence|Bachelor|BTS|DUT|Diplôme|Formation)[\s\S]*?(?:en\s+)?([A-Z][a-z\s]+)/gi,
        /(École|Université|Institut|IUT)[\s\S]*?([A-Z][a-z\s]+)/gi
    ];
    
    educationPatterns.forEach(pattern => {
        const matches = text.match(pattern) || [];
        cv.education.push(...matches.slice(0, 3)); // Limiter à 3 formations
    });

    return cv;
}

// Fonction de parsing intelligent pour Job
function parseJob(text) {
    console.log('🔍 Analyse de la fiche de poste...');
    
    const job = {
        job_info: {},
        requirements: {},
        benefits: {},
        company: {},
        salary: {}
    };

    // Extraction titre du poste
    const titlePatterns = [
        /^([A-Z][A-Z\s\-\/]+)(?:\s*\-\s*(?:CDI|CDD|Stage|Freelance))?$/m,
        /(?:Poste|Offre|Job|Position)[\s:]*([A-Z][A-Za-z\s\-\/]+)/i,
        /(Développeur|Developer|Ingénieur|Engineer|Manager|Chef|Lead|Architecte|Consultant|Analyst|Designer|Commercial|Chargé|Responsable)[\s\-]?([A-Za-z\s\-\/]+)/i
    ];
    
    for (const pattern of titlePatterns) {
        const match = text.match(pattern);
        if (match) {
            job.job_info.title = match[1].trim();
            break;
        }
    }

    // Extraction type de contrat
    const contractPatterns = [
        /(CDI|CDD|Stage|Freelance|Interim|Consultant)/i,
        /(?:Contrat|Contract|Type)[\s:]*([A-Z]+)/i
    ];
    
    for (const pattern of contractPatterns) {
        const match = text.match(pattern);
        if (match) {
            job.job_info.contract_type = match[1].toUpperCase();
            break;
        }
    }

    // Extraction localisation
    const locationPatterns = [
        /(?:Localisation|Location|Lieu|Ville|City)[\s:]*([A-Z][a-z\s,]+)/i,
        /(Paris|Lyon|Marseille|Toulouse|Nice|Nantes|Strasbourg|Montpellier|Bordeaux|Lille)(?:\s*,?\s*France)?/i,
        /(\d{5}\s+[A-Z][a-z\s]+)/
    ];
    
    for (const pattern of locationPatterns) {
        const match = text.match(pattern);
        if (match) {
            job.job_info.location = match[1].trim();
            break;
        }
    }

    // Extraction salaire
    const salaryPatterns = [
        /(\d+)[\s\-]*k?[€$][\s\-]*(?:par\s+an|annuel|yearly)?/i,
        /(?:Salaire|Salary|Rémunération)[\s:]*(\d+)[\s\-]*k?[€$]/i,
        /entre\s*(\d+)\s*et\s*(\d+)\s*k?[€$]/i,
        /(\d+)\s*000\s*[€$]/i
    ];
    
    for (const pattern of salaryPatterns) {
        const match = text.match(pattern);
        if (match) {
            job.salary.amount = parseInt(match[1]);
            job.salary.currency = text.includes('€') ? 'EUR' : 'USD';
            if (match[2]) {
                job.salary.max_amount = parseInt(match[2]);
            }
            break;
        }
    }

    // Extraction compétences requises
    const skillPatterns = [
        /(?:Compétences|Skills|Technologies|Outils|Requirements)[\s\S]*?(?:JavaScript|Python|Java|PHP|C\+\+|HTML|CSS|SQL|React|Vue|Angular|Node\.js)/gi,
        /(JavaScript|TypeScript|Python|Java|PHP|C\#|C\+\+|Ruby|HTML|CSS|SQL|React|Vue\.js|Angular|Node\.js|Express|Laravel|Symfony|Django|Flask|MongoDB|PostgreSQL|MySQL|Git|Docker|AWS|Azure|Linux)/gi
    ];
    
    job.requirements.technical_skills = [];
    skillPatterns.forEach(pattern => {
        const matches = text.match(pattern) || [];
        job.requirements.technical_skills.push(...matches.map(s => s.toLowerCase()));
    });
    
    job.requirements.technical_skills = [...new Set(job.requirements.technical_skills)];

    // Extraction expérience requise
    const expPatterns = [
        /(\d+)\s*(?:ans?|années?)\s*(?:d'|de\s)?(?:expérience|exp)/i,
        /(?:minimum|mini)\s*(\d+)\s*(?:ans?|années?)/i,
        /(\d+)\+?\s*(?:years?)\s*(?:of\s)?experience/i
    ];
    
    for (const pattern of expPatterns) {
        const match = text.match(pattern);
        if (match) {
            job.requirements.experience_years = parseInt(match[1]);
            break;
        }
    }

    // Extraction télétravail
    if (text.match(/télétravail|remote|hybride|home[\s\-]?office/i)) {
        job.benefits.remote_work = true;
        if (text.match(/hybride|hybrid/i)) {
            job.benefits.remote_type = 'hybrid';
        } else if (text.match(/100%|complet|full/i)) {
            job.benefits.remote_type = 'full_remote';
        }
    }

    // Extraction entreprise
    const companyPatterns = [
        /(?:Entreprise|Company|Société)[\s:]*([A-Z][A-Za-z\s&\.]+)/i,
        /^([A-Z][A-Za-z\s&\.]{2,30})$/m
    ];
    
    for (const pattern of companyPatterns) {
        const match = text.match(pattern);
        if (match && match[1].length < 50) {
            job.company.name = match[1].trim();
            break;
        }
    }

    return job;
}

// Fonction principale
async function parseRealDocuments() {
    console.log('🚀 Parser de Documents Réels - PROMPT 2');
    console.log('=========================================');

    try {
        // Lire les fichiers texte extraits
        let cvText = '';
        let jobText = '';

        // Chercher les fichiers texte extraits
        const possibleCVFiles = ['cv_extracted.txt', 'cv_christine.txt', 'cv_ocr.txt.txt'];
        const possibleJobFiles = ['fdp_extracted.txt', 'fdp.txt', 'fdp_ocr.txt.txt'];

        for (const file of possibleCVFiles) {
            if (fs.existsSync(file)) {
                cvText = fs.readFileSync(file, 'utf8');
                console.log(`✅ CV lu depuis: ${file}`);
                break;
            }
        }

        for (const file of possibleJobFiles) {
            if (fs.existsSync(file)) {
                jobText = fs.readFileSync(file, 'utf8');
                console.log(`✅ Fiche de poste lue depuis: ${file}`);
                break;
            }
        }

        if (!cvText && !jobText) {
            console.log('⚠️ Aucun fichier texte trouvé. Extraire d\'abord le contenu des PDF:');
            console.log('   textutil -convert txt cv_christine.pdf -output cv_extracted.txt');
            console.log('   textutil -convert txt fdp.pdf -output fdp_extracted.txt');
            return;
        }

        // Parser le CV
        if (cvText) {
            console.log('\n📄 === PARSING DU CV ===');
            const cvData = parseCV(cvText);
            
            console.log('\n📊 Résultats CV:');
            console.log(`👤 Nom: ${cvData.personal_info.name || 'Non détecté'}`);
            console.log(`📧 Email: ${cvData.personal_info.email || 'Non détecté'}`);
            console.log(`📱 Téléphone: ${cvData.personal_info.phone || 'Non détecté'}`);
            console.log(`🏠 Adresse: ${cvData.personal_info.address || 'Non détectée'}`);
            console.log(`🎯 Compétences (${cvData.skills.length}): ${cvData.skills.slice(0, 10).join(', ')}${cvData.skills.length > 10 ? '...' : ''}`);
            console.log(`🏷️ Expérience: ${cvData.experience_years || 'Non détectée'} ans`);
            console.log(`🗣️ Langues: ${cvData.languages.slice(0, 5).join(', ')}`);

            // Sauvegarder
            fs.writeFileSync('cv_parsed_real.json', JSON.stringify(cvData, null, 2));
            console.log('💾 CV sauvegardé: cv_parsed_real.json');
        }

        // Parser la fiche de poste
        if (jobText) {
            console.log('\n💼 === PARSING DE LA FICHE DE POSTE ===');
            const jobData = parseJob(jobText);
            
            console.log('\n📊 Résultats Fiche de Poste:');
            console.log(`💼 Titre: ${jobData.job_info.title || 'Non détecté'}`);
            console.log(`📋 Contrat: ${jobData.job_info.contract_type || 'Non détecté'}`);
            console.log(`🏠 Localisation: ${jobData.job_info.location || 'Non détectée'}`);
            console.log(`💰 Salaire: ${jobData.salary.amount ? jobData.salary.amount + 'k€' : 'Non détecté'}`);
            console.log(`🏢 Entreprise: ${jobData.company.name || 'Non détectée'}`);
            console.log(`🎯 Skills requis (${jobData.requirements.technical_skills.length}): ${jobData.requirements.technical_skills.slice(0, 10).join(', ')}`);
            console.log(`⏱️ Expérience requise: ${jobData.requirements.experience_years || 'Non spécifiée'} ans`);
            console.log(`🏠 Télétravail: ${jobData.benefits.remote_work ? 'Oui (' + (jobData.benefits.remote_type || 'non spécifié') + ')' : 'Non mentionné'}`);

            // Sauvegarder
            fs.writeFileSync('job_parsed_real.json', JSON.stringify(jobData, null, 2));
            console.log('💾 Fiche de poste sauvegardée: job_parsed_real.json');
        }

        // Matching si les deux sont disponibles
        if (cvText && jobText) {
            console.log('\n🎯 === ANALYSE DE MATCHING ===');
            const cvData = JSON.parse(fs.readFileSync('cv_parsed_real.json', 'utf8'));
            const jobData = JSON.parse(fs.readFileSync('job_parsed_real.json', 'utf8'));

            // Calcul du score de matching
            let score = 60; // Score de base

            // Matching des compétences
            const cvSkills = new Set(cvData.skills);
            const jobSkills = new Set(jobData.requirements.technical_skills);
            const commonSkills = [...cvSkills].filter(skill => jobSkills.has(skill));
            
            if (jobSkills.size > 0) {
                const skillMatch = commonSkills.length / jobSkills.size;
                score += skillMatch * 30;
                console.log(`🎯 Compétences communes: ${commonSkills.join(', ') || 'Aucune'}`);
                console.log(`📊 Match compétences: ${Math.round(skillMatch * 100)}%`);
            }

            // Matching expérience
            if (cvData.experience_years && jobData.requirements.experience_years) {
                if (cvData.experience_years >= jobData.requirements.experience_years) {
                    score += 10;
                    console.log(`✅ Expérience suffisante: ${cvData.experience_years} ans ≥ ${jobData.requirements.experience_years} ans requis`);
                } else {
                    score -= 5;
                    console.log(`⚠️ Expérience insuffisante: ${cvData.experience_years} ans < ${jobData.requirements.experience_years} ans requis`);
                }
            }

            const finalScore = Math.max(0, Math.min(100, score));
            
            const matchingResult = {
                score: Math.round(finalScore * 10) / 10,
                confidence: finalScore > 80 ? 'high' : finalScore > 60 ? 'medium' : 'low',
                common_skills: commonSkills,
                skill_match_percentage: jobSkills.size > 0 ? Math.round((commonSkills.length / jobSkills.size) * 100) : 0,
                experience_match: cvData.experience_years && jobData.requirements.experience_years ? 
                    cvData.experience_years >= jobData.requirements.experience_years : null,
                recommendation: finalScore > 80 ? 'Candidat fortement recommandé' : 
                               finalScore > 60 ? 'Candidat intéressant' : 'Candidat à considérer avec réserves'
            };

            console.log(`\n🏆 Score de matching: ${matchingResult.score}/100`);
            console.log(`🎯 Confiance: ${matchingResult.confidence}`);
            console.log(`💡 Recommandation: ${matchingResult.recommendation}`);

            // Sauvegarder le matching
            fs.writeFileSync('matching_real.json', JSON.stringify(matchingResult, null, 2));
            console.log('💾 Matching sauvegardé: matching_real.json');
        }

        console.log('\n✅ Parsing terminé avec succès !');
        console.log('📂 Fichiers générés:');
        if (fs.existsSync('cv_parsed_real.json')) console.log('   - cv_parsed_real.json');
        if (fs.existsSync('job_parsed_real.json')) console.log('   - job_parsed_real.json');
        if (fs.existsSync('matching_real.json')) console.log('   - matching_real.json');

    } catch (error) {
        console.error('❌ Erreur:', error.message);
    }
}

// Exécution si script appelé directement
if (require.main === module) {
    parseRealDocuments();
}

module.exports = { parseCV, parseJob, parseRealDocuments };
