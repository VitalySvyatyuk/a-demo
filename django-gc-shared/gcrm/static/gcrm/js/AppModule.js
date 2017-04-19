import uiRouter from 'angular-ui-router'
import uibs from 'angular-ui-bootstrap'
import ngSanitize from 'angular-sanitize'
import 'angular-ui-scroll'
import 'angular-loading-bar'
// window.ngInject = (f) => f  // for ngannotate

angular.module('GCRM', [ngSanitize, uiRouter, uibs, 'ui.scroll', 'angular-loading-bar'])
.config(($httpProvider, $interpolateProvider, $compileProvider, $sceProvider) => {
  $interpolateProvider.startSymbol("[[").endSymbol("]]")
  // $httpProvider.defaults.headers.common["X-CSRFToken"] = CSRFTOKEN
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
  $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|sip|skype):/) // allow mailto and such hrefs
  $sceProvider.enabled(false) // Disable it so we can set src for audiorecords
}).run(($http, $q, $state) => {
  window.http = $http
  window.q = $q
  window.$state = $state
})
