import geoApiService from './geoApiService';

/**
 * Service pour le géocodage des adresses
 */
const geocodingService = {
  /**
   * Géocode une adresse pour obtenir les coordonnées
   * 
   * @param {string} address - L'adresse à géocoder
   * @returns {Promise<Object>} - Coordonnées lat/lng
   */
  geocodeAddress: async (address) => {
    try {
      if (!address) {
        throw new Error('Adresse non fournie');
      }
      
      // Utiliser notre API backend de géocodage
      const geoResult = await geoApiService.geocodeAddress(address);
      
      if (!geoResult || !geoResult.lat || !geoResult.lng) {
        throw new Error('Aucun résultat trouvé pour cette adresse');
      }
      
      return { 
        lat: geoResult.lat, 
        lng: geoResult.lng,
        formatted_address: geoResult.formatted_address || address
      };
    } catch (error) {
      console.error('Erreur de géocodage:', error);
      
      // Fallback au service direct (méthode précédente)
      // Seulement en cas d'échec de notre API backend
      try {
        return await geocodeAddressFallback(address);
      } catch (fallbackError) {
        console.error('Fallback geocoding failed:', fallbackError);
        throw error; // Rethrow the original error if fallback also fails
      }
    }
  },
  
  /**
   * Géocode par lots plusieurs adresses
   * 
   * @param {Array<string>} addresses - Tableau d'adresses à géocoder
   * @returns {Promise<Array<Object>>} - Tableau de résultats
   */
  batchGeocode: async (addresses) => {
    if (!addresses || !addresses.length) {
      return [];
    }
    
    const results = [];
    
    // Process in batches to avoid rate limiting
    for (let i = 0; i < addresses.length; i++) {
      try {
        const coords = await geocodingService.geocodeAddress(addresses[i]);
        results.push({
          address: addresses[i],
          coordinates: coords,
          success: true
        });
      } catch (error) {
        results.push({
          address: addresses[i],
          error: error.message,
          success: false
        });
      }
      
      // Add a small delay between requests to respect rate limits
      if (i < addresses.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 200));
      }
    }
    
    return results;
  }
};

/**
 * Fonction de secours qui utilise l'API proxy précédente
 * Utilisée uniquement si l'API backend échoue
 */
async function geocodeAddressFallback(address) {
  try {
    // Utiliser l'API proxy locale comme fallback
    const response = await fetch('/api/geocode', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ address }),
    });
    
    if (!response.ok) {
      throw new Error(`Erreur HTTP: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.results || data.results.length === 0) {
      throw new Error('Aucun résultat trouvé pour cette adresse');
    }
    
    const { lat, lng } = data.results[0].geometry.location;
    return { 
      lat, 
      lng, 
      formatted_address: data.results[0].formatted_address || address 
    };
  } catch (error) {
    console.error('Fallback geocoding error:', error);
    throw new Error('Échec du géocodage: ' + error.message);
  }
}

export default geocodingService;