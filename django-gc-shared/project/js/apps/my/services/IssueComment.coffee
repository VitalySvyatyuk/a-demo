app.factory "IssueComment", ($resource, $http, $q, $upload, getFormData) ->
  Resource = $resource "/api/issue/:issue/comment/:id",
    id: "@id"
    issue: "@issue"

  Resource.createWithFile = (data, files) ->
    $upload.upload
      url: "/api/issue/#{data.issue}/comment/"
      data: data
      file: files
      fileFormDataName: 'files'

  Resource::formData = ->
    getFormData "/api/issue/#{@issue}/comment/#{@id or ''}"

  Resource
