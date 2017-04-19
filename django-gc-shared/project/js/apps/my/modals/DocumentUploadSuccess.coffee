app.factory "DocumentUploadSuccessModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/document_upload_success_modal.html"
    windowClass: "gc-small"
  ctrl: ngInject ($scope, $modalInstance) ->
    $scope.cancel = ->
      $modalInstance.dismiss()
