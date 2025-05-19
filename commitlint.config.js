// Configuration Commitlint pour les messages de commit
module.exports = {
  // Étendre la configuration conventionnelle
  extends: ['@commitlint/config-conventional'],
  
  // Rules personnalisées
  rules: {
    // Type de commit obligatoire
    'type-enum': [
      2,
      'always',
      [
        'feat',     // Nouvelle fonctionnalité
        'fix',      // Correction de bug
        'docs',     // Documentation uniquement
        'style',    // Changements de style (formatting, semicolons, etc.)
        'refactor', // Refactoring (ni bugfix ni feature)
        'perf',     // Amélioration de performance
        'test',     // Ajout ou modification de tests
        'chore',    // Maintenance (build, CI, dependencies, etc.)
        'ci',       // Changes to CI configuration
        'build',    // Changes to build system
        'revert'    // Revert d'un commit précédent
      ]
    ],
    
    // Longueur du sujet
    'subject-max-length': [2, 'always', 72],
    'subject-min-length': [2, 'always', 10],
    
    // Casse du sujet (lowercase)
    'subject-case': [2, 'always', 'lower-case'],
    
    // Pas de point final dans le sujet
    'subject-full-stop': [2, 'never', '.'],
    
    // Body obligatoire pour certains types
    'body-max-line-length': [1, 'always', 100],
    
    // Footer pour les breaking changes
    'footer-max-line-length': [1, 'always', 100],
    
    // Scope optionnel mais formaté
    'scope-case': [2, 'always', 'lower-case'],
    'scope-enum': [
      1,
      'always',
      [
        'api',          // API changes
        'cv-parser',    // CV parsing service
        'job-parser',   // Job parsing service
        'matching',     // Matching service
        'frontend',     // Frontend changes
        'backend',      // Backend changes
        'db',           // Database changes
        'config',       // Configuration changes
        'docker',       // Docker/containerization
        'ci',           // CI/CD pipeline
        'monitoring',   // Monitoring and observability
        'security',     // Security improvements
        'performance',  // Performance improvements
        'docs',         // Documentation
        'tests',        // Testing
        'deps',         // Dependencies
        'release'       // Release related
      ]
    ]
  },
  
  // Plugins
  plugins: [
    {
      rules: {
        // Rule personnalisée pour vérifier les références Jira
        'jira-ticket-reference': (parsed) => {
          const { subject, body, footer } = parsed;
          const content = `${subject || ''} ${body || ''} ${footer || ''}`;
          
          // Vérifier si c'est un commit de merge ou de revert
          if (subject && (subject.startsWith('Merge') || subject.startsWith('Revert'))) {
            return [true];
          }
          
          // Chercher une référence Jira (format: NEX-123)
          const jiraPattern = /NEX-\d+/;
          if (!jiraPattern.test(content)) {
            return [
              false,
              'Le commit doit référencer un ticket Jira (format: NEX-123)'
            ];
          }
          
          return [true];
        },
        
        // Rule pour vérifier les breaking changes
        'breaking-change-indicator': (parsed) => {
          const { subject, body, footer } = parsed;
          
          // Vérifier si c'est un breaking change
          const hasBreakingChange = 
            subject?.includes('!') ||
            body?.includes('BREAKING CHANGE:') ||
            footer?.includes('BREAKING CHANGE:');
          
          if (hasBreakingChange) {
            // S'assurer qu'il y a une description du breaking change
            const hasDescription = 
              body?.includes('BREAKING CHANGE:') ||
              footer?.includes('BREAKING CHANGE:');
            
            if (!hasDescription) {
              return [
                false,
                'Les breaking changes doivent inclure "BREAKING CHANGE:" avec description'
              ];
            }
          }
          
          return [true];
        }
      }
    }
  ],
  
  // Configuration des règles personnalisées
  rules: {
    ...module.exports.rules,
    'jira-ticket-reference': [1, 'always'], // Warning level
    'breaking-change-indicator': [2, 'always'] // Error level
  },
  
  // Ignorer certains patterns
  ignores: [
    // Ignorer les commits de merge automatiques
    (commit) => commit.includes('Merge branch'),
    (commit) => commit.includes('Merge pull request'),
    
    // Ignorer les commits de release automatiques
    (commit) => commit.startsWith('chore(release):'),
    (commit) => commit.startsWith('Release'),
    
    // Ignorer les reverts automatiques
    (commit) => commit.startsWith('Revert')
  ],
  
  // Configuration pour différents types de projet
  parserPreset: {
    parserOpts: {
      headerPattern: /^(\w*)(?:\((.*)\))?!?: (.*)$/,
      headerCorrespondence: ['type', 'scope', 'subject'],
      noteKeywords: ['BREAKING CHANGE', 'BREAKING-CHANGE'],
      revertPattern: /^(?:Revert|revert:)\s"?([\s\S]*?)"?\s*This reverts commit ([0-9a-f]{7,40})\./i,
      revertCorrespondence: ['header', 'hash']
    }
  },
  
  // Messages d'aide
  helpUrl: 'https://github.com/conventional-changelog/commitlint/#what-is-commitlint',
  
  // Configuration par défaut
  defaultIgnores: true,
  
  // Prompt configuration pour l'aide interactive
  prompt: {
    questions: {
      type: {
        description: 'Sélectionnez le type de changement que vous commitez:',
        enum: {
          feat: {
            description: 'Une nouvelle fonctionnalité',
            title: 'Features'
          },
          fix: {
            description: 'Une correction de bug',
            title: 'Bug Fixes'
          },
          docs: {
            description: 'Changements de documentation uniquement',
            title: 'Documentation'
          },
          style: {
            description: 'Changements qui n\'affectent pas le sens du code (white-space, formatting, missing semi-colons, etc)',
            title: 'Styles'
          },
          refactor: {
            description: 'Un changement de code qui ne corrige pas un bug ni n\'ajoute de fonctionnalité',
            title: 'Code Refactoring'
          },
          perf: {
            description: 'Un changement de code qui améliore les performances',
            title: 'Performance Improvements'
          },
          test: {
            description: 'Ajout de tests manquants ou correction de tests existants',
            title: 'Tests'
          },
          build: {
            description: 'Changements qui affectent le système de build ou les dépendances externes (npm, make, etc.)',
            title: 'Builds'
          },
          ci: {
            description: 'Changements dans les fichiers et scripts de configuration CI (Circle, BrowserStack, SauceLabs)',
            title: 'Continuous Integrations'
          },
          chore: {
            description: 'Autres changements qui ne modifient pas les fichiers src ou test',
            title: 'Chores'
          },
          revert: {
            description: 'Reverts un commit précédent',
            title: 'Reverts'
          }
        }
      },
      scope: {
        description: 'Quel est le scope de ce changement (ex. component, file name)? (optionnel)'
      },
      subject: {
        description: 'Écrivez une description courte et impérative du changement'
      },
      body: {
        description: 'Fournissez une description détaillée du changement (optionnel). Utilisez "|" pour les retours à la ligne'
      },
      isBreaking: {
        description: 'Y a-t-il des changements non rétrocompatibles?'
      },
      isIssueAffected: {
        description: 'Ce changement affecte-t-il des issues ouvertes?'
      },
      issuesBody: {
        description: 'Si des issues sont fermées, la description du commit est:\n"fix #123: un message", "re #123: un message", "refs #123: un message" ou "closes #123: un message".'
      }
    }
  }
};