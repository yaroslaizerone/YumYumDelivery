let orderedDishes = [];
let cartItems = [];
window.onload = function () {
    loadCart();
};

var restURL = localStorage.getItem('url_rest');

function addToCart(dishName, dishPhoto, dishID, dishCost, dishWeight) {
    const existingItemIndexCart = cartItems.findIndex(item => item.id === dishID);
    const existingItemIndexOD = orderedDishes.findIndex(item => item.id === dishID);

    if (existingItemIndexCart !== -1 && existingItemIndexOD !== -1) {
        cartItems[existingItemIndexCart].quantity += 1;
        orderedDishes[existingItemIndexOD].quantity += 1;
    } else {
        const dish = {
            'id': dishID,
            'name': dishName,
            'photo': dishPhoto,
            'cost': dishCost,
            'quantity': 1,
            'weight': dishWeight
        };
        const orderedDish = {'id': dishID, 'quantity': 1};

        cartItems.push(dish);
        orderedDishes.push(orderedDish);
    }

    updateCart();
    updateTotalCost();
    saveCart();
}

function increaseQuantity(dishID) {
    const existingItemIndexCart = cartItems.findIndex(item => item.id === dishID);
    const existingItemIndexOD = orderedDishes.findIndex(item => item.id === dishID);

    if (existingItemIndexCart !== -1 && existingItemIndexOD !== -1) {
        cartItems[existingItemIndexCart].quantity += 1;
        orderedDishes[existingItemIndexOD].quantity += 1;

        updateCart();
        updateTotalCost();
        saveCart();
    }
}

function decreaseQuantity(dishID) {
    const existingItemIndexCart = cartItems.findIndex(item => item.id === dishID);
    const existingItemIndexOD = orderedDishes.findIndex(item => item.id === dishID);

    if (existingItemIndexCart !== -1 && existingItemIndexOD !== -1) {
        if (cartItems[existingItemIndexCart].quantity > 1) {
            cartItems[existingItemIndexCart].quantity -= 1;
            orderedDishes[existingItemIndexOD].quantity -= 1;
        } else {
            // Remove the item if quantity is 0
            cartItems.splice(existingItemIndexCart, 1);
            orderedDishes.splice(existingItemIndexOD, 1);
        }

        updateCart();
        updateTotalCost();
        saveCart();
    }
}

function updateCart() {
    const cartList = document.getElementById('cart-list');
    cartList.innerHTML = '';

    cartItems.forEach(item => {
        const li = document.createElement('li');
        li.className = 'cart-item';

        const totalCostForItem = item.cost * item.quantity;

        li.innerHTML = `
            <img src="${item.photo}" alt="${item.name}">
            <div class="cart-item-details">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${totalCostForItem} ₽</div>
                <div class="cart-item-weight">${item.weight} г</div>
            </div>
            <div class="cart-item-counter">
                <button type="button" onclick="decreaseQuantity('${item.id}')">-</button>
                <input type="text" class="dish-quantity" value="${item.quantity}" readonly>
                <button type="button" onclick="increaseQuantity('${item.id}')">+</button>
            </div>
        `;
        cartList.appendChild(li);
    });

    // После обновления корзины вызываем функцию для обновления общей стоимости
    updateTotalCost();
}


function updateTotalCost() {
    const totalCost = cartItems.reduce((acc, item) => acc + item.cost * item.quantity, 0);

    const placeOrderButton = document.getElementById('btn_place');
    placeOrderButton.textContent = `Оформить заказ (${totalCost}₽)`;
    document.getElementById('cart-btn').innerText = totalCost + ' ₽';
}

function clearCart() {
    cartItems = [];
    orderedDishes = [];
    updateCart();
    updateTotalCost();
    saveCart();
}

function saveCart() {
    const uidCookie = getCookie('uid');
    if (!uidCookie) {
        // Если пользователь не авторизован, сохраняем в localStorage
        localStorage.setItem(`cart-${restURL}`, JSON.stringify(cartItems));
        localStorage.setItem(`orderedDishes-${restURL}`, JSON.stringify(orderedDishes));
    } else {
        const orderName = `orderDisher-${restURL}-${uidCookie}`;
        const cartName = `cart-${restURL}-${uidCookie}`;
        document.cookie = `${cartName}=${JSON.stringify(cartItems)}; path=/`;
        document.cookie = `${orderName}=${JSON.stringify(orderedDishes)}; path=/`;
    }
}

function loadCart() {
    const uidCookie = getCookie('uid');
    const orderedDishesName = `orderDisher-${restURL}-${uidCookie}`;
    const cartName = `cart-${restURL}-${uidCookie}`;

    if (!uidCookie) {
        // Если пользователь не авторизован, загружаем из localStorage
        const orderedDishesLocalStorage = localStorage.getItem(`orderedDishes-${restURL}`);
        orderedDishes = orderedDishesLocalStorage ? JSON.parse(orderedDishesLocalStorage) : [];
        // Загружаем данные из localStorage для корзины (это может быть аналогично для куки)
        const cartLocalStorage = localStorage.getItem(`cart-${restURL}`);
        cartItems = cartLocalStorage ? JSON.parse(cartLocalStorage) : [];
    } else {
        // Если пользователь авторизован, загружаем из куки
        const orderedDishesCookie = getCookie(orderedDishesName);
        orderedDishes = orderedDishesCookie ? JSON.parse(decodeURIComponent(orderedDishesCookie)) : [];
        const cartCookie = getCookie(cartName);
        cartItems = cartCookie ? JSON.parse(decodeURIComponent(cartCookie)) : [];
    }
    console.log(orderedDishes);
    console.log(cartItems);
    updateCart();
    updateTotalCost();
}

function getCookie(cookieName) {
    const name = cookieName + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    return null;
}

document.addEventListener('click', function (event) {
        if (event.target.tagName === 'A') {
            var targetId = event.target.getAttribute('href').substring(1);

            var targetElement = document.getElementById(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth' // Добавляет плавный скроллинг
                });
            }
        }
    });
// TODO Сделать Корзину для каждого ресторана