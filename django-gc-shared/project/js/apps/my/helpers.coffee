@app.filter 'titleize', () -> _.titleize
@app.filter 'capitalize', () -> _.capitalize


@app.filter 'momentFromNow', () ->
  (date) ->
    return date unless date
    m = moment(date)
    if Math.abs moment().diff(m, 'hours') > 3
      m.format 'L LT'
    else
      m.fromNow()


@app.filter 'momentHumanize', () ->
  (date, format='LLL') ->
    return date unless date
    moment(date).format(format)

@app.directive 'colorPicker', () ->
  restrict: 'E'
  replace: true
  require: 'ngModel'
  template: '<div></div>'
  link: (scope, el, attrs, ngModel) ->
    colpick = el.colpick
      layout: 'rgbhex'
      onSubmit: (hsb, hex, rgb, elem) ->
        color = '#' + hex
        el.css 'background-color', color
        el.colpickHide()
        scope.$apply () ->
          ngModel.$setViewValue color
    scope.$watch ngModel, ->
      colpick.colpickSetColor ngModel.$viewValue
      el.css 'background-color', ngModel.$viewValue


@app.directive 'gcDatepicker', () ->
  require: 'ngModel'
  scope:
    maxDate: '='
    minDate: '='
  link: (scope, el, attr, ngModel) ->
    el.datepicker
      changeMonth: true
      changeYear: true
      defaultDate: "1999-01-01"
      yearRange: "1900:#{new Date().getFullYear()-18}"
      dateFormat: "yy-mm-dd"
      onSelect: (dateText) ->
        scope.$apply () ->
          ngModel.$setViewValue dateText
    scope.$watch 'maxDate', (val) ->
      el.datepicker "option", "maxDate", val if val
    scope.$watch 'minDate', (val) ->
      el.datepicker "option", "minDate", val if val


@app.directive 'equalize', ($timeout) ->
  link: (scope, el, attr) ->
    options = {}
    options['children'] = attr['equalizeEl'] || '[equalize-me]'
    options['equalize'] = attr['equalize'] if attr['equalize']
    options['reset'] = true if attr['equalizeReset']
    #equalize on next step, give it a time to reflow
    $timeout () ->
      el.equalize options


@app.directive 'baron', ($timeout) ->
  link: (scope, el, attr) ->
    $timeout () ->
      el.baron
        scroller: '.vscroller'
        bar: '.third-vscroller-bar'
        track: '.third-vscroller-track'


@app.directive 'inputMask', ($timeout) ->
  require: "ngModel"
  link: (scope, el, attr, ctrl) ->
    scope.$watch attr['inputMask'], (val) ->
      el.mask val or '(999) 999-9999'

    el.on 'keyup', ->
      ctrl.$setViewValue el.val()


@app.directive 'accordionShow', ($timeout) ->
  link: (scope, el, attr) ->
    el.children('[title]').on 'click', ->
      scope.$eval attr['accordionClick']
      scope.$apply()

    scope.$watch attr['accordionShow'], (value) ->
      content = el.children '[content]'
      if value
        scope.isDataHidden = false
        el.addClass 'active'
        $timeout ->
          content.slideDown 300
          $timeout ->
            scope.isHidden = false
          , 300
      else
        scope.isHidden = true
        $timeout ->
          content.slideUp 300
          $timeout ->
            scope.isDataHidden = true
            el.removeClass 'active'
          , 300
        , 200


@app.directive 'sideMenuShow', ->
  link: (scope, el, attr) ->

    scope.$watch attr['sideMenuShow'], (value) ->
      content = el.children '[content]'
      if value
        scope.isHidden = false
      else
        scope.isHidden = true




@app.directive 'slideThisShow', ($timeout) ->
  link: (scope, el, attr) ->
    scope.$watch attr['slideThisShow'], (value) ->
      if value is true
        scope.isDataDisplayed = true
        $timeout ->
          el.slideDown 300
          $timeout ->
            scope.isDisplayed = true
          , 300
      else if value is false
        scope.isDisplayed = false
        $timeout ->
          el.slideUp 300
          $timeout ->
            scope.isDataDisplayed = false
          , 300
        , 200


@app.directive 'easySlideBlock', ->
  scope: true
  link: (scope, el, attr) ->
    scope.show = attr['default']
    el.on 'click', ->
      scope.show = !scope.show
      scope.$apply()

    scope.$watch 'show', (value) ->
      content = el.siblings '[content-block]'
      if value
        el.addClass 'active'
        content.slideDown 300
      else
        content.slideUp 300
        el.removeClass 'active'


@app.directive 'slideBlock', ->
  link: (scope, el, attr) ->
    content = el.siblings '[content-block]'
    initValue = scope.$eval attr['slideBlock']
    if initValue
      el.addClass 'active'
    else
      content.css 'display', 'none'
      el.removeClass 'active'

    scope.$watch attr['slideBlock'], (value) ->
      if value
        el.addClass 'active'
        content.slideDown 300
      else
        content.slideUp 300
        el.removeClass 'active'


@app.directive 'accountDesktopMenu', ($timeout) ->
  link: (scope, el, attr) ->
    scope.$on 'account:selected', (ev, data) ->
      $timeout ->
        activeRow = data.el
        el.css 'top', activeRow.position()['top'] + ((activeRow.height() / 2) - (el.height() / 2))


@app.directive 'accountDisplay', ->
  link: (scope, el, attr) ->
    scope.$watch attr['accountDisplay'], (value) ->
      scope.$emit 'account:selected', el: el if value


