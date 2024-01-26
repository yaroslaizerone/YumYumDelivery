function submitOrder() {
            // Получение данных из формы
            var deliveryAddress = document.getElementById("street").value;
            var orderItems = document.getElementById("orderItems").innerHTML;

            // Ваши логика и взаимодействие с платежной системой могут быть добавлены здесь

            // Просто для примера выводим информацию в консоль
            console.log("Адрес доставки:", deliveryAddress);
            console.log("Список заказанных блюд:", orderItems);

            // Здесь может быть логика отправки данных на сервер или обработки заказа
        }