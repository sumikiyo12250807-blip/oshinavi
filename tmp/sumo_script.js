//スマホメニュー
window.onload = function () {
    var nav = document.getElementById('sp_nav');
    var hamburger = document.getElementById('js-hamburger');
    hamburger.addEventListener('click', function () {
        nav.classList.toggle('open');
    });
};


//アコーディオン
$(function () {
  // ページ読み込み時
  $('.accordion').each(function(){
    // activeクラスの場合は初期状態で開いた状態にする
    if ( $(this).hasClass('active') ) {
      $(this).find('.accordion_head').removeClass('open');
      $(this).find('.accordion_head').addClass('open');
      $(this).find('.accordion_head').next().show()
    } else {
      $(this).find('.accordion_head').removeClass('open');
      $(this).find('.accordion_head').next().hide();
    }
  });

  $('.accordion_head').on('click', function () {
    $(this).next().slideToggle();
    // openクラスを切り替える
    $(this).toggleClass("open");
  });
});


//TOPページSPのみアコーディオン
$(function () {
   function initAccordion() {
    // 初期設定
    if (window.matchMedia('(max-width:768px)').matches) {
      // SPの処理
      $('.top_page').addClass('sp-mode');
    } else {
      // PCの処理
      $('.top_page').removeClass('sp-mode');
    }

    // 初期状態で開いておく
    $('.c_title').each(function(){
      $(this).removeClass('open');
      $(this).addClass('open');
      $(this).nextAll().show();
    });

    $('.c_title').on('click.accordion', function () {
      if (window.matchMedia('(max-width:768px)').matches) {
        $(this).next().slideToggle();
        //openクラスをつける
        $(this).toggleClass("open");
      }
    });
  }

   $(window).on('resize', function(){
    if (window.matchMedia('(max-width:768px)').matches) {
      if ( !$('.top_page').hasClass('sp-mode') ) {
        // PC表示からSP表示に切り替わった場合は初期化する
        $('.c_title').off('click.accordion');
        initAccordion();
      }
    } else {
      if ( $('.top_page').hasClass('sp-mode') ) {
        // SP表示からPC表示に切り替わった場合は初期化する
        $('.c_title').off('click.accordion');
        initAccordion();
      }
    }
  });

 // アコーディオンの初期化
 initAccordion();
 
});


// モーダルウィンドウ
$(function(){
$("#modal_open").click(function(){
	$(this).blur() ;
	if($("#modal-overlay")[0]) return false ;
	var dElm = document.documentElement , dBody = document.body;
	sX_syncerModal = dElm.scrollLeft || dBody.scrollLeft;
	sY_syncerModal = dElm.scrollTop || dBody.scrollTop;
	$("body").append('<div id="modal-overlay"></div>');
	$("#modal-overlay").fadeIn("slow");
	centeringModalSyncer();
	$("#modal-content").fadeIn("slow");
	$("#modal-overlay,#modal-close").unbind().click(function(){
		window.scrollTo( sX_syncerModal , sY_syncerModal );
		$("#modal-content,#modal-overlay").fadeOut("slow",function(){
			$('#modal-overlay').remove();
		});
	});
});

$(window).resize(centeringModalSyncer);
	function centeringModalSyncer(){
		var w = $(window).width();
		var h = $(window).height();
		var cw = $("#modal-content").outerWidth();
		var ch = $("#modal-content").outerHeight();
		$("#modal-content").css({"left": ((w - cw)/2) + "px","top": ((h - ch)/2) + "px"})
	}
});


//タブメニュー
jQuery(function($){
    $('.tab').click(function(){
        // クリックした要素の先祖要素の中で、classの値がgroupの要素を取得
        const group = $(this).parents('.modal_wrap'); 
        group.find('.is_active').removeClass('is_active');
        $(this).addClass('is_active');
        group.find('.is_show').removeClass('is_show');
        // クリックしたタブからインデックス番号を取得
        const index = $(this).index();
        // クリックしたタブと同じインデックス番号をもつコンテンツを表示
        //group.find(".panel").eq(index).addClass('is_show');
        // ふわっと表示
        group.find('.panel').eq(index).fadeIn(800).addClass('is_show');
        group.find('.panel').not('.is_show').hide();

        
        });
});


//スムーススクロール（ページ内リンク）
$(function(){
  $('a[href^="#"]').click(function(){
    var speed = 500;
    var href= $(this).attr("href");
    var target = $(href == "#" || href == "" ? 'html' : href);
    var position = target.offset().top;
    $("html, body").animate({scrollTop:position}, speed, "swing");
    return false;
  });
});

//テーブル横スクロールアシスト
$(function(){
  new ScrollHint('.js-scrollable', {
    i18n: {
      scrollable: 'スクロールできます'
    }
  });
});