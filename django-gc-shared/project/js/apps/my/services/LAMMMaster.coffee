app.constant 'LAMMManagedConstant',
  STATUS_PENDING: 7
  STATUS_ACCEPTED: 0
  STATUS_INVEST_REJECTED: 5
  STATUS_INVEST_FULL: 2
  INVEST_ADOPTED: 1

app.factory "LAMMMaster", ($resource, $http, $q, getFormData) ->
  Resource = $resource "/api/lamm/master/investment/:id/",
    id: "@id"
  ,
    patch:
      method: "PATCH"

  Resource::reject = ->
    $http.post "/api/lamm/master/investment/#{@id}/reject"

  Resource::accept = ->
    $http.post "/api/lamm/master/investment/#{@id}/accept"

  Resource::unbind = ->
    $http.post "/api/lamm/master/investment/#{@id}/disconnect"

  Resource::init = ->

  Resource