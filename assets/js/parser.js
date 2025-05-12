/**
 * Job Description Parser
 * Extracts key information from job descriptions
 */

// Main function to parse job description
function parseJobDescription(text) {
    if (!text || typeof text !== 'string') {
        return {
            error: 'Invalid job description'
        };
    }

    return {
        title: extractJobTitle(text),
        company: extractCompanyName(text),
        location: extractLocation(text),
        skills: extractSkills(text),
        experience: extractExperience(text),
        responsibilities: extractResponsibilities(text),
        requirements: extractRequirements(text),
        salary: extractSalary(text),
        benefits: extractBenefits(text),
        applicationProcess: extractApplicationProcess(text)
    };
}

// Function to extract job title
function extractJobTitle(text) {
    // Common patterns for job titles
    const titlePatterns = [
        /job title:?\s*([^,\n.]+)/i,
        /position:?\s*([^,\n.]+)/i,
        /role:?\s*([^,\n.]+)/i,
        /poste:?\s*([^,\n.]+)/i,
        /intitulé:?\s*([^,\n.]+)/i
    ];

    // Try each pattern
    for (const pattern of titlePatterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
            return match[1].trim();
        }
    }

    // Fallback: Look for the first line that might be a title
    const lines = text.split('\n');
    for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed && trimmed.length < 100 && !trimmed.includes(':')) {
            return trimmed;
        }
    }

    return 'Unknown Position';
}

// Function to extract company name
function extractCompanyName(text) {
    const companyPatterns = [
        /company:?\s*([^,\n.]+)/i,
        /at\s+([^,\n.]+)/i,
        /with\s+([^,\n.]+)/i,
        /entreprise:?\s*([^,\n.]+)/i,
        /société:?\s*([^,\n.]+)/i,
        /chez\s+([^,\n.]+)/i
    ];

    for (const pattern of companyPatterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
            return match[1].trim();
        }
    }

    return 'Unknown Company';
}

// Function to extract location
function extractLocation(text) {
    const locationPatterns = [
        /location:?\s*([^,\n.]+)/i,
        /based in:?\s*([^,\n.]+)/i,
        /lieu:?\s*([^,\n.]+)/i,
        /localisation:?\s*([^,\n.]+)/i,
        /basé à:?\s*([^,\n.]+)/i,
        /remote|work from home|wfh|on-site|hybrid|télétravail|présentiel|hybride/i
    ];

    for (const pattern of locationPatterns) {
        const match = text.match(pattern);
        if (match) {
            if (match[1]) {
                return match[1].trim();
            } else if (match[0]) {
                return match[0].trim();
            }
        }
    }

    return 'Unknown Location';
}

