import Head from 'next/head';
import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

export default function CVUploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = (acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setResult(null);
    setError(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/parse-cv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to parse CV');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Head>
        <title>Upload CV - NexTen</title>
        <meta name="description" content="Upload and parse your CV" />
      </Head>

      <main className="container mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold text-center mb-8">Upload Your CV</h1>
        
        <div className="max-w-2xl mx-auto">
          <div 
            {...getRootProps()} 
            className={`border-2 border-dashed p-6 rounded-lg text-center cursor-pointer mb-4 ${
              isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
          >
            <input {...getInputProps()} />
            <p className="text-gray-500">
              {isDragActive ? 'Drop the file here' : 'Drag & drop your CV here, or click to select file'}
            </p>
            <p className="text-xs text-gray-400 mt-1">Supported formats: PDF, DOCX</p>
          </div>

          {file && (
            <div className="mb-4">
              <p className="text-sm">Selected file: {file.name}</p>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Parse CV'}
          </button>

          {error && (
            <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-6 bg-white shadow-md rounded-lg p-4">
              <h3 className="text-lg font-medium mb-4">Parsed CV Data</h3>
              <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
