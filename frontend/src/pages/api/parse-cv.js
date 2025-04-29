import axios from 'axios';
import { formidable } from 'formidable';
import fs from 'fs';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const form = formidable();
  
  try {
    const [fields, files] = await form.parse(req);

    // Dans la v3, files est maintenant un objet avec des arrays
    const fileArray = files.file;
    if (!fileArray || fileArray.length === 0) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    const file = fileArray[0];
    
    // Create form data for the API request
    const formData = new FormData();
    formData.append('file', new Blob([fs.readFileSync(file.filepath)]), file.originalFilename);

    // Forward the request to the CV parser service
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5050';
    const response = await axios.post(`${apiUrl}/api/v1/cv/parse`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return res.status(200).json(response.data);
  } catch (error) {
    console.error('Error parsing CV:', error);
    return res.status(500).json({ 
      error: 'Error processing the CV', 
      details: error.response?.data || error.message 
    });
  }
}