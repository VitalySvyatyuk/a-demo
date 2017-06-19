app.controller "ProfileSubscriptionsController", ($scope, $rootScope, User, OTPService, campaignTypes) ->
  updateInitialUser = ->
    $scope.initialUser = angular.copy($rootScope.user)

  # Subscribe on event to restore values
  $scope.$on "$locationChangeStart", (event, next, current) ->
    $rootScope.user = $scope.initialUser

  updateInitialUser()


  $scope.toggleCampaignType = (id) ->
    if id in $scope.user.profile.subscription
      $scope.user.profile.subscription = _($scope.user.profile.subscription).without id
    else
      $scope.user.profile.subscription.push id

  $scope.isCampaignTypeSelected = (id) ->
    id in $scope.user.profile.subscription

  $scope.toggleAccountStatements = () ->
    $scope.user.profile.send_account_statements = !$scope.user.profile.send_account_statements

  $scope.isAccountStatementsEnabled = () ->
    $scope.user.profile.send_account_statements

  $scope.save = () ->
    delete $scope.errors
    $scope.setGlobalLoading true
    $rootScope.user.$patch()
    .finally -> $scope.setGlobalLoading false
    .then (data) -> updateInitialUser()
    .catch (res) ->
      if res.status is 511
        OTPService.processResource res.data.detail, $scope.user, $scope.user.$patch
        .then updateInitialUser
      else
        $scope.errors = res.data

  $scope.campaignTypes = campaignTypes