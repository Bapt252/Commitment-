import React, { useState } from 'react';
import Head from 'next/head';
import CVUploader from '../components/CVUploader';
import CVViewer from '../components/CVViewer';
import { CVData } from '../types/CVData';

const CVParserPage: React.FC = () => {
  const [parsedData, setParsedData] = useState<CVData | null>(null);

  const handleCVParsed = (data: CVData) => {
    setParsedData(data);
    
    // Scroll to the results section
    setTimeout(() => {
      document.getElementById('cv-results')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className="cv-parser-page">
      <Head>
        <title>Analyseur de CV - Commitment</title>
        <meta name="description" content="Analysez votre CV en quelques secondes grâce à notre outil d'extraction intelligent" />
      </Head>

      <header className="header">
        <div className="container">
          <h1>Analyseur de CV</h1>
          <p className="subtitle">
            Téléchargez votre CV pour extraire automatiquement vos compétences, expériences et formations
          </p>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <section className="uploader-section">
            <h2>Téléchargez votre CV</h2>
            <p className="description">
              Notre système analyse votre CV et extrait les informations pertinentes pour une meilleure compréhension de votre profil.
              Formats supportés: PDF, DOC, DOCX, TXT.
            </p>
            
            <CVUploader onCVParsed={handleCVParsed} />
          </section>

          {parsedData && (
            <section id="cv-results" className="results-section">
              <h2>Résultats de l'analyse</h2>
              <div className="results-container">
                <CVViewer data={parsedData} />
                
                <div className="actions">
                  <button 
                    className="edit-button"
                    onClick={() => {
                      // Ici vous pourriez implémenter la logique pour modifier les données
                      alert('Fonctionnalité de modification à implémenter');
                    }}
                  >
                    Modifier les données
                  </button>
                  
                  <button 
                    className="save-button"
                    onClick={() => {
                      // Ici vous pourriez implémenter la logique pour sauvegarder les données
                      const dataStr = JSON.stringify(parsedData, null, 2);
                      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                      
                      const exportFileDefaultName = 'cv-data.json';
                      
                      const linkElement = document.createElement('a');
                      linkElement.setAttribute('href', dataUri);
                      linkElement.setAttribute('download', exportFileDefaultName);
                      linkElement.click();
                    }}
                  >
                    Télécharger en JSON
                  </button>
                  
                  <button 
                    className="reset-button"
                    onClick={() => setParsedData(null)}
                  >
                    Réinitialiser
                  </button>
                </div>
              </div>
            </section>
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; {new Date().getFullYear()} Commitment - Tous droits réservés</p>
        </div>
      </footer>

      <style jsx>{`
        .cv-parser-page {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }
        
        .header {
          background-color: #2c3e50;
          color: white;
          padding: 40px 0;
          text-align: center;
        }
        
        .header h1 {
          font-size: 32px;
          margin-bottom: 10px;
        }
        
        .subtitle {
          font-size: 18px;
          opacity: 0.9;
        }
        
        .main {
          flex: 1;
          padding: 40px 0;
          background-color: #f5f7fa;
        }
        
        .uploader-section, .results-section {
          margin-bottom: 40px;
          background-color: white;
          border-radius: 8px;
          padding: 30px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .uploader-section h2, .results-section h2 {
          font-size: 24px;
          color: #2c3e50;
          margin-bottom: 15px;
        }
        
        .description {
          color: #666;
          margin-bottom: 20px;
        }
        
        .results-container {
          margin-top: 20px;
        }
        
        .actions {
          margin-top: 30px;
          display: flex;
          gap: 15px;
          justify-content: center;
          flex-wrap: wrap;
        }
        
        .edit-button, .save-button, .reset-button {
          padding: 10px 20px;
          border-radius: 4px;
          font-size: 16px;
          cursor: pointer;
          border: none;
          transition: background-color 0.3s;
        }
        
        .edit-button {
          background-color: #3498db;
          color: white;
        }
        
        .edit-button:hover {
          background-color: #2980b9;
        }
        
        .save-button {
          background-color: #2ecc71;
          color: white;
        }
        
        .save-button:hover {
          background-color: #27ae60;
        }
        
        .reset-button {
          background-color: #e74c3c;
          color: white;
        }
        
        .reset-button:hover {
          background-color: #c0392b;
        }
        
        .footer {
          background-color: #34495e;
          color: white;
          padding: 20px 0;
          text-align: center;
        }
      `}</style>
    </div>
  );
};

export default CVParserPage;
