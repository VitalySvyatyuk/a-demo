window.addEventListener('DOMContentLoaded', function (){
  'use strict';

  // START OF: utilities =====
  function throttle (callback, limit) {
    var wait = false;                  // Initially, we're not waiting
    return function () {               // We return a throttled function
      if (!wait) {                   // If we're not waiting
        callback.call();           // Execute users function
        wait = true;               // Prevent future invocations
        setTimeout(function () {   // After a period of time
          wait = false;          // And allow future invocations
        }, limit);
      }
    }
  }

  function isMobile() {
    //return (/Android|iPhone|iPad|iPod|BlackBerry/i).test(navigator.userAgent || navigator.vendor || window.opera);

    return window.outerWidth < 768;
  }

  function isCollapsedMenu(value) {
    return window.outerWidth <= value;
  }

  // ===== END OF: utilities

  // START OF: webfont loader  =====
  var fonts = (function(){
    var families = ['Lato:400,300,700:latin'];

    function load() {
      WebFont.load({
        google: {
          families: families
        }
      });
    }
    return {
      load: load
    }
  }());
  // ===== END OF: webfont loader

  // START OF: sliders =====
  //all the sliders are configurated via attributes in the markup
  (function() {

    var $sliders = $('.js-slider');
    $sliders.add('#frontpage-main-slider').on('init', function(slick){
      $('.slider_jumbotron__dots')
      .wrap('<div class="slider_jumbotron__dots_container"></div>');
    });

    $sliders.slick();
  })();


  $('#frontpage-main-slider').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    fade: false,
    arrows: true,
    dots: true,
    dotsClass: 'slider_jumbotron__dots',
    prevArrow: '.js-slider-prev-arrow',
    nextArrow: '.js-slider-next-arrow',
    autoplay: true,
    pauseOnHover: false,
    autoplaySpeed: 5000
  })

  $('#frontpage-main-slider-content').find('button').on('click', function() {
    $('#frontpage-main-slider').slick('slickPause');
  });
  // ===== END OF: sliders

  // START OF: scroll to =====
  var scrollTo = (function(){
    var $scrollIntro = $('.js-scroll-intro');
    var scrollIntro = function () {
      var value = $('.header').innerHeight() + $('.nav').innerHeight() + $('.subheader').innerHeight() + $('.slider_jumbotron').innerHeight();

      $('html,body').animate({scrollTop: value}, 500);
    }
    var bindScrollIntro = function () {
      $scrollIntro.on('click', function(event) {
        event.preventDefault();
        scrollIntro();
      });
    }

    return {
      bindScrollIntro: bindScrollIntro
    }
  }());

  // partnership scroll-to
  $('#partnership-button-scroll-from').on('click', function(e) {
    e.preventDefault()
    var value = $('#partnership-form-scroll-to').offset().top
    $('html,body').animate({scrollTop: value}, 500);
  })

  // ===== END OF: scroll to


  // START OF: content changer =====
  //var contentChanger = (function(){
  //  var $contentTrigger = $('.js-content-trigger');
  //  var $contentBox = $('.js-content-box');
  //  var slidingTime = 400;
  //  var bind = function () {
  //    $contentTrigger.on('click', function(event) {
  //      event.preventDefault();
  //      var contentAttr = $(this).attr('data-content-index');
  //
  //      $contentTrigger.removeClass('state-active');
  //      $(this).addClass('state-active');
  //
  //      $contentBox.slideUp(slidingTime);
  //
  //      setTimeout(function(){
  //        $('.js-content-box[data-content-index="' + contentAttr +'"]').slideDown(slidingTime);
  //      }, slidingTime/2);
  //    });
  //  }
  //  return {
  //    bind: bind
  //  }
  //}());
  // ===== END OF: content changer

  // START OF: dropdowns =====
  var dropdown = {
    toggle: function ($targetDropdown) {
      //$targetDropdown.toggleClass('state-visible');
      $targetDropdown.stop().slideToggle(200);
    },
    open: function ($targetDropdown) {
      //$targetDropdown.toggleClass('state-visible');
      $targetDropdown.stop().slideDown(200);
    },
    close: function ($targetDropdown) {
      //$targetDropdown.toggleClass('state-visible');
      $targetDropdown.stop().slideUp(200);
    },
    collapseAll: function () {
      //$('.js-dropdown').removeClass('state-visible');
      $('.js-dropdown').stop().slideUp(200);
    },
    bindCollapsingAll: function () {
      $(document).on('click', function(event) {
        dropdown.collapseAll();
      });
    },
    bindOpeners: function () {
      $('.js-dropdown-opener').off()
      if(!isMobile()){
        $('.js-dropdown-opener').on('mouseenter click', function(event) {
          var dropdownName = $(this).attr('data-dropdown-target');
          var $targetDropdown = $('[data-dropdown-name=' + dropdownName + ']');
          dropdown.open($targetDropdown);
        });
        $('.js-dropdown-opener').on('mouseleave', function(event) {
          var dropdownName = $(this).attr('data-dropdown-target');
          var $targetDropdown = $('[data-dropdown-name=' + dropdownName + ']');
          dropdown.close($targetDropdown);
        });
      } else {
        $('.js-dropdown-opener').on('click', function(event) {
          event.preventDefault();
          event.stopPropagation();

          if(isMobile()){
            var dropdownName = $(this).attr('data-dropdown-target');
            var $targetDropdown = $('[data-dropdown-name=' + dropdownName + ']');
            dropdown.toggle($targetDropdown);
          }else{
            dropdown.collapseAll();
          }
        });
      }
    },
    init: function () {
      this.bindCollapsingAll();
      this.bindOpeners();

      window.addEventListener('resize', function (){
        throttle(dropdown.bindOpeners(), 500);
      });
    }
  };
  // ===== END OF: dropdowns


  // START OF: menu =====
  var menu = (function(){
    var $menu = $('.js-menu');
    var $body = $('body');

    function bind() {
      $('.js-open-menu').on('click', function(event) {
        event.preventDefault();

        $(this).toggleClass('state-active');
        $menu.slideToggle(200);

        $body.toggleClass('state-fixed-body');
      });

      $(document).on('click', function(event) {
        if(!$(event.target).hasClass('js-open-menu')){
          $menu.slideUp(200);
          $('.js-open-menu').removeClass('state-active');

          if($('.js-popup:visible').length === 0){
            $body.removeClass('state-fixed-body');
          }
        }
      });
    }

    return {
      bind: bind
    }
  }());
  // ===== END OF: menu


  // START OF: submenu opening =====
  var openSubmenu = (function(){
    var init = function () {
      $('.js-open-submenu').on('click', function(event) {

        var breakpoint = parseInt($(this).attr('data-breakpoint'), 10);

        if(isCollapsedMenu(breakpoint)){
          event.preventDefault();
          event.stopPropagation();
          var $submenuToOpen = $(this).siblings('.js-menu-list');
          var $submenuToClose = $('.js-menu-list').not($submenuToOpen);
          $submenuToClose.slideUp(200);
          $submenuToOpen.slideToggle(200);

          var $titleToClose = $submenuToClose.siblings('.js-open-submenu');
          var $titleToOpen = $submenuToOpen.siblings('.js-open-submenu');

          $titleToClose.removeClass('state-active');
          $titleToOpen.toggleClass('state-active');
        }
      });
    }
    return {
      init: init
    }
  }());
  // ===== END OF: submenu opening


  // START OF: popups =====
  var popup = {
    OPENING_DURATION: 300, //a hardcoded value. equals the CSS transition-duration.
    DOM: {
      $popups: $('.js-popup'),
      $openers: $('.js-open-popup'),
      $ovelay: $('.js-overlay'),
      $closers: $('.js-close-all-popups'),
      $body: $('body'),
      $document: $(document)
    },
    toggleOverlay: function () {
      //this.DOM.$ovelay.toggleClass('state-visible');
      this.DOM.$ovelay.fadeToggle(this.OPENING_DURATION * 2/3);
    },
    toggleBodyFix: function () {
      this.DOM.$body.toggleClass('state-fixed-body');
    },
    open: function (name) {
      $('[data-popup-name="' + name + '"]').fadeIn(this.OPENING_DURATION);
      this.toggleOverlay();
      this.toggleBodyFix();
      this.DOM.$popups.css('top', this.DOM.$document.scrollTop() + 10)
    },
    closeOpened: function () {
      var self = this;
      self.DOM.$popups.fadeOut(self.OPENING_DURATION);
      //setTimeout(function(){
      //  self.DOM.$popups.removeClass('state-visible');
      //}, self.OPENING_DURATION);
      this.toggleOverlay();
      this.toggleBodyFix();
    },
    bindOverlay: function () {
      var self = this;
      self.DOM.$ovelay.on('click', function(event) {
        event.preventDefault();
        self.closeOpened();
      });
    },
    bindOpeners: function ($specificElement) {
      var self = this;
      var $triggers = $specificElement ? $specificElement : self.DOM.$openers;

      $triggers.on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();

        var name = $(this).attr('data-popup-target');

        self.open(name);
      });
    },
    bindClosers: function () {
      var self = this;
      self.DOM.$closers.on('click', function(event) {
        event.preventDefault();
        self.closeOpened();
      });
    },
    init: function () {
      this.bindOverlay();
      this.bindOpeners();
      this.bindClosers();
    }
  };
  // ===== END OF: popups


  // START OF: hacks =====
  var hacks = {
    DOM: {
      $covers: $('.js-cover')
    },
    //windowHeight: $(window).outerHeight(),
    setIntroHeight: function () {
      if($(window).outerWidth() <= 1024){
        this.DOM.$covers.css('min-height', $(window).outerHeight());
      }else{
        this.DOM.$covers.css('min-height', '100vh');
      }
    },
    bind: function () {
      var self = this;

      window.addEventListener('orientationchange', function (){
        self.setIntroHeight();
      });
    },
    init: function () {
      this.bind();
    }

  };
  if (hacks.DOM.$covers.length){
    hacks.setIntroHeight();
    hacks.init();
  }
