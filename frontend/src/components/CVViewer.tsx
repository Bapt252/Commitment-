import React from 'react';
import { CVData, WorkExperience, Education, Language } from '../types/CVData';

interface CVViewerProps {
  data: CVData;
  className?: string;
}

const CVViewer: React.FC<CVViewerProps> = ({ data, className = '' }) => {
  if (!data) return null;

  const { personal_info, skills, work_experience, education, languages, certifications, projects } = data;

  return (
    <div className={`cv-viewer ${className}`}>
      <h2 className="section-title">Profil du candidat</h2>
      
      {/* Informations personnelles */}
      <div className="section personal-info">
        <h3>{personal_info.name || 'Sans nom'}</h3>
        
        <div className="contact-info">
          {personal_info.email && (
            <div className="info-item">
              <span className="label">Email:</span> {personal_info.email}
            </div>
          )}
          
          {personal_info.phone && (
            <div className="info-item">
              <span className="label">Téléphone:</span> {personal_info.phone}
            </div>
          )}
          
          {personal_info.address && (
            <div className="info-item">
              <span className="label">Adresse:</span> {personal_info.address}
            </div>
          )}
          
          {personal_info.linkedin && (
            <div className="info-item">
              <span className="label">LinkedIn:</span> 
              <a href={personal_info.linkedin} target="_blank" rel="noopener noreferrer">
                {personal_info.linkedin}
              </a>
            </div>
          )}
        </div>
        
        {personal_info.summary && (
          <div className="summary">
            <h4>Résumé</h4>
            <p>{personal_info.summary}</p>
          </div>
        )}
      </div>
      
      {/* Compétences */}
      {skills && skills.length > 0 && (
        <div className="section">
          <h3 className="subsection-title">Compétences</h3>
          <div className="skills-list">
            {skills.map((skill, index) => (
              <span key={index} className="skill-tag">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Expériences professionnelles */}
      {work_experience && work_experience.length > 0 && (
        <div className="section">
          <h3 className="subsection-title">Expériences professionnelles</h3>
          {work_experience.map((exp, index) => (
            <div key={index} className="experience-item">
              <div className="job-header">
                <h4 className="job-title">{exp.title}</h4>
                <div className="company-info">
                  <span className="company-name">{exp.company}</span>
                  {exp.location && <span className="location">{exp.location}</span>}
                </div>
                <div className="date-range">
                  {exp.start_date} - {exp.current ? 'Présent' : exp.end_date}
                </div>
              </div>
              
              {exp.description && (
                <p className="description">{exp.description}</p>
              )}
              
              {exp.achievements && exp.achievements.length > 0 && (
                <div className="achievements">
                  <h5>Réalisations</h5>
                  <ul>
                    {exp.achievements.map((achievement, achIndex) => (
                      <li key={achIndex}>{achievement}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {exp.skills && exp.skills.length > 0 && (
                <div className="job-skills">
                  <h5>Technologies utilisées</h5>
                  <div className="skills-list">
                    {exp.skills.map((skill, skillIndex) => (
                      <span key={skillIndex} className="skill-tag small">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      {/* Formation */}
      {education && education.length > 0 && (
        <div className="section">
          <h3 className="subsection-title">Formation</h3>
          {education.map((edu, index) => (
            <div key={index} className="education-item">
              <div className="education-header">
                <h4 className="degree">{edu.degree}</h4>
                <div className="institution-info">
                  <span className="institution">{edu.institution}</span>
                  {edu.location && <span className="location">{edu.location}</span>}
                </div>
                <div className="date-range">
                  {edu.start_date} - {edu.end_date}
                </div>
              </div>
              
              {edu.gpa && (
                <div className="gpa">GPA: {edu.gpa}</div>
              )}
              
              {edu.description && (
                <p className="description">{edu.description}</p>
              )}
            </div>
          ))}
        </div>
      )}
      
      {/* Langues */}
      {languages && languages.length > 0 && (
        <div className="section">
          <h3 className="subsection-title">Langues</h3>
          <div className="languages-list">
            {languages.map((lang, index) => (
              <div key={index} className="language-item">
                <span className="language">{lang.language}</span>
                <span className="level">{lang.level}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Certifications */}
      {certifications && certifications.length > 0 && (
        <div className="section">
          <h3 className="subsection-title">Certifications</h3>
          <ul className="certifications-list">
            {certifications.map((cert, index) => (
              <li key={index}>{cert}</li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Projets */}
      {projects && projects.length > 0 && (
        <div className="section">
          <h3 className="subsection-title">Projets</h3>
          {projects.map((project, index) => (
            <div key={index} className="project-item">
              <div className="project-header">
                <h4 className="project-title">
                  {project.url ? (
                    <a href={project.url} target="_blank" rel="noopener noreferrer">
                      {project.name}
                    </a>
                  ) : (
                    project.name
                  )}
                </h4>
              </div>
              
              <p className="description">{project.description}</p>
              
              {project.technologies && project.technologies.length > 0 && (
                <div className="project-technologies">
                  <div className="skills-list">
                    {project.technologies.map((tech, techIndex) => (
                      <span key={techIndex} className="skill-tag small">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        .cv-viewer {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
          color: #333;
        }
        
        .section {
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 1px solid #eee;
        }
        
        .section:last-child {
          border-bottom: none;
        }
        
        .section-title {
          font-size: 26px;
          color: #2c3e50;
          margin-bottom: 20px;
          padding-bottom: 10px;
          border-bottom: 2px solid #3498db;
        }
        
        .subsection-title {
          font-size: 20px;
          color: #2c3e50;
          margin-bottom: 15px;
        }
        
        .personal-info h3 {
          font-size: 24px;
          margin-bottom: 15px;
        }
        
        .contact-info {
          display: flex;
          flex-wrap: wrap;
          margin-bottom: 15px;
        }
        
        .info-item {
          margin-right: 20px;
          margin-bottom: 8px;
        }
        
        .label {
          font-weight: bold;
          color: #666;
        }
        
        .summary h4 {
          font-size: 16px;
          margin-bottom: 5px;
          color: #555;
        }
        
        .skills-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        
        .skill-tag {
          background-color: #f0f7ff;
          color: #3498db;
          padding: 5px 10px;
          border-radius: 4px;
          font-size: 14px;
          border: 1px solid #d6e9ff;
        }
        
        .skill-tag.small {
          font-size: 12px;
          padding: 3px 8px;
        }
        
        .experience-item, .education-item, .project-item {
          margin-bottom: 20px;
          padding: 15px;
          background-color: #f9f9f9;
          border-radius: 4px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .job-header, .education-header, .project-header {
          margin-bottom: 10px;
        }
        
        .job-title, .degree, .project-title {
          font-size: 18px;
          margin: 0 0 5px;
          color: #2980b9;
        }
        
        .company-info, .institution-info {
          display: flex;
          font-size: 16px;
          margin-bottom: 5px;
        }
        
        .company-name, .institution {
          font-weight: bold;
          margin-right: 10px;
        }
        
        .location {
          color: #777;
        }
        
        .date-range {
          font-style: italic;
          color: #666;
          font-size: 14px;
          margin-bottom: 10px;
        }
        
        .description {
          margin-bottom: 15px;
          line-height: 1.5;
        }
        
        .achievements h5, .job-skills h5 {
          font-size: 15px;
          margin: 10px 0 5px;
          color: #555;
        }
        
        .achievements ul {
          margin-left: 20px;
        }
        
        .achievements li {
          margin-bottom: 5px;
        }
        
        .languages-list {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 10px;
        }
        
        .language-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 12px;
          background-color: #f9f9f9;
          border-radius: 4px;
        }
        
        .language {
          font-weight: bold;
        }
        
        .level {
          color: #666;
        }
        
        .certifications-list li {
          margin-bottom: 5px;
        }
        
        a {
          color: #3498db;
          text-decoration: none;
        }
        
        a:hover {
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
};

export default CVViewer;
