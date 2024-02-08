let orderedDishes = [];
let cartItems = [];
window.onload = function () {
    loadCart();
};
let uidCookie = getCookie('uid');
let restURL = localStorage.getItem('url_rest');
let orderedDishesName = `orderDishes-${restURL}-${uidCookie}`;
let cartName = `cart-${restURL}-${uidCookie}`;
let orderedDishesNameLS = `orderedDishes-${restURL}`;
let cartNameLS = `cart-${restURL}`;

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
            'weight': dishWeight,
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
    const cartList = document.getElementById('cart_list_rest');
    cartList.innerHTML = '';

    cartItems.forEach(item => {
        const li = document.createElement('li');
        li.className = 'cart-item-rest';

        const totalCostForItem = item.cost * item.quantity;

        li.innerHTML = `
            <img src="${item.photo}" alt="${item.name}">
            <div class="cart-item-rest-content">
                <div class="cart-item-rest-details">
                    <div class="cart-item-rest-name">${item.name}</div>
                    <div class="cart-item-rest-price">${totalCostForItem} ₽</div>
                    <div class="cart-item-rest-weight">${item.weight} г</div>
                </div>
                <div class="cart-item-rest-counter">
                    <button type="button" onclick="decreaseQuantity('${item.id}')">-</button>
                    <input type="text" class="dish-quantity" value="${item.quantity}" readonly>
                    <button type="button" onclick="increaseQuantity('${item.id}')">+</button>
                </div>
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
}

function clearCart() {
    cartItems = [];
    orderedDishes = [];

    updateCart();
    updateTotalCost();
    saveCart();
}

function saveCart() {
    if (!uidCookie) {
        if (Array.isArray(cartItems) && cartItems.length > 0) {
            document.cookie = `${cartNameLS}=${JSON.stringify(cartItems)}; path=/`;
            document.cookie = `${orderedDishesNameLS}=${JSON.stringify(orderedDishes)}; path=/`;
        } else {
            // Если cartItems пуст или не является массивом
            document.cookie = `${cartNameLS}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
            document.cookie = `${orderedDishesNameLS}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }
    } else {
        // Если пользователь авторизован, сохраняем в cookie
        if (Array.isArray(cartItems) && cartItems.length > 0) {
            document.cookie = `${cartName}=${JSON.stringify(cartItems)}; path=/`;
            document.cookie = `${orderedDishesName}=${JSON.stringify(orderedDishes)}; path=/`;
        } else {
            // Если cartItems пуст или не является массивом
            document.cookie = `${cartName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
            document.cookie = `${orderedDishesName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }
    }
}

function loadCart() {
    if (!uidCookie) {
        // Если пользователь не авторизирован, загружаем данные из localStorage
        const orderedDishesLocalStorage = getCookie(orderedDishesNameLS);
        orderedDishes = orderedDishesLocalStorage ? JSON.parse(orderedDishesLocalStorage) : [];
        const cartLocalStorage = getCookie(cartNameLS);
        cartItems = cartLocalStorage ? JSON.parse(cartLocalStorage) : [];
    } else {
        if (!isCookieEmpty(orderedDishesNameLS) || !isCookieEmpty(cartNameLS)) {
            const userDecision = confirm('Хотите перенести выбранные блюда на корзину вашего аккаунта?');
            if (userDecision) {
                const orderedDishesLocalStorage = getCookie(`orderedDishes-${restURL}`);
                const cartLocalStorage = getCookie(`cart-${restURL}`);

                const orderedDishesFromLocalStorage = orderedDishesLocalStorage ? JSON.parse(orderedDishesLocalStorage) : [];
                const cartItemsFromLocalStorage = cartLocalStorage ? JSON.parse(cartLocalStorage) : [];
                // Если пользователь решит перенести элементы из локального хранилища в файлы cookies, при этом cookies пустые
                if (isCookieEmpty(orderedDishesName) || isCookieEmpty(cartName)) {
                    document.cookie = `${cartName}=${JSON.stringify(cartItemsFromLocalStorage)}; path=/`;
                    document.cookie = `${orderedDishesName}=${JSON.stringify(orderedDishesFromLocalStorage)}; path=/`;

                    document.cookie = `orderedDishes-${restURL}` + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                    document.cookie = `cart-${restURL}` + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';

                } else {
                    // Если пользователь решит перенести элементы из локального хранилища в файлы cookies, при этом cookies Не пустые
                    const orderedDishesCookie = getCookie(orderedDishesName);
                    const cartCookie = getCookie(cartName);

                    let mergedCart, mergedOrderedDishes;
                    mergedCart = mergeItems(JSON.parse(cartLocalStorage), JSON.parse(cartCookie));
                    mergedOrderedDishes = mergeItems(JSON.parse(orderedDishesLocalStorage), JSON.parse(orderedDishesCookie))

                    document.cookie = `${cartName}=${JSON.stringify(mergedCart)}; path=/`;
                    document.cookie = `${orderedDishesName}=${JSON.stringify(mergedOrderedDishes)}; path=/`;

                    document.cookie = `orderedDishes-${restURL}` + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                    document.cookie = `cart-${restURL}` + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                }
            }
        }
        const orderedDishesCookie = getCookie(orderedDishesName);
        orderedDishes = orderedDishesCookie ? JSON.parse(decodeURIComponent(orderedDishesCookie)) : [];
        const cartCookie = getCookie(cartName);
        cartItems = cartCookie ? JSON.parse(decodeURIComponent(cartCookie)) : [];
    }
    console.log(cartItems);
    updateCart();
    updateTotalCost();
}

function mergeItems(LocalStorage, Cookie) {

// Создаем Map для уникальных элементов, где ключ - id
    const uniqueItemsMapCart = new Map();

// Добавляем элементы из cart1 с приоритетом
    LocalStorage.forEach(item => {
        const key = item.id;
        if (!uniqueItemsMapCart.has(key)) {
            uniqueItemsMapCart.set(key, item);
        }
    });

// Добавляем элементы из cart2 с приоритетом, перезаписывая, если элемент уже есть
    Cookie.forEach(item => {
        const key = item.id;
        uniqueItemsMapCart.set(key, item);
    });

// Преобразуем Map обратно в массив
    const mergedArray = Array.from(uniqueItemsMapCart.values());

    return mergedArray;
}

function isCookieEmpty(cookieName) {
    const cookieValue = getCookie(cookieName);
    return !cookieValue || cookieValue.trim() === '';
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

function placeByOrder(restURL) {
    var uidCookie = getCookie('uid');
    if (!uidCookie) {
        alert('Для оформления заказа необходимо авторизоваться!');
        location.href = '/logout';
        return;
    } else {
        var cartRest = getCookie(cartName);
        if (cartRest == null) {
            alert('Для оформления заказа необходимо выбрать хотя бы один товар.');
            return;
        } else{
            window.location.href = restURL;
        }
    }
}

$(document).ready(function () {
    $('.col.cart-container').hide();
});