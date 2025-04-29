/**
 * Structure des informations personnelles extraites du CV
 */
export interface PersonalInfo {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
  linkedin?: string;
  website?: string;
  github?: string;
  summary?: string;
}

/**
 * Structure d'une expérience professionnelle
 */
export interface WorkExperience {
  title?: string;
  company?: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  current?: boolean;
  description?: string;
  achievements?: string[];
  skills?: string[];
}

/**
 * Structure d'une formation
 */
export interface Education {
  degree?: string;
  institution?: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  description?: string;
}

/**
 * Structure d'une langue maîtrisée
 */
export interface Language {
  language: string;
  level: string;
}

/**
 * Structure complète des données extraites d'un CV
 */
export interface CVData {
  personal_info: PersonalInfo;
  skills?: string[];
  work_experience?: WorkExperience[];
  education?: Education[];
  languages?: Language[];
  certifications?: string[];
  projects?: {
    name: string;
    description: string;
    technologies?: string[];
    url?: string;
  }[];
  awards?: string[];
  publications?: string[];
}

/**
 * Statut d'un job de parsing
 */
export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

/**
 * Structure de la réponse du statut d'un job
 */
export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  message?: string;
  position?: number;
  total_jobs?: number;
}

/**
 * Structure de la réponse de création d'un job
 */
export interface CreateJobResponse {
  job_id: string;
  message: string;
}
