/**
 * Ce script configure un serveur proxy pour connecter le frontend au backend JOB PARSER
 * Il permet de résoudre les problèmes de CORS et de rediriger les requêtes API
 */

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const path = require('path');

// Configuration
const PORT = process.env.PORT || 8080;
const JOB_PARSER_SERVICE_URL = process.env.JOB_PARSER_SERVICE_URL || 'http://localhost:5053';

// Création de l'application Express
const app = express();

// Activation de CORS
app.use(cors());

// Middleware pour les logs
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

// Configuration du proxy pour l'API job-parser
app.use('/api/job-parser', createProxyMiddleware({
    target: JOB_PARSER_SERVICE_URL,
    pathRewrite: {
        '^/api/job-parser': '/api',  // Réécrit /api/job-parser/xxx en /api/xxx
    },
    changeOrigin: true,
    logLevel: 'debug',
}));

// Servir les fichiers statiques
app.use(express.static(path.join(__dirname)));

// Route par défaut pour rediriger vers la page d'accueil
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Démarrage du serveur
app.listen(PORT, () => {
    console.log(`Proxy server running on port ${PORT}`);
    console.log(`Proxying job-parser API requests to ${JOB_PARSER_SERVICE_URL}`);
});