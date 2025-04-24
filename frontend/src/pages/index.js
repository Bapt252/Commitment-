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

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
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
        </div>
      </main>
    </div>
  );
}
