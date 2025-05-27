/**
 * Page dédiée au SuperSmartMatch Unifié
 * Point d'entrée principal pour le nouveau système de matching
 */

import React from 'react';
import Head from 'next/head';
import SuperSmartMatchPipeline from '../components/matching/SuperSmartMatchPipeline';

const SuperSmartMatchPage = () => {
  return (
    <>
      <Head>
        <title>SuperSmartMatch Unifié - Matching Intelligence</title>
        <meta name="description" content="Algorithme de matching intelligent avec pipeline automatisé : Parsing → Questionnaire → Matching" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900">
                  🚀 Nexten - SuperSmartMatch
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <a href="/" className="text-gray-600 hover:text-gray-900">
                  Accueil
                </a>
                <a href="/dashboard" className="text-gray-600 hover:text-gray-900">
                  Dashboard
                </a>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  Connexion
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Contenu principal */}
        <div className="py-8">
          <SuperSmartMatchPipeline />
        </div>

        {/* Footer */}
        <footer className="bg-white border-t mt-16">
          <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
            <div className="text-center text-gray-600">
              <p className="mb-4">
                🤖 Propulsé par SuperSmartMatch Unifié - Algorithme de matching intelligent
              </p>
              <div className="flex justify-center space-x-6 text-sm">
                <span>✅ Parsing automatique</span>
                <span>✅ ML sémantique</span>
                <span>✅ Auto-apprentissage</span>
                <span>✅ Cache intelligent</span>
              </div>
              <p className="mt-4 text-sm">
                © 2024 Nexten. SuperSmartMatch Unifié v1.0
              </p>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
};

export default SuperSmartMatchPage;