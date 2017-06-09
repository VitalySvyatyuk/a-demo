angular.module('GCRM').component('accountTypeSelectFilter', {
  bindings: {
    model: '=',
    onChange: '&',
    typesInfo: '='
  },
  templateUrl: '/gcrm/templates/component.accountTypeSelectFilter.html',
  controllerAs: "accountTypeSelectFilter",
  controller: function () {
    this.addType = (type) => {
      this.model.push(type)
      this.onChange()
    }
    this.removeType = (type) => {
      this.model.splice(this.model.indexOf(type), 1)
      this.onChange()
    }
  }
})
