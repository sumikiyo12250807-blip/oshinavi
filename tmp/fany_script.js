/**************** トップページ ローテーションバナー *******************/
$(document).ready(function () {
  $('.top_slide').slick({
    infinite: true,
    dots: true,
    autoplay: true,
    autoplaySpeed: 3000,
  });
});

/**************** PAGE TOP   *******************/
$(function () {
  var pageTop = $('.g-back-to-top');
  pageTop.css('bottom', '-100px');
  var showFlag = false;
  $(window).scroll(function () {
    if ($(this).scrollTop() > 80) {
      if (showFlag == false) {
        showFlag = true;
        pageTop.stop().animate({
          'bottom': '30px'
        }, 200);
      }
    } else {
      if (showFlag) {
        showFlag = false;
        pageTop.stop().animate({
          'bottom': '-100px'
        }, 200);
      }
    }
  });
  pageTop.click(function () {
    $('body,html').animate({
      scrollTop: 0
    }, 1200, "easeOutQuint");
    return false;
  });
});


document.addEventListener("DOMContentLoaded", function () {
  /* ハンバーガーメニュー */
  $(function() {
      $('.hamburger').click(function() {
          $(this).toggleClass('active');

          if ($(this).hasClass('active')) {
              $('.globalMenuSp').addClass('active');
              $('body').addClass('fixed');
          } else {
              $('.globalMenuSp').removeClass('active');
              $('body').removeClass('fixed');
          }
      });
  });

    // acordion
    $(".g-accordion-item").on("click", function(){
      $(this).parent().children().eq(1).slideToggle(300);
      $(this).parent().children().eq(0).toggleClass("g-accordion-no-bar");
      $(this).parent().siblings().find(".g-accordion-header").removeClass("g-accordion-open");
      $(this).parent().siblings().find(".g-accordion-header i.fa-angle-down").removeClass("rotate-fa");
      $(this).parent().find(".g-accordion-header").toggleClass("g-accordion-open");
      $(this).parent().find(".fa-angle-down").toggleClass("rotate-fa");
      $(".g-accordion-wrap .g-accordion-body").not($(this).parent().children().eq(1)).slideUp(300);
  });
});

// select初期値の文字色変更
$(function(){
    $("select.g-input").each(function(){
        $(this).on("change", function(){
            if ( $("option:selected", this).val() === "0" ) {
                return false;
            } else {
                return false;
            }
        });
    });
});

// 検索条件クリア
$(function(){
    $("button[name=reset-btn]").click(function(){
        $('input[type="text"], input[type="radio"], input[type="checkbox"], select').val("").removeAttr('checked').removeAttr('selected');
        $('select.g-input option[value="0"]').prop('selected', true);
    })
});

//カレンダー公演詳細切替
$(function(){
  var calendar = $(".g-calendarList");
  if (calendar.length) {
    var calendarBtn = calendar.find(".g-calendar_btn");
    if (calendarBtn.length) {
      calendarBtn.click(function() {
        var parentCalendar = $(this).closest(".g-calendarList");
        if (parentCalendar) {
          var siblingCalendarBtn = $(parentCalendar).find(".g-calendar_btn").not(this);
          if (siblingCalendarBtn.length) {
            siblingCalendarBtn.each(function(k, v) {
              if ($(v).attr("aria-expanded") === "true") {
                $(v).attr("aria-expanded", "false");
                var ariaControls = $(v).attr("aria-controls");
                if (ariaControls) {
                  var calendarEvent = $(parentCalendar).find("#" + ariaControls);
                  if (calendarEvent.length) {
                    calendarEvent.each(function(k, v) {
                      if ($(v).attr("aria-hidden") === "false") {
                        $(v).attr("aria-hidden", "true");
                      }
                    });
                  }
                }
              }
            });
          }
        }
      });
    }
  }
});
