/* ==========================================================================
   VICTEX Renewal - HERO (Main Visual) script
   --------------------------------------------------------------------------
   index.html 하단 인라인 스크립트에 있던 히어로 관련 로직을 분리한 파일.
   동작은 원본과 동일하다.
     - Owl Carousel 2 페이드 슬라이드 (3장, loop, dots + prev/next)
     - 재생/정지 토글 (.mv_play / .mv_stop)
     - SCROLL 아이콘 클릭 시 fullPage.js 2번째 섹션으로 이동
   의존성: jQuery 1.11, owl.carousel.min.js, fullpage.js (index.html 에서 로드)
   ========================================================================== */
(function ($) {
	'use strict';

	var HERO_AUTOPLAY_TIMEOUT = 8000;

	$(function () {
		var $hero = $('.mv_sec');
		if (!$hero.length) return;

		var Mv_owl = $hero.find('.mv_owl').owlCarousel({
			animateOut : 'fadeOut',
			animateIn : 'fadeIn',
			items : 1,
			loop : true,
			margin : 0,
			autoplay : false,
			autoplayTimeout : HERO_AUTOPLAY_TIMEOUT,
			dots : true,
			nav : true
		});

		// 재생/정지 토글: .on 이 붙은 버튼은 숨김 처리됨 (hero.css 참고)
		$hero.find('.mv_play').on('click', function () {
			Mv_owl.trigger('play.owl.autoplay', [HERO_AUTOPLAY_TIMEOUT]);
			$(this).addClass('on');
			$hero.find('.mv_stop').removeClass('on');
		});
		$hero.find('.mv_stop').on('click', function () {
			Mv_owl.trigger('stop.owl.autoplay');
			$(this).addClass('on');
			$hero.find('.mv_play').removeClass('on');
		});

		// SCROLL 아이콘 → 다음 섹션
		$hero.find('.mv_scroll').on('click', function () {
			if ($.fn.fullpage && $.fn.fullpage.moveTo) $.fn.fullpage.moveTo(2);
		});
	});
})(jQuery);
