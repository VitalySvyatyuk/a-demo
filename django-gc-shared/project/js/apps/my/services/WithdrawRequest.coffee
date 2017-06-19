app.factory "WithdrawRequest", ($resource, $http) ->
  Resource = $resource "/api/payments/withdraw/:id",
    id: "@id"

  Resource::type = 'withdraw'

  Resource::cancel = ->
    self = @
    $http.post "/api/payments/withdraw/#{@id}/cancel"
    .then (res) ->
      angular.extend self, res.data.object if res.data.object
    .catch (res)->
      angular.extend self, res.data.object if res.data.object

  Resource
