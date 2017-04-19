import {Region} from '../models/Region'

angular.module('GCRM').component('regionSelect', {
  bindings: {
    model: '=',
    onChange: '&',
  },
  templateUrl: '/gcrm/templates/component.regionSelect.html',
  controllerAs: 'regionSelect',
  controller: function ($timeout) {
    this.model = this.model || []
    this.selectedRegion = []

    if (this.model.length && !this.selectedRegion.length)
      Region.getList({ids: this.model}).then((objects) => {
        this.selectedRegion = []
        for (let region of objects.items) {
          this.selectedRegion.push(region)
        }
      })

    this.searchRegion = (regionName) => {
      Region.getList({search: regionName, per_page: 5}).then((objects) => {
        this.regions = []
        for (let region of objects.items) {
          if (!(this.model.indexOf(region.data.id)+1))
            this.regions.push(region)
        }
      })
    }

    this.addRegion = (item) => {
      this.selectedRegion.push(item)
      this.model.push(item.data.id)
      this.regionName = undefined
      $timeout(this.onChange.bind(this), 1);
    }

    this.removeRegion = (item) => {
      this.selectedRegion.splice(this.selectedRegion.indexOf(item), 1)
      this.model.splice(this.model.indexOf(item.data.id), 1)
      $timeout(this.onChange.bind(this), 1);
    }
  }
})
