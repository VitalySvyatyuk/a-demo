app.controller "PaymentController", ($filter, $http, $location, $routeParams, $rootScope, $scope, $sce, OTPService, initData) ->
  $scope.initData = initData
  $scope.operationType = $routeParams.operation_type
  $scope.chooseSystemTrans = window.choose_system_trans
  $scope.accountAppUrl = window.account_app_url


  orderBy = $filter('orderBy')
  $scope.depositSystems =  []
  $scope.withdrawSystems =  []
  for system, value of $scope.initData.systems_list.deposit
    $scope.depositSystems.push {system:system, value:value}

  for system, value of $scope.initData.systems_list.withdraw
    $scope.withdrawSystems.push {system:system, value:value}

  $scope.depositSystems = orderBy($scope.depositSystems, 'value.order', false)
  $scope.withdrawSystems = orderBy($scope.withdrawSystems, 'value.order', false)


  $scope.downloadPdfExtraParams = ''

  $scope.showFill = ->
    $scope.step = 'fill'

  renderForm = ->
    $scope.setGlobalLoading true

    ps = if $scope.selectedPS then $scope.selectedPS.slug else ''
    $http.get '/api/payments/payment_form',
      params:
        ps: ps,
        operation: $scope.operationType
        account: $routeParams.account or ''
    .finally -> $scope.setGlobalLoading false
    .then (result) ->
      #successCallback
      $scope.selectedPSForm = $sce.trustAsHtml result.data.form
    ,(reason) ->
      #errorCallback
      data = reason.data
      if data.detail
        $scope.errors = $sce.trustAsHtml data.detail

  #--renderForm() END

  $scope.selectPS = (ps) ->
    $scope.errors = false
    return unless ps

    $scope.selectedPS = ps
    $scope.selectedPSIsBank = ps.slug.indexOf('bank') is 0
    $location.search('s', ps.slug)
    renderForm()

  getSystemBySlug = (ps_slug) ->
    system = null
    _.find $scope.initData.systems_list[$scope.operationType], (value, key) ->
      _.find value.systems, (sys, slug) ->
        system = sys if slug is ps_slug
    system


  formData = {}

  $scope.processPaymentConfirmed = () ->
    formData.confirmed = true
    processPayment()

  $scope.processPaymentPreview = ($event) ->
    delete formData.confirmed
    angular.extend formData,
      ps: if $scope.operationType isnt 'transfer' then $scope.selectedPS.slug else ''
      operation: $scope.operationType

    $.each $($event.target).serializeArray(), (_, kv) ->
        formData[kv.name] = kv.value

    processPayment()


  processPayment = () ->
    return if $rootScope.globalLoading

    $scope.setGlobalLoading true
    $scope.errors = false
    OTPService.post "/api/payments/process_#{$scope.operationType}", formData
    .finally -> $scope.setGlobalLoading false
    .then (result) ->
      data = result.data
      if data.preview_items
        #------ Response before "confirmed"-------------
        $scope.previewItems = data.preview_items
        $scope.restrictedCountry = data.restricted_country

        if $scope.operationType is 'deposit' and $scope.selectedPSIsBank
          $scope.previewBankDownloadPDFParams = "?#{$.param(formData)}"

        $scope.step = 'preview'

      else
        #------ Response after "confirmed"-------------
        if data.html
          $scope.responseHtml = $sce.trustAsHtml data.html
          $scope.step = 'html'

        else if data.redirect
          window.location.href = data.redirect

        else if data.success
            if Android?
              Android.closeWebView()
            else
              window.location.href = $scope.accountAppUrl
          else
            $scope.errors = $sce.trustAsHtml "Didn't successed"

      #successCallback END

    .catch (reason) ->
      data = reason.data
      if data.form
        $scope.selectedPSForm = $sce.trustAsHtml data.form
      else if data.detail
        $scope.errors = $sce.trustAsHtml data.detail

      #errorCallback END
  #processPayment() END

  $scope.showFill()
  $scope.selectPS getSystemBySlug($routeParams.s) if $routeParams.s
  renderForm() if $scope.operationType is 'transfer'