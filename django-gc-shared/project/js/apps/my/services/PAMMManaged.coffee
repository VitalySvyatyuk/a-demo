app.constant 'PAMMManagedConstant',
  STATUS_PENDING: 1
  STATUS_ACCEPTED: 2

app.factory "PAMMManaged", ($resource, $http, $q, OTPService, getFormData) ->
  Resource = $resource "/api/pamm/managed/:id",
    id: "@id"
  ,
    patch:
      method: "PATCH"

  Resource::formData = ->
    getFormData $q, $http, "/api/pamm/managed/#{@id}"


  Resource::quit = (quitType) ->
    OTPService.post "/api/pamm/managed/#{@id}/quit",
      type: quitType
  Resource::quitFormData = (quitType) ->
    getFormData "/api/pamm/managed/#{@id}/quit"


  Resource::cancel = ->
    $http.post "/api/pamm/managed/#{@id}/cancel"


  Resource::changeReplicationRatio = (newReplicationRatio) ->
    OTPService.post "/api/pamm/managed/#{@id}/replication_ratio",
      replication_ratio: newReplicationRatio
  Resource::changeReplicationRatioFormData = ->
    getFormData "/api/pamm/managed/#{@id}/replication_ratio"


  Resource::init = ->

  Resource
