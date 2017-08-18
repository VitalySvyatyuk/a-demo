fs = require 'fs'
path = require 'path'
glob = require 'glob'
gulp = require 'gulp'
sass = require 'gulp-sass'
rename = require 'gulp-rename'
sourcemaps = require 'gulp-sourcemaps'
uglify = require 'gulp-uglify'
ngAnnotate = require 'gulp-ng-annotate'
gulpif = require 'gulp-if'
coffee = require 'gulp-coffee'
concat = require 'gulp-concat'
rtlcss = require 'gulp-rtlcss'
autoprefixer =  require 'gulp-autoprefixer'

config =
  production: true

paths =
  scss: [
    'django-gc-shared/project/css/private_office.scss',
    'django-gc-shared/project/css/marketing_site/main.scss'
  ]

  coffee: [
    'django-gc-shared/**/js/**/*.coffee',
    'django-gc-shared/**/coffee/**/*.coffee',
  ]
  
  coffee_otp: [
    'django-gc-shared/project/js/apps/otp/app.coffee',
    'django-gc-shared/project/js/apps/otp/controllers/ProfileSecurity.coffee',
    'django-gc-shared/project/js/apps/my/services/OTP.coffee',
    'django-gc-shared/project/js/apps/my/modals/Profile.coffee',
    'django-gc-shared/project/js/apps/my/modals/OTP.coffee',
    'django-gc-shared/project/js/apps/my/services/User.coffee',
  ]

  coffee_helpers: [
    'django-gc-shared/project/js/apps/my/helpers.coffee'
  ]

  bundle_base: [
    'bower_components/jquery/dist/jquery.min.js',
    'bower_components/underscore/underscore-min.js',
    'bower_components/modernizr/modernizr.js',
    'bower_components/fastclick/lib/fastclick.js',
    'bower_components/foundation/js/foundation.min.js',
    'bower_components/jquery.cookie/jquery.cookie.js',
    'bower_components/foundation/js/vendor/placeholder.js',
    'django-gc-shared/project/static/js/vendor/jquery.autocomplete.js'
    'django-gc-shared/project/static/js/vendor/uuid.js'
    'django-gc-shared/project/static/js/reveal_links.js'
  ]

  bundle_marketing: [
    'bower_components/jquery/dist/jquery.min.js'
    # 'bower_components/webfontloader/webfontloader.js'
    'bower_components/jquery.inputmask/dist/min/jquery.inputmask.bundle.min.js'
    'bower_components/slick-carousel/slick/slick.min.js'
    'bower_components/tooltipster/dist/js/tooltipster.bundle.min.js'
  ]

  bundle_angular: [
    'bower_components/angular/angular.min.js',
    'bower_components/angular-route/angular-route.min.js',
    'bower_components/angular-resource/angular-resource.min.js',
    'bower_components/angular-animate/angular-animate.min.js',
    'bower_components/angular-sanitize/angular-sanitize.min.js',
    'bower_components/angular-mm-foundation/mm-foundation-tpls.min.js'
  ]

  images:
    inout: 'django-gc-shared/project/static/img/for-sprites/in-out/*.png'

gulp.task 'enable-dev-mode', (cb) ->
  config.production = false
  cb()

gulp.task 'bundle', ->
  gulp.src paths.bundle_base
    .pipe concat 'bundle.base.js'
    .pipe uglify
      mangle: false
    .pipe gulp.dest 'static/js/compiled'

  gulp.src paths.bundle_marketing
    .pipe concat 'bundle.marketing.js'
    .pipe uglify
      mangle: false
    .pipe gulp.dest 'static/js/compiled'

  gulp.src paths.bundle_angular
    .pipe concat 'bundle.angular.js'
    .pipe gulp.dest 'static/js/compiled'


