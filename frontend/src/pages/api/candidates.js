import axios from 'axios';

/**
 * API endpoint to get candidate data for the map
 */
export default async function handler(req, res) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed. Please use GET.' });
  }

  try {
    // Fetch candidates from the main API
    // In production, connect to the actual API endpoint
    
    // For demo purposes, return mock data
    const mockData = [
      {
        id: 1,
        personal_info: {
          name: 'Jean Dupont',
          email: 'jean.dupont@example.com',
          phone: '01 23 45 67 89',
          address: '15 Rue de Rivoli, Paris, France'
        },
        position: 'Développeur Web',
        skills: ['JavaScript', 'React', 'Node.js']
      },
      {
        id: 2,
        personal_info: {
          name: 'Marie Martin',
          email: 'marie.martin@example.com',
          phone: '01 98 76 54 32',
          address: '8 Avenue des Champs-Élysées, Paris, France'
        },
        position: 'Designer UX/UI',
        skills: ['Figma', 'Sketch', 'Adobe XD']
      },
      {
        id: 3,
        personal_info: {
          name: 'Lucas Bernard',
          email: 'lucas.bernard@example.com',
          phone: '06 12 34 56 78',
          address: '25 Boulevard Saint-Germain, Paris, France'
        },
        position: 'Développeur Web',
        skills: ['JavaScript', 'Vue.js', 'PHP']
      },
      {
        id: 4,
        personal_info: {
          name: 'Sophie Petit',
          email: 'sophie.petit@example.com',
          phone: '07 65 43 21 09',
          address: '10 Rue de Lyon, Lyon, France'
        },
        position: 'Chef de Projet',
        skills: ['Agile', 'Scrum', 'Jira']
      },
      {
        id: 5,
        personal_info: {
          name: 'Thomas Leroux',
          email: 'thomas.leroux@example.com',
          phone: '06 98 76 54 32',
          address: '5 Rue Garibaldi, Lyon, France'
        },
        position: 'Data Scientist',
        skills: ['Python', 'TensorFlow', 'SQL']
      },
      {
        id: 6,
        personal_info: {
          name: 'Julie Moreau',
          email: 'julie.moreau@example.com',
          phone: '06 22 33 44 55',
          address: '42 Cours Franklin Roosevelt, Marseille, France'
        },
        position: 'Développeur Mobile',
        skills: ['Swift', 'Kotlin', 'Flutter']
      },
      {
        id: 7,
        personal_info: {
          name: 'Nicolas Roux',
          email: 'nicolas.roux@example.com',
          phone: '07 11 22 33 44',
          address: '18 Rue du Faubourg Saint-Antoine, Paris, France'
        },
        position: 'DevOps Engineer',
        skills: ['Docker', 'Kubernetes', 'AWS']
      }
    ];

    // Production version would look like this:
    // const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/candidates`, {
    //   headers: {
    //     'Authorization': `Bearer ${req.cookies.token}` // If authentication is needed
    //   }
    // });
    // return res.status(200).json(response.data);

    // Return mock data for now
    return res.status(200).json(mockData);
  } catch (error) {
    console.error('Failed to fetch candidates:', error);
    return res.status(500).json({ 
      error: 'Internal server error', 
      details: error.message 
    });
  }
}
