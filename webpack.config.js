const path = require('path')
const ExtractTextPlugin = require('extract-text-webpack-plugin')
const LiveReloadPlugin = require('webpack-livereload-plugin')
const UglifyJsPlugin = require('uglifyjs-webpack-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin')
const webpack = require('webpack')

const extractSass = new ExtractTextPlugin({
  filename: '../css/[name].css',
  disable: process.env.NODE_ENV === 'development'
})

const config = {
  entry: {
    food: ['./frontend/javascript/main.js']
  },
  output: {
    path: path.resolve(__dirname, 'froide_food/static/food/js'),
    filename: '[name].js',
    library: ['Froide', 'components', '[name]'],
    libraryTarget: 'umd'
  },
  devtool: 'source-map', // any "source-map"-like devtool is possible
  resolve: {
    modules: ['node_modules'],
    extensions: ['.js', '.vue', '.json'],
    alias: {
      'vue$': 'vue/dist/vue.esm.js'
    }
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        include: /(froide-food\/frontend|node_modules\/(bootstrap))/,
        use: {
          loader: 'babel-loader'
        }
      },
      {
        test: /\.vue/,
        use: {
          loader: 'vue-loader'
        }
      },
      {
        test: /\.scss$/,
        use: extractSass.extract({
          use: [{
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
              includePaths: ['node_modules/']
            }
          }],
          // use style-loader in development
          fallback: 'style-loader'
        })
      },
      {
        test: /(\.(woff2?|eot|ttf|otf)|font\.svg)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: '../fonts/[name].[ext]',
          emitFile: true,
          context: 'froide_food/static/',
          publicPath: ''
        }
      },
      {
        test: /\.(jpg|png)$/,
        use: {
          loader: 'url-loader',
          options: {
            limit: 8192,
            name: '[path][name].[ext]',
            emitFile: false,
            context: 'froide_food/static',
            publicPath: '../'
          }
        }
      }
    ]
  },
  plugins: [
    new CopyWebpackPlugin([
      {
        from: 'node_modules/leaflet/dist/images',
        to: '../images/leaflet'
      }
    ]),
    extractSass,
    new LiveReloadPlugin(),
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: `"${process.env.NODE_ENV}"`
      }
    })
  ].concat(process.env.NODE_ENV === 'production' ? [
    new UglifyJsPlugin({
      sourceMap: true,
      uglifyOptions: {
        ie8: true,
        ecma: 5,
        mangle: false
      }
    }),
    new OptimizeCssAssetsPlugin({
      assetNameRegExp: /\.css$/,
      cssProcessorOptions: { discardComments: { removeAll: true } }
    })] : [])
}

module.exports = config
