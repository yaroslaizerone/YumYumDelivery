document.addEventListener('DOMContentLoaded', function () {
    updateTotalCost();
    var selectedAddress = getCookie("selectedAddress");
    var streetInput = document.getElementById("street");
    if (selectedAddress && streetInput) {
        streetInput.value = selectedAddress;
    }
    var selectedAddressDetails = getCookie("selectedAddress-details");

    var detailsObject = selectedAddressDetails ? JSON.parse(selectedAddressDetails) : {};

    // Устанавливаем значения в соответствующие поля формы
    setValueIfExists("flatNumber", detailsObject.flat);
    setValueIfExists("entrance", detailsObject.entrance);
    setValueIfExists("intercom", detailsObject.intercom);
    setValueIfExists("floor", detailsObject.floor);
});

function setValueIfExists(fieldId, value) {
    var field = document.getElementById(fieldId);
    if (field && value !== undefined) {
        field.value = value;
    }
}

function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
}

function submitOrder() {
    var deliveryAddress = document.getElementById("street").value;
    var orderItems = document.getElementById("orderItems").innerHTML;
    console.log("Адрес доставки:", deliveryAddress);
    console.log("Список заказанных блюд:", orderItems);
}

function removeDish(dishId, dishCost) {
    // Удаление разметки
    var dishElement = document.getElementById('dish_' + dishId);
    if (dishElement) {
        dishElement.parentNode.removeChild(dishElement);

        // Обновление данных в cookie
        var orderedDishes = getOrderedDishesFromCookie();
        var updatedDishes = orderedDishes.filter(function (dish) {
            return dish.id !== dishId;
        });

        setOrderedDishesToCookie(updatedDishes);

        // Обновление общей суммы
        updateTotalCost();
    }
}

function updateTotalCost() {
    var dishesList = document.querySelectorAll('#orderItems li[data-cost][data-quantity]');

    var totalCost = 0;
    var detalCost = 0;

    dishesList.forEach(function (dish) {
        var cost = parseFloat(dish.getAttribute('data-cost'));
        var quantity = parseFloat(dish.getAttribute('data-quantity'));
        var subtotal = cost * quantity;
        totalCost += subtotal;
        detalCost += totalCost + 20;
    });

    var totalCostValueElement = document.getElementById('totalCostValue');
    totalCostValueElement.textContent = 'Итого: ' + totalCost + ' ₽';
    var WithDeliveryValueElement = document.getElementById('totalCostWithDeliveryValue');
    WithDeliveryValueElement.textContent = 'Общая сумма: ' + detalCost + ' ₽';
}

function getOrderedDishesFromCookie() {
    var cookieValue = document.cookie.replace(/(?:(?:^|.*;\s*)orderedDishes\s*=\s*([^;]*).*$)|^.*$/, "$1");
    return cookieValue ? JSON.parse(cookieValue) : [];
}

function setOrderedDishesToCookie(orderedDishes) {
    document.cookie = "orderedDishes=" + JSON.stringify(orderedDishes) + "; path=/";
}

function goBack() {
    window.history.back();
}