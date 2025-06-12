#!/usr/bin/env node

/**
 * 🚀 Enhanced Mission Parser - SuperSmartMatch V2 
 * Parser enrichi avec extraction et matching des missions détaillées
 * Nouveau scoring : 40% missions + 30% compétences + 15% expérience + 15% qualité
 */

const fs = require('fs');

class EnhancedMissionParser {
    
    constructor() {
        this.missionPatterns = {
            // Patterns spécifiques pour l'extraction de missions
            facturation: [
                /facturation\s+(?:des\s+)?(?:clients?|ventes?)/gi,
                /émission\s+(?:de\s+)?factures?/gi,
                /gestion\s+(?:de\s+la\s+)?facturation/gi,
                /suivi\s+(?:des\s+)?factures?/gi
            ],
            saisie: [
                /saisie\s+(?:des\s+)?(?:écritures?|données?|informations?)/gi,
                /saisie\s+comptable/gi,
                /saisie\s+(?:des\s+)?pièces?\s+comptables?/gi,
                /enregistrement\s+(?:des\s+)?données?/gi
            ],
            controle: [
                /contrôle\s+(?:de\s+)?qualité/gi,
                /contrôle\s+(?:des\s+)?comptes?/gi,
                /vérification\s+(?:des\s+)?données?/gi,
                /validation\s+(?:des\s+)?informations?/gi
            ],
            reporting: [
                /(?:établissement|création|préparation)\s+(?:de\s+)?(?:rapports?|tableaux?)/gi,
                /reporting\s+(?:financier|comptable|mensuel)/gi,
                /suivi\s+(?:des\s+)?indicateurs?/gi
            ],
            gestion: [
                /gestion\s+(?:des\s+)?(?:stocks?|fournisseurs?|clients?)/gi,
                /administration\s+(?:des\s+)?(?:ventes?|achats?)/gi,
                /suivi\s+(?:des\s+)?(?:commandes?|livraisons?)/gi
            ]
        };

        this.technicalSkills = [
            // ERP/CRM
            'Oracle', 'SAP', 'PeopleSoft', 'Sage', 'JD Edwards', 'Microsoft Dynamics',
            'Salesforce', 'HubSpot', 'Zoho', 'SugarCRM',
            
            // Comptabilité
            'Ciel Compta', 'EBP', 'QuickBooks', 'FreshBooks', 'Xero',
            
            // Bureautique
            'Excel', 'Word', 'PowerPoint', 'Outlook', 'Access', 'SharePoint',
            'Google Workspace', 'LibreOffice',
            
            // Développement
            'SQL', 'Python', 'JavaScript', 'VBA', 'PowerBI', 'Tableau',
            
            // Systèmes
            'Windows', 'Linux', 'macOS', 'VMware', 'Active Directory'
        ];
    }

    // === PARSING CV ENRICHI AVEC MISSIONS ===
    parseEnhancedCV(text) {
        console.log('🧠 Parsing CV enrichi avec extraction des missions...');
        
        const cv = {
            personal_info: {},
            skills: [],
            professional_experience: [],
            languages: [],
            education: [],
            certifications: [],
            extracted_missions: []
        };

        // Extraction des informations de base
        this.extractBasicInfo(text, cv);
        
        // Extraction des compétences techniques
        this.extractTechnicalSkills(text, cv);
        
        // Extraction enrichie de l'expérience avec missions détaillées
        this.extractProfessionalExperienceWithMissions(text, cv);
        
        // Extraction des langues
        this.extractLanguages(text, cv);

        console.log(`   ✅ CV enrichi parsé avec ${cv.professional_experience.length} postes et ${cv.extracted_missions.length} missions`);
        return cv;
    }

    // === PARSING JOB ENRICHI AVEC MISSIONS ===
    parseEnhancedJob(text) {
        console.log('💼 Parsing Job enrichi avec extraction des missions...');
        
        const job = {
            job_info: {},
            requirements: { 
                technical_skills: [],
                required_missions: [],
                experience_years: 0
            },
            missions: [], // Missions principales du poste
            benefits: {},
            company: {},
            salary: {}
        };

        // Extraction des informations de base du job
        this.extractJobBasicInfo(text, job);
        
        // Extraction des compétences requises
        this.extractRequiredSkills(text, job);
        
        // Extraction enrichie des missions du poste
        this.extractJobMissions(text, job);
        
        // Extraction des exigences d'expérience
        this.extractExperienceRequirements(text, job);

        console.log(`   ✅ Job enrichi parsé avec ${job.missions.length} missions et ${job.requirements.technical_skills.length} compétences requises`);
        return job;
    }

