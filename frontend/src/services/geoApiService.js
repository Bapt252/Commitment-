import axios from 'axios';

/**
 * Service pour gérer les appels API liés à la géolocalisation
 */
const geoApiService = {
  /**
   * Géocode une adresse pour obtenir les coordonnées
   * 
   * @param {string} address - Adresse à géocoder
   * @returns {Promise<Object>} - Coordonnées et adresse formatée
   */
  geocodeAddress: async (address) => {
    try {
      // La clé API est protégée côté backend
      const response = await axios.post('/api/geo/geocode', { address });
      return response.data;
    } catch (error) {
      console.error('Error geocoding address:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Échec du géocodage');
    }
  },
  
  /**
   * Effectue un géocodage inversé pour obtenir une adresse depuis des coordonnées
   * 
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   * @returns {Promise<Object>} - Adresse formatée et informations sur le lieu
   */
  reverseGeocode: async (lat, lng) => {
    try {
      const response = await axios.post('/api/geo/reverse-geocode', { lat, lng });
      return response.data;
    } catch (error) {
      console.error('Error reverse geocoding:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Échec du géocodage inversé');
    }
  },
  
  /**
   * Recherche des lieux à proximité d'un point
   * 
   * @param {Object} params - Paramètres de recherche
   * @param {number} params.lat - Latitude
   * @param {number} params.lng - Longitude
   * @param {number} [params.radius=5000] - Rayon de recherche en mètres
   * @param {string} [params.keyword] - Mot-clé de recherche
   * @param {string} [params.place_type] - Type de lieu
   * @returns {Promise<Array>} - Liste des lieux trouvés
   */
  getPlacesNearby: async ({ lat, lng, radius = 5000, keyword, place_type }) => {
    try {
      const response = await axios.post('/api/geo/places-nearby', { 
        lat, 
        lng, 
        radius,
        keyword,
        place_type
      });
      return response.data.results;
    } catch (error) {
      console.error('Error finding places nearby:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Échec de la recherche de lieux');
    }
  },
  
  /**
   * Calcule la distance entre deux points
   * 
   * @param {string} origin - Adresse ou coordonnées d'origine
   * @param {string} destination - Adresse ou coordonnées de destination
   * @param {string} [mode='driving'] - Mode de transport
   * @returns {Promise<Object>} - Informations sur la distance et le temps de trajet
   */
  calculateDistance: async (origin, destination, mode = 'driving') => {
    try {
      const response = await axios.post('/api/geo/distance', {
        origin,
        destination,
        mode
      });
      return response.data;
    } catch (error) {
      console.error('Error calculating distance:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Échec du calcul de distance');
    }
  }
};

export default geoApiService;