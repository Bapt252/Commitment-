// Script pour gérer le stockage et l'affichage des postes et processus
// Fonction pour sauvegarder les données du formulaire
function saveJobData(jobData) {
  // Récupérer les données existantes ou initialiser un tableau vide
  const existingJobs = JSON.parse(localStorage.getItem('commitmentJobs') || '[]');
  
  // Ajouter les nouvelles données avec un ID unique
  jobData.id = Date.now(); // Utiliser le timestamp comme ID unique
  jobData.createdAt = new Date().toISOString();
  
  existingJobs.push(jobData);
  
  // Sauvegarder dans localStorage
  localStorage.setItem('commitmentJobs', JSON.stringify(existingJobs));
  
  return jobData.id;
}

// Fonction pour récupérer tous les postes
function getAllJobs() {
  return JSON.parse(localStorage.getItem('commitmentJobs') || '[]');
}

// Fonction pour récupérer un poste spécifique par ID
function getJobById(jobId) {
  const jobs = getAllJobs();
  return jobs.find(job => job.id === jobId);
}

// Fonction pour supprimer un poste
function deleteJob(jobId) {
  let jobs = getAllJobs();
  jobs = jobs.filter(job => job.id !== jobId);
  localStorage.setItem('commitmentJobs', JSON.stringify(jobs));
}
