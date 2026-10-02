/* ==========================================================================
   VICTEX Renewal_1 - HERO (Main Visual) script  ·  1-1안
   --------------------------------------------------------------------------
   - "빅텍스 소개 영상 재생하기" 버튼 → <dialog> 레이어에 YouTube 영상 재생
     · 열려 있는 동안 fullPage.js 휠/키보드 섹션 이동을 멈춘다
     · Esc / 닫기 버튼 / 바깥 영역 클릭으로 닫고, 닫으면 영상도 멈춘다
   - 영상 ID 는 버튼의 data-hero-video 속성에서 읽는다 (교체 시 그 값만 변경)
   의존성 없음. fullPage.js 가 있으면 함께 제어한다.
   ========================================================================== */
(function () {
	'use strict';

	var trigger = document.querySelector('.hero [data-hero-video]');
	var dialog = document.querySelector('.hero-modal');
	if (!trigger || !dialog) return;

	var frame = dialog.querySelector('.hero-modal__frame');
	var closeBtn = dialog.querySelector('.hero-modal__close');
	var supportsDialog = typeof dialog.showModal === 'function';

	function fullpage(method, value) {
		var api = window.fullpage_api || (window.jQuery && window.jQuery.fn.fullpage);
		if (api && typeof api[method] === 'function') api[method](value);
	}

	function lockPage(locked) {
		fullpage('setAllowScrolling', !locked);
		fullpage('setKeyboardScrolling', !locked);
		document.documentElement.classList.toggle('hero-modal-open', locked);
	}

	function open() {
		var id = encodeURIComponent(trigger.getAttribute('data-hero-video'));
		frame.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id +
			'?autoplay=1&rel=0&playsinline=1" title="빅텍스 소개 영상" ' +
			'allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
		if (supportsDialog) dialog.showModal();
		else dialog.setAttribute('open', '');
		lockPage(true);
		closeBtn.focus();
	}

	function close() {
		if (supportsDialog) dialog.close();
		else { dialog.removeAttribute('open'); onClosed(); }
	}

	function onClosed() {
		frame.innerHTML = ''; // 재생 중지
		lockPage(false);
		trigger.focus();
	}

	trigger.addEventListener('click', open);
	closeBtn.addEventListener('click', close);
	dialog.addEventListener('close', onClosed);
	// 바깥(backdrop) 클릭 시 닫기 — 영상 영역 클릭은 iframe 이 받으므로 dialog 자체가 target 일 때만
	dialog.addEventListener('click', function (e) { if (e.target === dialog) close(); });
	if (!supportsDialog) {
		document.addEventListener('keydown', function (e) {
			if (e.key === 'Escape' && dialog.hasAttribute('open')) close();
		});
	}
})();
