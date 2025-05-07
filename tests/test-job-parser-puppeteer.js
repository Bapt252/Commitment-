/**
 * Script de test Puppeteer pour le job parser
 * 
 * Ce script permet de tester automatiquement l'interface du job parser
 * en simulant les actions d'un utilisateur.
 * 
 * Installation: npm install puppeteer
 * Exécution: node test-job-parser-puppeteer.js
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Configuration
const config = {
  // URL de la page à tester (locale ou hébergée)
  url: 'http://localhost:3000/templates/client-questionnaire.html',
  // Chemin vers le fichier PDF à tester (relatif à ce script)
  pdfPath: '../fichedeposte.pdf',
  // Mode headless (false pour voir le navigateur, true pour le cacher)
  headless: false,
  // Délai en ms pour les actions (augmenter en cas de problème)
  delay: 1000,
  // Temps d'attente après chargement de la page (ms)
  loadDelay: 3000,
  // Temps d'attente après l'ouverture du modal (ms)
  modalLoadDelay: 2000,
  // Temps d'attente après la soumission du formulaire (ms)
  formSubmitDelay: 5000
};

// Fonction principale de test
async function testJobParser() {
  console.log('Démarrage du test du job parser...');
  
  // Vérifier si le fichier PDF existe
  const pdfAbsolutePath = path.resolve(__dirname, config.pdfPath);
  if (!fs.existsSync(pdfAbsolutePath)) {
    console.error(`Erreur: Le fichier ${pdfAbsolutePath} n'existe pas.`);
    console.log('Vous devez placer votre fichier "fichedeposte.pdf" dans le répertoire racine du projet.');
    process.exit(1);
  }
  
  // Lancer un navigateur
  const browser = await puppeteer.launch({ 
    headless: config.headless,
    defaultViewport: null, // Taille de fenêtre automatique
    args: ['--start-maximized'], // Démarrer en plein écran
    slowMo: 50 // Ralentir les actions pour mieux voir
  });
  
  try {
    const page = await browser.newPage();
    
    // Activer la journalisation des consoles et des erreurs
    page.on('console', msg => console.log('Page Console:', msg.text()));
    page.on('pageerror', error => console.error('Page Error:', error.message));
    
    // Intercepter les requêtes réseau
    await page.setRequestInterception(true);
    page.on('request', request => {
      if (request.url().includes('localhost:5054')) {
        console.log('Requête API détectée:', request.url());
      }
      request.continue();
    });
    
    // Naviguer vers la page
    console.log(`Navigation vers ${config.url}...`);
    await page.goto(config.url, { waitUntil: 'networkidle2' });
    console.log('Page chargée');
    
    // Attendre que la page soit complètement chargée
    await page.waitForTimeout(config.loadDelay);
    
    // Capturer une capture d'écran initiale
    await page.screenshot({ path: 'test-initial.png' });
    
    // Vérifier si le bouton radio "Oui" est présent et le sélectionner
    console.log('Sélection de l\'option "Oui"...');
    const radioSelector = 'input[name="has-position"][value="yes"]';
    
    if (await page.$(radioSelector) !== null) {
      await page.click(radioSelector);
      console.log('Option "Oui" sélectionnée');
      
      // Attendre que les éléments conditionnels apparaissent
      await page.waitForTimeout(config.delay);
    } else {
      console.warn('Bouton radio "Oui" non trouvé');
    }
    
    // Cliquer sur le bouton "Analyser ma fiche de poste"
    console.log('Clic sur "Analyser ma fiche de poste"...');
    const analyzeButtonSelector = '#open-job-parser';
    
    if (await page.$(analyzeButtonSelector) !== null) {
      await page.click(analyzeButtonSelector);
      console.log('Bouton cliqué');
      
      // Attendre que le modal s'ouvre
      await page.waitForTimeout(config.modalLoadDelay);
      
      // Capturer une capture d'écran du modal
      await page.screenshot({ path: 'test-modal-open.png' });
      
      // Vérifier si le modal est bien ouvert
      const modalSelector = '#job-parser-modal.active';
      if (await page.$(modalSelector) !== null) {
        console.log('Modal correctement ouvert');
        
        // Maintenant, nous devons interagir avec l'iframe
        // Récupérer l'iframe
        const frameElement = await page.$('iframe.modal-iframe');
        if (frameElement) {
          // Attendre que l'iframe soit chargée
          console.log('Attente du chargement de l\'iframe...');
          
          // Attendre encore un peu
          await page.waitForTimeout(config.delay);
          
          // Récupérer le frame
          const frame = page.frames().find(f => f.name() === 'job-parser-iframe') || 
                       (await frameElement.contentFrame());
          
          if (frame) {
            console.log('Iframe récupérée, test des éléments...');
            
            // Trouver le sélecteur de fichier dans l'iframe
            const fileInputSelector = '#file-input';
            const fileInput = await frame.$(fileInputSelector);
            
            if (fileInput) {
              console.log(`Chargement du fichier ${pdfAbsolutePath}...`);
              
              // Télécharger le fichier
              await fileInput.uploadFile(pdfAbsolutePath);
              console.log('Fichier téléchargé avec succès');
              
              // Attendre un moment
              await page.waitForTimeout(config.delay);
              
              // Trouver et cliquer sur le bouton d'analyse
              const analyseButtonSelector = '#analyse-button';
              const analyseButton = await frame.$(analyseButtonSelector);
              
              if (analyseButton) {
                console.log('Clic sur le bouton d\'analyse...');
                await analyseButton.click();
                
                // Attendre le traitement
                console.log(`Attente du traitement pendant ${config.formSubmitDelay}ms...`);
                await page.waitForTimeout(config.formSubmitDelay);
                
                // Capturer une capture d'écran après le traitement
                await page.screenshot({ path: 'test-after-processing.png' });
                
                // Vérifier si les résultats sont affichés dans l'iframe
                const resultSectionSelector = '#result-section';
                const resultSection = await frame.$(resultSectionSelector);
                
                if (resultSection) {
                  console.log('Résultats affichés dans l\'iframe');
                  
                  // Prendre une capture d'écran des résultats
                  const resultBoundingBox = await resultSection.boundingBox();
                  if (resultBoundingBox) {
                    await page.screenshot({
                      path: 'test-results.png',
                      clip: {
                        x: resultBoundingBox.x,
                        y: resultBoundingBox.y,
                        width: resultBoundingBox.width,
                        height: resultBoundingBox.height
                      }
                    });
                  }
                  
                  // Chercher le bouton d'application
                  const applyButtonSelector = '#apply-results';
                  const applyButton = await frame.$(applyButtonSelector);
                  
                  if (applyButton) {
                    console.log('Clic sur le bouton "Appliquer ces informations"...');
                    await applyButton.click();
                    
                    // Attendre la fermeture du modal
                    await page.waitForTimeout(config.delay);
                    
                    // Vérifier si les données ont été appliquées dans la page principale
                    const jobInfoContainerSelector = '#job-info-container';
                    if (await page.$(jobInfoContainerSelector) !== null) {
                      console.log('Les informations ont été correctement appliquées à la page principale');
                      
                      // Capturer une capture d'écran finale
                      await page.screenshot({ path: 'test-final.png' });
                    } else {
                      console.error('Les informations n\'ont pas été appliquées à la page principale');
                    }
                  } else {
                    console.error('Bouton "Appliquer ces informations" non trouvé');
                  }
                } else {
                  console.error('Résultats non affichés dans l\'iframe');
                }
              } else {
                console.error('Bouton d\'analyse non trouvé dans l\'iframe');
              }
            } else {
              console.error('Sélecteur de fichier non trouvé dans l\'iframe');
            }
          } else {
            console.error('Impossible d\'accéder au contenu de l\'iframe');
          }
        } else {
          console.error('Iframe non trouvée');
        }
      } else {
        console.error('Le modal ne s\'est pas ouvert correctement');
      }
    } else {
      console.error('Bouton "Analyser ma fiche de poste" non trouvé');
    }
  } catch (error) {
    console.error('Erreur pendant le test:', error);
    
    // Capturer une capture d'écran en cas d'erreur
    try {
      const page = (await browser.pages())[0];
      await page.screenshot({ path: 'test-error.png' });
    } catch (screenshotError) {
      console.error('Impossible de prendre une capture d\'écran:', screenshotError);
    }
  } finally {
    // Fermer le navigateur
    await browser.close();
    console.log('Test terminé');
  }
}

// Exécuter le test
testJobParser().catch(error => {
  console.error('Erreur fatale:', error);
  process.exit(1);
});
