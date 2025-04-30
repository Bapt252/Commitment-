import axios from 'axios';

/**
 * API proxy endpoint for Google Maps Geocoding API
 * This protects the API key from being exposed to the client
 */
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed. Please use POST.' });
  }

  try {
    const { address } = req.body;
    
    if (!address) {
      return res.status(400).json({ error: 'Address is required' });
    }

    // Get API key from environment variables
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
    
    if (!apiKey) {
      console.error('Google Maps API key is missing');
      return res.status(500).json({ error: 'Server configuration error' });
    }

    // Call Google Maps Geocoding API
    const response = await axios.get('https://maps.googleapis.com/maps/api/geocode/json', {
      params: {
        address,
        key: apiKey
      }
    });

    // Check for API errors
    if (response.data.status !== 'OK') {
      console.error('Geocoding API error:', response.data.status);
      return res.status(400).json({ 
        error: `Geocoding failed: ${response.data.status}`,
        details: response.data.error_message
      });
    }

    // Return the geocoding results
    return res.status(200).json(response.data);
  } catch (error) {
    console.error('Geocoding request failed:', error);
    return res.status(500).json({ 
      error: 'Internal server error', 
      details: error.message 
    });
  }
}