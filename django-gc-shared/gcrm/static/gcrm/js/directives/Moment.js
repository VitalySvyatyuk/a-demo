import moment from 'moment-timezone'

angular.module('GCRM').filter('moment', () => {
  return (input, format, tz) => {
    if(!input)
      return '-'
    let dt = input === 'now'? moment() : moment(input)
    if(tz)
      dt = dt.tz(tz)
    if(format && format=='calendar') {
      if(Math.abs(dt.dayOfYear() - moment().dayOfYear()) < 2)
        dt = dt.calendar(null, {sameElse: 'L LT'})
      else
        dt = dt.format('L LT')
    }
    else if(format)
      dt = dt.format(format)
    return dt
  }
})