    // === EXTRACTION INFORMATIONS DE BASE CV ===
    extractBasicInfo(text, cv) {
        // Nom (patterns améliorés)
        const namePatterns = [
            /(?:^|\\n)([A-ZÀ-ÿ][a-zà-ÿ]+\\s+[A-ZÀ-ÿ][a-zà-ÿ]+(?:\\s+[A-ZÀ-ÿ][a-zà-ÿ]+)?)\\s*(?:\\n|$)/,
            /(Christine\\s+DA\\s+SILVA)/i,
            /([A-ZÀ-ÿ]{2,}\\s+[A-ZÀ-ÿ]{2,}(?:\\s+[A-ZÀ-ÿ]{2,})?)/
        ];
        
        for (const pattern of namePatterns) {
            const match = text.match(pattern);
            if (match && match[1] && match[1].length < 50) {
                cv.personal_info.name = match[1].trim();
                console.log(`   ✅ Nom: ${cv.personal_info.name}`);
                break;
            }
        }

        // Email
        const emailMatch = text.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})/);
        if (emailMatch) {
            cv.personal_info.email = emailMatch[1];
            console.log(`   ✅ Email: ${cv.personal_info.email}`);
        }

        // Téléphone
        const phonePatterns = [
            /(\\+33\\s?[1-9](?:[\\s.-]?\\d{2}){4})/,
            /(0[1-9](?:[\\s.-]?\\d{2}){4})/
        ];
        
        for (const pattern of phonePatterns) {
            const match = text.match(pattern);
            if (match) {
                cv.personal_info.phone = match[1].trim();
                console.log(`   ✅ Téléphone: ${cv.personal_info.phone}`);
                break;
            }
        }
    }

    // === EXTRACTION COMPÉTENCES TECHNIQUES ===
    extractTechnicalSkills(text, cv) {
        const foundSkills = new Set();
        
        this.technicalSkills.forEach(skill => {
            const regex = new RegExp('\\\\b' + skill.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + '\\\\b', 'gi');
            if (text.match(regex)) {
                foundSkills.add(skill.toLowerCase());
            }
        });
        
        cv.skills = Array.from(foundSkills);
        console.log(`   ✅ Compétences techniques (${cv.skills.length}): ${cv.skills.slice(0, 5).join(', ')}${cv.skills.length > 5 ? '...' : ''}`);
    }

    // === EXTRACTION EXPÉRIENCE AVEC MISSIONS ===
    extractProfessionalExperienceWithMissions(text, cv) {
        // Recherche des blocs d'expérience professionnelle
        const experienceBlocks = this.findExperienceBlocks(text);
        
        experienceBlocks.forEach((block, index) => {
            const experience = {
                position: this.extractPosition(block),
                company: this.extractCompany(block),
                duration: this.extractDuration(block),
                missions: this.extractMissionsFromBlock(block)
            };
            
            cv.professional_experience.push(experience);
            cv.extracted_missions.push(...experience.missions);
        });

        console.log(`   ✅ Expérience professionnelle: ${cv.professional_experience.length} postes`);
        cv.professional_experience.forEach((exp, i) => {
            console.log(`      • ${exp.position} - ${exp.missions.length} missions`);
        });
    }

    // === EXTRACTION MISSIONS D'UN BLOC D'EXPÉRIENCE ===
    extractMissionsFromBlock(block) {
        const missions = [];
        
        // Recherche des missions par catégorie
        Object.entries(this.missionPatterns).forEach(([category, patterns]) => {
            patterns.forEach(pattern => {
                const matches = block.match(pattern);
                if (matches) {
                    matches.forEach(match => {
                        const cleanMission = this.cleanMissionText(match);
                        if (cleanMission && cleanMission.length > 10) {
                            missions.push({
                                text: cleanMission,
                                category: category,
                                confidence: this.calculateMissionConfidence(match, category)
                            });
                        }
                    });
                }
            });
        });

        // Recherche de patterns génériques de missions
        const genericPatterns = [
            /(?:•|-)\\s*([^\\n•-]{20,100})/g,
            /(?:Mission|Responsabilité|Tâche)\\s*:?\\s*([^\\n]{20,150})/gi,
            /(?:Réalisation|Gestion|Suivi|Développement)\\s+(?:de\\s+|des\\s+)?([^\\n]{15,100})/gi
        ];

        genericPatterns.forEach(pattern => {
            let match;
            while ((match = pattern.exec(block)) !== null) {
                const cleanMission = this.cleanMissionText(match[1]);
                if (cleanMission && cleanMission.length > 15) {
                    missions.push({
                        text: cleanMission,
                        category: 'general',
                        confidence: 0.7
                    });
                }
            }
        });

        return this.deduplicateMissions(missions);
    }

    // === EXTRACTION INFORMATIONS JOB ===
    extractJobBasicInfo(text, job) {
        // Titre du poste
        const titlePatterns = [
            /^([A-ZÀ-ÿ][A-Za-zà-ÿ\\s\\-\\/]{5,50})\\s*(?:\\n|Lieu|\\-|—|–)/m,
            /(Assistant\\s+[A-Za-zà-ÿ\\s]+)/i,
            /(?:Poste|Offre|Job|Position)[\\s:]*([A-ZÀ-ÿ][A-Za-zà-ÿ\\s\\-\\/]+)/i
        ];
        
        for (const pattern of titlePatterns) {
            const match = text.match(pattern);
            if (match) {
                job.job_info.title = match[1].trim();
                console.log(`   ✅ Titre: ${job.job_info.title}`);
                break;
            }
        }

        // Type de contrat
        const contractMatch = text.match(/(CDD|CDI|Stage|Freelance)(?:\\s+de\\s+(\\d+)\\s+(mois|semaines?))?/i);
        if (contractMatch) {
            job.job_info.contract_type = contractMatch[1].toUpperCase();
            if (contractMatch[2]) {
                job.job_info.contract_duration = `${contractMatch[2]} ${contractMatch[3]}`;
            }
        }

        // Localisation
        const locationPatterns = [
            /Lieu[\\s:]*([A-ZÀ-ÿ][a-zà-ÿ\\s\\-]+(?:\\(\\d{5}\\))?)/i,
            /(\\d{5})\\s*([A-ZÀ-ÿ][a-zà-ÿ\\s\\-]+)/
        ];
        
        for (const pattern of locationPatterns) {
            const match = text.match(pattern);
            if (match) {
                job.job_info.location = (match[1] + (match[2] || '')).trim();
                break;
            }
        }
    }

    // === EXTRACTION MISSIONS DU JOB ===
    extractJobMissions(text, job) {
        const missions = [];
        
        // Recherche par catégories de missions
        Object.entries(this.missionPatterns).forEach(([category, patterns]) => {
            patterns.forEach(pattern => {
                const matches = text.match(pattern);
                if (matches) {
                    matches.forEach(match => {
                        const cleanMission = this.cleanMissionText(match);
                        if (cleanMission && cleanMission.length > 10) {
                            missions.push({
                                text: cleanMission,
                                category: category,
                                priority: this.calculateMissionPriority(match, category),
                                required: true
                            });
                        }
                    });
                }
            });
        });

        // Recherche dans les sections "Missions" ou "Responsabilités"
        const missionSectionRegex = /(?:Missions?|Responsabilités?|Tâches?)\\s*:?([^\\n\\r]{0,500}(?:\\n[^\\n\\r]{0,100})*)/gi;
        let sectionMatch;
        while ((sectionMatch = missionSectionRegex.exec(text)) !== null) {
            const sectionText = sectionMatch[1];
            const sectionMissions = this.extractMissionsFromText(sectionText);
            missions.push(...sectionMissions);
        }

        job.missions = this.deduplicateMissions(missions);
        job.requirements.required_missions = job.missions.filter(m => m.required);
        
        console.log(`   ✅ Missions du poste (${job.missions.length}): ${job.missions.slice(0, 3).map(m => m.category).join(', ')}`);
    }

    // === EXTRACTION COMPÉTENCES REQUISES ===
    extractRequiredSkills(text, job) {
        const requiredSkills = [];
        
        this.technicalSkills.forEach(skill => {
            const regex = new RegExp('\\\\b' + skill.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + '\\\\b', 'gi');
            if (text.match(regex)) {
                requiredSkills.push({
                    name: skill,
                    required: this.isSkillRequired(text, skill),
                    level: this.extractSkillLevel(text, skill)
                });
            }
        });
        
        job.requirements.technical_skills = requiredSkills;
        console.log(`   ✅ Compétences requises (${requiredSkills.length}): ${requiredSkills.slice(0, 3).map(s => s.name).join(', ')}`);
    }

    // === MATCHING ENRICHI AVEC MISSIONS ===
    calculateEnhancedMatching(cvData, jobData) {
        console.log('🎯 Calcul de matching enrichi avec missions...');
        
        const scoring = {
            missions: 0,     // 40% du score
            skills: 0,       // 30% du score  
            experience: 0,   // 15% du score
            quality: 0       // 15% du score
        };

        // === 1. MATCHING MISSIONS (40 points) ===
        const missionScore = this.calculateMissionMatching(cvData, jobData);
        scoring.missions = missionScore * 0.4;

        // === 2. MATCHING COMPÉTENCES (30 points) ===
        const skillScore = this.calculateSkillMatching(cvData, jobData);
        scoring.skills = skillScore * 0.3;

        // === 3. MATCHING EXPÉRIENCE (15 points) ===
        const experienceScore = this.calculateExperienceMatching(cvData, jobData);
        scoring.experience = experienceScore * 0.15;

        // === 4. SCORE QUALITÉ (15 points) ===
        const qualityScore = this.calculateQualityScore(cvData, jobData);
        scoring.quality = qualityScore * 0.15;

        const finalScore = Math.round(scoring.missions + scoring.skills + scoring.experience + scoring.quality);

        const result = {
            score: finalScore,
            confidence: finalScore > 85 ? 'high' : finalScore > 70 ? 'medium' : 'low',
            scoring_breakdown: {
                missions: { score: Math.round(scoring.missions), weight: '40%' },
                skills: { score: Math.round(scoring.skills), weight: '30%' },
                experience: { score: Math.round(scoring.experience), weight: '15%' },
                quality: { score: Math.round(scoring.quality), weight: '15%' }
            },
            mission_matching: this.getMissionMatchingDetails(cvData, jobData),
            skill_matching: this.getSkillMatchingDetails(cvData, jobData),
            recommendation: this.getRecommendation(finalScore),
            improvements: this.getSuggestedImprovements(cvData, jobData)
        };

        console.log(`\\n🏆 Score final enrichi: ${finalScore}/100`);
        console.log(`📊 Détail: Missions(${Math.round(scoring.missions)}) + Compétences(${Math.round(scoring.skills)}) + Expérience(${Math.round(scoring.experience)}) + Qualité(${Math.round(scoring.quality)})`);
        console.log(`💡 ${result.recommendation}`);

        return result;
    }

    // === CALCUL MATCHING MISSIONS ===
    calculateMissionMatching(cvData, jobData) {
        if (!jobData.missions || jobData.missions.length === 0) return 50;
        
        const cvMissions = cvData.extracted_missions || [];
        const jobMissions = jobData.missions || [];
        
        let totalMatches = 0;
        let totalPossible = jobMissions.length;
        
        jobMissions.forEach(jobMission => {
            const bestMatch = this.findBestMissionMatch(jobMission, cvMissions);
            if (bestMatch && bestMatch.similarity > 0.6) {
                totalMatches += bestMatch.similarity;
            }
        });
        
        const missionScore = totalPossible > 0 ? (totalMatches / totalPossible) * 100 : 50;
        
        console.log(`   🎯 Matching missions: ${Math.round(missionScore)}% (${totalMatches.toFixed(1)}/${totalPossible} missions matchées)`);
        return missionScore;
    }

    // === CALCUL MATCHING COMPÉTENCES ===
    calculateSkillMatching(cvData, jobData) {
        const cvSkills = new Set((cvData.skills || []).map(s => s.toLowerCase()));
        const jobSkills = jobData.requirements?.technical_skills || [];
        
        if (jobSkills.length === 0) return 50;
        
        let matchedSkills = 0;
        jobSkills.forEach(jobSkill => {
            const skillName = typeof jobSkill === 'string' ? jobSkill : jobSkill.name;
            if (cvSkills.has(skillName.toLowerCase())) {
                matchedSkills++;
            }
        });
        
        const skillScore = (matchedSkills / jobSkills.length) * 100;
        console.log(`   🔧 Matching compétences: ${Math.round(skillScore)}% (${matchedSkills}/${jobSkills.length} compétences)`);
        return skillScore;
    }

    // === CALCUL MATCHING EXPÉRIENCE ===
    calculateExperienceMatching(cvData, jobData) {
        const cvExperience = this.calculateTotalExperience(cvData);
        const requiredExperience = jobData.requirements?.experience_years || 0;
        
        if (requiredExperience === 0) return 75;
        
        if (cvExperience >= requiredExperience) {
            return 100;
        } else {
            const ratio = cvExperience / requiredExperience;
            return Math.max(0, ratio * 100);
        }
    }

    // === CALCUL SCORE QUALITÉ ===
    calculateQualityScore(cvData, jobData) {
        let qualityScore = 0;
        
        // Contact valide
        if (cvData.personal_info?.email) qualityScore += 25;
        if (cvData.personal_info?.phone) qualityScore += 25;
        
        // Multilinguisme
        if (cvData.languages && cvData.languages.length > 1) qualityScore += 25;
        
        // Parcours structuré
        if (cvData.professional_experience && cvData.professional_experience.length > 0) qualityScore += 25;
        
        return qualityScore;
    }

    // === FONCTIONS UTILITAIRES ===
    
    findExperienceBlocks(text) {
        // Implémentation simplifiée - découpe le texte en blocs d'expérience
        const blocks = text.split(/(?:\\n\\s*){2,}/).filter(block => 
            block.length > 50 && 
            (block.match(/\\d{4}/) || block.match(/mois|ans?|année/i))
        );
        return blocks.slice(0, 5); // Maximum 5 expériences
    }

    extractPosition(block) {
        const positionPatterns = [
            /([A-ZÀ-ÿ][A-Za-zà-ÿ\\s]{10,50})(?:\\n|\\s+chez\\s+|\\s+\\-\\s+|\\s+à\\s+)/,
            /(Assistant[^\\n]{5,30})/i
        ];
        
        for (const pattern of positionPatterns) {
            const match = block.match(pattern);
            if (match) return match[1].trim();
        }
        return 'Poste non spécifié';
    }

    extractCompany(block) {
        const companyPatterns = [
            /(?:chez|à)\\s+([A-ZÀ-ÿ][^\\n]{5,30})/i,
            /\\-\\s*([A-ZÀ-ÿ][^\\n]{5,30})/
        ];
        
        for (const pattern of companyPatterns) {
            const match = block.match(pattern);
            if (match) return match[1].trim();
        }
        return 'Entreprise non spécifiée';
    }

    extractDuration(block) {
        const durationMatch = block.match(/(\\d{1,2})\\s*(mois|ans?|année)/i);
        return durationMatch ? durationMatch[0] : 'Durée non spécifiée';
    }

    cleanMissionText(text) {
        return text.replace(/[•\\-]/g, '').trim();
    }

    calculateMissionConfidence(mission, category) {
        return 0.8; // Implémentation simplifiée
    }

    deduplicateMissions(missions) {
        const seen = new Set();
        return missions.filter(mission => {
            const key = mission.text.toLowerCase().replace(/\\s+/g, ' ');
            if (seen.has(key)) return false;
            seen.add(key);
            return true;
        });
    }

    extractMissionsFromText(text) {
        // Implémentation simplifiée
        return [];
    }

    isSkillRequired(text, skill) {
        const requiredKeywords = ['requis', 'obligatoire', 'indispensable', 'nécessaire'];
        const skillContext = this.getTextAroundSkill(text, skill, 50);
        return requiredKeywords.some(keyword => 
            skillContext.toLowerCase().includes(keyword)
        );
    }

    extractSkillLevel(text, skill) {
        const skillContext = this.getTextAroundSkill(text, skill, 30);
        if (skillContext.match(/expert|avancé|confirmé/i)) return 'expert';
        if (skillContext.match(/intermédiaire|bon niveau/i)) return 'intermediate';
        if (skillContext.match(/débutant|notions|bases/i)) return 'beginner';
        return 'not_specified';
    }

    getTextAroundSkill(text, skill, radius) {
        const skillIndex = text.toLowerCase().indexOf(skill.toLowerCase());
        if (skillIndex === -1) return '';
        
        const start = Math.max(0, skillIndex - radius);
        const end = Math.min(text.length, skillIndex + skill.length + radius);
        return text.substring(start, end);
    }

    findBestMissionMatch(jobMission, cvMissions) {
        let bestMatch = null;
        let bestSimilarity = 0;
        
        cvMissions.forEach(cvMission => {
            const similarity = this.calculateMissionSimilarity(jobMission, cvMission);
            if (similarity > bestSimilarity) {
                bestSimilarity = similarity;
                bestMatch = { mission: cvMission, similarity };
            }
        });
        
        return bestMatch;
    }

    calculateMissionSimilarity(mission1, mission2) {
        // Implémentation simplifiée basée sur les catégories et mots-clés
        if (mission1.category === mission2.category) return 0.8;
        
        const text1 = mission1.text.toLowerCase();
        const text2 = mission2.text.toLowerCase();
        
        const commonWords = this.getCommonWords(text1, text2);
        const similarity = commonWords.length / Math.max(text1.split(' ').length, text2.split(' ').length);
        
        return Math.min(0.95, similarity);
    }

    getCommonWords(text1, text2) {
        const words1 = new Set(text1.split(' ').filter(w => w.length > 3));
        const words2 = new Set(text2.split(' ').filter(w => w.length > 3));
        return [...words1].filter(word => words2.has(word));
    }

    calculateTotalExperience(cvData) {
        // Calcul simplifié basé sur le nombre d'expériences
        const experiences = cvData.professional_experience || [];
        return experiences.length * 2; // Estimation : 2 ans par poste en moyenne
    }

    getMissionMatchingDetails(cvData, jobData) {
        return {
            cv_missions_count: cvData.extracted_missions?.length || 0,
            job_missions_count: jobData.missions?.length || 0,
            matched_categories: []
        };
    }

    getSkillMatchingDetails(cvData, jobData) {
        const cvSkills = new Set((cvData.skills || []).map(s => s.toLowerCase()));
        const jobSkills = jobData.requirements?.technical_skills || [];
        
        return {
            cv_skills_count: cvSkills.size,
            job_skills_count: jobSkills.length,
            matched_skills: jobSkills.filter(skill => {
                const skillName = typeof skill === 'string' ? skill : skill.name;
                return cvSkills.has(skillName.toLowerCase());
            })
        };
    }

    getRecommendation(score) {
        if (score >= 85) return 'Candidat fortement recommandé - Excellent match sur les missions';
        if (score >= 75) return 'Candidat recommandé - Bon match global';
        if (score >= 65) return 'Candidat intéressant - Match partiel';
        if (score >= 50) return 'Candidat à considérer - Formation nécessaire';
        return 'Candidat peu adapté - Écart important';
    }

    getSuggestedImprovements(cvData, jobData) {
        const improvements = [];
        
        // Suggestions basées sur l'analyse
        if (!cvData.personal_info?.email) {
            improvements.push('Ajouter une adresse email valide');
        }
        
        const cvSkills = new Set((cvData.skills || []).map(s => s.toLowerCase()));
        const jobSkills = jobData.requirements?.technical_skills || [];
        const missingSkills = jobSkills.filter(skill => {
            const skillName = typeof skill === 'string' ? skill : skill.name;
            return !cvSkills.has(skillName.toLowerCase());
        }).slice(0, 3);
        
        if (missingSkills.length > 0) {
            improvements.push(`Développer les compétences: ${missingSkills.map(s => typeof s === 'string' ? s : s.name).join(', ')}`);
        }
        
        return improvements;
    }

    // === EXTRACTION DES LANGUES ===
    extractLanguages(text, cv) {
        const languagePatterns = [
            /(Français|Anglais|Espagnol|Allemand|Italien)[\\s\\-]*(?:\\([^)]*\\))?[\\s\\-]*(natif|native|courant|fluent|bilingue|intermédiaire|débutant|scolaire|professionnel)?/gi
        ];
        
        const languagesFound = new Set();
        languagePatterns.forEach(pattern => {
            const matches = text.match(pattern) || [];
            matches.forEach(match => languagesFound.add(match.trim().toLowerCase()));
        });
        
        cv.languages = Array.from(languagesFound);
    }

    // === EXTRACTION EXIGENCES D'EXPÉRIENCE ===
    extractExperienceRequirements(text, job) {
        const expPatterns = [
            /(\\d+)\\s*(?:ans?|années?)\\s*(?:d'|de\\s)?(?:expérience|exp)/i,
            /(?:minimum|mini)\\s*(\\d+)\\s*(?:ans?|années?)/i
        ];
        
        for (const pattern of expPatterns) {
            const match = text.match(pattern);
            if (match) {
                job.requirements.experience_years = parseInt(match[1]);
                console.log(`   ✅ Expérience requise: ${job.requirements.experience_years} ans`);
                break;
            }
        }
    }

    calculateMissionPriority(mission, category) {
        // Priorité basée sur la catégorie de mission
        const priorities = {
            'facturation': 0.9,
            'saisie': 0.8,
            'controle': 0.7,
            'reporting': 0.6,
            'gestion': 0.5
        };
        return priorities[category] || 0.5;
    }
}

