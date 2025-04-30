import axios from 'axios';

/**
 * Service for geocoding addresses using the Google Maps Geocoding API
 * Through a proxy endpoint to protect the API key
 */
const geocodingService = {
  /**
   * Geocode an address to get its coordinates
   * 
   * @param {string} address - The address to geocode
   * @returns {Promise<Object>} - Promise resolving to coordinates { lat, lng }
   */
  geocodeAddress: async (address) => {
    try {
      if (!address) {
        throw new Error('Adresse non fournie');
      }
      
      // Using our own API proxy to protect the API key
      const response = await axios.post('/api/geocode', { address });
      
      if (!response.data || !response.data.results || response.data.results.length === 0) {
        throw new Error('Aucun résultat trouvé pour cette adresse');
      }
      
      const { lat, lng } = response.data.results[0].geometry.location;
      return { lat, lng };
    } catch (error) {
      console.error('Erreur de géocodage:', error);
      throw error;
    }
  },
  
  /**
   * Batch geocode multiple addresses
   * 
   * @param {Array<string>} addresses - Array of addresses to geocode
   * @returns {Promise<Array<Object>>} - Promise resolving to array of results
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

export default geocodingService;