import moment from 'moment-timezone'
import 'fullcalendar'
import 'fullcalendar/dist/lang/ru'
import 'fullcalendar/dist/lang/en-gb'

angular.module('GCRM').component('fullcalendar', {
  bindings: {
    load: '&',
  },
  restrict: 'A',
  transclude: false,
  controllerAs: 'fullcalendar',
  controller: function ($scope, $element) {
    jQuery($element).fullCalendar({
      lang: moment.locale(),
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,basicWeek,agendaWeek'
      },
      eventLimit: 15,

      events: (start, end, tz, cb) => {
        this.load({start: start, end: end, tz: tz, cb: cb})
      }
    })

    $scope.$on('fullcalendar.refetch', () => {
      jQuery($element).fullCalendar( 'refetchEvents' )
    })
  }
})
