/**
 * NEXTEN GEO MATCHER V2 - INTÉGRATION SYSTÈME UNIFIÉ
 * Extension seamless du NextenOptimizedSystem avec CommuteOptimizer
 * Critère #2 Géolocalisation (20%) + Critère #1 Sémantique (25%) = 45% du score total
 */

class NextenGeoMatcher extends CommuteOptimizer {
    constructor(nextenSystem, compatibilityEngine) {
        super();
        this.nextenSystem = nextenSystem;
        this.compatibilityEngine = compatibilityEngine;
        this.unifiedSchema = nextenSystem?.unifiedSchema;
        
        this.initializeGlobalScoring();
    }

    /**
     * CONFIGURATION DU SCORING GLOBAL NEXTEN
     * Intégration des critères #1 et #2 (45% du total)
     */
    initializeGlobalScoring() {
        this.globalConfig = {
            criteria: {
                semanticCompatibility: 0.25,  // 25% - Critère #1 (déjà implémenté)
                geographicalCommute: 0.20,    // 20% - Critère #2 (nouveau)
                experienceLevel: 0.20,        // 20% - Critère #3 (futur)
                culturalFit: 0.15,           // 15% - Critère #4 (futur)
                availability: 0.10,          // 10% - Critère #5 (futur)
                otherFactors: 0.10           // 10% - Autres critères
            },
            performance: {
                targetTime: 150,             // < 150ms pour calcul complet (critères 1+2)
                cacheGoal: 0.85             // 85% cache hit rate
            }
        };
    }

    /**
     * MATCHING AVANCÉ AVEC GÉOLOCALISATION
     * Hook principal pour l'architecture Nexten
     */
    async enhancedGeoMatching(candidateId, jobId) {
        const startTime = performance.now();
        
        try {
            if (!this.nextenSystem) {
                throw new Error("NextenOptimizedSystem requis pour geo matching");
            }

            // Récupération des données via le système unifié
            const candidateData = await this.nextenSystem.getCandidateData(candidateId);
            const jobData = await this.nextenSystem.getJobData(jobId);

            // Validation des données géographiques
            if (!this.hasGeographicalData(candidateData, jobData)) {
                return this.handleMissingGeoData(candidateId, jobId);
            }

            // Calcul parallèle des critères #1 et #2
            const [semanticResult, commuteResult] = await Promise.all([
                this.calculateSemanticScore(candidateData, jobData),
                this.calculateCommuteScore(candidateData, jobData)
            ]);

            // Score composite final (45% du total)
            const compositeScore = this.calculateCompositeGlobalScore(semanticResult, commuteResult);

            // Métriques de performance
            const totalTime = performance.now() - startTime;
            this.updateGlobalPerformanceMetrics(totalTime);

            return {
                // Scores individuels
                criterium1_semantic: {
                    score: semanticResult.score,
                    weight: this.globalConfig.criteria.semanticCompatibility,
                    contribution: semanticResult.score * this.globalConfig.criteria.semanticCompatibility,
                    details: semanticResult
                },
                criterium2_commute: {
                    score: commuteResult.finalScore,
                    weight: this.globalConfig.criteria.geographicalCommute,
                    contribution: commuteResult.finalScore * this.globalConfig.criteria.geographicalCommute,
                    details: commuteResult
                },
                
                // Score global combiné (45%)
                combined_score: compositeScore,
                combined_percentage: compositeScore * 100,
                
                // Métadonnées Nexten
                nexten_integration: {
                    candidateId,
                    jobId,
                    calculatedAt: new Date().toISOString(),
                    algorithm_version: "v2.0_geo_enhanced",
                    performance: {
                        totalTime: totalTime,
                        meetsPerfGoal: totalTime < this.globalConfig.performance.targetTime
                    }
                },
                
                // Recommandations intelligentes
                recommendations: this.generateIntelligentRecommendations(semanticResult, commuteResult),
                
                // Données pour visualisation
                visualization: this.prepareVisualizationData(candidateData, jobData, commuteResult)
            };

        } catch (error) {
            console.error('Erreur enhanced geo matching:', error);
            return this.handleMatchingError(candidateId, jobId, error);
        }
    }

    /**
     * CALCUL SCORE SÉMANTIQUE (CRITÈRE #1)
     * Intégration avec NextenCompatibilityEngine existant
     */
    async calculateSemanticScore(candidateData, jobData) {
        if (this.compatibilityEngine) {
            return await this.compatibilityEngine.calculateCompatibility(candidateData, jobData);
        }
        
        // Fallback si engine non disponible
        console.warn('NextenCompatibilityEngine non disponible, utilisation fallback');
        return {
            score: 0.5,
            fallback: true,
            breakdown: { title: { score: 0.5 }, skills: { score: 0.5 }, responsibilities: { score: 0.5 } }
        };
    }

