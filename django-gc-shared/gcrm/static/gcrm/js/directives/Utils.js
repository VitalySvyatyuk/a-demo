angular.module('GCRM').filter('toColor', () => {
  return (input) => {
    let sum = 0;
    for(let i = 0; i < input.length; i++) sum += input.charCodeAt(i)
    return window.HOT_COLORS[Math.round((sum * 3.1415926535)) % window.HOT_COLORS.length]
  }
})


// window.HOT_COLORS =  ['#2478A5',
//  '#259A4D',
//  '#28760A',
//  '#3681C9',
//  '#389DDB',
//  '#3B588D',
//  '#45AC20',
//  '#4979B3',
//  '#4E962E',
//  '#5184E6',
//  '#5D9E17',
//  '#6172C3',
//  '#6299EB',
//  '#655BA1',
//  '#9588EA',
//  '#A0478D',
//  '#C45320',
//  '#D75840',
//  '#D94667',
//  '#DF4F8C',
//  '#DF8311',
//  '#E05EB2',
//  '#E6552E',
//  '#E73C55',
//  '#EF721F',
//  '#FF572C']
window.HOT_COLORS = [
  '#2478A5',
  '#6e6b6d',
  '#3B588D',
  '#28760A',
  '#3B588D',
  '#655BA1'
]


angular.module('GCRM').filter('nl2br', ($sanitize) => (msg) => $sanitize(msg.replace(/(\r\n|\n\r|\r|\n|&#10;&#13;|&#13;&#10;|&#10;|&#13;)+/g, '<br />$1')));
