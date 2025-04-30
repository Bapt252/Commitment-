import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import axios from 'axios';
import GoogleMapComponent from '../components/GoogleMapComponent';
import geocodingService from '../services/geocodingService';

export default function CandidateMap() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mapMarkers, setMapMarkers] = useState([]);
  const [mapCenter, setMapCenter] = useState({ lat: 48.856614, lng: 2.3522219 }); // Paris par défaut
  const [selectedJob, setSelectedJob] = useState('all');
  const [jobs, setJobs] = useState([]);

  // Charger les candidats depuis l'API
  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        setLoading(true);
        
        // Remplacer par l'endpoint réel de l'API
        const response = await axios.get('/api/candidates');
        setCandidates(response.data);
        
        // Extraire les types d'emplois uniques pour le filtre
        const uniqueJobs = [...new Set(response.data.map(c => c.position))].filter(Boolean);
        setJobs(uniqueJobs);
        
        setLoading(false);
      } catch (err) {
        console.error('Erreur lors du chargement des candidats:', err);
        setError('Impossible de charger les candidats');
        setLoading(false);
      }
    };

    fetchCandidates();
  }, []);

  // Géocoder les adresses des candidats lorsque la liste est mise à jour
  useEffect(() => {
    const geocodeCandidateAddresses = async () => {
      if (!candidates.length) return;
      
      try {
        // Filtrer les candidats en fonction du job sélectionné
        const filteredCandidates = selectedJob === 'all' 
          ? candidates 
          : candidates.filter(c => c.position === selectedJob);
        
        // Créer un tableau des adresses à géocoder
        const addressesToGeocode = filteredCandidates
          .filter(c => c.personal_info?.address)
          .map(c => ({
            id: c.id,
            address: c.personal_info.address
          }));
        
        if (!addressesToGeocode.length) {
          setMapMarkers([]);
          return;
        }
        
        // Géocoder les adresses
        const markers = [];
        let sumLat = 0;
        let sumLng = 0;
        let validCoordinatesCount = 0;
        
        for (const item of addressesToGeocode) {
          try {
            const coords = await geocodingService.geocodeAddress(item.address);
            
            // Trouver le candidat correspondant
            const candidate = filteredCandidates.find(c => c.id === item.id);
            
            if (coords && candidate) {
              // Ajouter le marqueur
              markers.push({
                lat: coords.lat,
                lng: coords.lng,
                title: candidate.personal_info?.name || 'Candidat',
                description: candidate.position || 'Poste non spécifié',
                address: candidate.personal_info?.address
              });
              
              // Cumuler les coordonnées pour calculer le centre
              sumLat += coords.lat;
              sumLng += coords.lng;
              validCoordinatesCount++;
            }
          } catch (error) {
            console.error(`Erreur de géocodage pour l'adresse: ${item.address}`, error);
          }
        }
        
        // Mettre à jour les marqueurs
        setMapMarkers(markers);
        
        // Calculer et définir le centre de la carte
        if (validCoordinatesCount > 0) {
          setMapCenter({
            lat: sumLat / validCoordinatesCount,
            lng: sumLng / validCoordinatesCount
          });
        }
      } catch (error) {
        console.error('Erreur lors du géocodage des adresses:', error);
      }
    };

    geocodeCandidateAddresses();
  }, [candidates, selectedJob]);

  // Fonction pour simuler des données de candidats (à remplacer par des données réelles)
  const mockCandidates = async () => {
    const mockData = [
      {
        id: 1,
        personal_info: {
          name: 'Jean Dupont',
          email: 'jean.dupont@example.com',
          phone: '01 23 45 67 89',
          address: '15 Rue de Rivoli, Paris, France'
        },
        position: 'Développeur Web'
      },
      {
        id: 2,
        personal_info: {
          name: 'Marie Martin',
          email: 'marie.martin@example.com',
          phone: '01 98 76 54 32',
          address: '8 Avenue des Champs-Élysées, Paris, France'
        },
        position: 'Designer UX/UI'
      },
      {
        id: 3,
        personal_info: {
          name: 'Lucas Bernard',
          email: 'lucas.bernard@example.com',
          phone: '06 12 34 56 78',
          address: '25 Boulevard Saint-Germain, Paris, France'
        },
        position: 'Développeur Web'
      },
      {
        id: 4,
        personal_info: {
          name: 'Sophie Petit',
          email: 'sophie.petit@example.com',
          phone: '07 65 43 21 09',
          address: '10 Rue de Lyon, Lyon, France'
        },
        position: 'Chef de Projet'
      },
      {
        id: 5,
        personal_info: {
          name: 'Thomas Leroux',
          email: 'thomas.leroux@example.com',
          phone: '06 98 76 54 32',
          address: '5 Rue Garibaldi, Lyon, France'
        },
        position: 'Data Scientist'
      }
    ];
    
    // Utiliser les données fictives comme si elles venaient de l'API
    setCandidates(mockData);
    
    // Extraire les types d'emplois uniques pour le filtre
    const uniqueJobs = [...new Set(mockData.map(c => c.position))].filter(Boolean);
    setJobs(uniqueJobs);
    
    setLoading(false);
  };
  
  // Utiliser les données fictives en l'absence d'API réelle
  useEffect(() => {
    mockCandidates();
  }, []);

  return (
    <div>
      <Head>
        <title>Carte des Candidats - NexTen</title>
        <meta name="description" content="Visualisez géographiquement les candidats" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">Carte des Candidats</h1>

        <div className="max-w-6xl mx-auto">
          {/* Filtres */}
          <div className="mb-6 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex flex-wrap items-center gap-4">
              <div>
                <label htmlFor="jobFilter" className="block text-sm font-medium text-gray-700 mb-1">
                  Filtrer par poste:
                </label>
                <select
                  id="jobFilter"
                  value={selectedJob}
                  onChange={(e) => setSelectedJob(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">Tous les postes</option>
                  {jobs.map((job, index) => (
                    <option key={index} value={job}>{job}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Carte */}
          {loading ? (
            <div className="bg-white p-8 rounded-lg shadow text-center">
              <svg className="animate-spin h-8 w-8 text-blue-500 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-gray-600">Chargement de la carte...</p>
            </div>
          ) : error ? (
            <div className="bg-red-100 p-4 rounded-lg text-red-700 text-center">
              {error}
            </div>
          ) : (
            <div className="space-y-6">
              <GoogleMapComponent
                markers={mapMarkers}
                center={mapCenter}
                zoom={12}
              />
              
              <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
                <h2 className="text-xl font-semibold mb-4">Statistiques</h2>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-blue-700">Total des candidats</p>
                    <p className="text-2xl font-bold">{candidates.length}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-green-700">Candidats affichés</p>
                    <p className="text-2xl font-bold">{mapMarkers.length}</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm text-purple-700">Postes différents</p>
                    <p className="text-2xl font-bold">{jobs.length}</p>
                  </div>
                </div>
              </div>
              
              {/* Liste des candidats */}
              <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
                <h2 className="text-xl font-semibold p-4 border-b">Liste des candidats</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nom</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Poste</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Adresse</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {candidates
                        .filter(c => selectedJob === 'all' || c.position === selectedJob)
                        .map((candidate, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {candidate.personal_info?.name || 'Non spécifié'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {candidate.position || 'Non spécifié'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {candidate.personal_info?.address || 'Non spécifié'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {candidate.personal_info?.email}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
