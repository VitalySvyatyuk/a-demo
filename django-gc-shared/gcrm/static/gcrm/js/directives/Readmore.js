angular.module('GCRM').component('readmoreLines', {
  bindings: {
    text: '=',
  },
  template: `
    <span ng-bind-html="::readmoreLines.short"></span>
    <span ng-if="::readmoreLines.more" ng-switch="readmoreLines.shown">
      <br />
      <span ng-switch-default>
        &nbsp;&nbsp;&nbsp;
        <a ng-click="readmoreLines.shown=true">&#x3E;&#x3E;&#x3E;&#x3E;</a>
      </span>
      <span ng-switch-when="true">
        <span ng-bind-html="::readmoreLines.more"></span>
        <br />
        &nbsp;&nbsp;&nbsp;
        <a ng-click="readmoreLines.shown=false">&#x3C;&#x3C;&#x3C;&#x3C;</a>
      </span>
    </span>
  `,
  restrict: 'AE',
  controllerAs: 'readmoreLines',
  controller: function () {
    let lines = this.text.split(/\<br ?\/\>/g)
    if(lines.length <= 4)
      this.short = this.text
    else {
      this.short = lines.slice(0, 4).join('<br />')
      this.more = lines.slice(4).join('<br />')
    }
  }
})
