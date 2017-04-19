app.controller "ProfileDocumentsController", ($location, $q, $scope, $upload, UserDocument, userDocuments, userDocumentsOptions, userDocumentsFields, DocumentUploadSuccessModal) ->
  $scope.initForm = ->
    $scope.newDocument =
      name: $scope.formFields.name.choices[0].value
      fields: {}
    $scope.documentFieldsVals = {}
  $scope.errors = {};
  $scope.create = ->

    $scope.setGlobalLoading true
    allUpload = Object.keys($scope.files).map((val) ->
      data = {
        name: val,
        fields: {}
      };

      return $q((resolve, reject) ->
        $upload.upload
          url: "/api/user_document/"
          data: data
          file: $scope.files[val][0]
        .success (data, status, headers, config) ->
          $scope.documents.unshift new UserDocument(data)
          resolve();
        .error (data, status, headers, config) ->
          $scope.errors[val] = data;
          resolve()
      )


    )

    $q.all(allUpload).then(() ->
      $scope.setGlobalLoading false
      if Object.keys($scope.errors).length == 0
        $location.path($scope.BASE_URL + 'create')

    )


  $scope.remove = (index) ->
    $scope.setGlobalLoading true
    $scope.documents[index].$remove ->
      $scope.documents.splice index, 1
      $scope.setGlobalLoading false

  $scope.documents = userDocuments
  $scope.options = userDocumentsOptions
  $scope.formFields = userDocumentsOptions.actions.POST
  $scope.files = {}

  $scope.documentsFields = userDocumentsFields


  $scope.bulk_upload = ->
    $scope.setGlobalLoading true
    data = {}
    Object.keys($scope.files).forEach((name) -> 
      data[name] = $scope.files[name][0]
    )
    console.log(data)

    $q((resolve, reject) ->
      $upload.upload
        url: "/api/user_document/bulk_upload"
        data: data
      .success (data, status, headers, config) ->
        console.log("Docs Bulk Uploaded!")
        $scope.setGlobalLoading false
        if Object.keys($scope.errors).length == 0
          $location.path($scope.BASE_URL + 'create')
        for name, doc of data
          $scope.documents.unshift new UserDocument(doc)
        resolve()
      .error (data, status, headers, config) ->
        $scope.errors["all"] = data
        console.log("Docs Error #{status}")
        resolve()
    )