gulp.task 'image-variables', ->
  if !fs.existsSync("static/css/compiled")
    fs.mkdirSync("static/css/compiled")
  file = fs.createWriteStream "static/css/compiled/image-variables.scss"
  file.once 'open' , () ->
    for block, filePaths of paths.images
      do (block, filePaths) ->
        names = glob.sync filePaths
        ext = path.extname names[0]
        file.write "$#{ block }-extname: '#{ ext }';\n"
        file.write "$#{ block }-names: (#{ names.map (a) -> path.basename a, ext });\n"
    file.end()

gulp.task 'scss', ['image-variables'], ->
  gulp.src paths.scss
    .pipe sass
      outputStyle: if config.production then 'compressed' else 'nested'
    .pipe autoprefixer()
    .pipe rename
      suffix: '.min'
    .pipe gulp.dest 'static/css/'
    .pipe livereload()


gulp.task 'coffee', ->
  gulp.src paths.coffee
    .pipe gulpif not config.production, sourcemaps.init()
      .pipe coffee()
      .pipe ngAnnotate()
      .pipe uglify
        mangle: false
        compress: config.production

      .pipe gulpif /[\/|\\]apps[\/|\\]my[\/|\\]/, concat 'my.js'
    .pipe gulpif not config.production, sourcemaps.write()
    .pipe rename
      dirname: ''
      extname: '.min.js'
    .pipe gulp.dest 'static/js/compiled/'

  gulp.src paths.coffee_helpers
    .pipe gulpif not config.production, sourcemaps.init()
      .pipe coffee()
      .pipe ngAnnotate()
      .pipe uglify
        mangle: false
        compress: config.production
      .pipe concat 'helpers.js'
    .pipe gulpif not config.production, sourcemaps.write()
    .pipe rename
      dirname: ''
      extname: '.min.js'
    .pipe gulp.dest 'static/js/compiled/'

  gulp.src paths.coffee_otp
    .pipe gulpif not config.production, sourcemaps.init()
      .pipe coffee()
      .pipe ngAnnotate()
      .pipe uglify
        mangle: false
        compress: config.production
      .pipe concat 'otp.js'
    .pipe gulpif not config.production, sourcemaps.write()
    .pipe rename
      dirname: ''
      extname: '.min.js'
    .pipe gulp.dest 'static/js/compiled/'

livereload = require 'gulp-livereload'

custom_apps = []
apps = []
mappings = (apps.map (app) -> 'css-'+app).concat(custom_apps.map (app) -> 'css-'+app)
gulp.task 'css', mappings

gulp.task 'watch', () ->
  livereload.listen()
  gulp.watch paths.coffee, ['coffee']
  gulp.watch ['django-gc-shared/project/css/**/*.scss'], ['scss']

apps.forEach (app) ->
  gulp.task 'css-'+app, () ->
    gulp.src 'django-gc-shared/'+app+'/css/app.scss'
      .pipe sass()
      .pipe rename(app+'.css')
      .pipe gulp.dest 'static/compiled/css/'
      .pipe livereload()

  gulp.task 'watch-'+app, ['css-'+app], () ->
    livereload.listen()
    gulp.watch ['django-gc-shared/'+app+'/css/**/*.scss'], ['css-'+app]


custom_apps.forEach (custom_app) ->
  [app, target] = custom_app.split('.')
  gulp.task 'css-'+custom_app, () ->
    gulp.src 'django-gc-shared/'+app+'/css/app.'+target+'.scss'
      .pipe sass()
      .pipe rename(custom_app+'.css')
      .pipe gulp.dest 'static/compiled/css/'
      .pipe livereload()

  gulp.task 'watch-'+custom_app, ['css-'+custom_app], () ->
    livereload.listen()
    gulp.watch ['django-gc-shared/'+app+'/css/**/*.scss'], ['css-'+custom_app]

gulp.task 'dev', ['enable-dev-mode', 'scss', 'coffee', 'bundle'].concat mappings
gulp.task 'production', ['scss', 'coffee', 'bundle'].concat mappings
gulp.task 'prod', ['production']
