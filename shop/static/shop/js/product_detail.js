/* ===== FlowerBooM — product_detail.js ===== */
/* Інтерактивний вибір зірок у формі рейтингу */

document.addEventListener('DOMContentLoaded', function () {
    const labels = document.querySelectorAll('.star-label');
    const inputs = document.querySelectorAll('input[name="rating"]');

    if (!labels.length) return;  // сторінка без форми рейтингу

    function highlight(upTo) {
        labels.forEach(function (lbl, idx) {
            lbl.style.color = idx <= upTo ? '#f5a623' : '#ccc';
        });
    }

    inputs.forEach(function (inp, idx) {
        inp.addEventListener('change', function () { highlight(idx); });
    });

    labels.forEach(function (lbl, idx) {
        lbl.addEventListener('mouseover', function () { highlight(idx); });
        lbl.addEventListener('mouseout', function () {
            const checked = Array.from(inputs).findIndex(function (i) { return i.checked; });
            highlight(checked >= 0 ? checked : -1);
        });
    });
});
