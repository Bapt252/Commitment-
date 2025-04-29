
import Head from 'next/head';
import { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

export default function CVUploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [forceRefresh, setForceRefresh] = useState(false);
  const [detailedMode, setDetailedMode] = useState(true); // Activer par défaut pour de meilleurs résultats
  const [selectedTab, setSelectedTab] = useState('structured');

  // Simuler la progression pendant le chargement
  useEffect(() => {
    let progressInterval;
    if (loading) {
      progressInterval = setInterval(() => {
        setProgress((prevProgress) => {
          // Progression artificielle jusqu'à 95% (le 100% sera atteint lorsque la réponse est reçue)
          const newProgress = prevProgress + (Math.random() * 3);
          return newProgress > 95 ? 95 : newProgress;
        });
      }, 300);
    } else {
      setProgress(loading ? 0 : 100);
    }

    return () => {
      if (progressInterval) clearInterval(progressInterval);
    };
  }, [loading]);

  const onDrop = (acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setResult(null);
    setError(null);
    setProgress(0);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'application/rtf': ['.rtf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!file) {
      setError('Veuillez sélectionner un fichier');
      return;
    }

    setLoading(true);
    setProgress(0);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('force_refresh', forceRefresh);
    formData.append('detailed_mode', detailedMode);

    try {
      const response = await axios.post('/api/parse-cv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      console.log("Résultat brut du parsing:", response.data);
      
      // S'assurer que le résultat a la structure attendue
      const processedData = normalizeParserResult(response.data);
      setResult(processedData);
      setError(null);
    } catch (err) {
      console.error('Error parsing CV:', err);
      setError(err.response?.data?.error || 'Échec du parsing du CV');
      setResult(null);
    } finally {
      setLoading(false);
      setProgress(100);
    }
  };
  
  // Fonction pour normaliser le résultat du parsing et garantir une structure cohérente
  const normalizeParserResult = (data) => {
    // Si les données sont imbriquées dans un sous-objet 'data'
    const parsedData = data.data || data;
    
    // S'assurer que toutes les propriétés principales existent
    const normalized = {
      personal_info: parsedData.personal_info || {},
      position: parsedData.position || "",
      skills: Array.isArray(parsedData.skills) ? parsedData.skills : [],
      experience: Array.isArray(parsedData.experience) ? parsedData.experience : [],
      education: Array.isArray(parsedData.education) ? parsedData.education : [],
      languages: Array.isArray(parsedData.languages) ? parsedData.languages : [],
      softwares: Array.isArray(parsedData.softwares) ? parsedData.softwares : []
    };
    
    // S'assurer que personal_info a tous les champs
    normalized.personal_info = {
      name: normalized.personal_info.name || "",
      email: normalized.personal_info.email || "",
      phone: normalized.personal_info.phone || "",
      address: normalized.personal_info.address || ""
    };
    
    // Normaliser les compétences avec une structure cohérente
    normalized.skills = normalized.skills.map(skill => {
      // Si skill est déjà un objet avec propriété 'name'
      if (typeof skill === 'object' && skill !== null) {
        return skill;
      }
      // Si skill est une chaîne
      return { name: String(skill) };
    });
    
    // Enlever le préfixe "undefined" des noms si présent
    if (normalized.personal_info.name && normalized.personal_info.name.startsWith("undefined ")) {
      normalized.personal_info.name = normalized.personal_info.name.replace("undefined ", "");
    }
    
    return normalized;
  };

  // Fonction pour rendre les champs du CV de manière structurée
  const renderParsedData = () => {
    if (!result) return null;

    if (selectedTab === 'json') {
      return (
        <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto max-h-96">
          {JSON.stringify(result, null, 2)}
        </pre>
      );
    }

    // Vue structurée
    return (
      <div className="space-y-6">
        {/* Informations personnelles */}
        <div className="border-b pb-4">
          <h4 className="font-semibold text-lg mb-3 text-blue-700">Informations personnelles</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-3 rounded">
              <span className="font-medium text-blue-800">Nom: </span>
              <span>{result.personal_info?.name || "Non détecté"}</span>
            </div>
            <div className="bg-blue-50 p-3 rounded">
              <span className="font-medium text-blue-800">Email: </span>
              <span>{result.personal_info?.email || "Non détecté"}</span>
            </div>
            <div className="bg-blue-50 p-3 rounded">
              <span className="font-medium text-blue-800">Téléphone: </span>
              <span>{result.personal_info?.phone || "Non détecté"}</span>
            </div>
            <div className="bg-blue-50 p-3 rounded">
              <span className="font-medium text-blue-800">Poste actuel: </span>
              <span>{result.position || "Non détecté"}</span>
            </div>
            {result.personal_info?.address && (
              <div className="bg-blue-50 p-3 rounded md:col-span-2">
                <span className="font-medium text-blue-800">Adresse: </span>
                <span>{result.personal_info.address}</span>
              </div>
            )}
          </div>
        </div>

        {/* Compétences */}
        {result.skills && result.skills.length > 0 && (
          <div className="border-b pb-4">
            <h4 className="font-semibold text-lg mb-3 text-blue-700">Compétences</h4>
            <div className="flex flex-wrap gap-2">
              {result.skills.map((skill, index) => (
                <span key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded">
                  {typeof skill === 'object' ? skill.name : skill}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Logiciels */}
        {result.softwares && result.softwares.length > 0 && (
          <div className="border-b pb-4">
            <h4 className="font-semibold text-lg mb-3 text-blue-700">Logiciels maîtrisés</h4>
            <div className="flex flex-wrap gap-2">
              {result.softwares.map((software, index) => (
                <span key={index} className="bg-purple-100 text-purple-800 px-3 py-1 rounded">
                  {software}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {/* Langues */}
        {result.languages && result.languages.length > 0 && (
          <div className="border-b pb-4">
            <h4 className="font-semibold text-lg mb-3 text-blue-700">Langues</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {result.languages.map((lang, index) => (
                <div key={index} className="bg-yellow-50 p-3 rounded">
                  <span className="font-medium text-yellow-800">{lang.language}: </span>
                  <span>{lang.level}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Expériences professionnelles */}
        {result.experience && result.experience.length > 0 && (
          <div className="border-b pb-4">
            <h4 className="font-semibold text-lg mb-3 text-blue-700">Expérience professionnelle</h4>
            <div className="space-y-4">
              {result.experience.map((exp, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded shadow-sm">
                  <p className="font-medium text-lg text-gray-800">
                    {exp.title || "Poste non précisé"} 
                    {exp.company ? ` - ${exp.company}` : ""}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {exp.start_date || "Date non précisée"} - {exp.end_date || "Présent"}
                  </p>
                  {exp.description && (
                    <p className="text-sm mt-2 text-gray-700">{exp.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Formations */}
        {result.education && result.education.length > 0 && (
          <div className="pb-4">
            <h4 className="font-semibold text-lg mb-3 text-blue-700">Formation</h4>
            <div className="space-y-4">
              {result.education.map((edu, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded shadow-sm">
                  <p className="font-medium text-gray-800">
                    {edu.degree || "Diplôme non précisé"} 
                    {edu.institution ? ` - ${edu.institution}` : ""}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {edu.start_date || "Date non précisée"} - {edu.end_date || "Présent"}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <Head>
        <title>Upload CV - NexTen</title>
        <meta name="description" content="Upload and parse your CV" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">Téléchargez votre CV</h1>
        
        <div className="max-w-4xl mx-auto">
          <div 
            {...getRootProps()} 
            className={`border-2 border-dashed p-6 rounded-lg text-center cursor-pointer mb-6 ${
              isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-blue-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-gray-600 text-lg">
                {isDragActive ? 'Déposez le fichier ici' : 'Glissez-déposez votre CV ici, ou cliquez pour sélectionner un fichier'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Formats supportés: PDF, DOCX, DOC, TXT, RTF, JPG, PNG (max: 10MB)
              </p>
            </div>
          </div>

          {file && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg flex items-center border border-blue-200">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div className="flex-1">
                <span className="font-medium">Fichier sélectionné: </span>
                <span className="text-blue-700">{file.name}</span>
                <span className="text-sm text-gray-500 ml-2">({(file.size / 1024).toFixed(2)} KB)</span>
              </div>
            </div>
          )}

          <div className="mb-6 space-y-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
            <h3 className="font-medium text-gray-700">Options de parsing</h3>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="forceRefresh"
                checked={forceRefresh}
                onChange={() => setForceRefresh(!forceRefresh)}
                className="h-4 w-4 text-blue-600 rounded"
              />
              <label htmlFor="forceRefresh" className="ml-2 text-sm text-gray-700">
                Force refresh (ignorer le cache)
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="detailedMode"
                checked={detailedMode}
                onChange={() => setDetailedMode(!detailedMode)}
                className="h-4 w-4 text-blue-600 rounded"
              />
              <label htmlFor="detailedMode" className="ml-2 text-sm text-gray-700">
                Mode détaillé (parsing plus approfondi)
              </label>
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-md font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex justify-center items-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Traitement en cours...
              </>
            ) : (
              'Analyser le CV'
            )}
          </button>

          {loading && (
            <div className="mt-6">
              <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-600 transition-all duration-300 ease-out" 
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 mt-2 text-center">
                Analyse en cours ({Math.round(progress)}%)...
              </p>
            </div>
          )}

          {error && (
            <div className="mt-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
              <strong className="font-bold">Erreur! </strong>
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          {result && (
            <div className="mt-8 bg-white shadow-lg rounded-lg overflow-hidden border">
              <div className="flex border-b">
                <button 
                  className={`px-4 py-3 font-medium ${selectedTab === 'structured' ? 'bg-gray-100 text-blue-600 border-b-2 border-blue-500' : 'text-gray-600 hover:bg-gray-50'}`}
                  onClick={() => setSelectedTab('structured')}
                >
                  Vue structurée
                </button>
                <button 
                  className={`px-4 py-3 font-medium ${selectedTab === 'json' ? 'bg-gray-100 text-blue-600 border-b-2 border-blue-500' : 'text-gray-600 hover:bg-gray-50'}`}
                  onClick={() => setSelectedTab('json')}
                >
                  Format JSON
                </button>
              </div>
              
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-800">Données extraites du CV</h3>
                  <span className="text-xs text-gray-500">
                    Traité en {result.processing_time ? result.processing_time.toFixed(2) + 's' : 'N/A'}
                  </span>
                </div>
                {renderParsedData()}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
