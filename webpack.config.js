const path = require('path');

module.exports = {
  entry: './back/api/static/js/main.js', // ruta relativa a la raíz
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'back/api/static/dist'), // carpeta donde quieres generar bundle.js
  },
  mode: 'development', // quita el warning
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: 'babel-loader', // compatibilidad con navegadores antiguos
      },
    ],
  },
};


