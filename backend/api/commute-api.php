<?php
/**
 * NEXTEN COMMUTE API - BACKEND OPTIMISÉ GOOGLE MAPS
 * Gestion intelligente des appels Distance Matrix API avec cache Redis
 * Optimisation des coûts et rate limiting
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Gestion des requêtes OPTIONS (CORS)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

class NextenCommuteAPI {
    private $redis;
    private $googleApiKey;
    private $config;
    private $metrics;

    public function __construct() {
        $this->initializeConfig();
        $this->initializeRedis();
        $this->initializeMetrics();
    }

    /**
     * CONFIGURATION API
     */
    private function initializeConfig() {
        $this->config = [
            'google_maps' => [
                'base_url' => 'https://maps.googleapis.com/maps/api/distancematrix/json',
                'max_elements_per_request' => 625, // 25x25 matrice
                'rate_limit_per_minute' => 100,
                'cost_per_element' => 0.005 // 0.5€ per 100 elements
            ],
            'cache' => [
                'ttl_exact' => 24 * 3600,        // 24h pour cache exact
                'ttl_pattern' => 7 * 24 * 3600,  // 7 jours pour patterns
                'ttl_approx' => 30 * 24 * 3600,  // 30 jours pour approximations
                'max_size' => 100000              // Limite taille cache
            ],
            'performance' => [
                'target_response_time' => 150,    // < 150ms objectif
                'batch_size_optimal' => 25,       // Taille batch optimale
                'retry_attempts' => 3             // Tentatives en cas d'erreur
            ]
        ];

        // Récupération clé API depuis variables d'environnement
        $this->googleApiKey = $_ENV['GOOGLE_MAPS_API_KEY'] ?? $this->getApiKeyFromConfig();
    }

    /**
     * INITIALISATION REDIS
     */
    private function initializeRedis() {
        try {
            $this->redis = new Redis();
            $redisHost = $_ENV['REDIS_HOST'] ?? 'localhost';
            $redisPort = $_ENV['REDIS_PORT'] ?? 6379;
            $redisPassword = $_ENV['REDIS_PASSWORD'] ?? null;
            
            $this->redis->connect($redisHost, $redisPort);
            
            if ($redisPassword) {
                $this->redis->auth($redisPassword);
            }
            
            // Test de connexion
            $this->redis->ping();
            
        } catch (Exception $e) {
            error_log("Erreur connexion Redis: " . $e->getMessage());
            $this->redis = null; // Fallback sans cache
        }
    }

    /**
     * INITIALISATION MÉTRIQUES
     */
    private function initializeMetrics() {
        $this->metrics = [
            'requests_total' => 0,
            'cache_hits' => 0,
            'api_calls' => 0,
            'cost_tracking' => 0.0,
            'average_response_time' => 0,
            'errors' => 0
        ];
    }

    /**
     * ENDPOINT PRINCIPAL - CALCUL TRAJET
     */
    public function calculateCommute() {
        $startTime = microtime(true);
        
        try {
            // Validation et parsing des données
            $input = $this->validateInput();
            
            // Vérification rate limiting
            if (!$this->checkRateLimit()) {
                return $this->errorResponse(429, 'Rate limit exceeded');
            }
            
            // Tentative récupération cache
            $cacheResult = $this->tryGetFromCache($input);
            if ($cacheResult) {
                $this->updateMetrics($startTime, true);
                return $this->successResponse($cacheResult, 'cache');
            }
            
            // Appel API Google Maps
            $apiResult = $this->callGoogleMapsAPI($input);
            
            // Calcul du scoring
            $scoredResult = $this->calculateScoringAPI($apiResult, $input);
            
            // Mise en cache
            $this->storeInCache($input, $scoredResult);
            
            // Métriques et réponse
            $this->updateMetrics($startTime, false);
            return $this->successResponse($scoredResult, 'api');
            
        } catch (Exception $e) {
            $this->metrics['errors']++;
            error_log("Erreur calculate commute: " . $e->getMessage());
            return $this->errorResponse(500, $e->getMessage());
        }
    }

    /**
     * ENDPOINT BATCH - CALCULS MULTIPLES
     */
    public function calculateBatchCommute() {
        $startTime = microtime(true);
        
        try {
            $input = $this->validateBatchInput();
            
            // Optimisation: grouper les requêtes par proximité géographique
            $batches = $this->optimizeBatches($input);
            $results = [];
            
            foreach ($batches as $batch) {
                $batchResult = $this->processBatch($batch);
                $results = array_merge($results, $batchResult);
            }
            
            $this->updateMetrics($startTime, false);
            return $this->successResponse($results, 'batch');
            
        } catch (Exception $e) {
            $this->metrics['errors']++;
            return $this->errorResponse(500, $e->getMessage());
        }
    }

    /**
     * VALIDATION INPUT
     */
    private function validateInput() {
        $rawInput = file_get_contents('php://input');
        $input = json_decode($rawInput, true);
        
        if (!$input) {
            throw new Exception('Invalid JSON input');
        }
        
        // Validation des champs requis
        $required = ['candidate_location', 'job_location'];
        foreach ($required as $field) {
            if (!isset($input[$field])) {
                throw new Exception("Missing required field: $field");
            }
        }
        
        // Validation coordonnées
        $this->validateCoordinates($input['candidate_location']);
        $this->validateCoordinates($input['job_location']);
        
        return $input;
    }

    private function validateCoordinates($location) {
        if (!isset($location['coordinates']) || 
            !isset($location['coordinates']['lat']) || 
            !isset($location['coordinates']['lng'])) {
            throw new Exception('Invalid coordinates format');
        }
        
        $lat = $location['coordinates']['lat'];
        $lng = $location['coordinates']['lng'];
        
        if (!is_numeric($lat) || !is_numeric($lng) || 
            $lat < -90 || $lat > 90 || $lng < -180 || $lng > 180) {
            throw new Exception('Invalid coordinate values');
        }
    }

    /**
     * GESTION CACHE REDIS INTELLIGENT
     */
    private function tryGetFromCache($input) {
        if (!$this->redis) {
            return null;
        }
        
        try {
            // Cache Level 1: Exact match
            $exactKey = $this->generateCacheKey($input, 'exact');
            $cached = $this->redis->get($exactKey);
            
            if ($cached) {
                $this->metrics['cache_hits']++;
                return json_decode($cached, true);
            }
            
            // Cache Level 2: Pattern géographique
            $patternKey = $this->generateCacheKey($input, 'pattern');
            $cached = $this->redis->get($patternKey);
            
            if ($cached) {
                $this->metrics['cache_hits']++;
                $data = json_decode($cached, true);
                $data['cache_level'] = 2;
                return $data;
            }
            
            // Cache Level 3: Approximation géographique
            $approxData = $this->findApproximateMatch($input);
            if ($approxData) {
                $this->metrics['cache_hits']++;
                $approxData['cache_level'] = 3;
                return $approxData;
            }
            
            return null;
            
        } catch (Exception $e) {
            error_log("Erreur cache Redis: " . $e->getMessage());
            return null;
        }
    }

    private function storeInCache($input, $result) {
        if (!$this->redis) {
            return;
        }
        
        try {
            $exactKey = $this->generateCacheKey($input, 'exact');
            $patternKey = $this->generateCacheKey($input, 'pattern');
            
            $cacheData = json_encode($result);
            
            // Cache exact (24h)
            $this->redis->setex($exactKey, $this->config['cache']['ttl_exact'], $cacheData);
            
            // Cache pattern (7 jours)
            $this->redis->setex($patternKey, $this->config['cache']['ttl_pattern'], $cacheData);
            
            // Nettoyage cache si nécessaire
            $this->cleanupCacheIfNeeded();
            
        } catch (Exception $e) {
            error_log("Erreur stockage cache: " . $e->getMessage());
        }
    }

    /**
     * APPEL API GOOGLE MAPS OPTIMISÉ
     */
    private function callGoogleMapsAPI($input) {
        if (!$this->googleApiKey) {
            throw new Exception('Google Maps API key not configured');
        }
        
        $this->metrics['api_calls']++;
        
        $candidate = $input['candidate_location']['coordinates'];
        $job = $input['job_location']['coordinates'];
        
        // Modes de transport à tester
        $modes = $input['transport_modes'] ?? ['driving', 'transit', 'walking', 'bicycling'];
        $results = [];
        
        foreach ($modes as $mode) {
            $apiResult = $this->singleModeAPICall($candidate, $job, $mode, $input);
            $results[$mode] = $apiResult;
            
            // Tracking des coûts
            $this->metrics['cost_tracking'] += $this->config['google_maps']['cost_per_element'];
        }
        
        return $results;
    }

    private function singleModeAPICall($origin, $destination, $mode, $input) {
        $originStr = $origin['lat'] . ',' . $origin['lng'];
        $destinationStr = $destination['lat'] . ',' . $destination['lng'];
        
        // Heure de départ (par défaut 8h du matin)
        $departureTime = $input['departure_time'] ?? time() + 3600; // +1h
        
        $params = [
            'origins' => $originStr,
            'destinations' => $destinationStr,
            'mode' => $mode,
            'departure_time' => $departureTime,
            'traffic_model' => 'best_guess',
            'key' => $this->googleApiKey
        ];
        
        if ($mode === 'transit') {
            $params['transit_mode'] = 'bus|subway|train|tram';
            $params['transit_routing_preference'] = 'less_walking';
        }
        
        $url = $this->config['google_maps']['base_url'] . '?' . http_build_query($params);
        
        // Appel avec retry logic
        return $this->apiCallWithRetry($url);
    }

    private function apiCallWithRetry($url, $attempt = 1) {
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10,
            CURLOPT_USERAGENT => 'Nexten Commute Optimizer/1.0',
            CURLOPT_SSL_VERIFYPEER => false
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error || $httpCode !== 200) {
            if ($attempt < $this->config['performance']['retry_attempts']) {
                sleep(1); // Attente avant retry
                return $this->apiCallWithRetry($url, $attempt + 1);
            }
            throw new Exception("API call failed: $error (HTTP $httpCode)");
        }
        
        $data = json_decode($response, true);
        
        if ($data['status'] !== 'OK') {
            throw new Exception("Google Maps API error: " . $data['status']);
        }
        
        return $data;
    }

    /**
     * CALCUL SCORING BACKEND
     */
    private function calculateScoringAPI($apiResults, $input) {
        $scores = [];
        $bestScore = 0;
        $bestMode = '';
        
        foreach ($apiResults as $mode => $data) {
            if (!isset($data['rows'][0]['elements'][0]) || 
                $data['rows'][0]['elements'][0]['status'] !== 'OK') {
                continue;
            }
            
            $element = $data['rows'][0]['elements'][0];
            $durationSeconds = $element['duration']['value'];
            $durationMinutes = $durationSeconds / 60;
            
            // Score basé sur la durée
            $durationScore = $this->calculateDurationScore($durationMinutes);
            
            // Score facilité transport
            $easeScore = $this->calculateTransportEaseScore($mode, $element);
            
            // Score coût
            $costScore = $this->calculateCostScore($mode, $durationMinutes);
            
            // Bonus préférences
            $preferencesBonus = $this->calculatePreferencesBonus(
                $mode, 
                $input['candidate_location']['preferences'] ?? []
            );
            
            // Score composite
            $compositeScore = (
                $durationScore * 0.40 +
                $easeScore * 0.30 +
                $costScore * 0.20 +
                $preferencesBonus * 0.10
            );
            
            $scores[$mode] = [
                'score' => $compositeScore,
                'duration_minutes' => $durationMinutes,
                'duration_text' => $element['duration']['text'],
                'distance_text' => $element['distance']['text'],
                'breakdown' => [
                    'duration' => $durationScore,
                    'ease' => $easeScore,
                    'cost' => $costScore,
                    'preferences' => $preferencesBonus
                ]
            ];
            
            if ($compositeScore > $bestScore) {
                $bestScore = $compositeScore;
                $bestMode = $mode;
            }
        }
        
        return [
            'final_score' => $bestScore,
            'best_mode' => $bestMode,
            'breakdown' => $scores,
            'metadata' => [
                'calculated_at' => date('Y-m-d H:i:s'),
                'api_version' => '2.0',
                'cache_level' => 0 // Direct API call
            ]
        ];
    }

    private function calculateDurationScore($durationMinutes) {
        if ($durationMinutes <= 30) return 1.0;
        if ($durationMinutes <= 45) return 0.8 + (30 - $durationMinutes) / 15 * 0.2;
        if ($durationMinutes <= 60) return 0.6 + (45 - $durationMinutes) / 15 * 0.2;
        if ($durationMinutes <= 90) return 0.2 + (60 - $durationMinutes) / 30 * 0.4;
        
        return max(0.1, 0.2 - ($durationMinutes - 90) / 60 * 0.1);
    }

    private function calculateTransportEaseScore($mode, $element) {
        $baseScore = 0.8;
        
        $modeMultipliers = [
            'transit' => 0.9,
            'driving' => 0.85,
            'bicycling' => 0.75,
            'walking' => 0.7
        ];
        
        return $baseScore * ($modeMultipliers[$mode] ?? 0.8);
    }

    private function calculateCostScore($mode, $durationMinutes) {
        $costs = [
            'transit' => 1.90,
            'driving' => $durationMinutes * 0.15,
            'walking' => 0,
            'bicycling' => 0.10
        ];
        
        $cost = $costs[$mode] ?? 2.0;
        return max(0.1, 1.0 - ($cost / 10));
    }

    private function calculatePreferencesBonus($mode, $preferences) {
        if (empty($preferences)) {
            return 0.5;
        }
        
        $modeKeywords = [
            'driving' => ['voiture', 'vehicule', 'conduite', 'parking'],
            'transit' => ['metro', 'bus', 'tramway', 'transport_public', 'rer'],
            'walking' => ['marche', 'pied', 'walking'],
            'bicycling' => ['velo', 'bicyclette', 'cyclisme', 'bike']
        ];
        
        $keywords = $modeKeywords[$mode] ?? [];
        
        foreach ($preferences as $pref) {
            foreach ($keywords as $keyword) {
                if (stripos($pref, $keyword) !== false) {
                    return 1.0;
                }
            }
        }
        
        return 0.3;
    }

    /**
     * ENDPOINTS MÉTRIQUES ET MONITORING
     */
    public function getMetrics() {
        return $this->successResponse([
            'metrics' => $this->metrics,
            'cache_stats' => $this->getCacheStats(),
            'system_info' => $this->getSystemInfo()
        ]);
    }

    private function getCacheStats() {
        if (!$this->redis) {
            return ['status' => 'disabled'];
        }
        
        try {
            $info = $this->redis->info('memory');
            return [
                'status' => 'active',
                'memory_usage' => $info['used_memory_human'] ?? 'unknown',
                'keys_count' => $this->redis->dbSize(),
                'hit_rate' => $this->metrics['requests_total'] > 0 ? 
                    round($this->metrics['cache_hits'] / $this->metrics['requests_total'] * 100, 2) : 0
            ];
        } catch (Exception $e) {
            return ['status' => 'error', 'message' => $e->getMessage()];
        }
    }

    /**
     * UTILITAIRES
     */
    private function generateCacheKey($input, $type) {
        $candidate = $input['candidate_location']['coordinates'];
        $job = $input['job_location']['coordinates'];
        
        $key = sprintf(
            'nexten_commute_%s_%s_%s_%s_%s',
            $type,
            round($candidate['lat'], 4),
            round($candidate['lng'], 4),
            round($job['lat'], 4),
            round($job['lng'], 4)
        );
        
        return $key;
    }

    private function checkRateLimit() {
        if (!$this->redis) {
            return true; // Pas de rate limiting sans Redis
        }
        
        $clientIp = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
        $rateLimitKey = "rate_limit_$clientIp";
        
        $current = $this->redis->incr($rateLimitKey);
        
        if ($current === 1) {
            $this->redis->expire($rateLimitKey, 60); // 1 minute
        }
        
        return $current <= $this->config['google_maps']['rate_limit_per_minute'];
    }

    private function updateMetrics($startTime, $wasCacheHit) {
        $this->metrics['requests_total']++;
        
        if ($wasCacheHit) {
            $this->metrics['cache_hits']++;
        }
        
        $responseTime = (microtime(true) - $startTime) * 1000; // en ms
        $this->metrics['average_response_time'] = 
            (($this->metrics['average_response_time'] * ($this->metrics['requests_total'] - 1)) + $responseTime) 
            / $this->metrics['requests_total'];
    }

    private function successResponse($data, $source = 'api') {
        http_response_code(200);
        echo json_encode([
            'success' => true,
            'data' => $data,
            'source' => $source,
            'timestamp' => time()
        ]);
        exit;
    }

    private function errorResponse($code, $message) {
        http_response_code($code);
        echo json_encode([
            'success' => false,
            'error' => $message,
            'timestamp' => time()
        ]);
        exit;
    }

    private function getApiKeyFromConfig() {
        // En production, stocker dans un fichier de config sécurisé
        // ou variables d'environnement
        return 'YOUR_GOOGLE_MAPS_API_KEY_HERE';
    }

    private function getSystemInfo() {
        return [
            'php_version' => PHP_VERSION,
            'memory_usage' => memory_get_usage(true),
            'memory_peak' => memory_get_peak_usage(true),
            'server_time' => date('Y-m-d H:i:s'),
            'api_version' => '2.0.0'
        ];
    }

    private function findApproximateMatch($input) {
        // TODO: Implémenter recherche approximative dans le cache
        return null;
    }

    private function cleanupCacheIfNeeded() {
        // TODO: Implémenter nettoyage cache intelligent
    }

    private function validateBatchInput() {
        // TODO: Validation pour requêtes batch
        return [];
    }

    private function optimizeBatches($input) {
        // TODO: Optimisation batches géographiques
        return [$input];
    }

    private function processBatch($batch) {
        // TODO: Traitement batch optimisé
        return [];
    }
}

// ROUTEUR PRINCIPAL
try {
    $api = new NextenCommuteAPI();
    
    $endpoint = $_GET['endpoint'] ?? '';
    
    switch ($endpoint) {
        case 'calculate':
            $api->calculateCommute();
            break;
            
        case 'batch':
            $api->calculateBatchCommute();
            break;
            
        case 'metrics':
            $api->getMetrics();
            break;
            
        default:
            http_response_code(404);
            echo json_encode([
                'success' => false,
                'error' => 'Endpoint not found',
                'available_endpoints' => ['calculate', 'batch', 'metrics']
            ]);
    }
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Internal server error: ' . $e->getMessage()
    ]);
}
?>