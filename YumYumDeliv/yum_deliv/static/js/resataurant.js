let orderedDishes = [];
let cartItems = [];
window.onload = function () {
    loadCart();
};

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

        // Вычисляем общую стоимость для текущего продукта
        const totalCostForItem = item.cost * item.quantity;

        li.innerHTML = `
            <img src="${item.photo}" alt="${item.name}">
            <div class="cart-item-details">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${totalCostForItem} ₽</div> <!-- Обновлено отображение цены -->
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

    const orderedDishesJSON = JSON.stringify(orderedDishes);
    const expirationDate = new Date();
    expirationDate.setDate(expirationDate.getDate() + 3);
    document.cookie = `orderedDishes=${orderedDishesJSON}; expires=${expirationDate.toUTCString()}; path=/`;
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
    localStorage.setItem('cart', JSON.stringify(cartItems));
    localStorage.setItem('orderedDishes', JSON.stringify(orderedDishes));
}

function loadCart() {
    const savedCart = localStorage.getItem('cart');
    const savedOD = localStorage.getItem('orderedDishes');

    if (savedCart) {
        cartItems = JSON.parse(savedCart);
        orderedDishes = JSON.parse(savedOD);
        updateCart();
        updateTotalCost();
    }
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
