app.controller "MyPageController",
($scope, $rootScope, $interval, $timeout, $http, $location, User, $modal, $modalStack) ->
  $rootScope.setInboxCount = (count) ->
    $rootScope.inboxCount = count
  $rootScope.updateInboxCount = ->
    $http.get("/api/message/inbox_count").success (data) ->
      $rootScope.inboxCount = data

  $rootScope.registrationCompleteLink = () ->
      if $rootScope.user.profile
        ['registration/info',
         'registration/documents'][$rootScope.user.profile.status_info.code]

  $rootScope.registrationRedirectDone = false
  $rootScope.redirectUser = () ->
    $rootScope.user.$promise.then (user) -> 
      if !$rootScope.registrationRedirectDone
        $rootScope.registrationRedirectDone = true
        $location.path($rootScope.registrationCompleteLink())

  $rootScope.setGlobalLoading = (globalLoading) ->
    $rootScope.globalLoading = globalLoading
  $rootScope.reloadUser = ->
    $rootScope.user = User.get id: "me"

  $rootScope.getUserImage = ->
    "/static/img/photo.jpg"

  $interval $rootScope.updateInboxCount, 60000

  $scope.$on "$locationChangeStart", (event, next, current) ->
    $rootScope.pageCategory = null
    $rootScope.openPage = null
  $scope.$on '$routeChangeStart', ->
    $scope.setGlobalLoading true
    $modalStack.dismissAll()
  $scope.$on '$routeChangeSuccess', ->
    $scope.setGlobalLoading false
  $scope.$on '$routeChangeError', ->
    $scope.setGlobalLoading false

  $rootScope.$location = $location
  $rootScope.globalLoading = false

  $rootScope.reloadUser()
  $rootScope.redirectUser()
  $rootScope.updateInboxCount()

  # last unread message popup
  $rootScope.getLastUnreadMessage = ->
    $http.get("/api/message/last_unread").success (data) ->
      if data
        $rootScope.lastUnreadMessage = data
        $rootScope.displayLastMessage = true

  $rootScope.getLastUnreadMessage()

  # friend invitation popup
  $scope.friendInvitationPopup = ->
    $scope.inviteActive = true
    FriendInvitationSideModal.open $modal
    .result.finally -> $scope.inviteActive = false

  $scope.financeSummaryModal = ->
    $scope.setGlobalLoading true
    FinanceSummaryModal.open $modal
    .finally -> $scope.setGlobalLoading false

  $scope.friendInvitationModal = ->
    $scope.setGlobalLoading true
    FriendInvitationModal.open $modal
    .opened.finally -> $scope.setGlobalLoading false

  $scope.getTotalWatchers = ->
    getWatchers().length

  $scope.init = (config) ->
    if config
      $scope.BASE_URL = config.url
      $scope.available_accounts = config.available_accounts
      $scope.available_modules = config.available_modules
    else
      $scope.BASE_URL = '/account/'
      $scope.available_modules = 'all'
      $scope.available_accounts = 'all'

  $scope.checkAvailableModules = (module) ->
    if $scope.available_modules == 'all'
      true
    else if module in $scope.available_modules
      true
    else
      false

  $scope.checkAvailableAccounts = (group, type) ->
    if $scope.available_accounts == 'all'
      true
    else if $scope.available_accounts[group]?
      if type
        type in $scope.available_accounts[group]
      else
        $scope.available_accounts[group].length > 0
    else
      false