    /**
     * SCORE COMPOSITE GLOBAL
     * Combinaison intelligente critères #1 + #2
     */
    calculateCompositeGlobalScore(semanticResult, commuteResult) {
        const semanticContribution = semanticResult.score * this.globalConfig.criteria.semanticCompatibility;
        const commuteContribution = commuteResult.finalScore * this.globalConfig.criteria.geographicalCommute;
        
        // Score combiné des critères implémentés (45% du total)
        const implementedScore = semanticContribution + commuteContribution;
        
        return Math.min(implementedScore, 1.0);
    }

    /**
     * VALIDATION DONNÉES GÉOGRAPHIQUES
     * Vérification présence coordonnées et adresses
     */
    hasGeographicalData(candidateData, jobData) {
        const candidateGeo = candidateData.coordonnees && candidateData.adresse;
        const jobGeo = jobData.coordonnees && jobData.adresse;
        
        return candidateGeo && jobGeo;
    }

    /**
     * GESTION DONNÉES GÉOGRAPHIQUES MANQUANTES
     * Fallback intelligent avec estimation
     */
    handleMissingGeoData(candidateId, jobId) {
        console.warn(`Données géographiques manquantes pour candidat ${candidateId} et/ou job ${jobId}`);
        
        return {
            criterium2_commute: {
                score: 0.3, // Score par défaut réduit
                weight: this.globalConfig.criteria.geographicalCommute,
                contribution: 0.3 * this.globalConfig.criteria.geographicalCommute,
                error: 'Données géographiques manquantes'
            },
            combined_score: 0.3 * this.globalConfig.criteria.geographicalCommute,
            warning: 'Matching géographique impossible - données manquantes'
        };
    }

    /**
     * RECOMMANDATIONS INTELLIGENTES
     * Suggestions basées sur les deux critères
     */
    generateIntelligentRecommendations(semanticResult, commuteResult) {
        const recommendations = [];
        
        // Analyse sémantique
        if (semanticResult.score > 0.8) {
            recommendations.push({
                type: 'semantic_excellent',
                message: 'Excellente correspondance de profil et compétences',
                priority: 'high'
            });
        } else if (semanticResult.score < 0.4) {
            recommendations.push({
                type: 'semantic_improvement',
                message: 'Formations recommandées pour améliorer l\'adéquation',
                priority: 'medium',
                suggestions: this.generateSkillSuggestions(semanticResult)
            });
        }
        
        // Analyse géographique
        if (commuteResult.finalScore > 0.8) {
            recommendations.push({
                type: 'commute_excellent',
                message: `Trajet optimal en ${commuteResult.bestMode}`,
                priority: 'high'
            });
        } else if (commuteResult.finalScore < 0.4) {
            recommendations.push({
                type: 'commute_challenging',
                message: 'Trajet long - négociation télétravail recommandée',
                priority: 'high',
                alternatives: commuteResult.details.alternatives
            });
        }
        
        // Recommandations combinées
        const combinedScore = this.calculateCompositeGlobalScore(semanticResult, commuteResult);
        if (combinedScore > 0.75) {
            recommendations.push({
                type: 'excellent_match',
                message: 'Candidat hautement recommandé - profil et localisation optimaux',
                priority: 'critical'
            });
        }
        
        return recommendations;
    }

    /**
     * PRÉPARATION DONNÉES VISUALISATION
     * Format pour cartes interactives dans l'interface
     */
    prepareVisualizationData(candidateData, jobData, commuteResult) {
        return {
            // Points sur la carte
            locations: {
                candidate: {
                    name: 'Domicile candidat',
                    coordinates: candidateData.coordonnees,
                    address: candidateData.adresse,
                    icon: 'home'
                },
                job: {
                    name: 'Lieu de travail',
                    coordinates: jobData.coordonnees,
                    address: jobData.adresse,
                    icon: 'work'
                }
            },
            
            // Routes par mode de transport
            routes: Object.entries(commuteResult.breakdown || {}).map(([mode, data]) => ({
                mode: mode,
                name: this.transportModes[mode]?.name || mode,
                duration: data.duration,
                score: data.score,
                color: this.getModeColor(mode),
                recommended: mode === commuteResult.bestMode
            })),
            
            // Zones d'intérêt
            zones: this.getRelevantZones(candidateData.coordonnees, jobData.coordonnees),
            
            // Configuration carte
            mapConfig: {
                center: this.calculateMapCenter(candidateData.coordonnees, jobData.coordonnees),
                zoom: this.calculateOptimalZoom(candidateData.coordonnees, jobData.coordonnees)
            }
        };
    }