@app.directive 'uploadButton', ($timeout) ->
  template:
    '<div class="button medium upload-button inverted">
      <input type="file" name="file" ng-file-select="fileSelectHandler($files)">
      <span ng-transclude></span>&nbsp;
      <span class="file-names" ng-repeat="file in files" ng-bind="file.name"></span>
    </div>'
  transclude: true
  scope:
    files: '='
  link: (scope, el, attr) ->
    el.on 'click', () ->
      el.find('input').click()

    el.find('input').on 'click', (e) ->
      e.stopPropagation()

    scope.fileSelectHandler = (files) ->
      scope.files = files


@app.directive 'inlineEdit', ->
  template:
    '<a ng-if="!editing" ng-click="edit()">' +
      '<span class="valign" ng-transclude></span>' +
      '<span class="icon-edit"></span>' +
    '</a>' +
    '<form ng-if="editing" ng-submit="ok(value)">' +
      '<input class="small-input offset-bottom-5" type="text" ng-disabled="isLoading" ng-model="value">' +
      '<a class="icon-ok" ng-click="ok(value)"></a>' +
      '<a class="icon-cancel" ng-click="cancel()"></a>' +
    '</form>'
  transclude: true
  require: 'ngModel'
  scope:
    save: '&'

  link: (scope, el, attr, ngModel) ->
    scope.isLoading = scope.editing = false

    scope.edit = ->
      scope.value = ngModel.$viewValue
      scope.editing = true
      scope.isLoading = false

    scope.ok = (newValue) ->
      return if scope.isLoading

      oldValue = ngModel.$viewValue
      ngModel.$setViewValue newValue

      promise = scope.save
        oldValue: oldValue
        newValue: newValue

      if not promise.then
        scope.editing = false
      else
        scope.isLoading = true
        promise
        .finally -> scope.isLoading = false
        .then -> scope.editing = false
        .catch (err) ->
          ngModel.$setViewValue oldValue
          alert err
    scope.cancel = ->
      scope.editing = false

#@app.directive 'gcField', ->
#  template:
#    '<div ng-class="::labelContainerClass">' +
#        '<label class="required" ng-bind="::formData.label|capitalize"></label>' +
#        '<div class="description" ng-bind="::formData.help_text|capitalize"></div>' +
#    '</div>' +
#    '<div ng-class="::inputContainerClass">' +
#        '<input ng-model="parent[name]" ng-disabled="isLoading" type="text">' +
#        '<div ng-if="errors.length" ng-repeat="err in errors" ng-bind="::err" class="error"></div>' +
#    '</div>'
#  scope:
#    errors: '='
#    formData: '='
#    parent: '='
#    name: '@'
#    labelContainerClass: '@'
#    inputContainerClass: '@'

@app.directive 'iframeSetDimensionsOnload', ->
    link: (scope, element, attrs) ->
        element.on 'load', ->
               element.css 'height', element[0].contentWindow.document.body.scrollHeight + 'px'


@getWatchers = (root) ->
  getElemWatchers = (element) ->
    isolateWatchers = getWatchersFromScope(element.data().$isolateScope)
    scopeWatchers = getWatchersFromScope(element.data().$scope)
    watchers = scopeWatchers.concat(isolateWatchers)
    angular.forEach element.children(), (childElement) ->
      watchers = watchers.concat(getElemWatchers(angular.element(childElement)))
      return

    watchers
  getWatchersFromScope = (scope) ->
    if scope
      scope.$$watchers or []
    else
      []
  root = angular.element(root or document.documentElement)
  watcherCount = 0
  getElemWatchers root


@app.directive 'paginator', ->
  template:
    '<ul>' +
      '<li class="prev">' +
        '<a ng-click="object.gotoPrev()"></a>' +
      '</li>' +
      '<li ng-repeat="p in object.pages" ng-switch on="object.page === p" ng-class="{active: object.page === p}">' +
        '<span ng-switch-when="true" ng-bind="::p"></span>' +
        '<a ng-switch-default ng-bind="::p" ng-click="object.goto(p)"></a>' +
      '</li>' +
      '<li class="next">' +
        '<a ng-click="object.gotoNext()"></a>' +
      '</li>' +
    '</ul>'
  scope:
    object: '='

@app.directive 'perPage', ->
  template:
    '<ul class="right">' +
      '<li class="title" ng-transclude></li>' +
      '<li ng-repeat="pp in object.perPageChoices"' +
        'ng-class="{active: object.perPage === pp}"' +
        'ng-switch on="object.perPage === pp">' +
        '<span ng-switch-when="true" ng-bind="::pp"></span>' +
        '<a ng-switch-default ng-bind="::pp" ng-click="object.setPerPage(pp)"></a>' +
      '</li>' +
    '</ul>'
  transclude: true
  scope:
    object: '='

#helper to create modal windows
@app.factory "newModal", ($rootScope, $modal) ->
  (data) ->
    ->
      throw 'No controller for modal window, just' + data.ctrl unless data.ctrl?
      $rootScope.setGlobalLoading true
      options =
        controller: data.ctrl
        resolve: {}
      angular.extend options, data.options
      if data.resolve?
        angular.extend options.resolve, data.resolve.apply this, arguments

      promise = $modal.open options
      promise.opened.finally -> $rootScope.setGlobalLoading false
      promise


@app.factory "getFormData", ($q, $http) ->
  (url) ->
    $q (resolve, reject) ->
      $http
        method: "OPTIONS"
        url: url
      .success (data) -> resolve (data.actions.POST or data.actions.PUT)
      .catch reject

@app.filter('nl2br', ($sanitize) => (msg) => $sanitize(msg.replace(/(\r\n|\n\r|\r|\n|&#10;&#13;|&#13;&#10;|&#10;|&#13;)+/g, '<br />$1')))