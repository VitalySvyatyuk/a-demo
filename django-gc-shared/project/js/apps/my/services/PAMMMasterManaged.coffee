app.factory "PAMMMasterManaged", ($resource, $http, $q, OTPService, $modal) ->
  Resource = $resource "/api/pamm/master_managed/:id/:action",
    id: "@id"
  ,
    patch:
      method: "PATCH"

  Resource::accept = ->
    $http.post "/api/pamm/master_managed/#{@id}/accept"

  Resource::reject = ->
    $http.post "/api/pamm/master_managed/#{@id}/reject"

  Resource::unbind = ->
    $http.post "/api/pamm/master_managed/#{@id}/unbind"

  Resource::init = ->

  Resource
