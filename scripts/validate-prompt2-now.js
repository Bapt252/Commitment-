#!/usr/bin/env node

/**
 * 🚀 SCRIPT DE VALIDATION IMMÉDIATE PROMPT 2
 * Exécution: node validate-prompt2-now.js
 * 
 * Tests les performances critiques en 2 minutes
 */

const WebSocket = require('ws');
const { performance } = require('perf_hooks');

// Polyfill pour fetch si node-fetch n'est pas disponible
let fetch;
try {
  fetch = require('node-fetch');
} catch (e) {
  // Fallback pour Node.js 18+
  fetch = global.fetch || require('node:fetch');
}

class Prompt2Validator {
  constructor() {
    this.results = [];
    this.startTime = Date.now();
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString().slice(11, 19);
    const icons = {
      'info': 'ℹ️',
      'success': '✅',
      'error': '❌',
      'warning': '⚠️',
      'test': '🧪'
    };
    console.log(`[${timestamp}] ${icons[type]} ${message}`);
  }

  async validateServices() {
    this.log('Validation des services...', 'test');
    
    const services = [
      { name: 'CV Parser', url: 'http://localhost:5051/health' },
      { name: 'Job Parser', url: 'http://localhost:5053/health' },
      { name: 'Matching', url: 'http://localhost:5052/health' },
      { name: 'API Gateway', url: 'http://localhost:5050/health' }
    ];

    const serviceResults = [];

    for (const service of services) {
      try {
        const startTime = performance.now();
        
        // Timeout controller pour fetch
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(service.url, { 
          signal: controller.signal,
          headers: { 'User-Agent': 'PROMPT2-Validator/1.0' }
        });
        
        clearTimeout(timeoutId);
        const responseTime = performance.now() - startTime;
        
        if (response.ok) {
          serviceResults.push({ 
            name: service.name, 
            status: 'UP', 
            responseTime: `${responseTime.toFixed(0)}ms` 
          });
          this.log(`${service.name}: UP (${responseTime.toFixed(0)}ms)`, 'success');
        } else {
          serviceResults.push({ 
            name: service.name, 
            status: 'ERROR', 
            error: `HTTP ${response.status}` 
          });
          this.log(`${service.name}: ERROR - HTTP ${response.status}`, 'error');
        }
      } catch (error) {
        serviceResults.push({ 
          name: service.name, 
          status: 'DOWN', 
          error: error.message 
        });
        this.log(`${service.name}: DOWN - ${error.message}`, 'error');
      }
    }

    this.results.push({
      test: 'Services Health Check',
      results: serviceResults,
      passed: serviceResults.every(s => s.status === 'UP')
    });

    return serviceResults.every(s => s.status === 'UP');
  }

