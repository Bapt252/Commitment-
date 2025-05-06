// Proxy CORS pour faciliter la communication entre le frontend et le backend
const express = require('express');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

// Activer CORS pour toutes les routes
app.use(cors({
  origin: '*', // En production, remplacer par l'origine spécifique
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Configuration des endpoints proxy
const JOB_PARSER_SERVICE = 'http://localhost:5053';

// Proxy pour les endpoints du job parser
app.use('/api/job-parser', createProxyMiddleware({
  target: JOB_PARSER_SERVICE,
  changeOrigin: true,
  pathRewrite: {
    '^/api/job-parser': '/api' // Réécriture du chemin
  },
  onError: (err, req, res) => {
    console.error('Erreur proxy:', err);
    res.status(500).json({ error: 'Erreur proxy', message: err.message });
  }
}));

// Servir les fichiers statiques (pour les fichiers HTML, CSS et JS)
app.use(express.static('public'));
app.use('/static', express.static('static'));
app.use('/templates', express.static('templates'));

// Port sur lequel le serveur proxy s'exécute
const PORT = 8000;

app.listen(PORT, () => {
  console.log(`Serveur proxy CORS en cours d'exécution sur le port ${PORT}`);
  console.log(`Endpoint job parser: http://localhost:${PORT}/api/job-parser/parse-job`);
  console.log(`Accédez à l'interface via: http://localhost:${PORT}/templates/client-questionnaire.html`);
});
