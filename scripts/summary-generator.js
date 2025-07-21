// Summary Generator Script
// Génère automatiquement le récapitulatif des informations saisies

class SummaryGenerator {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('✅ Summary Generator initialisé');
    }
    
    // Générer le récapitulatif complet
    generateFullSummary() {
        const summary = {
            company: this.getCompanyInfo(),
            contact: this.getContactInfo(),
            recruitment: this.getRecruitmentInfo(),
            jobDetails: this.getJobDetails()
        };
        
        return summary;
    }
    
    // Informations sur l'entreprise
    getCompanyInfo() {
        return {
            name: this.getFieldValue('company-name'),
            address: this.getFieldValue('company-address'),
            website: this.getFieldValue('company-website'),
            description: this.getFieldValue('company-description'),
            size: this.getFieldValue('company-size')
        };
    }
    
    // Informations de contact
    getContactInfo() {
        return {
            name: this.getFieldValue('contact-name'),
            title: this.getFieldValue('contact-title'),
            email: this.getFieldValue('contact-email'),
            phone: this.getFieldValue('contact-phone'),
            preferredMethod: this.getFieldValue('contact-preferred')
        };
    }
    
    // Informations sur le recrutement
    getRecruitmentInfo() {
        const hasRecruitmentNeed = document.querySelector('input[name="recruitment-need"]:checked');
        
        return {
            hasNeed: hasRecruitmentNeed ? hasRecruitmentNeed.value === 'yes' : false,
            needValue: hasRecruitmentNeed ? hasRecruitmentNeed.value : null
        };
    }
    
    // Détails du poste (si extraction effectuée)
    getJobDetails() {
        return {
            title: this.getFieldValue('job-title-value'),
            contract: this.getFieldValue('job-contract-value'),
            location: this.getFieldValue('job-location-value'),
            experience: this.getFieldValue('job-experience-value'),
            education: this.getFieldValue('job-education-value'),
            salary: this.getFieldValue('job-salary-value'),
            responsibilities: this.getFieldValue('job-responsibilities-value'),
            benefits: this.getFieldValue('job-benefits-value'),
            skills: this.getSkillsList()
        };
    }
    
    // Obtenir la liste des compétences
    getSkillsList() {
        const skillsContainer = document.getElementById('job-skills-value');
        if (!skillsContainer) return [];
        
        const skillTags = skillsContainer.querySelectorAll('.tag');
        return Array.from(skillTags).map(tag => tag.textContent.trim());
    }
    
    // Obtenir la valeur d'un champ
    getFieldValue(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return '';
        
        if (field.tagName === 'INPUT' || field.tagName === 'TEXTAREA' || field.tagName === 'SELECT') {
            return field.value.trim();
        } else {
            return field.textContent.trim();
        }
    }
    
    // Générer le HTML du récapitulatif
    generateSummaryHTML() {
        const summary = this.generateFullSummary();
        
        let html = '';
        
        // Section entreprise
        if (this.hasCompanyInfo(summary.company)) {
            html += this.generateCompanySection(summary.company);
        }
        
        // Section contact
        if (this.hasContactInfo(summary.contact)) {
            html += this.generateContactSection(summary.contact);
        }
        
        // Section recrutement
        html += this.generateRecruitmentSection(summary.recruitment, summary.jobDetails);
        
        return html;
    }
    
    // Vérifier si les informations entreprise sont renseignées
    hasCompanyInfo(company) {
        return company.name || company.address || company.website || company.description || company.size;
    }
    
    // Vérifier si les informations contact sont renseignées
    hasContactInfo(contact) {
        return contact.name || contact.email || contact.phone || contact.title;
    }
    
    // Générer la section entreprise
    generateCompanySection(company) {
        let html = '<div class=\"summary-section\">';
        html += '<h4><i class=\"fas fa-building\"></i> Informations de l\'entreprise</h4>';
        
        if (company.name) {
            html += `<p><strong>Nom :</strong> ${company.name}</p>`;
        }
        
        if (company.address) {
            html += `<p><strong>Adresse :</strong> ${company.address}</p>`;
        }
        
        if (company.website) {
            html += `<p><strong>Site web :</strong> <a href=\"${company.website}\" target=\"_blank\">${company.website}</a></p>`;
        }
        
        if (company.size) {
            const sizeLabel = this.getSizeLabel(company.size);
            html += `<p><strong>Taille :</strong> ${sizeLabel}</p>`;
        }
        
        if (company.description) {
            html += `<p><strong>Description :</strong> ${company.description}</p>`;
        }
        
        html += '</div>';
        return html;
    }
    
    // Générer la section contact
    generateContactSection(contact) {
        let html = '<div class=\"summary-section\">';
        html += '<h4><i class=\"fas fa-user\"></i> Informations de contact</h4>';
        
        if (contact.name) {
            html += `<p><strong>Nom :</strong> ${contact.name}</p>`;
        }
        
        if (contact.title) {
            html += `<p><strong>Fonction :</strong> ${contact.title}</p>`;
        }
        
        if (contact.email) {
            html += `<p><strong>Email :</strong> <a href=\"mailto:${contact.email}\">${contact.email}</a></p>`;
        }
        
        if (contact.phone) {
            html += `<p><strong>Téléphone :</strong> <a href=\"tel:${contact.phone}\">${contact.phone}</a></p>`;
        }
        
        if (contact.preferredMethod) {
            const methodLabel = this.getContactMethodLabel(contact.preferredMethod);
            html += `<p><strong>Méthode de contact préférée :</strong> ${methodLabel}</p>`;
        }
        
        html += '</div>';
        return html;
    }
    
    // Générer la section recrutement
    generateRecruitmentSection(recruitment, jobDetails) {
        let html = '<div class=\"summary-section\">';
        html += '<h4><i class=\"fas fa-user-plus\"></i> Besoin en recrutement</h4>';
        
        if (recruitment.needValue === 'yes') {
            html += '<p><strong>Besoin de recrutement :</strong> <span class=\"text-success\">Oui</span></p>';
            
            // Si des détails de poste ont été extraits
            if (this.hasJobDetails(jobDetails)) {
                html += this.generateJobDetailsHTML(jobDetails);
            }
        } else if (recruitment.needValue === 'no') {
            html += '<p><strong>Besoin de recrutement :</strong> <span class=\"text-muted\">Non</span></p>';
        } else {
            html += '<p><strong>Besoin de recrutement :</strong> <em>Non spécifié</em></p>';
        }
        
        html += '</div>';
        return html;
    }
    
    // Vérifier si des détails de poste sont disponibles
    hasJobDetails(jobDetails) {
        return jobDetails.title && jobDetails.title !== 'Non spécifié' && 
               (jobDetails.contract !== 'Non spécifié' || 
                jobDetails.location !== 'Non spécifié' || 
                jobDetails.skills.length > 0);
    }
    
    // Générer le HTML des détails du poste
    generateJobDetailsHTML(jobDetails) {
        let html = '<div class=\"job-details-summary\">';
        html += '<h5 style=\"margin-top: 1rem; margin-bottom: 0.5rem; color: var(--primary);\">Détails du poste</h5>';
        
        if (jobDetails.title && jobDetails.title !== 'Non spécifié') {
            html += `<p><strong>Titre :</strong> ${jobDetails.title}</p>`;
        }
        
        if (jobDetails.contract && jobDetails.contract !== 'Non spécifié') {
            html += `<p><strong>Type de contrat :</strong> ${jobDetails.contract}</p>`;
        }
        
        if (jobDetails.location && jobDetails.location !== 'Non spécifié') {
            html += `<p><strong>Lieu :</strong> ${jobDetails.location}</p>`;
        }
        
        if (jobDetails.experience && jobDetails.experience !== 'Non spécifié') {
            html += `<p><strong>Expérience :</strong> ${jobDetails.experience}</p>`;
        }
        
        if (jobDetails.salary && jobDetails.salary !== 'Non spécifié') {
            html += `<p><strong>Rémunération :</strong> ${jobDetails.salary}</p>`;
        }
        
        if (jobDetails.skills && jobDetails.skills.length > 0) {
            html += '<p><strong>Compétences :</strong> ';
            jobDetails.skills.forEach((skill, index) => {
                html += `<span class=\"tag\" style=\"font-size: 0.8rem; margin: 2px;\">${skill}</span>`;
            });
            html += '</p>';
        }
        
        html += '</div>';
        return html;
    }
    
    // Obtenir le label de la taille d'entreprise
    getSizeLabel(size) {
        const sizeLabels = {
            'tpe': 'TPE (Très Petite Entreprise)',
            'pme': 'PME (Petite et Moyenne Entreprise)',
            'eti': 'ETI (Entreprise de Taille Intermédiaire)',
            'groupe': 'Groupe / Grande Entreprise',
            'startup': 'Startup'
        };
        
        return sizeLabels[size] || size;
    }
    
    // Obtenir le label de la méthode de contact
    getContactMethodLabel(method) {
        const methodLabels = {
            'email': 'Email',
            'phone': 'Téléphone',
            'video': 'Visioconférence'
        };
        
        return methodLabels[method] || method;
    }
    
    // Mettre à jour l'affichage du récapitulatif
    updateSummaryDisplay() {
        const summaryContent = document.getElementById('summary-content');
        if (!summaryContent) return;
        
        const html = this.generateSummaryHTML();
        summaryContent.innerHTML = html;
    }
    
    // Générer un récapitulatif en format JSON pour l'API
    generateJSONSummary() {
        return JSON.stringify(this.generateFullSummary(), null, 2);
    }
    
    // Générer un récapitulatif en format texte simple
    generateTextSummary() {
        const summary = this.generateFullSummary();
        let text = 'RÉCAPITULATIF DU QUESTIONNAIRE CLIENT\n';
        text += '======================================\n\n';
        
        // Entreprise
        if (this.hasCompanyInfo(summary.company)) {
            text += 'ENTREPRISE\n';
            text += '----------\n';
            if (summary.company.name) text += `Nom: ${summary.company.name}\n`;
            if (summary.company.address) text += `Adresse: ${summary.company.address}\n`;
            if (summary.company.website) text += `Site web: ${summary.company.website}\n`;
            if (summary.company.size) text += `Taille: ${this.getSizeLabel(summary.company.size)}\n`;
            if (summary.company.description) text += `Description: ${summary.company.description}\n`;
            text += '\n';
        }
        
        // Contact
        if (this.hasContactInfo(summary.contact)) {
            text += 'CONTACT\n';
            text += '-------\n';
            if (summary.contact.name) text += `Nom: ${summary.contact.name}\n`;
            if (summary.contact.title) text += `Fonction: ${summary.contact.title}\n`;
            if (summary.contact.email) text += `Email: ${summary.contact.email}\n`;
            if (summary.contact.phone) text += `Téléphone: ${summary.contact.phone}\n`;
            text += '\n';
        }
        
        // Recrutement
        text += 'RECRUTEMENT\n';
        text += '-----------\n';
        if (summary.recruitment.needValue === 'yes') {
            text += 'Besoin de recrutement: Oui\n';
            if (this.hasJobDetails(summary.jobDetails)) {
                if (summary.jobDetails.title) text += `Poste: ${summary.jobDetails.title}\n`;
                if (summary.jobDetails.contract) text += `Contrat: ${summary.jobDetails.contract}\n`;
                if (summary.jobDetails.location) text += `Lieu: ${summary.jobDetails.location}\n`;
            }
        } else if (summary.recruitment.needValue === 'no') {
            text += 'Besoin de recrutement: Non\n';
        } else {
            text += 'Besoin de recrutement: Non spécifié\n';
        }
        
        return text;
    }
}

// Initialiser le générateur de récapitulatif
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        window.summaryGenerator = new SummaryGenerator();
    }, 300);
});

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SummaryGenerator;
}