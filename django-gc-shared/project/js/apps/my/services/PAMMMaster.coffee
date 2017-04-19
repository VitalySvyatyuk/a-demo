app.factory "PAMMMaster", ($resource, $http, $q, getFormData) ->
  Resource = $resource "/api/pamm/master/:id/:action",
    id: "@id"
  ,
    patch:
      method: "PATCH"

  Resource.formData = ->
    getFormData "/api/pamm/master/"

  Resource::formData = ->
    getFormData "/api/pamm/master/#{@id}"

  Resource::init = ->

  Resource
