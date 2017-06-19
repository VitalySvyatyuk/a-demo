@.ngInject = (f)-> f  # for ngannotate

@app = angular.module("Otp", [
  "ngSanitize"
  "ngResource"
  "mm.foundation"
]).config ($httpProvider, $interpolateProvider) ->
  $interpolateProvider.startSymbol("[[").endSymbol("]]")
  $httpProvider.defaults.headers.common["X-CSRFToken"] = CSRFTOKEN
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'


@app.factory "getFormData", ($q, $http) ->
  (url) ->
    $q (resolve, reject) ->
      $http
        method: "OPTIONS"
        url: url
      .success (data) -> resolve (data.actions.POST or data.actions.PUT)
      .catch reject
