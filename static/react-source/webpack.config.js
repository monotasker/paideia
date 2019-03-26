var HTMLWebpackPlugin = require('html-webpack-plugin');
// var NpmInstallPlugin = require('npm-install-webpack-plugin');
var path = require('path');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'app.js',
    publicPath: '/'
  },
  mode: 'development',
  devtool: 'inline-source-map',
  module: {
    rules: [
      {test: /\.(png|jpg|gif|svg)$/,
       use: [{loader: 'file-loader', options: {outputPath: 'images'}}],
      },
      {test: /\.(eot|ttf|woff)$/,
       use: [{loader: 'file-loader', options: {outputPath: 'fonts'}}],
      },
      {test: /\.(js|jsx)$/, exclude: /node_modules/, use: 'babel-loader'},
      {test: /\.css$/, use: ['style-loader', 'css-loader']},
      {test: /\.scss$/,
       use: [
          'style-loader',
          'css-loader',
          'sass-loader'
        ]
      },
      { test: /\.json$/, loader: 'json-loader' }
    ]
  },
  resolve: {extensions: ['.js', '.jsx']},
  // node: {
  //   fs: 'empty',
  //   console: true,
  //   net: 'empty',
  //   tls: 'empty'
  // },
  devServer: {
    historyApiFallback: true
  },
  plugins: [
    new HTMLWebpackPlugin({
        template: "./src/index.html",
        filename: "./index.html"
    }),
  ]
}
