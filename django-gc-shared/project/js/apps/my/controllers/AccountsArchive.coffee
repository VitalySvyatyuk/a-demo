app.controller "AccountsArchiveController", ($scope, accounts) ->
  $scope.accounts = accounts
  $scope.restore = (acc) ->
    $scope.setGlobalLoading true
    acc.restoreFromArchive()
    .finally -> $scope.setGlobalLoading false