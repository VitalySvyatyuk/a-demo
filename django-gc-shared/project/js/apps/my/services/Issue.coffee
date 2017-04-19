app.factory "Issue", ($resource, $http, $q, $upload, getFormData) ->
  Resource = $resource "/api/issue/:id",
    id: "@id"

  Resource.createWithFile = (data, files) ->
    $upload.upload
      url: "/api/issue/"
      data: data
      file: files
      fileFormDataName: 'files'

  Resource::refresh = ->
    self = @
    $q (resolve, reject) ->
      Resource.get id: self.id
      .$promise.catch reject
      .then (data) ->
        angular.extend self, data
        resolve self

  Resource.formData = ->
    getFormData "/api/issue/"
  Resource::formData = ->
    getFormData "/api/issue/#{@id}"

  Resource
