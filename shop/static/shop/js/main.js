/* ===== FlowerBooM — main.js ===== */
/* Загальний JS для всіх сторінок  */

document.addEventListener('DOMContentLoaded', function () {
    // Автозакриття alert-повідомлень через 5 секунд
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            const btn = alert.querySelector('.btn-close');
            if (btn) btn.click();
        }, 5000);
    });
});
