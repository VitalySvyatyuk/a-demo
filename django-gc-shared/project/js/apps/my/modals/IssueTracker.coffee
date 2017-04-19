app.factory "IssueCreateModal", (newModal) -> newModal
  options:
    templateUrl: "/templates/my/issue_create_modal.html"
    windowClass: "gc-small"
  resolve: ->
    formData: ngInject (Issue) -> Issue.formData()
    accounts: ngInject (Mt4Account) -> Mt4Account.query().$promise
  ctrl: ngInject ($scope, $modalInstance, Issue, formData, $q, accounts) ->
    $scope.isLoading = false
    $scope.formData = formData
    $scope.issue =
      department: formData.department.choices[0].value
    $scope.labels = {}

    $scope.selectCommentFiles = (files) ->
      $scope.files ?= []
      #add files and remove dupes by name
      $scope.files = _($scope.files.concat files).uniq (f) -> f.name

    $scope.unselectCommentFile = (file) ->
      $scope.files = _($scope.files).without file

    $scope.additional_info = {}
    $scope.accounts = accounts
    $scope.save = ->
      $scope.isLoading = true
      $scope.issue.text = ''
      for key, value of $scope.additional_info
        $scope.issue.text += $scope.labels[key] + ': ' + value + '\n' if value?
      Issue.createWithFile $scope.issue, $scope.files
      .success (data) ->
        $modalInstance.close new Issue(data)
      .error (data) ->
        $scope.isLoading = false
        $scope.errors = data

    $scope.cancel = ->
      $modalInstance.dismiss()
