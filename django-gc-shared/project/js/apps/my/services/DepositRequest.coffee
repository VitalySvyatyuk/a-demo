app.factory "DepositRequest", ($resource, $http) ->
  Resource = $resource "/api/payments/deposit/:id",
    id: "@id"

  Resource::type = 'deposit'

  Resource::cancel = ->
    self = @
    $http.post "/api/payments/deposit/#{@id}/cancel"
    .then (res) ->
      angular.extend self, res.data.object if res.data.object
    .catch (res)->
      angular.extend self, res.data.object if res.data.object

  Resource
