/**
 * Created by pgubin on 14.12.15.
 */
angular.module('GCRM').component('paginator', {
  bindings: {
    objects: '=',
  },
  controllerAs: "paginator",
  controller: function() {},
  template: `
    <div class="btn-group pull-left">
      <button class="btn btn-secondary" type="button" ng-click="paginator.objects.gotoPrev()"><i class="fa fa-angle-left icon"></i></button>
      <button class="btn btn-secondary" type="button"
        ng-repeat="p in paginator.objects.pages"
        ng-class="{active: !paginator.objects.isLoading && paginator.objects.page === p, loading: paginator.objects.page === p && paginator.objects.isLoading }"
        ng-bind="::p"
        ng-click="paginator.objects.goto(p)"
        ></button>
      <button class="btn btn-secondary" type="button" ng-click="paginator.objects.gotoNext()"><i class="fa fa-angle-right icon"></i></button>
    </div>
    `,
})