// ===== END OF: hacks


  // START OF: subnav opening =====
  var subnav = {
    DOM: {
      $subnav: $('.js-subnav')
    },
    toggle: function ($targetSubnav) {
      $targetSubnav.slideToggle(200);
    },
    collapseAll: function () {
      this.DOM.$subnav.slideUp(200);
    },
    bindCollapsingAll: function () {
      $(document).on('click', function(event) {
        subnav.collapseAll();
      });
    },
    bindOpeners: function () {
      $('.js-open-subnav').off().on('mouseenter', function(event) {
        event.preventDefault();
        event.stopPropagation();

        subnav.collapseAll();

        var $targetSubnav = $(this).find('.js-subnav');
        if(!$targetSubnav.is(":visible")){
          subnav.toggle($targetSubnav);
        }
      });
      $('.js-open-subnav').on('mouseleave', function(event) {
        subnav.collapseAll();
      });
    },
    init: function () {
      this.bindCollapsingAll();
      this.bindOpeners();
    }
  };
  // ===== END OF: subnav opening


  // START OF: pseudolink =====
  var pseudolink = (function(){
    var bind = function() {
      $('.js-pseudolink').on('click', function(event) {
        event.preventDefault();
        var href = $(this).attr('data-href');

        window.open(href, '_blank');
      });
    }
    return {
      bind: bind
    }
  }());
  // ===== END OF: pseudolink


  // START OF: tabs =====
  var tabs = (function(){
    var bind = function () {
      $('.js-tab').on('click', function(event) {
        event.preventDefault();
        var index = $(this).attr('data-tab-index');
        var category = $(this).attr('data-tab-category');

        $('.js-tab[data-tab-category=' + category + ']').removeClass('state-active-tab');
        $(this).addClass('state-active-tab');
        $('.js-tab-content[data-tab-category=' + category + ']').removeClass('state-visible');
        $('.js-tab-content[data-tab-index=' + index + ']').addClass('state-visible');
      });
    }
    return {
      bind: bind
    }
  }());

  var tabsB = (function(){
    var bind = function () {
      $('.js-tab-b').on('click', function(event) {
        event.preventDefault();
        var index = $(this).attr('data-tab-index');
        var category = $(this).attr('data-tab-category');

        $('.js-tab-b[data-tab-category=' + category + ']').removeClass('state-active-tab');
        $(this).addClass('state-active-tab');
        $('.js-tab-content-b[data-tab-category=' + category + ']').removeClass('state-visible');
        $('.js-tab-content-b[data-tab-index=' + index + ']').addClass('state-visible');
      });
    }
    return {
      bind: bind
    }
  }());
  // ===== END OF: tabs


  // START OF: transform menu =====
  var transformMenu = (function(){
    var $header = $('.js-header');
    var offset = $('.js-main-nav').offset().top;

    var bind = function () {
      $(window).on('scroll', function(event) {
        if(window.outerWidth >= 1280 && window.scrollY > offset){
          $header.addClass('state-full');
        }else{
          $header.removeClass('state-full');
        }
      });
    }

    return {
      bind: bind
    }
  }());
  // ===== END OF: transform menu


  $(document).ready(function() {
    //to create a tooltip make an element with .tooltip.js-tooltip(title="Tooltip content")
    $('.js-tooltip').tooltipster({side:  ['bottom']});
  });


  // START OF: inout mask =====
  Inputmask().mask(document.querySelectorAll("input"));
  // ===== END OF: inout mask

  openSubmenu.init();
  transformMenu.bind();
  tabs.bind();
  tabsB.bind();
  popup.init();
  menu.bind();
  pseudolink.bind();
  scrollTo.bindScrollIntro();
  subnav.bindCollapsingAll();
  subnav.bindOpeners();
  dropdown.init();

  //fonts.load();
  //scrollTo.bindScrollFullscreen();
  //contentChanger.bind();
  //charts.init();
  //navigation.bind();
  //showWorks.bind();
  //if($('.filtr-container').length > 0){
  //  filterizr.init();domain=.example.com;
  //}
});

