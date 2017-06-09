var PROD = JSON.parse(process.env.PROD_DEV || "0");

var webpack = require("webpack");
var path = require('path');

WebPackConfig = {
  devtool: 'source-map',
  module: {
    loaders: [{
      test: /\.jsx?$/,
      exclude: /(node_modules|bower_components)/,
      loader: 'babel',
      query: {
        presets: ['es2015', 'stage-0'],
        plugins: [
          'babel-plugin-transform-decorators-legacy',
        ]
      }
    }, {
      test: /\.json$/, loader: "json"
    }, {
      test: require.resolve("jquery"), loader: "expose?$!expose?jQuery"
    }, {
      test: /moment-timezone.js$/, loader: "expose?moment"
    }, {
      test: /lodash.js$/, loader: "expose?_"
    }, {
      test: /\.scss$/,
      loaders: ["style", "css", "sass"]
    }],
  },
  resolve: {
    modulesDirectories: ["node_modules", "django-gc-shared"]
  },
  entry: {
    gcrm: "./django-gc-shared/gcrm/static/gcrm/js/app.js",
  },
  output: {
    path: './static/compiled/js/',
    filename: "[name].js",
  },

  plugins: [
    new webpack.optimize.DedupePlugin(),
    new webpack.optimize.OccurenceOrderPlugin(),
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': 'production'
      }
    }),
    new webpack.optimize.UglifyJsPlugin({
      mangle: false,
      compress: {
        warnings: false,
      },
      comments: true,
      sourceMap: true,
    }),
  ],
}
module.exports = WebPackConfig
