app.factory "LAMMInvestor", ($resource, $http, $q, getFormData) ->
  Resource = $resource "/api/lamm/investor/investment/:id/",
    id: "@id"
  ,
    patch:
      method: "PATCH"

  Resource::unbind = ->
    $http.post "/api/lamm/investor/investment/#{@id}/disconnect"

  Resource::reject = ->
    $http.post "/api/lamm/investor/investment/#{@id}/reject"

  Resource::init = ->

  Resource