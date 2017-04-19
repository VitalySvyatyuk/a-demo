angular.module('GCRM').component('tagSelectFilter', {
  bindings: {
    model: '=',
    onChange: '&',
    tagsInfo: '='
  },
  templateUrl: '/gcrm/templates/component.tagSelectFilter.html',
  controllerAs: "tagSelectFilter",
  controller: function () {
    this.addTag = (tag) => {
      this.model.push(tag)
      this.onChange()
    }
    this.removeTag = (tag) => {
      this.model.splice(this.model.indexOf(tag), 1)
      this.onChange()
    }
  }
})