// Function to extract skills
function extractSkills(text) {
    const skillsSection = extractSection(text, 
        /(skills|technologies|technical requirements|qualifications|requirements|what you'll need|compétences|technologies requises|qualifications|prérequis)/i, 
        /(responsibilities|about the role|benefits|about the company|what you'll do|responsabilités|missions|avantages|à propos)/i
    );

    if (skillsSection) {
        // Extract skills using bullet points or commas
        const skillsList = [];
        const bulletItems = skillsSection.match(/[•\-*]\s*([^\n]+)/g);
        
        if (bulletItems) {
            bulletItems.forEach(item => {
                const skill = item.replace(/[•\-*]\s*/, '').trim();
                if (skill) skillsList.push(skill);
            });
        }
        
        // If no bullet points, try splitting by commas or semicolons
        if (skillsList.length === 0) {
            const skills = skillsSection.split(/[,;]/).map(s => s.trim()).filter(s => s.length > 0);
            skillsList.push(...skills);
        }
        
        return skillsList.length > 0 ? skillsList : ['Not specified'];
    }
    
    return ['Not specified'];
}

// Function to extract experience requirements
function extractExperience(text) {
    const experiencePatterns = [
        /(\d+)\+?\s*years? experience/i,
        /experience:?\s*(\d+)\+?\s*years?/i,
        /minimum of\s*(\d+)\+?\s*years?/i,
        /(\d+)\s*\+\s*years/i,
        /(\d+)\+?\s*ans? d'expérience/i,
        /expérience:?\s*(\d+)\+?\s*ans?/i,
        /minimum de\s*(\d+)\+?\s*ans?/i,
        /(\d+)\s*\+\s*ans/i
    ];

    for (const pattern of experiencePatterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
            return `${match[1]} years`;
        }
    }

    if (text.match(/entry level|junior|no experience required|beginner|débutant|aucune expérience requise/i)) {
        return 'Entry Level';
    }

    if (text.match(/mid level|intermediate|confirmé|intermédiaire/i)) {
        return 'Mid Level';
    }

    if (text.match(/senior|expert|lead|principal|chevronné/i)) {
        return 'Senior Level';
    }

    return 'Not specified';
}

// Function to extract responsibilities
function extractResponsibilities(text) {
    const responsibilitiesSection = extractSection(text, 
        /(responsibilities|duties|what you'll do|the role|job description|about the role|responsabilités|missions|tâches|description du poste)/i, 
        /(requirements|qualifications|skills|about the company|about us|benefits|perks|prérequis|compétences|à propos|avantages)/i
    );

    if (responsibilitiesSection) {
        const responsibilities = [];
        const bulletItems = responsibilitiesSection.match(/[•\-*]\s*([^\n]+)/g);
        
        if (bulletItems) {
            bulletItems.forEach(item => {
                const responsibility = item.replace(/[•\-*]\s*/, '').trim();
                if (responsibility) responsibilities.push(responsibility);
            });
        }
        
        // If no bullet points found, use sentences
        if (responsibilities.length === 0) {
            const sentences = responsibilitiesSection.match(/[^.!?]+[.!?]+/g);
            if (sentences) {
                sentences.forEach(sentence => {
                    const trimmed = sentence.trim();
                    if (trimmed && !trimmed.match(/^(responsibilities|duties|what you'll do|the role|responsabilités|missions):/i)) {
                        responsibilities.push(trimmed);
                    }
                });
            }
        }
        
        return responsibilities.length > 0 ? responsibilities : ['Not specified'];
    }
    
    return ['Not specified'];
}

// Function to extract requirements
function extractRequirements(text) {
    const requirementsSection = extractSection(text, 
        /(requirements|qualifications|what you'll need|what we're looking for|who you are|prérequis|qualifications|profil recherché|qui vous êtes)/i, 
        /(benefits|perks|what we offer|about the company|about us|application|salary|avantages|ce que nous offrons|à propos|candidature|salaire)/i
    );

    if (requirementsSection) {
        const requirements = [];
        const bulletItems = requirementsSection.match(/[•\-*]\s*([^\n]+)/g);
        
        if (bulletItems) {
            bulletItems.forEach(item => {
                const requirement = item.replace(/[•\-*]\s*/, '').trim();
                if (requirement) requirements.push(requirement);
            });
        }
        
        // If no bullet points found, use sentences
        if (requirements.length === 0) {
            const sentences = requirementsSection.match(/[^.!?]+[.!?]+/g);
            if (sentences) {
                sentences.forEach(sentence => {
                    const trimmed = sentence.trim();
                    if (trimmed && !trimmed.match(/^(requirements|qualifications|what you'll need|prérequis):/i)) {
                        requirements.push(trimmed);
                    }
                });
            }
        }
        
        return requirements.length > 0 ? requirements : ['Not specified'];
    }
    
    return ['Not specified'];
}

// Function to extract salary information
function extractSalary(text) {
    const salaryPatterns = [
        /salary:?\s*([^,\n.]+)/i,
        /compensation:?\s*([^,\n.]+)/i,
        /\$(\d+,?\d*)\s*-\s*\$?(\d+,?\d*)/i,
        /(\d+,?\d*)\s*-\s*(\d+,?\d*)\s*\$/i,
        /\$(\d+,?\d*)/i,
        /salaire:?\s*([^,\n.]+)/i,
        /rémunération:?\s*([^,\n.]+)/i,
        /(\d+,?\d*)\s*-\s*(\d+,?\d*)\s*€/i,
        /(\d+,?\d*)\s*€/i
    ];

    for (const pattern of salaryPatterns) {
        const match = text.match(pattern);
        if (match) {
            if (match[1] && match[2]) {
                // Check if currency symbol was included
                if (text.includes('€')) {
                    return `${match[1]} - ${match[2]} €`;
                } else {
                    return `$${match[1]} - $${match[2]}`;
                }
            } else if (match[1]) {
                if (match[1].includes('$')) {
                    return match[1].trim();
                } else if (text.includes('€')) {
                    return `${match[1].trim()} €`;
                } else {
                    return `$${match[1].trim()}`;
                }
            }
        }
    }

    return 'Not specified';
}

// Function to extract benefits
function extractBenefits(text) {
    const benefitsSection = extractSection(text, 
        /(benefits|perks|what we offer|why join us|avantages|ce que nous offrons|pourquoi nous rejoindre)/i, 
        /(application|apply|how to apply|contact|candidature|postuler|comment postuler|contact)/i
    );

    if (benefitsSection) {
        const benefits = [];
        const bulletItems = benefitsSection.match(/[•\-*]\s*([^\n]+)/g);
        
        if (bulletItems) {
            bulletItems.forEach(item => {
                const benefit = item.replace(/[•\-*]\s*/, '').trim();
                if (benefit) benefits.push(benefit);
            });
        }
        
        // If no bullet points found, use sentences
        if (benefits.length === 0) {
            const sentences = benefitsSection.match(/[^.!?]+[.!?]+/g);
            if (sentences) {
                sentences.forEach(sentence => {
                    const trimmed = sentence.trim();
                    if (trimmed && !trimmed.match(/^(benefits|perks|what we offer|avantages):/i)) {
                        benefits.push(trimmed);
                    }
                });
            }
        }
        
        return benefits.length > 0 ? benefits : ['Not specified'];
    }
    
    return ['Not specified'];
}

// Function to extract application process
function extractApplicationProcess(text) {
    const applicationSection = extractSection(text, 
        /(how to apply|application process|application|apply|to apply|comment postuler|processus de candidature|candidature|postuler|pour postuler)/i, 
        /(about us|company|à propos|entreprise|$)/i
    );

    if (applicationSection) {
        // Look for email address
        const emailMatch = applicationSection.match(/[\w.-]+@[\w.-]+\.\w+/);
        if (emailMatch) {
            return `Apply by sending your application to ${emailMatch[0]}`;
        }
        
        // Look for URL
        const urlMatch = applicationSection.match(/https?:\/\/\S+/);
        if (urlMatch) {
            return `Apply online at ${urlMatch[0]}`;
        }
        
        // Return the section as is
        return applicationSection.trim();
    }
    
    return 'Not specified';
}

// Helper function to extract a section of text between two patterns
function extractSection(text, startPattern, endPattern) {
    const startMatch = text.match(startPattern);
    if (!startMatch) return null;
    
    const startIndex = startMatch.index + startMatch[0].length;
    
    const endMatch = text.substr(startIndex).match(endPattern);
    const endIndex = endMatch ? startIndex + endMatch.index : text.length;
    
    return text.substring(startIndex, endIndex).trim();
}

// Export functions for use in other files
window.JobParser = {
    parseJobDescription,
    extractJobTitle,
    extractCompanyName,
    extractLocation,
    extractSkills,
    extractExperience,
    extractResponsibilities,
    extractRequirements,
    extractSalary,
    extractBenefits,
    extractApplicationProcess
};