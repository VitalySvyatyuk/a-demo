parseQueryString = (str) ->
  query = str.substr(1)
  result = {}
  return result if not query
  query.split("&").forEach (part) ->
    item = part.split("=")
    result[item[0]] = decodeURIComponent(item[1])
    return
  result

checkFlashSupport = ->
  if navigator.plugins and typeof navigator.plugins["Shockwave Flash"] == "object"
    return true
  else if typeof window.ActiveXObject != "undefined"
    try
      if new ActiveXObject("ShockwaveFlash.ShockwaveFlash")
        return true
    catch error
  return false

app.controller "ReferralController", ($scope, Mt4Account, $sce, PartnerDomain, domains, accounts, bannerLanguages, Banner,
                                      currentResult) ->

  $scope.selectFirstDomain = ->
    if $scope.selectedAccount
      $scope.selectedDomain = _.findWhere $scope.domains, ib_account: $scope.selectedAccount.id
    else
      $scope.selectedDomain = null

  $scope.selectDomain = (domain) ->
    $scope.selectedDomain = domain
  $scope.setDomainInputState = (val) ->
    $scope.domainInputState = val
  $scope.createDomain = (newDomain) ->
    $scope.domainErrors = null
    $scope.setGlobalLoading true
    domain = new PartnerDomain
      domain: newDomain
      ib_account: $scope.selectedAccount.id
    domain.$save()
    .finally -> $scope.setGlobalLoading false
    .then (res) ->
      $scope.domains.push domain
      $scope.selectedDomain = domain
      $scope.setDomainInputState null
    .catch (res) ->
      $scope.domainErrors = res.data

  $scope.deleteDomain = ->
    $scope.setGlobalLoading true
    $scope.selectedDomain.$delete()
    .finally -> $scope.setGlobalLoading false
    .then (res) ->
      $scope.domains = _($scope.domains).without $scope.selectedDomain
      $scope.selectFirstDomain()

  updateRefLinks = ->
    if !$scope.selectedAccount
      $scope.refLink = $scope.refLinkAlt = null
      return

    base = $scope.pageLink or "https://#{window.location.host}/"
    urlParser.href = base
    queryData = parseQueryString urlParser.search
    urlParser.search = $.param(_.extend({
      partner_id: $scope.selectedAccount.mt4_id
    }, queryData))
    searchPart = urlParser.search
    $scope.refLink = urlParser.href

    urlParser.search = $.param(_.extend({
      note: $scope.selectedAccount.mt4_id
    }, queryData))
    $scope.refLinkAlt = urlParser.href

    $scope.productLink = base + $scope.selectedProduct + '/' + searchPart
    $scope.productLink = '' if $scope.selectedProduct == 0
    
    $scope.landingLink = base + $scope.selectedLanding + '/' + searchPart
    $scope.landingLink = '' if $scope.selectedLanding == 0


  urlParser = document.createElement 'a'
  $scope.domains = domains
  $scope.accounts = accounts
  $scope.selectedAccount = $scope.accounts[0] if $scope.accounts
  $scope.selectedProduct = 0
  $scope.selectedLanding = 0
  $scope.selectFirstDomain()
  $scope.pageLink = "https://#{window.location.host}/"
  $scope.$watch 'selectedAccount', updateRefLinks
  $scope.$watch 'pageLink', updateRefLinks
  $scope.$watch 'selectedProduct', updateRefLinks
  $scope.$watch 'selectedLanding', updateRefLinks

  $scope.currentResult = currentResult


  # $scope.$watch 'selectedAccount', (val) ->
  #   if val
  #     $scope.refLink = "https://#{window.location.host}/?partner_id=#{$scope.selectedAccount.mt4_id}"
  #     $scope.refLinkAlt = "https://#{window.location.host}/?note=#{$scope.selectedAccount.mt4_id}"
  #   else
  #     $scope.refLink = $scope.refLinkAlt = null


  ####banners
  $scope.trustHTML = $sce.trustAsHtml
  $scope.formatSize = (size) -> "#{size[0]}x#{size[1]}"
  $scope.reloadBanners = ->
    filters = {}
    filters.language = $scope.selectedBannerLang.slug
    filters.flashSupport = checkFlashSupport()
    [filters.width, filters.height] = $scope.selectedBannerSize if $scope.selectedBannerSize
    Banner.query filters
    .$promise
    .then (data) ->
      $scope.banners = data

    filters.api_key = $scope.selectedDomain.api_key if $scope.selectedDomain
    $scope.bannersCode = "<script src=\"//#{window.location.host}/my/referral/banner_rotator.js?#{$.param filters}\"></script>"

  ####dublicated temporary code just to make toggleShowMoney work

  getTotalRealUSD = ->
    _($scope.accounts).reduce (memo, acc) ->
      return memo unless $scope.mt4Data[acc.mt4_id] and not acc.is_demo
      memo + $scope.mt4Data[acc.mt4_id].balance_usd_amount
    , 0

  $scope.loadMt4Data = (ids) ->
    return unless ids.length > 0
    Mt4Account.batchMt4Data ids
    .then (res) ->
      _($scope.mt4Data).extend res.data

  $scope.toggleShowMoney = ->
    $scope.showMoney = !$scope.showMoney

  $scope.mt4Data = {}
  $scope.showMoney = true
  $scope.accounts = accounts
  $scope.totalRealUSD = null

  if $scope.accounts.length > 0
    $scope.loadMt4Data _($scope.accounts).pluck('mt4_id')
    .then (res) ->
      $scope.totalRealUSD = getTotalRealUSD()

  ####end of dublicated temporary code

  $scope.bannerLangs = bannerLanguages
  $scope.selectedBannerLang = $scope.bannerLangs[0] || {slug: "", sizes: []}
  $scope.selectedBannerSize = $scope.selectedBannerLang.sizes[0]
  $scope.$watch 'selectedDomain', $scope.reloadBanners
  $scope.reloadBanners()
