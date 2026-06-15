/* ════════════════════════════════════════════════════════════════════════
   Landing — interacción del slider antes/después
   ════════════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.reveal').forEach(function (reveal) {
    const range = reveal.querySelector('.reveal__range');
    const before = reveal.querySelector('.reveal__before');
    const handle = reveal.querySelector('.reveal__handle');

    if (!range || !before || !handle) return;

    function actualizar(valor) {
      before.style.clipPath = 'inset(0 ' + (100 - valor) + '% 0 0)';
      handle.style.left = valor + '%';
    }

    actualizar(range.value);
    range.addEventListener('input', function (e) {
      actualizar(e.target.value);
    });
  });
});
