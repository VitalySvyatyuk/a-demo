app.factory "User", ($resource, $http, $q, OTPService, getFormData) ->
  Resource = $resource "/api/user/:id/:action",
    id: "@id"
  ,
    patch:
      method: "PATCH"

  Resource.formData = ->
    getFormData "/api/user/me"

  Resource::formData = ->
    getFormData "/api/user/#{@id}"

  Resource::changePassword = (oldPassword, newPassword) ->
    self = @
    $q (resolve, reject) ->
      $http.post "/api/user/#{self.id}/change_password",
        old: oldPassword
        new: newPassword
      .success resolve
      .catch (res) ->
        if res.status is 511
          OTPService.processPOST res.data.detail,
            "/api/user/#{self.id}/change_password",
            old: oldPassword
            new: newPassword
          .then resolve
        else
          reject res

  Resource
