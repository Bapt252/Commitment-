import React, { useState, useRef } from 'react';
import { parseJobDirect, parseJobText } from '../../services/jobParserService';

/**
 * Composant pour l'upload et le parsing de fiches de poste
 */
const JobParserForm = ({ onParsingResult, initialLoading = false }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobText, setJobText] = useState('');
  const [isLoading, setIsLoading] = useState(initialLoading);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setError(null);
  };

  const handleTextChange = (event) => {
    setJobText(event.target.value);
    setError(null);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      const file = event.dataTransfer.files[0];
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleParseFile = async () => {
    if (!selectedFile) {
      setError("Veuillez sélectionner un fichier");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const result = await parseJobDirect(selectedFile);
      
      if (onParsingResult) {
        onParsingResult(result);
      }
    } catch (err) {
      console.error("Erreur lors du parsing:", err);
      setError(err.message || "Une erreur est survenue lors du parsing");
    } finally {
      setIsLoading(false);
    }
  };

  const handleParseText = async () => {
    if (!jobText.trim()) {
      setError("Veuillez saisir du texte à analyser");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const result = await parseJobText(jobText);
      
      if (onParsingResult) {
        onParsingResult(result);
      }
    } catch (err) {
      console.error("Erreur lors du parsing du texte:", err);
      setError(err.message || "Une erreur est survenue lors du parsing");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setJobText('');
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 text-purple-700">Analyse de fiche de poste</h2>
      
      <div className="mb-6">
        <div 
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer mb-2
                      ${selectedFile ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-purple-400'}
                    `}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <input 
            type="file" 
            className="hidden" 
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx,.txt"
          />
          
          {selectedFile ? (
            <div className="text-green-600">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-lg font-medium">{selectedFile.name}</p>
              <p className="text-sm">{Math.round(selectedFile.size / 1024)} KB</p>
            </div>
          ) : (
            <div className="text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="font-medium">Glissez-déposez votre fichier ici</p>
              <p className="text-sm">ou cliquez pour sélectionner un fichier</p>
              <p className="text-xs mt-2 text-gray-400">Formats supportés: PDF, DOCX, DOC, TXT</p>
            </div>
          )}
        </div>
        
        <button 
          className={`w-full py-2 px-4 rounded-md font-medium
                      ${selectedFile 
                        ? 'bg-purple-600 hover:bg-purple-700 text-white'
                        : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      }`}
          onClick={handleParseFile}
          disabled={!selectedFile || isLoading}
        >
          {isLoading && selectedFile ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyse en cours...
            </span>
          ) : (
            'Analyser le fichier'
          )}
        </button>
      </div>
      
      <div className="my-6 flex items-center">
        <hr className="flex-grow border-gray-300" />
        <span className="px-4 text-gray-500 text-sm">OU</span>
        <hr className="flex-grow border-gray-300" />
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Collez le texte de votre fiche de poste
        </label>
        <textarea
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          rows="6"
          value={jobText}
          onChange={handleTextChange}
          placeholder="Collez ici le texte de votre fiche de poste..."
        ></textarea>
      </div>
      
      <button 
        className={`w-full py-2 px-4 rounded-md font-medium mb-4
                    ${jobText.trim() 
                      ? 'bg-purple-600 hover:bg-purple-700 text-white'
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    }`}
        onClick={handleParseText}
        disabled={!jobText.trim() || isLoading}
      >
        {isLoading && !selectedFile ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Analyse en cours...
          </span>
        ) : (
          'Analyser ce texte'
        )}
      </button>
      
      <button 
        className="w-full py-2 px-4 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        onClick={handleReset}
        disabled={isLoading}
      >
        Réinitialiser
      </button>
      
      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
          <p className="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        </div>
      )}
    </div>
  );
};

export default JobParserForm;