// === FONCTION PRINCIPALE ===
async function main() {
    console.log('🚀 Enhanced Mission Parser - SuperSmartMatch V2');
    console.log('===================================================');

    const parser = new EnhancedMissionParser();

    try {
        // Lire les fichiers extraits
        let cvText = '';
        let jobText = '';

        const cvFiles = ['cv_christine_clean_extracted.txt', 'cv_extracted.txt', 'cv_christine.txt'];
        const jobFiles = ['fdp_clean_extracted.txt', 'fdp_extracted.txt', 'fdp.txt'];

        for (const file of cvFiles) {
            if (fs.existsSync(file)) {
                cvText = fs.readFileSync(file, 'utf8');
                console.log(`✅ CV lu depuis: ${file}`);
                break;
            }
        }

        for (const file of jobFiles) {
            if (fs.existsSync(file)) {
                jobText = fs.readFileSync(file, 'utf8');
                console.log(`✅ Fiche de poste lue depuis: ${file}`);
                break;
            }
        }

        if (!cvText || !jobText) {
            console.log('❌ Fichiers texte non trouvés. Lancez d\\'abord: node fix-pdf-extraction.js');
            return;
        }

        // Parsing enrichi
        console.log('\\n📄 === PARSING CV ENRICHI AVEC MISSIONS ===');
        const cvData = parser.parseEnhancedCV(cvText);
        
        console.log('\\n💼 === PARSING JOB ENRICHI AVEC MISSIONS ==='); 
        const jobData = parser.parseEnhancedJob(jobText);

        // Sauvegarder les données enrichies
        fs.writeFileSync('cv_parsed_enhanced.json', JSON.stringify(cvData, null, 2));
        fs.writeFileSync('job_parsed_enhanced.json', JSON.stringify(jobData, null, 2));
        console.log('\\n💾 Données enrichies sauvegardées');

        // Matching enrichi avec missions
        console.log('\\n🎯 === MATCHING ENRICHI AVEC MISSIONS ===');
        const matchingResult = parser.calculateEnhancedMatching(cvData, jobData);
        
        fs.writeFileSync('matching_enhanced.json', JSON.stringify(matchingResult, null, 2));
        console.log('\\n💾 Matching enrichi sauvegardé: matching_enhanced.json');

        console.log('\\n✅ Enhanced Mission Parser terminé avec succès !');
        console.log('📂 Fichiers générés:');
        console.log('   - cv_parsed_enhanced.json');
        console.log('   - job_parsed_enhanced.json'); 
        console.log('   - matching_enhanced.json');

        console.log('\\n🎯 Nouveau scoring appliqué :');
        console.log('   • 40% Missions détaillées');
        console.log('   • 30% Compétences techniques');
        console.log('   • 15% Expérience');
        console.log('   • 15% Qualité du profil');

    } catch (error) {
        console.error('❌ Erreur:', error.message);
    }
}

if (require.main === module) {
    main();
}

module.exports = EnhancedMissionParser;