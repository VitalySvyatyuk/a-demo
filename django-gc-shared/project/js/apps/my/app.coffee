@.ngInject = (f)-> f  # for ngannotate

@app = angular.module("My", [
  "ngRoute"
  "ngResource"
  "ngAnimate"
  "ngSanitize"
  "angularFileUpload"
  "mm.foundation"
  "infinite-scroll"
]).config ($httpProvider, $interpolateProvider) ->
  $interpolateProvider.startSymbol("[[").endSymbol("]]")
  $httpProvider.defaults.headers.common["X-CSRFToken"] = CSRFTOKEN
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
