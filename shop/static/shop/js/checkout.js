/* ===== FlowerBooM — checkout.js ===== */
/* Логіка сторінки оформлення замовлення: доставка, оплата, PayPal */

/* SUBTOTAL і DELIVERY_COSTS передаються через data-атрибути на тезі <body> або div,
   або через глобальну змінну CHECKOUT_DATA, яка задається в шаблоні */
const SUBTOTAL       = parseFloat(window.CHECKOUT_DATA && window.CHECKOUT_DATA.subtotal || 0);
const DELIVERY_COSTS = (window.CHECKOUT_DATA && window.CHECKOUT_DATA.deliveryCosts) || {
    pickup:      0,
    nova_poshta: 60,
    ukrposhta:   40,
    meest:       55,
};

// ── Підсвічування обраного варіанту доставки/оплати ──────────────────────
function updateActiveCards(radioName, prefix) {
    document.querySelectorAll('input[name="' + radioName + '"]').forEach(function (radio) {
        const card = document.getElementById(prefix + radio.value);
        if (card) card.classList.toggle('active', radio.checked);
    });
}

// ── Оновлення вартості доставки в підсумку ───────────────────────────────
function updateDeliveryCost() {
    const selected = document.querySelector('input[name="delivery_method"]:checked');
    const method   = selected ? selected.value : 'pickup';
    const cost     = DELIVERY_COSTS[method] || 0;
    const total    = SUBTOTAL + cost;

    const costDisplay  = document.getElementById('delivery-cost-display');
    const totalDisplay = document.getElementById('total-display');
    if (costDisplay)  costDisplay.textContent  = cost === 0 ? 'Безкоштовно' : cost + ' грн';
    if (totalDisplay) totalDisplay.textContent = total.toFixed(0) + ' грн';

    // показуємо/приховуємо поля міста
    const addrBlock = document.getElementById('delivery-address-block');
    if (addrBlock) addrBlock.style.display = (method === 'pickup') ? 'none' : 'block';

    const cityField = document.getElementById('city_field');
    if (cityField) cityField.required = (method !== 'pickup');
}

// ── Показуємо/приховуємо PayPal кнопку оплати ────────────────────────────
function togglePaymentBlocks() {
    const selected = document.querySelector('input[name="payment_method"]:checked');
    const method   = selected ? selected.value : 'cash';
    const block = document.getElementById('paypal-payment-block');
    if (block) block.style.display = method === 'paypal' ? 'block' : 'none';
}

// ── Слухачі ──────────────────────────────────────────────────────────────
document.querySelectorAll('input[name="delivery_method"]').forEach(function (r) {
    r.addEventListener('change', function () {
        updateDeliveryCost();
        updateActiveCards('delivery_method', 'card-');
    });
});

document.querySelectorAll('input[name="payment_method"]').forEach(function (r) {
    r.addEventListener('change', function () {
        togglePaymentBlocks();
        updateActiveCards('payment_method', 'pay-card-');
    });
});

// ── PayPal ─────────────────────────────────────────────────────────────────
function initPayPal() {
    if (!window.paypal) return;

    // Кнопка автозаповнення форми даними PayPal-акаунту
    paypal.Buttons({
        style: { layout: 'horizontal', color: 'blue', shape: 'rect', label: 'paypal', height: 38 },
        createOrder: function (data, actions) {
            return actions.order.create({
                purchase_units: [{ amount: { value: '0.01', currency_code: 'USD' } }]
            });
        },
        onApprove: function (data, actions) {
            return actions.order.capture().then(function (details) {
                const payer = details.payer;
                if (payer.name) {
                    const fn = document.getElementById('first_name');
                    const ln = document.getElementById('last_name');
                    if (fn) fn.value = payer.name.given_name || '';
                    if (ln) ln.value = payer.name.surname    || '';
                }
                if (payer.email_address) {
                    const ef = document.getElementById('email_field');
                    if (ef) ef.value = payer.email_address;
                }
                const pid = document.getElementById('paypal_order_id');
                if (pid) pid.value = data.orderID;

                const paypalRadio = document.querySelector('input[value="paypal"]');
                if (paypalRadio) { paypalRadio.checked = true; }
                togglePaymentBlocks();
                updateActiveCards('payment_method', 'pay-card-');
                alert('✅ PayPal дані підтверджено! Ім\'я та email заповнені автоматично. Натисніть «Підтвердити замовлення».');
            });
        },
        onError: function (err) { console.error('PayPal error:', err); }
    }).render('#paypal-autofill-btn');

    // Кнопка реальної оплати
    paypal.Buttons({
        style: { layout: 'vertical', color: 'gold', shape: 'rect', label: 'pay', height: 45 },
        createOrder: function (data, actions) {
            const r       = document.querySelector('input[name="delivery_method"]:checked');
            const dCost   = DELIVERY_COSTS[r ? r.value : 'pickup'] || 0;
            const totalUSD = ((SUBTOTAL + dCost) / 41).toFixed(2);
            return actions.order.create({
                purchase_units: [{ amount: { value: totalUSD, currency_code: 'USD' }, description: 'FlowerBooM замовлення' }]
            });
        },
        onApprove: function (data, actions) {
            return actions.order.capture().then(function (details) {
                const payer = details.payer;
                if (payer.name) {
                    const fn = document.getElementById('first_name');
                    const ln = document.getElementById('last_name');
                    if (fn) fn.value = payer.name.given_name || '';
                    if (ln) ln.value = payer.name.surname    || '';
                }
                if (payer.email_address) {
                    const ef = document.getElementById('email_field');
                    if (ef) ef.value = payer.email_address;
                }
                const pid = document.getElementById('paypal_order_id');
                if (pid) pid.value = data.orderID;
                const form = document.getElementById('checkout-form');
                if (form) form.submit();
            });
        },
        onError: function (err) { console.error('PayPal payment error:', err); }
    }).render('#paypal-payment-btn');
}

// ── Ініціалізація після завантаження PayPal SDK ───────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    updateDeliveryCost();
    togglePaymentBlocks();
    updateActiveCards('delivery_method', 'card-');
    updateActiveCards('payment_method', 'pay-card-');
    // PayPal SDK завантажується асинхронно, тому чекаємо трохи
    if (window.paypal) {
        initPayPal();
    } else {
        window.addEventListener('load', initPayPal);
    }
});
