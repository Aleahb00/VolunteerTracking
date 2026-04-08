document.addEventListener("DOMContentLoaded", () => {
  const slider = document.getElementById("slider");
  const beforeWrapper = document.getElementById("beforeWrapper");
  const sliderLine = document.getElementById("sliderLine");

  let isDragging = false;
sliderLine.classList.add("nudge");
  const move = (e) => {
    if (!isDragging) return;
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const rect = slider.getBoundingClientRect();
    let x = clientX - rect.left;
    if (x < 0) x = 0;
    if (x > rect.width) x = rect.width;
    const percentage = (x / rect.width) * 100;
    beforeWrapper.style.clipPath = `inset(0 ${100 - percentage}% 0 0)`;

    sliderLine.style.left = `${percentage}%`;
  };
  slider.addEventListener("pointerdown", (e) => {
    isDragging = true;
    sliderLine.classList.remove("nudge");
    slider.setPointerCapture(e.pointerId);
    move(e);
  });
  window.addEventListener("pointermove", move);
  window.addEventListener("pointerup", () => {
    isDragging = false;
  });
});