import {Manager} from '../models/Manager'

angular.module('GCRM').service('Info', function($interval, $rootScope) {
  this.reload = () => {
    return Manager.getInfo().then((objects) => {
      this.objects = objects
    })
  }

  this.reload()
  $interval(() => {this.reload()}, 10*60*1000)
  $rootScope.$on('$stateChangeStart', this.reload.bind(this))
})