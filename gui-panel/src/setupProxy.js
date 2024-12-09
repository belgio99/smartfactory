const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api', // Usa "/api" come path per indirizzare le richieste
    createProxyMiddleware({
      //target: 'http://localhost:10040',
      target: 'http://smartfactory-api-1:8000',
      changeOrigin: true,
      pathRewrite: { '^/api': '' }, // Riscrive il path eliminando "/api" se necessario
    })
  );
};
