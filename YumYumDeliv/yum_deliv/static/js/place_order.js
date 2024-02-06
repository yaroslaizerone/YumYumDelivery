document.addEventListener('DOMContentLoaded', function () {
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