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

  console.log('Receiving CV parsing request...');
  
  const form = formidable({
    keepExtensions: true,
    maxFileSize: 10 * 1024 * 1024, // 10MB max size
  });
  
  try {
    const [fields, files] = await form.parse(req);
    console.log('Form parsed, fields:', Object.keys(fields));

    // Dans la v3, files est maintenant un objet avec des arrays
    const fileArray = files.file;
    if (!fileArray || fileArray.length === 0) {
      console.error('No file uploaded');
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    const file = fileArray[0];
    console.log(`File received: ${file.originalFilename}, size: ${file.size} bytes, type: ${file.mimetype}`);
    
    // Options from fields
    const forceRefresh = fields.force_refresh && fields.force_refresh[0] === 'true';
    const detailedMode = fields.detailed_mode && fields.detailed_mode[0] === 'true';
    
    console.log(`Options - Force refresh: ${forceRefresh}, Detailed mode: ${detailedMode}`);
    
    // Create form data for the API request
    const formData = new FormData();
    formData.append('file', new Blob([fs.readFileSync(file.filepath)]), file.originalFilename);
    
    // Add the options to the form data
    if (forceRefresh) {
      formData.append('force_refresh', 'true');
    }
    
    if (detailedMode) {
      formData.append('detailed_mode', 'true');
    }

    // Forward the request to the CV parser service
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5050';
    console.log(`Forwarding request to ${apiUrl}/api/v1/cv/parse`);
    
    const response = await axios.post(`${apiUrl}/api/v1/cv/parse`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 secondes timeout
    });

    console.log('CV parsing successful');
    return res.status(200).json(response.data);
  } catch (error) {
    console.error('Error parsing CV:', error);
    
    // Detailed error information
    const errorDetails = {
      error: 'Error processing the CV',
      message: error.message,
      status: error.response?.status,
      details: error.response?.data || 'Unknown error'
    };
    
    console.error('Error details:', JSON.stringify(errorDetails));
    return res.status(error.response?.status || 500).json(errorDetails);
  }
}
