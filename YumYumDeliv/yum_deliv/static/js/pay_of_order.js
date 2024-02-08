document.querySelector('.card-number-input').oninput = () => {
    document.querySelector('.card-number-box').innerText = document.querySelector('.card-number-input').value;
}

document.querySelector('.card-holder-input').oninput = () => {
    document.querySelector('.card-holder-name').innerText = document.querySelector('.card-holder-input').value;
}

document.querySelector('.month-input').oninput = () => {
    document.querySelector('.exp-month').innerText = document.querySelector('.month-input').value;
}

document.querySelector('.year-input').oninput = () => {
    document.querySelector('.exp-year').innerText = document.querySelector('.year-input').value;
}

document.querySelector('.cvv-input').onmouseenter = () => {
    document.querySelector('.front').style.transform = 'perspective(1000px) rotateY(-180deg)';
    document.querySelector('.back').style.transform = 'perspective(1000px) rotateY(0deg)';
}

document.querySelector('.cvv-input').onmouseleave = () => {
    document.querySelector('.front').style.transform = 'perspective(1000px) rotateY(0deg)';
    document.querySelector('.back').style.transform = 'perspective(1000px) rotateY(180deg)';
}

document.querySelector('.cvv-input').oninput = () => {
    document.querySelector('.cvv-box').innerText = document.querySelector('.cvv-input').value;
}
function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
}

function getCookieByPartialName(partialName) {
    const cookies = document.cookie.split('; ');

    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        if (cookie.includes(partialName)) {
            const [name, value] = cookie.split('=');
            return getCookie(name);
        }
    }

    return null;
}

document.addEventListener('DOMContentLoaded', function () {
    var cardHolderInput = document.querySelector('.card-holder-input');
    cardHolderInput.addEventListener('input', function () {
        var inputValue = this.value;
        var englishPattern = /^[A-Za-z\s]*$/; // Регулярное выражение для проверки только английских символов
        if (!englishPattern.test(inputValue)) {
            this.value = inputValue.replace(/[^A-Za-z\s]/g, ''); // Удаление всех символов, кроме английских букв и пробелов
        }
    });
});

$('.card-number-input').on('input', function () {
    // Удаляем все нечисловые символы и пробелы
    var cardNumber = $(this).val().replace(/\D/g, '');

    // Форматируем номер карты, добавляя пробелы после каждых четырех цифр
    var formattedCardNumber = '';
    for (var i = 0; i < cardNumber.length; i++) {
        if (i > 0 && i % 4 === 0) {
            formattedCardNumber += ' ';
        }
        formattedCardNumber += cardNumber.charAt(i);
    }

    // Устанавливаем отформатированный номер карты обратно в поле ввода
    $(this).val(formattedCardNumber);

    // Проверяем длину номера карты после удаления нечисловых символов и пробелов
    // Если длина больше 16 символов, обрезаем номер до 16 символов
    if (cardNumber.length > 16) {
        cardNumber = cardNumber.slice(0, 16);
    }

    // Проверка контрольной суммы по алгоритму Луна
    var sum = 0;
    var shouldDouble = false;
    for (var i = cardNumber.length - 1; i >= 0; i--) {
        var digit = parseInt(cardNumber.charAt(i));

        if (shouldDouble) {
            if ((digit *= 2) > 9) digit -= 9;
        }

        sum += digit;
        shouldDouble = !shouldDouble;
    }
    var valid = (sum % 10) === 0;

    // Устанавливаем стиль для указания валидности/невалидности номера карты
    $(this).css('border', valid ? '2px solid green' : '2px solid red');
});
