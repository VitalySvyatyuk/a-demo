app.factory "Mt4Trade", ($resource, $http, $q, $modal, $routeParams) ->
  Resource = $resource "/api/mt4account/:mt4account_id/mt4trade",
    mt4account_id: '@mt4account_id'
  ,
    query:
      isArray: false

  Resource
