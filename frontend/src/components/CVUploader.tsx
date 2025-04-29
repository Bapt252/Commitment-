import React, { useState, useRef, useEffect } from 'react';
import { cvParserService } from '../services/cvParserService';
import { CVData, JobStatus, JobStatusResponse } from '../types/CVData';

interface CVUploaderProps {
  onCVParsed?: (data: CVData) => void;
}

const CVUploader: React.FC<CVUploaderProps> = ({ onCVParsed }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [parsedData, setParsedData] = useState<CVData | null>(null);
  const [useAsyncParsing, setUseAsyncParsing] = useState<boolean>(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const statusCheckInterval = useRef<NodeJS.Timeout | null>(null);

  // Nettoyer l'intervalle quand le composant est démonté
  useEffect(() => {
    return () => {
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current);
      }
    };
  }, []);

  // Vérifier régulièrement l'état du job si un jobId existe
  useEffect(() => {
    if (jobId && useAsyncParsing) {
      statusCheckInterval.current = setInterval(async () => {
        try {
          const status = await cvParserService.checkJobStatus(jobId);
          setJobStatus(status);
          
          if (status.status === 'completed') {
            const result = await cvParserService.getJobResult(jobId);
            setParsedData(result);
            if (onCVParsed) onCVParsed(result);
            
            if (statusCheckInterval.current) {
              clearInterval(statusCheckInterval.current);
              statusCheckInterval.current = null;
            }
            setIsLoading(false);
          } else if (status.status === 'failed') {
            setError('Le parsing du CV a échoué. Veuillez réessayer.');
            if (statusCheckInterval.current) {
              clearInterval(statusCheckInterval.current);
              statusCheckInterval.current = null;
            }
            setIsLoading(false);
          }
        } catch (err) {
          setError('Erreur lors de la vérification du statut du job');
          if (statusCheckInterval.current) {
            clearInterval(statusCheckInterval.current);
            statusCheckInterval.current = null;
          }
          setIsLoading(false);
        }
      }, 2000); // Vérifier toutes les 2 secondes
    }
    
    return () => {
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current);
      }
    };
  }, [jobId, useAsyncParsing, onCVParsed]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Veuillez sélectionner un fichier');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setJobId(null);
    setJobStatus(null);
    setParsedData(null);
    
    try {
      if (useAsyncParsing) {
        // Parsing asynchrone (mise en file d'attente)
        const jobId = await cvParserService.queueCVParsing(file);
        setJobId(jobId);
      } else {
        // Parsing synchrone (attente de la réponse)
        const data = await cvParserService.parseCV(file);
        setParsedData(data);
        if (onCVParsed) onCVParsed(data);
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Erreur lors du parsing du CV:', err);
      setError('Une erreur est survenue lors du parsing du CV');
      setIsLoading(false);
    }
  };

  return (
    <div className="cv-uploader">
      <div className="upload-options">
        <label>
          <input
            type="checkbox"
            checked={useAsyncParsing}
            onChange={() => setUseAsyncParsing(!useAsyncParsing)}
          />
          Utiliser le parsing asynchrone (recommandé pour les gros fichiers)
        </label>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div 
          className="drop-zone"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={handleUploadClick}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept=".pdf,.doc,.docx,.txt"
          />
          {file ? (
            <div className="selected-file">
              <p>Fichier sélectionné: {file.name}</p>
              <p>Taille: {(file.size / 1024).toFixed(2)} KB</p>
            </div>
          ) : (
            <div className="upload-prompt">
              <p>Glissez votre CV ici ou cliquez pour sélectionner un fichier</p>
              <p className="file-types">PDF, DOC, DOCX, TXT</p>
            </div>
          )}
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <button 
          type="submit" 
          className="upload-button" 
          disabled={!file || isLoading}
        >
          {isLoading ? 'Traitement en cours...' : 'Analyser le CV'}
        </button>
      </form>
      
      {isLoading && jobStatus && (
        <div className="job-status">
          <p>État du job: {jobStatus.status}</p>
          {jobStatus.position !== undefined && jobStatus.total_jobs !== undefined && (
            <p>Position dans la file: {jobStatus.position + 1}/{jobStatus.total_jobs}</p>
          )}
          {jobStatus.message && <p>{jobStatus.message}</p>}
        </div>
      )}
      
      {parsedData && (
        <div className="parsed-data-preview">
          <h3>Données extraites:</h3>
          <pre>{JSON.stringify(parsedData, null, 2)}</pre>
        </div>
      )}
      
      <style jsx>{`
        .cv-uploader {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }
        
        .drop-zone {
          border: 2px dashed #ccc;
          border-radius: 5px;
          padding: 40px;
          text-align: center;
          cursor: pointer;
          margin-bottom: 20px;
          transition: border-color 0.3s;
        }
        
        .drop-zone:hover {
          border-color: #007bff;
        }
        
        .selected-file {
          color: #333;
        }
        
        .upload-prompt {
          color: #666;
        }
        
        .file-types {
          font-size: 0.8em;
          color: #999;
        }
        
        .upload-button {
          background-color: #007bff;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 16px;
          transition: background-color 0.3s;
        }
        
        .upload-button:hover:not(:disabled) {
          background-color: #0056b3;
        }
        
        .upload-button:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
        }
        
        .error-message {
          color: #dc3545;
          margin-bottom: 15px;
        }
        
        .job-status {
          margin-top: 20px;
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
          border-left: 4px solid #17a2b8;
        }
        
        .parsed-data-preview {
          margin-top: 20px;
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 4px;
          overflow-x: auto;
        }
        
        .parsed-data-preview pre {
          white-space: pre-wrap;
          font-size: 14px;
        }
        
        .upload-options {
          margin-bottom: 20px;
        }
      `}</style>
    </div>
  );
};

export default CVUploader;
