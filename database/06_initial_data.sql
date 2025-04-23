-- 1. Insérer des données de configuration système
INSERT INTO analytics.system_config (key, value, description)
VALUES 
('matching_weights', 
 '{
    "skills_weight": 0.6,
    "experience_weight": 0.3,
    "location_weight": 0.1,
    "skills_params": {
        "required_weight": 1.0,
        "optional_weight": 0.5
    }
 }', 
 'Pondérations pour l''algorithme de matching standard');

-- 2. Insérer un algorithme de matching par défaut
INSERT INTO matching.matching_algorithms (name, description, parameters, is_active)
VALUES (
    'default_algorithm',
    'Algorithme standard de matching avec pondération équilibrée',
    '{
        "skills_weight": 0.6,
        "experience_weight": 0.3,
        "location_weight": 0.1,
        "skills_params": {
            "required_weight": 1.0,
            "optional_weight": 0.5
        }
    }',
    true
);

-- 3. Insérer des catégories de compétences initiales
INSERT INTO profiles.skill_categories (name, parent_id, level)
VALUES 
('Développement', NULL, 0),
('Frontend', 1, 1),
('Backend', 1, 1),
('DevOps', 1, 1),
('Mobile', 1, 1),
('Intelligence Artificielle', NULL, 0),
('Machine Learning', 6, 1),
('Deep Learning', 6, 1),
('NLP', 6, 1),
('Data', NULL, 0),
('Data Science', 10, 1),
('Data Engineering', 10, 1),
('Business Intelligence', 10, 1),
('Management', NULL, 0),
('Gestion de Projet', 14, 1),
('Leadership', 14, 1),
('Design', NULL, 0),
('UX/UI', 17, 1),
('Graphisme', 17, 1);

-- 4. Insérer quelques compétences initiales
INSERT INTO profiles.skills (name, category_id, description, aliases)
VALUES 
('JavaScript', 2, 'Langage de programmation pour le web', ARRAY['js', 'ecmascript']),
('React', 2, 'Bibliothèque JavaScript pour créer des interfaces utilisateur', ARRAY['reactjs', 'react.js']),
('Vue.js', 2, 'Framework JavaScript progressif', ARRAY['vue', 'vuejs']),
('Angular', 2, 'Framework web développé par Google', ARRAY['angular.js', 'ng']),
('HTML', 2, 'Langage de balisage pour les pages web', ARRAY['html5']),
('CSS', 2, 'Langage de style pour les pages web', ARRAY['css3', 'scss', 'sass']),
('Python', 3, 'Langage de programmation interprété', ARRAY['py']),
('Java', 3, 'Langage de programmation orienté objet', ARRAY['jvm']),
('Node.js', 3, 'Environnement d''exécution JavaScript côté serveur', ARRAY['nodejs', 'node']),
('PHP', 3, 'Langage de script côté serveur', NULL),
('C#', 3, 'Langage de programmation orienté objet développé par Microsoft', ARRAY['csharp', 'dotnet']),
('Ruby', 3, 'Langage de programmation dynamique', ARRAY['rails', 'ruby on rails']),
('SQL', 11, 'Langage de requête structurée pour bases de données', NULL),
('PostgreSQL', 11, 'Système de gestion de base de données relationnelle', ARRAY['postgres']),
('MySQL', 11, 'Système de gestion de base de données relationnelle', NULL),
('MongoDB', 11, 'Base de données NoSQL orientée documents', ARRAY['mongo']),
('Docker', 4, 'Plateforme de conteneurisation', NULL),
('Kubernetes', 4, 'Système d''orchestration de conteneurs', ARRAY['k8s']),
('AWS', 4, 'Amazon Web Services, plateforme de cloud computing', NULL),
('Azure', 4, 'Microsoft Azure, plateforme de cloud computing', NULL),
('Swift', 5, 'Langage de programmation pour iOS et macOS', NULL),
('Kotlin', 5, 'Langage de programmation pour Android', NULL),
('Flutter', 5, 'Framework UI pour des applications mobiles multi-plateformes', NULL),
('React Native', 5, 'Framework pour le développement d''applications mobiles', ARRAY['reactnative']),
('TensorFlow', 7, 'Bibliothèque open-source pour l''apprentissage automatique', NULL),
('PyTorch', 7, 'Bibliothèque open-source pour l''apprentissage automatique', NULL),
('scikit-learn', 7, 'Bibliothèque d''apprentissage automatique pour Python', ARRAY['sklearn']),
('NLTK', 9, 'Natural Language Toolkit, bibliothèque pour le traitement du langage naturel', NULL),
('spaCy', 9, 'Bibliothèque pour le traitement avancé du langage naturel', NULL),
('Hadoop', 11, 'Framework pour le traitement distribué de grands ensembles de données', NULL),
('Spark', 11, 'Moteur de traitement de données rapide et général', ARRAY['apache spark']),
('Power BI', 13, 'Outil d''analyse de données et de business intelligence de Microsoft', NULL),
('Tableau', 13, 'Logiciel de visualisation de données', NULL),
('Agile', 15, 'Méthodologie de gestion de projet', ARRAY['scrum', 'kanban']),
('JIRA', 15, 'Logiciel de suivi de projets et de bugs', NULL),
('Figma', 18, 'Outil de conception d''interface utilisateur', NULL),
('Sketch', 18, 'Outil de conception d''interface utilisateur pour macOS', NULL),
('Adobe XD', 18, 'Outil de conception d''interface utilisateur', ARRAY['xd']),
('Photoshop', 19, 'Logiciel d''édition d''images', ARRAY['ps', 'adobe photoshop']),
('Illustrator', 19, 'Logiciel d''illustration vectorielle', ARRAY['ai', 'adobe illustrator']);

-- 5. Insérer des tags par catégorie
INSERT INTO profiles.tags (name, category)
VALUES 
-- Tags pour compétences
('frontend', 'tech'),
('backend', 'tech'),
('devops', 'tech'),
('mobile', 'tech'),
('ai', 'tech'),
('data', 'tech'),
-- Tags pour secteurs
('fintech', 'industry'),
('healthtech', 'industry'),
('e-commerce', 'industry'),
('saas', 'industry'),
('edtech', 'industry'),
-- Tags pour conditions
('télétravail', 'workstyle'),
('flexible', 'workstyle'),
('international', 'workstyle'),
('startup', 'workstyle'),
-- Tags pour taille
('startup', 'company_size'),
('scale-up', 'company_size'),
('pme', 'company_size'),
('enterprise', 'company_size');