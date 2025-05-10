/**
 * Script pour l'amélioration de l'expérience utilisateur
 * de la page CV du projet Nexten
 */

document.addEventListener('DOMContentLoaded', function() {
    // Menu mobile toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Animation au défilement
    const animatedElements = document.querySelectorAll('.fade-in, .scale-in, .slide-in-left, .slide-in-right');
    
    function checkIfInView() {
        const windowHeight = window.innerHeight;
        const windowTop = window.scrollY;
        const windowBottom = windowTop + windowHeight;
        
        animatedElements.forEach(function(element) {
            const elementTop = element.getBoundingClientRect().top + windowTop;
            const elementBottom = elementTop + element.offsetHeight;
            
            // Si l'élément est visible dans la fenêtre
            if (elementBottom > windowTop && elementTop < windowBottom) {
                element.classList.add('visible');
            }
        });
    }
    
    // Vérifier au chargement de la page
    checkIfInView();
    
    // Vérifier lors du défilement
    window.addEventListener('scroll', checkIfInView);
    
    // Navigation par ancre active
    const navLinks = document.querySelectorAll('.cv-nav-link');
    const sections = document.querySelectorAll('.cv-section');
    
    function setActiveNavLink() {
        let currentSection = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            
            if (window.scrollY >= (sectionTop - 150)) {
                currentSection = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSection}`) {
                link.classList.add('active');
            }
        });
    }
    
    window.addEventListener('scroll', setActiveNavLink);
    
    // Défilement fluide pour les liens d'ancrage
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Bouton de retour en haut
    const backToTop = document.getElementById('back-to-top');
    
    if (backToTop) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });
        
        backToTop.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Bouton de retour en haut du footer
    const scrollToTopButton = document.getElementById('scroll-to-top');
    
    if (scrollToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 500) {
                scrollToTopButton.classList.add('visible');
            } else {
                scrollToTopButton.classList.remove('visible');
            }
        });
        
        scrollToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Notification de sauvegarde
    const saveButton = document.getElementById('save-cv');
    const saveNotification = document.getElementById('save-notification');
    
    if (saveButton && saveNotification) {
        saveButton.addEventListener('click', function() {
            saveNotification.classList.add('show');
            
            setTimeout(function() {
                saveNotification.classList.remove('show');
            }, 3000);
        });
    }
    
    // Suggestions de compétences
    const skillInput = document.querySelector('.add-skill input');
    const skillSuggestions = document.querySelector('.skill-suggestions');
    const suggestionItems = document.querySelectorAll('.skill-suggestion-item');
    
    if (skillInput && skillSuggestions) {
        skillInput.addEventListener('focus', function() {
            skillSuggestions.classList.add('active');
        });
        
        skillInput.addEventListener('blur', function() {
            // Petit délai pour permettre la sélection d'une suggestion
            setTimeout(function() {
                skillSuggestions.classList.remove('active');
            }, 150);
        });
        
        // Filtrer les suggestions en fonction de la saisie
        skillInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            
            suggestionItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Afficher les suggestions si l'input n'est pas vide
            if (query.length > 0) {
                skillSuggestions.classList.add('active');
            } else {
                skillSuggestions.classList.remove('active');
            }
        });
        
        // Sélectionner une suggestion
        suggestionItems.forEach(item => {
            item.addEventListener('mousedown', function() {
                skillInput.value = this.textContent;
                skillSuggestions.classList.remove('active');
            });
        });
    }
    
    // Amélioration de l'expérience utilisateur pour les compétences
    const skillTags = document.querySelectorAll('.skill-tag');
    
    skillTags.forEach(function(tag) {
        const deleteIcon = tag.querySelector('i.fa-times-circle');
        const addIcon = tag.querySelector('i.fa-plus-circle');
        
        if (deleteIcon) {
            deleteIcon.addEventListener('click', function(e) {
                e.stopPropagation();
                tag.style.opacity = '0';
                tag.style.transform = 'translateY(10px)';
                setTimeout(function() {
                    tag.remove();
                }, 300);
            });
        }
        
        if (addIcon) {
            addIcon.addEventListener('click', function(e) {
                e.stopPropagation();
                const skillsContainer = document.querySelector('.skills-container');
                const skillText = tag.textContent.trim().replace(' plus', '');
                
                const newTag = document.createElement('div');
                newTag.className = 'skill-tag';
                newTag.innerHTML = skillText + ' <i class="fas fa-times-circle"></i>';
                
                // Animation d'ajout
                newTag.style.opacity = '0';
                newTag.style.transform = 'translateY(10px)';
                
                skillsContainer.appendChild(newTag);
                
                setTimeout(function() {
                    newTag.style.opacity = '1';
                    newTag.style.transform = 'translateY(0)';
                }, 10);
                
                // Ajouter l'événement de suppression au nouveau tag
                const newDeleteIcon = newTag.querySelector('i.fa-times-circle');
                if (newDeleteIcon) {
                    newDeleteIcon.addEventListener('click', function(e) {
                        e.stopPropagation();
                        newTag.style.opacity = '0';
                        newTag.style.transform = 'translateY(10px)';
                        setTimeout(function() {
                            newTag.remove();
                        }, 300);
                    });
                }
                
                // Supprimer la suggestion après l'avoir ajoutée
                tag.style.opacity = '0';
                tag.style.transform = 'translateY(10px)';
                setTimeout(function() {
                    tag.remove();
                }, 300);
            });
        }
    });
    
    // Ajout de nouvelles compétences
    const addSkillForm = document.querySelector('.add-skill');
    if (addSkillForm) {
        const skillInput = addSkillForm.querySelector('input');
        const addButton = addSkillForm.querySelector('button');
        
        addButton.addEventListener('click', function() {
            addSkill();
        });
        
        skillInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSkill();
            }
        });
        
        function addSkill() {
            const skillName = skillInput.value.trim();
            if (skillName) {
                const skillsContainer = document.querySelector('.skills-container');
                const newTag = document.createElement('div');
                newTag.className = 'skill-tag';
                newTag.innerHTML = skillName + ' <i class="fas fa-times-circle"></i>';
                
                // Animation d'ajout
                newTag.style.opacity = '0';
                newTag.style.transform = 'translateY(10px)';
                
                skillsContainer.appendChild(newTag);
                
                setTimeout(function() {
                    newTag.style.opacity = '1';
                    newTag.style.transform = 'translateY(0)';
                }, 10);
                
                // Vider l'input
                skillInput.value = '';
                
                // Ajouter l'événement de suppression au nouveau tag
                const newDeleteIcon = newTag.querySelector('i.fa-times-circle');
                if (newDeleteIcon) {
                    newDeleteIcon.addEventListener('click', function(e) {
                        e.stopPropagation();
                        newTag.style.opacity = '0';
                        newTag.style.transform = 'translateY(10px)';
                        setTimeout(function() {
                            newTag.remove();
                        }, 300);
                    });
                }
            }
        }
    }
});