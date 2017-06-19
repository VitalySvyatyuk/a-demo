/**
 * Created by pgubin on 14.12.15.
 */
angular.module('GCRM').component('perpage', {
  bindings: {
    objects: '=',
  },
  controllerAs: "perpage",
  controller: function () {},
  template: `
    <div class="btn-group pull-right" role="group">
        <button class="btn btn-secondary" type="button" ng-click="perpage.objects.setPerPage(10)">10</button>
        <button class="btn btn-secondary" type="button" ng-click="perpage.objects.setPerPage(50)">50</button>
        <button class="btn btn-secondary" type="button" ng-click="perpage.objects.setPerPage(100)">100</button>
    </div>
    `,
})
