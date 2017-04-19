app.config ($routeProvider, $locationProvider) ->
  $locationProvider.html5Mode true
  $routeProvider

  .when "/trading",
    templateUrl: "/templates/my/accounts.html"
    controller: "AccountsController"
    resolve:
      type: ngInject ($rootScope) ->
        $rootScope.pageCategory = "trading"
        $rootScope.openPage = "trading"
      accounts: ngInject (Mt4Account) -> Mt4Account.query(trading: true).$promise

  .when "/partnership",
    templateUrl: "/templates/my/accounts.html"
    controller: "AccountsController"
    resolve:
      type: ngInject ($rootScope) -> $rootScope.pageCategory = "partnership"
      accounts: ngInject (Mt4Account) -> Mt4Account.query(real_ib: true).$promise

  .when "/create/:category?",
    templateUrl: "/templates/my/account_create.html"
    controller: "AccountCreateController"
    resolve:
      setType: ngInject ($rootScope) -> $rootScope.openPage = "create"

  .when "/profile/security",
    templateUrl: "/templates/my/profile_security.html"
    controller: "ProfileSecurityController"

  .when "/profile/info",
    templateUrl: "/templates/my/profile_info.html"
    controller: "ProfileInfoController"
    resolve:
      formData: ngInject (User) -> User.formData()
      countries: ngInject (Country) -> Country.query().$promise
      regions: ngInject (Region) -> Region.query().$promise


  .when "/profile/documents",
    templateUrl: "/templates/my/profile_documents.html"
    controller: "ProfileDocumentsController"
    resolve:
      userDocumentsOptions: ngInject (UserDocument) -> UserDocument.options().$promise
      userDocuments: ngInject (UserDocument) -> UserDocument.query().$promise
      userDocumentsFields: ngInject (UserDocument) -> UserDocument.getFields()

  .when "/profile/subscriptions",
    templateUrl: "/templates/my/profile_subscriptions.html"
    controller: "ProfileSubscriptionsController"
    resolve:
      campaignTypes: ngInject (CampaignType) -> CampaignType.query().$promise

  .when "/registration/info",
    templateUrl: "/templates/my/profile_registration_info.html"
    controller: "ProfileInfoController"
    resolve:
      formData: ngInject (User) -> User.formData()
      countries: ngInject (Country) -> Country.query().$promise
      regions: ngInject (Region) -> Region.query().$promise

  .when "/registration/documents",
    templateUrl: "/templates/my/profile_registration_documents.html"
    controller: "ProfileDocumentsController"
    resolve:
      userDocumentsOptions: ngInject (UserDocument) -> UserDocument.options().$promise
      userDocuments: ngInject (UserDocument) -> UserDocument.query().$promise
      userDocumentsFields: ngInject (UserDocument) -> UserDocument.getFields()

  .when "/downloads",
    templateUrl: "/templates/my/downloads.html"
    resolve:
      setType: ngInject ($rootScope) ->
        $rootScope.openPage = "downloads"

  .when "/archive",
    templateUrl: "/templates/my/accounts_archive.html"
    controller: "AccountsArchiveController"
    resolve:
      accounts: ngInject (Mt4Account) -> Mt4Account.query(archived: true).$promise

  .when "/issues",
    templateUrl: "/templates/my/issues.html"
    controller: "IssueTrackerController"
    resolve:
      userIssues: ngInject (Issue) -> Issue.query().$promise

  .when "/referral",
    templateUrl: "/templates/my/referral.html"
    controller: "ReferralController"
    resolve:
      setType: ngInject ($rootScope) ->
        $rootScope.pageCategory = "partnership"
        $rootScope.openPage = "referral"
      accounts: ngInject (Mt4Account) -> Mt4Account.query(real_ib: true).$promise
      domains: ngInject (PartnerDomain) -> PartnerDomain.query().$promise
      # bannerLanguages: ngInject (Banner) -> Banner.getLanguages()
      bannerLanguages: ngInject (Banner) -> {}
      currentResult: ngInject (Report) -> Report.getCurrentResult()

  .when "/reports",
    templateUrl: "/templates/my/reports_list.html"
    controller: "ReportsController"
    resolve:
      setType: ngInject ($rootScope) -> $rootScope.pageCategory = "partnership"
      reports: ngInject (Report) -> Report.get().$promise

  .when "/payments/:operation_type",
    controller: "PaymentController"
    templateUrl: "/templates/my/payments.html"
    resolve:
      initData: ngInject ($q, $http) ->
        $q (resolve, reject) ->
          $http.get "/api/payments/init_data"
          .success resolve
          .catch reject
    reloadOnSearch: false

  .when "/bonus",
    templateUrl: "/templates/my/bonus.html"
    resolve:
      setType: ngInject ($rootScope) -> $rootScope.openPage = "bonus"

  .when "/messages",
    controller: "PrivateMessageController"
    templateUrl: "/templates/my/messages.html"
    resolve:
      messages: ngInject (Paginator, PrivateMessage) -> new Paginator(PrivateMessage).load()

  .when "/webinars",
    controller: "WebinarsController"
    templateUrl: "/templates/my/webinars.html"
    resolve:
      setType: ngInject ($rootScope) -> $rootScope.pageCategory = "trading"
      registrations: ngInject (Paginator, WebinarRegistration) -> new Paginator(WebinarRegistration).load()

  .when "/:mt4account/history",
    controller: "AccountHistoryController"
    templateUrl: "/templates/my/account_history.html"
    resolve:
      openTrades: ngInject ($route, Paginator, Mt4Trade) ->
        new Paginator(Mt4Trade, {open: true, mt4account_id: $route.current.params.mt4account}).load()
      closeTrades: ngInject ($route, Paginator, Mt4Trade) ->
        new Paginator(Mt4Trade, {close: true, mt4account_id: $route.current.params.mt4account}).load()

  .when "/agreements",
    templateUrl: "/templates/my/agreements.html"

  .otherwise
    redirectTo: "/trading"