// Modal Language Popup

function getCookie(c_name)
{
  if (document.cookie.length>0)
  {
   c_start=document.cookie.indexOf(c_name + "=");
   if (c_start!=-1)
   {
    return true;
  }
}
return false;
}

var showIt = getCookie('show');
if (!showIt) {
 document.getElementById('modal_language_selection_overlay').style.display='block';
 document.cookie='show=true; path=/; expires=Mon, 01-Jan-2020 00:00:00 GMT';
}


$( ".modal_language_selection button" ).click(function(){
  $('#modal_language_selection_overlay').fadeOut( "slow" );
});
$( ".current-lang" ).click(function(){
  $('#modal_language_selection_overlay').fadeOut( "slow" );
});

// Cookies pop-ap
$(document).ready(function(){
  $.cookieBar();
});

// Cookies warning risk
$(document).ready(function(){
  setTimeout(function() {
    $('.cookies_risk-warning').fadeOut('slow');
    $('#cookie-bar, #cookie-barB').css({
      'bottom' : '0',
      'transition-duration' : '1.5s'
    });
  }, 60000);
});

// Requset form on partnership page
$(document).ready(function(){
  $('#partnership-form').submit(function(e) {
    console.log($(this).serialize());
    $.post('/partnership/', $(this).serialize(), function() {
      $('#success-partnershipForm-send_overlay').show();
    });
    e.preventDefault();
  });
  $( "#success-partnershipForm-send button" ).click(function() {
    $('#success-partnershipForm-send_overlay').fadeOut();
  });
});

