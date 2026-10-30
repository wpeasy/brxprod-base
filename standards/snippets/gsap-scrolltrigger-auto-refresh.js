// GSAP ScrollTrigger auto-refresh — store as a JS snippet named
// "GSAP ScrollTrigger auto-refresh" (AGENTS.md › Motion › GSAP). It must run
// after BRXProd's gsap-loader has defined gsap and ScrollTrigger.
// ScrollTrigger measures once at load and again only on window resize; this
// re-measures when the document height changes (late images/fonts, opened
// panels, Bricks editor re-renders), at most once per animation frame.
(() => {
	if (!window.gsap || !window.ScrollTrigger) return;
	if (document.body.hasAttribute('data-st-refresh')) return;
	document.body.setAttribute('data-st-refresh', '');
	let frame = 0;
	let height = document.documentElement.scrollHeight;
	const refresh = () => {
		cancelAnimationFrame(frame);
		frame = requestAnimationFrame(() => ScrollTrigger.refresh());
	};
	new ResizeObserver(() => {
		const next = document.documentElement.scrollHeight;
		if (next === height) return;
		height = next;
		refresh();
	}).observe(document.body);
	window.addEventListener('load', refresh, { once: true });
})();
