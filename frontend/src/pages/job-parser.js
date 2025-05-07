import React, { useState } from 'react';
import Head from 'next/head';
import { JobParserForm, JobParsingResults } from '../components/JobParser';

const JobParserPage = () => {
  const [parsingResults, setParsingResults] = useState(null);

  const handleParsingResult = (results) => {
    setParsingResults(results);
    // Scroll to results after a small delay to ensure rendering
    setTimeout(() => {
      const resultsElement = document.getElementById('parsing-results');
      if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };

  return (
    <>
      <Head>
        <title>Analyse de fiches de poste | NexTen</title>
        <meta name="description" content="Analysez vos fiches de poste pour en extraire des informations structurées" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-2 text-blue-600">Analyse de fiches de poste</h1>
        <p className="text-center text-gray-600 mb-8">
          Utilisez notre outil pour extraire automatiquement les informations clés de vos fiches de poste
        </p>

        <div className="max-w-3xl mx-auto">
          <JobParserForm onParsingResult={handleParsingResult} />
          
          {parsingResults && (
            <div id="parsing-results" className="mt-8">
              <JobParsingResults results={parsingResults} />
            </div>
          )}
        </div>
      </main>

      <footer className="bg-gray-100 py-8 mt-16">
        <div className="container mx-auto px-4 text-center text-gray-600 text-sm">
          <p>&copy; {new Date().getFullYear()} NexTen - Tous droits réservés</p>
        </div>
      </footer>
    </>
  );
};

export default JobParserPage;
