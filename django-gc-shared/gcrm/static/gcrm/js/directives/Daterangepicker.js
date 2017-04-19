import moment from 'moment-timezone'
import 'bootstrap-daterangepicker/daterangepicker'

angular.module('GCRM').component('daterangepicker', {
  bindings: {
    start: '=',
    end: '=',
    onChange: '&',
    classes: '='
  },
  controllerAs: 'daterangepicker',
  template: `<input type="daterange" class="form-control" ng-class="::daterangepicker.classes">`,
  controller: function ($scope, $element, $timeout) {
    let ranges = {}
    ranges[LOCALE["All Time"]] = [
      moment("2001-01-01"),
      moment().add(6, 'month')
    ]
    ranges[LOCALE["Today"]] = [
      moment().startOf('day'),
      moment().endOf('day')
    ]
    ranges[LOCALE["Yesterday"]] = [
      moment().add(-1, 'days').startOf('day'),
      moment().add(-1, 'days').endOf('day')
    ]
    ranges[LOCALE["Last 3 Days"]] = [
      moment().add(-2, 'days').startOf('day'),
      moment().endOf('day')
    ]
    ranges[LOCALE["Last 7 Days"]] = [
      moment().add(-6, 'days').startOf('day'),
      moment().endOf('day')
    ]
    ranges[LOCALE["Last 30 Days"]] = [
      moment().add(-29, 'days').startOf('day'),
      moment().endOf('day')
    ]
    ranges[LOCALE["This Month"]] = [
      moment().startOf('month'),
          moment().endOf('month')
    ]
    jQuery($element.find('input')).daterangepicker({
      ranges: ranges,
      locale: {
        format: moment.localeData().longDateFormat('L'),
        daysOfWeek: moment.weekdaysMin(),
        monthNames: moment.monthsShort(),
        firstDay: moment.localeData().firstDayOfWeek()
      },
      minDate: moment("2001-01-01"),
      showDropdowns: true,
      autoApply: true,
      startDate: this.start || moment("2001-01-01"),
      endDate: this.end || moment().add(6, 'month')

    }, (start, end, label) => {
      $scope.$apply(() => {
          this.start = start.toDate()
          this.end = end.toDate()
          $timeout(this.onChange.bind(this), 1);
      })
    });
  }
})
