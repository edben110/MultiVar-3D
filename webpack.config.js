const path = require('path');

module.exports = {
  entry: './back/api/static/js/main.js', // ruta relativa a la raíz
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'back/api/static/dist'), // carpeta donde quieres generar bundle.js
  },
  mode: 'production', // modo producción para el despliegue
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      },
    ],
  },
  resolve: {
    fallback: {
      "fs": false,
      "path": false,
      "crypto": false
    }
  }
};


