$(document).ready(function(){
  $('a.footer_nav__link[href="/mt4/"]').each(function() {
    $(this).addClass("not-ready-platform-en");
  });
  $('a.footer_nav__link[href="/arumpro/"]').each(function() {
    $(this).addClass("not-ready-platform-en");
  });
});