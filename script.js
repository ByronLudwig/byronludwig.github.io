// Current year in the footer.
document.getElementById('year').textContent = new Date().getFullYear();

// Drag-to-scroll the screenshot strips on desktop; touch scrolling is native.
document.querySelectorAll('.shots').forEach(strip => {
  let startX = 0;
  let startScroll = 0;
  let dragging = false;

  strip.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'mouse') return;
    dragging = true;
    startX = event.clientX;
    startScroll = strip.scrollLeft;
    strip.classList.add('is-grabbing');
    strip.setPointerCapture(event.pointerId);
  });

  strip.addEventListener('pointermove', event => {
    if (!dragging) return;
    strip.scrollLeft = startScroll - (event.clientX - startX);
  });

  const stop = () => {
    dragging = false;
    strip.classList.remove('is-grabbing');
  };

  strip.addEventListener('pointerup', stop);
  strip.addEventListener('pointercancel', stop);

  // Left/right keys scroll the strip once it has focus.
  strip.addEventListener('keydown', event => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const step = strip.clientWidth * 0.6;
    strip.scrollBy({ left: event.key === 'ArrowRight' ? step : -step, behavior: 'smooth' });
  });
});