// Subscribe form block

$(document).ready(function() {
  $('#subscribe-form').submit(function(e) {
    $.post('/subscribe/', $(this).serialize(), function() {
    });
    e.preventDefault();
  })
});


// Callback request popup
$(document).ready(function() {
  $('#callback_request-form').submit(function(e) {
    $.post('/callback_request/', $(this).serialize(), function() {
      $('#success-callbackForm-send_overlay').show();
    });
    e.preventDefault();
  })
  $( "#success-callbackForm-send button" ).click(function() {
    $('#success-callbackForm-send_overlay').fadeOut();
    $(".js-overlay.js-close-navigation.js-close-menu.overlay").fadeOut();
    $(".popup.popup--callback.js-popup").fadeOut();
    $("#callback_request-form")[0].reset();
  });
});

// Profile info show/hide div on checkbox choice

function Selected(a) {
  var label = a.value;
  if (label=="Open") {
   document.getElementById("Block1").style.display='block';
 } else {
   document.getElementById("Block1").style.display='none';
 }
}

// Requset form on partnership page
$(document).ready(function(){
  $('.subscribe-form form').submit(function(e) {
    $('#success-subscribe-overlay').show();
    e.preventDefault();
  });
  $( "#success-subscribe-send button" ).click(function() {
    $('#success-subscribe-overlay').fadeOut();
    $('.subscribe-form form')[0].reset();
  });
  $(".subscribe-form-checkbox").on("change", function () {
    if (!$(".subscribe-form-checkbox:checked").length)
      $("button.button").prop("disabled", "disabled");
    else
      $("button.button").removeAttr("disabled");
  });
})

