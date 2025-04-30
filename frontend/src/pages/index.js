import Head from 'next/head';
import Link from 'next/link';

export default function Home() {
  return (
    <div>
      <Head>
        <title>NexTen - CV Parsing & Job Matching</title>
        <meta name="description" content="Smart CV parsing and job matching platform" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-center mb-8">
          <span className="text-blue-600">Nex</span>
          <span>Ten</span>
        </h1>
        
        <p className="text-center text-lg mb-12">
          Intelligent CV parsing and job matching for the modern hiring process
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">CV Parsing</h2>
            <p className="mb-6">
              Upload your CV in PDF or DOCX format and get structured information extracted automatically.
            </p>
            <Link href="/cv-upload" 
                  className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded">
              Upload CV
            </Link>
          </div>

          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Job Matching</h2>
            <p className="mb-6">
              Find the best job matches based on your skills, experience, and career goals.
            </p>
            <Link href="/job-matching" 
                  className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded">
              Find Matches
            </Link>
          </div>
          
          <div className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Candidate Map</h2>
            <p className="mb-6">
              Visualize candidates geographically to identify talent distribution and optimize recruitment.
            </p>
            <Link href="/candidate-map" 
                  className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded">
              View Map
            </Link>
          </div>
        </div>
        
        {/* Feature highlights */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-center mb-8">Key Features</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            <div className="bg-blue-50 p-5 rounded-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2">AI-Powered Parsing</h3>
              <p className="text-gray-600">Extract structured data from CVs with advanced AI algorithms</p>
            </div>
            
            <div className="bg-green-50 p-5 rounded-lg">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2">Smart Matching</h3>
              <p className="text-gray-600">Intelligent algorithms for accurate candidate-job matching</p>
            </div>
            
            <div className="bg-purple-50 p-5 rounded-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2">Geographic Insights</h3>
              <p className="text-gray-600">Visualize candidate distribution with interactive maps</p>
            </div>
            
            <div className="bg-yellow-50 p-5 rounded-lg">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2">High Performance</h3>
              <p className="text-gray-600">Fast processing with reliable microservices architecture</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}