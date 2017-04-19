import {Country} from '../models/Country'

angular.module('GCRM').component('countrySelect', {
  bindings: {
    model: '=',
    onChange: '&',
  },
  templateUrl: '/gcrm/templates/component.countrySelect.html',
  controllerAs: 'countrySelect',
  controller: function ($timeout) {
    this.model = this.model || []
    this.selectedCountry = []
    if (this.model.length && !this.selectedCountry.length)
      Country.getList({ids: this.model}).then((objects) => {
        this.selectedCountry = []
        for (let country of objects.items) {
          this.selectedCountry.push(country)
        }
      })

    this.searchCountry = (countryName) => {
      Country.getList({search: countryName, per_page: 5}).then((objects) => {
        this.countries = []
        for (let country of objects.items) {
          if (!(this.model.indexOf(country.data.id)+1))
            this.countries.push(country)
        }
      })
    }

    this.addCountry = (item) => {
      this.selectedCountry.push(item)
      this.model.push(item.data.id)
      this.countryName = undefined
      $timeout(this.onChange.bind(this), 1);
    }

    this.removeCountry = (item) => {
      this.selectedCountry.splice(this.selectedCountry.indexOf(item), 1)
      this.model.splice(this.model.indexOf(item.data.id), 1)
      $timeout(this.onChange.bind(this), 1);
    }
  }
})
