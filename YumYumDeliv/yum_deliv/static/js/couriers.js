function getOrder(orderID, uid) {
    var statusButton = document.getElementById('status_' + orderID);
    if (statusButton) {
        statusButton.removeAttribute('disabled');
        document.getElementById("order-list").style.display = "none";
        let getOrderBtn = document.getElementById("get_order-dtn_" + orderID);
        getOrderBtn.style.display = "none";
    }

    const csrftoken = getCookie('csrftoken');

    fetch(`/get_order/${uid}/${orderID}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
    })
        .then(response => {
            if (response.ok) {
                return response.json();  // Parse the JSON response
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(data => {
            console.log(data);  // Handle the data from the server
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}


window.onload = function () {
    let url = window.location.href;

    let parts = url.split('/');
    let courierId = parts[parts.length - 1];

    var orderList = document.getElementById('order-list');
    var orders = orderList.querySelectorAll('.order-summary');

    orders.forEach(function (order) {
        var courierElement = order.querySelector('#courier');
        var courierUID = courierElement.innerText.trim();
        var orderStatus = order.querySelector('#status');
        var orderStat = orderStatus.innerText.trim();
        console.log(orderStat);
        // Если статус заказа отличен от "Выполнен", показываем подробности заказа и скрываем список заказов
        if (orderStat !== "Выполнен" && courierUID == courierId) {
            var orderId = order.getAttribute('onclick').match(/\d+/)[0]; // Получаем ID заказа из атрибута onclick
            showOrderDetails(orderId);
            orderList.style.display = 'none';

            // Скрываем кнопку "Взять заказ" для данного заказа
            var button = document.getElementById('get_order-dtn_' + orderId);
            if (button) {
                button.style.display = 'none';
            }
        }
    });
};

function markOrderAsCompleted(orderId) {
    var csrftoken = getCookie('csrftoken');
    // Отправляем AJAX-запрос на сервер
    $.ajax({
        headers: {
            "X-CSRFToken": csrftoken
        },
        url: '/mark_order_completed/', // Укажите адрес вашего предполагаемого URL-маршрута в Django
        method: 'POST',
        data: {
            'order_id': orderId // Передаем id заказа на сервер
        },
        success: function (response) {
            location.reload();
            console.log('Заказ успешно отмечен как выполненный');
        },
        error: function (xhr, status, error) {
            // Обработка ошибки, если необходимо
            console.error('Ошибка при отправке запроса:', error);
        }
    });
}

// Добавляем обработчик события клика на кнопку "Заказ выполнен"
$(document).ready(function () {
    $('button[id^="status_"]').on('click', function () {
        // Получаем id заказа из атрибута id кнопки
        var orderId = $(this).attr('id').split('_')[1];

        // Вызываем функцию для отправки AJAX-запроса с id заказа на сервер Django
        markOrderAsCompleted(orderId);
    });
});