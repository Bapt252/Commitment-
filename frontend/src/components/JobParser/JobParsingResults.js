import React from 'react';

/**
 * Composant pour afficher les résultats du parsing d'une fiche de poste
 */
const JobParsingResults = ({ results }) => {
  if (!results || !results.data) {
    return null;
  }

  const { 
    title, 
    company, 
    location, 
    contract_type, 
    required_skills, 
    preferred_skills, 
    responsibilities, 
    requirements, 
    benefits,
    salary_range,
    remote_policy,
    application_process
  } = results.data;

  const renderTextItem = (text) => {
    return text ? <span>{text}</span> : <span className="text-gray-400 italic">Non spécifié</span>;
  };

  const renderListItems = (items) => {
    if (!items || items.length === 0) {
      return <span className="text-gray-400 italic">Aucun élément</span>;
    }

    return (
      <ul className="list-disc pl-5 space-y-1">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 text-purple-700">Informations extraites</h2>
      
      <div className="bg-purple-50 rounded-md p-4 mb-6 border border-purple-200">
        <div className="flex items-start space-x-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-purple-600 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div className="text-sm text-purple-700">
            <p>Parsé avec {results.model || "AI"} en {results.processing_time ? `${results.processing_time.toFixed(2)} secondes` : "quelques secondes"}</p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="pb-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-800">{title || "Titre non spécifié"}</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {company && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {company}
              </span>
            )}
            {location && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {location}
              </span>
            )}
            {contract_type && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                {contract_type}
              </span>
            )}
            {remote_policy && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                {remote_policy}
              </span>
            )}
          </div>
          {salary_range && (
            <p className="mt-2 text-sm text-gray-600">
              <span className="font-medium">Salaire :</span> {salary_range}
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Compétences requises</h4>
            {renderListItems(required_skills)}
          </div>
          
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Compétences souhaitées</h4>
            {renderListItems(preferred_skills)}
          </div>
        </div>

        <div>
          <h4 className="font-medium text-gray-800 mb-2">Responsabilités</h4>
          {renderListItems(responsibilities)}
        </div>
        
        <div>
          <h4 className="font-medium text-gray-800 mb-2">Prérequis</h4>
          {renderListItems(requirements)}
        </div>
        
        <div>
          <h4 className="font-medium text-gray-800 mb-2">Avantages</h4>
          {renderListItems(benefits)}
        </div>

        {application_process && (
          <div>
            <h4 className="font-medium text-gray-800 mb-2">Processus de candidature</h4>
            <p className="text-gray-600">{application_process}</p>
          </div>
        )}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <button 
          className="inline-flex items-center px-4 py-2 border border-purple-300 text-sm font-medium rounded-md text-purple-700 bg-white hover:bg-purple-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
          onClick={() => {
            // Copier les résultats dans le presse-papier
            navigator.clipboard.writeText(JSON.stringify(results.data, null, 2))
              .then(() => alert('Résultats copiés dans le presse-papier'))
              .catch(err => console.error('Erreur lors de la copie:', err));
          }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
          </svg>
          Copier les résultats
        </button>
      </div>
    </div>
  );
};

export default JobParsingResults;