  async validateWebSocketPerformance() {
    this.log('Test performance WebSocket (<500ms promise)...', 'test');
    
    const connectionTimes = [];
    const TARGET_MS = 500;
    const TEST_COUNT = 5;

    for (let i = 0; i < TEST_COUNT; i++) {
      try {
        const startTime = performance.now();
        const ws = new WebSocket('ws://localhost:5051');
        
        const connectionTime = await new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            ws.close();
            reject(new Error('Connection timeout'));
          }, 2000);

          ws.on('open', () => {
            const time = performance.now() - startTime;
            clearTimeout(timeout);
            ws.close();
            resolve(time);
          });

          ws.on('error', (error) => {
            clearTimeout(timeout);
            reject(error);
          });
        });

        connectionTimes.push(connectionTime);
        this.log(`Connexion ${i + 1}: ${connectionTime.toFixed(0)}ms`, 'info');
        
        // Pause entre tests
        await new Promise(resolve => setTimeout(resolve, 200));
        
      } catch (error) {
        this.log(`Connexion ${i + 1}: FAILED - ${error.message}`, 'error');
        connectionTimes.push(9999); // Valeur d'échec
      }
    }

    const avgTime = connectionTimes.reduce((a, b) => a + b) / connectionTimes.length;
    const maxTime = Math.max(...connectionTimes);
    const successRate = connectionTimes.filter(t => t < 2000).length / TEST_COUNT;

    const performanceResults = {
      avgConnectionTime: avgTime,
      maxConnectionTime: maxTime,
      successRate: successRate,
      targetMet: avgTime < TARGET_MS,
      individual: connectionTimes
    };

    this.log(`Moyenne: ${avgTime.toFixed(0)}ms | Max: ${maxTime.toFixed(0)}ms | Succès: ${(successRate * 100).toFixed(0)}%`, 'info');
    
    if (avgTime < TARGET_MS) {
      this.log(`✅ Performance WebSocket: OBJECTIF ATTEINT (<${TARGET_MS}ms)`, 'success');
    } else {
      this.log(`❌ Performance WebSocket: OBJECTIF MANQUÉ (${avgTime.toFixed(0)}ms > ${TARGET_MS}ms)`, 'error');
    }

    this.results.push({
      test: 'WebSocket Performance',
      results: performanceResults,
      passed: avgTime < TARGET_MS && successRate >= 0.8
    });

    return performanceResults;
  }

  async validateRealTimeParsing() {
    this.log('Test parsing temps réel...', 'test');
    
    try {
      const ws = new WebSocket('ws://localhost:5051');
      
      const parsingResult = await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          ws.close();
          reject(new Error('Parsing timeout (>10s)'));
        }, 10000);

        const progressUpdates = [];
        let startTime;

        ws.on('open', () => {
          startTime = performance.now();
          
          ws.on('message', (data) => {
            try {
              const message = JSON.parse(data);
              
              if (message.type === 'parsing_progress') {
                progressUpdates.push({
                  progress: message.progress,
                  stage: message.stage,
                  timestamp: Date.now()
                });
                this.log(`Progress: ${message.progress}% - ${message.stage}`, 'info');
              }
              
              if (message.type === 'parsing_completed') {
                const totalTime = performance.now() - startTime;
                clearTimeout(timeout);
                ws.close();
                resolve({
                  duration: totalTime,
                  progressUpdates: progressUpdates.length,
                  finalData: message.data
                });
              }
            } catch (parseError) {
              this.log(`Message parsing error: ${parseError.message}`, 'warning');
            }
          });

          // Envoyer demande de parsing
          ws.send(JSON.stringify({
            type: 'parse_cv',
            taskId: 'validation-test-' + Date.now(),
            fileBuffer: Buffer.from('Jean Dupont\nDéveloppeur Full Stack\njean.dupont@email.com\n+33 6 12 34 56 78').toString('base64'),
            fileName: 'test-validation.txt',
            fileType: 'text/plain'
          }));
        });

        ws.on('error', (error) => {
          clearTimeout(timeout);
          reject(error);
        });
      });

      const passed = parsingResult.duration < 5000 && parsingResult.progressUpdates > 0;
      
      this.log(`Parsing terminé: ${(parsingResult.duration / 1000).toFixed(2)}s | ${parsingResult.progressUpdates} updates`, 'info');
      
      if (passed) {
        this.log('✅ Parsing temps réel: FONCTIONNEL', 'success');
      } else {
        this.log('❌ Parsing temps réel: PROBLÈMES DÉTECTÉS', 'error');
      }

      this.results.push({
        test: 'Real-time Parsing',
        results: parsingResult,
        passed: passed
      });

      return parsingResult;
      
    } catch (error) {
      this.log(`Parsing failed: ${error.message}`, 'error');
      
      this.results.push({
        test: 'Real-time Parsing',
        results: { error: error.message },
        passed: false
      });
      
      return null;
    }
  }

  async validateConcurrentLoad() {
    this.log('Test charge concurrent (10 connexions)...', 'test');
    
    const CONCURRENT_COUNT = 10;
    const connectionPromises = [];

    for (let i = 0; i < CONCURRENT_COUNT; i++) {
      connectionPromises.push(this.testSingleConnection(i));
    }

    try {
      const results = await Promise.allSettled(connectionPromises);
      
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;
      const successRate = successful / CONCURRENT_COUNT;

      const times = results
        .filter(r => r.status === 'fulfilled')
        .map(r => r.value);

      const avgTime = times.length > 0 ? times.reduce((a, b) => a + b) / times.length : 0;

      this.log(`Charge concurrent: ${successful}/${CONCURRENT_COUNT} succès (${(successRate * 100).toFixed(0)}%)`, 'info');
      this.log(`Temps moyen: ${avgTime.toFixed(0)}ms`, 'info');

      const passed = successRate >= 0.8 && avgTime < 1000;
      
      if (passed) {
        this.log('✅ Test de charge: RÉUSSI', 'success');
      } else {
        this.log('❌ Test de charge: PROBLÈMES DE SCALABILITÉ', 'error');
      }

      this.results.push({
        test: 'Concurrent Load',
        results: {
          totalConnections: CONCURRENT_COUNT,
          successful: successful,
          failed: failed,
          successRate: successRate,
          avgTime: avgTime
        },
        passed: passed
      });

      return { successful, failed, successRate, avgTime };
      
    } catch (error) {
      this.log(`Load test failed: ${error.message}`, 'error');
      return null;
    }
  }

  async testSingleConnection(index) {
    const startTime = performance.now();
    const ws = new WebSocket('ws://localhost:5051');
    
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        ws.close();
        reject(new Error(`Connection ${index} timeout`));
      }, 3000);

      ws.on('open', () => {
        const connectionTime = performance.now() - startTime;
        clearTimeout(timeout);
        ws.close();
        resolve(connectionTime);
      });

      ws.on('error', (error) => {
        clearTimeout(timeout);
        reject(error);
      });
    });
  }

  generateReport() {
    const totalTime = (Date.now() - this.startTime) / 1000;
    
    console.log('\n' + '='.repeat(60));
    console.log('📊 RAPPORT DE VALIDATION PROMPT 2');
    console.log('='.repeat(60));
    
    this.results.forEach((result, index) => {
      const status = result.passed ? '✅ PASS' : '❌ FAIL';
      console.log(`${index + 1}. ${result.test}: ${status}`);
    });

    const passedTests = this.results.filter(r => r.passed).length;
    const totalTests = this.results.length;
    const overallScore = (passedTests / totalTests * 100).toFixed(0);

    console.log('\n' + '-'.repeat(40));
    console.log(`📈 Score global: ${passedTests}/${totalTests} (${overallScore}%)`);
    console.log(`⏱️  Temps total: ${totalTime.toFixed(1)}s`);
    
    if (passedTests === totalTests) {
      console.log('🎉 PROMPT 2 - PRÊT POUR PRODUCTION !');
    } else if (passedTests >= totalTests * 0.8) {
      console.log('⚠️  PROMPT 2 - NÉCESSITE DES AJUSTEMENTS');
    } else {
      console.log('🚨 PROMPT 2 - PROBLÈMES CRITIQUES DÉTECTÉS');
    }

    console.log('\n' + '='.repeat(60));

    // Sauvegarde rapport détaillé
    const detailedReport = {
      timestamp: new Date().toISOString(),
      totalTime: totalTime,
      score: overallScore,
      passed: passedTests,
      total: totalTests,
      tests: this.results
    };

    try {
      const fs = require('fs');
      if (!fs.existsSync('test-results')) {
        fs.mkdirSync('test-results');
      }
      fs.writeFileSync(
        `test-results/prompt2-validation-${Date.now()}.json`,
        JSON.stringify(detailedReport, null, 2)
      );
      console.log('💾 Rapport détaillé sauvegardé dans test-results/');
    } catch (error) {
      console.log('⚠️  Impossible de sauvegarder le rapport');
    }

    return { passed: passedTests, total: totalTests, score: overallScore };
  }

  async runFullValidation() {
    console.log('🚀 DÉMARRAGE VALIDATION PROMPT 2\n');
    
    try {
      // 1. Services Health Check
      await this.validateServices();
      
      // 2. WebSocket Performance  
      await this.validateWebSocketPerformance();
      
      // 3. Real-time Parsing
      await this.validateRealTimeParsing();
      
      // 4. Concurrent Load
      await this.validateConcurrentLoad();
      
      // 5. Rapport final
      const summary = this.generateReport();
      
      return summary;
      
    } catch (error) {
      this.log(`Validation failed: ${error.message}`, 'error');
      throw error;
    }
  }
}

// Script principal
async function main() {
  const validator = new Prompt2Validator();
  
  try {
    const summary = await validator.runFullValidation();
    
    // Exit code basé sur les résultats
    const exitCode = summary.passed === summary.total ? 0 : 1;
    process.exit(exitCode);
    
  } catch (error) {
    console.error('❌ Validation échouée:', error.message);
    process.exit(1);
  }
}

// Exécution si script lancé directement
if (require.main === module) {
  main();
}

module.exports = { Prompt2Validator };