    /**
     * INTÉGRATION CANDIDATE-MATCHING-IMPROVED.HTML
     * Hook pour l'interface utilisateur existante
     */
    async updateMatchingInterface(candidateId, jobId, containerSelector = '#matching-results') {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.warn('Container pour matching interface non trouvé');
            return;
        }

        try {
            // Calcul du matching complet
            const matchingResult = await this.enhancedGeoMatching(candidateId, jobId);
            
            // Mise à jour de l'interface
            this.renderMatchingResults(container, matchingResult);
            this.renderInteractiveMap(container, matchingResult.visualization);
            this.renderRecommendations(container, matchingResult.recommendations);
            
        } catch (error) {
            console.error('Erreur mise à jour interface:', error);
            this.renderErrorState(container, error);
        }
    }

    /**
     * RENDU RÉSULTATS MATCHING
     */
    renderMatchingResults(container, result) {
        const resultsHTML = `
            <div class="nexten-matching-results">
                <div class="score-overview">
                    <h3>Score de compatibilité global</h3>
                    <div class="score-circle" data-score="${result.combined_percentage}">
                        <span class="score-value">${result.combined_percentage.toFixed(1)}%</span>
                    </div>
                </div>
                
                <div class="criteria-breakdown">
                    <div class="criterion semantic">
                        <h4>🧠 Compatibilité Sémantique</h4>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${result.criterium1_semantic.score * 100}%"></div>
                        </div>
                        <span>${(result.criterium1_semantic.score * 100).toFixed(1)}% (25% du total)</span>
                    </div>
                    
                    <div class="criterion commute">
                        <h4>🗺️ Optimisation Trajet</h4>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${result.criterium2_commute.score * 100}%"></div>
                        </div>
                        <span>${(result.criterium2_commute.score * 100).toFixed(1)}% (20% du total)</span>
                    </div>
                </div>
                
                <div class="performance-info">
                    <small>Calculé en ${result.nexten_integration.performance.totalTime.toFixed(2)}ms</small>
                </div>
            </div>
        `;
        
        const resultsDiv = container.querySelector('.matching-results') || 
                          this.createElement('div', 'matching-results');
        resultsDiv.innerHTML = resultsHTML;
        
        if (!container.contains(resultsDiv)) {
            container.appendChild(resultsDiv);
        }
    }

    /**
     * RENDU CARTE INTERACTIVE
     */
    renderInteractiveMap(container, visualizationData) {
        const mapHTML = `
            <div class="nexten-interactive-map">
                <div id="map-container" style="height: 400px; width: 100%;"></div>
                <div class="transport-options">
                    ${visualizationData.routes.map(route => `
                        <div class="transport-option ${route.recommended ? 'recommended' : ''}" 
                             data-mode="${route.mode}">
                            <span class="mode-name">${route.name}</span>
                            <span class="duration">${Math.round(route.duration)} min</span>
                            <span class="score">${(route.score * 100).toFixed(0)}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        const mapDiv = container.querySelector('.interactive-map') || 
                      this.createElement('div', 'interactive-map');
        mapDiv.innerHTML = mapHTML;
        
        if (!container.contains(mapDiv)) {
            container.appendChild(mapDiv);
        }

        // Initialisation de la carte (Google Maps ou Leaflet)
        this.initializeMap(visualizationData);
    }

    /**
     * TESTS AVEC PROFIL DOROTHÉE LIM ÉTENDU
     * Validation complète critères #1 + #2
     */
    async runExtendedDorotheTests() {
        console.log("🧪 TESTS NEXTEN GEO MATCHER - DOROTHÉE LIM ÉTENDU");
        console.log("=================================================");
        
        const dorotheeProfil = {
            // Données sémantiques (existantes)
            experiences_professionnelles: [
                {
                    poste: "Office Manager",
                    entreprise: "Hermès",
                    date_debut: "2020",
                    date_fin: "2024"
                }
            ],
            competences_detaillees: ["SAP Business One", "ERP Management", "Office Management"],
            
            // Nouvelles données géographiques
            adresse: "Boulogne-Billancourt, 92100",
            coordonnees: { lat: 48.8356, lng: 2.2501 },
            preferences_transport: ["metro", "tramway", "velo"],
            mobilite_acceptee: "paris_proche_banlieue",
            duree_trajet_max: "45min"
        };
        
        const jobsTest = [
            {
                titre_poste: "Office Manager Secteur Luxe",
                competences: ["SAP", "Office Management", "Luxe"],
                adresse: "La Défense, 92400 Courbevoie",
                coordonnees: { lat: 48.8908, lng: 2.2383 },
                context: "La Défense - RER A direct"
            },
            {
                titre_poste: "Coordinatrice Administrative",
                competences: ["Coordination", "Microsoft Office"],
                adresse: "République, 75003 Paris",
                coordonnees: { lat: 48.8673, lng: 2.3629 },
                context: "République - Centre Paris"
            }
        ];
        
        for (const job of jobsTest) {
            console.log(`\n🔍 TEST: ${job.context}`);
            console.log("-".repeat(50));
            
            const result = await this.enhancedGeoMatching('dorothee_test', 'job_test');
            
            console.log(`📊 Score global: ${result.combined_percentage.toFixed(1)}%`);
            console.log(`🧠 Sémantique: ${(result.criterium1_semantic.score * 100).toFixed(1)}%`);
            console.log(`🗺️ Trajet: ${(result.criterium2_commute.score * 100).toFixed(1)}%`);
            console.log(`⏱️ Performance: ${result.nexten_integration.performance.totalTime.toFixed(2)}ms`);
            
            if (result.recommendations.length > 0) {
                console.log("💡 Recommandations:");
                result.recommendations.forEach(rec => {
                    console.log(`  • ${rec.message} (${rec.priority})`);
                });
            }
        }
    }

    /**
     * UTILITAIRES D'INTERFACE
     */
    createElement(tag, className) {
        const element = document.createElement(tag);
        element.className = className;
        return element;
    }

    getModeColor(mode) {
        const colors = {
            driving: '#4285f4',
            transit: '#34a853',
            walking: '#fbbc04',
            bicycling: '#ea4335'
        };
        return colors[mode] || '#9aa0a6';
    }

    calculateMapCenter(coord1, coord2) {
        return {
            lat: (coord1.lat + coord2.lat) / 2,
            lng: (coord1.lng + coord2.lng) / 2
        };
    }

    calculateOptimalZoom(coord1, coord2) {
        const distance = this.calculateEuclideanDistance(coord1, coord2);
        if (distance < 5) return 13;
        if (distance < 15) return 11;
        if (distance < 50) return 9;
        return 7;
    }

    getRelevantZones(candidateCoords, jobCoords) {
        return Object.entries(this.popularZones).filter(([name, zone]) => {
            const distanceToCandidate = this.calculateEuclideanDistance(candidateCoords, zone.center);
            const distanceToJob = this.calculateEuclideanDistance(jobCoords, zone.center);
            return distanceToCandidate < 10 || distanceToJob < 10; // Dans un rayon de 10km
        }).map(([name, zone]) => ({
            name,
            center: zone.center,
            radius: zone.radius,
            transport: zone.transport
        }));
    }

    initializeMap(visualizationData) {
        // Placeholder pour l'initialisation de la carte
        // En production, intégrer Google Maps API ou Leaflet
        console.log('Initialisation carte avec données:', visualizationData);
    }

    generateSkillSuggestions(semanticResult) {
        // Analyse des gaps de compétences pour suggestions de formation
        return [
            "Formation SAP avancée recommandée",
            "Certification secteur luxe suggérée"
        ];
    }

    handleMatchingError(candidateId, jobId, error) {
        return {
            error: true,
            message: error.message,
            candidateId,
            jobId,
            fallbackScore: 0.1
        };
    }

    renderErrorState(container, error) {
        container.innerHTML = `
            <div class="error-state">
                <h3>❌ Erreur de calcul</h3>
                <p>${error.message}</p>
            </div>
        `;
    }

    renderRecommendations(container, recommendations) {
        if (!recommendations.length) return;
        
        const recHTML = `
            <div class="recommendations">
                <h4>💡 Recommandations</h4>
                ${recommendations.map(rec => `
                    <div class="recommendation ${rec.priority}">
                        <span class="message">${rec.message}</span>
                    </div>
                `).join('')}
            </div>
        `;
        
        const recDiv = this.createElement('div', 'recommendations-container');
        recDiv.innerHTML = recHTML;
        container.appendChild(recDiv);
    }

    updateGlobalPerformanceMetrics(totalTime) {
        // Mise à jour des métriques globales de performance
        this.updatePerformanceMetrics(totalTime, false);
    }
}

// Extension pour compatibility avec NextenSemanticMatcherV2
class NextenUnifiedMatcher extends NextenGeoMatcher {
    constructor(nextenSystem, compatibilityEngine) {
        super(nextenSystem, compatibilityEngine);
        this.semanticMatcher = new NextenSemanticMatcherV2(nextenSystem);
    }

    async calculateSemanticScore(candidateData, jobData) {
        // Utilisation directe du NextenSemanticMatcherV2
        return await this.semanticMatcher.calculateCompatibility(candidateData, jobData);
    }
}

// Export pour intégration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NextenGeoMatcher, NextenUnifiedMatcher };
}

if (typeof window !== 'undefined') {
    window.NextenGeoMatcher = NextenGeoMatcher;
    window.NextenUnifiedMatcher = NextenUnifiedMatcher;
}