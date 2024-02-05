// Получение публичного ключа Stripe
const stripe = Stripe('pk_test_51OfyQwCnR33iv6iiVbuStuYuEeYvF2G9cJOuikYvu2hYUAf31ncveX3bRwWUUBBavqxquArlGHHomSY9sZtyCxHQ00d8FswAWJ');

// Создание элемента Card для ввода данных карты
const elements = stripe.elements();
const cardElement = elements.create('card');

// Монтируем элемент карты на странице
cardElement.mount('#card-element');

// Обработка события отправки формы
const form = document.getElementById('payment-form');
form.addEventListener('submit', async (event) => {
    event.preventDefault();

    // Получаем дополнительные данные из формы
    const cardHolderName = document.getElementById('card_holder_name').value;

    // Отправляем запрос на создание токена карты
    const { token, error } = await stripe.createToken(cardElement, { name: cardHolderName });

    // Обрабатываем результат создания токена
    if (error) {
        // Ошибка при создании токена
        console.error(error);
    } else {
        // Успешно создан токен
        console.log('Token:', token);
        // Отправляем токен на сервер для обработки платежа
        processPaymentOnServer(token);
    }
});

// Функция для отправки токена на сервер
function processPaymentOnServer(token) {
    // Ваш код для отправки токена на сервер Django
    // Можете использовать AJAX-запрос или другие методы
}
