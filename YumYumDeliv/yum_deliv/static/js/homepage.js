$(document).ready(function () {
    const newAddressInput = document.querySelector('.address-input');

    $('#add-address').click(function () {
                    const dialog = $("#address-dialog");
                    dialog.show();
                    $('#map-dialog').show();

                    if (!dialog.dialog('instance')) {
                        dialog.dialog({
                            autoOpen: false,
                            width: 'auto',
                            modal: true
                        });
                    }
                    dialog.dialog('open');
                });

                $('#close-address-dialog').click(function () {
                    $("#address-dialog").dialog('close');
                });

                function init() {
                        myMap = new ymaps.Map("map", {
                            center: [55.04, 82.91],
                            zoom: 14
                        });

                        locationDot = createMarker(myMap.getCenter(), true);
                        locationDot.events.add('dragend', function (event) {
                            reverseGeocode();
                        });

                    }

                function createMarker(coordinates, draggable) {
                    if (!coordinates || coordinates.length < 2) {
                        console.error('Invalid coordinates:', coordinates);
                        return;
                    }

                    var geometry = {
                        type: 'Point',
                        coordinates: coordinates
                    };

                    var marker = new ymaps.Placemark(geometry.coordinates, {}, {
                        draggable: draggable
                    });
                    myMap.geoObjects.add(marker);

                    myMap.setCenter(geometry.coordinates);

                    return marker;
                }


                function reverseGeocode() {
                    var coordinates = locationDot.geometry.getCoordinates();

                    if (!Array.isArray(coordinates) || coordinates.length < 2) {
                        console.error('Invalid coordinates:', coordinates);
                        return;
                    }

                    fetch('https://api.opencagedata.com/geocode/v1/json?q=' + coordinates[0] + ',' + coordinates[1] + '&key=67c24bfd1b1b4786a3e7a0538ca9b1b5&pretty=1')
                        .then(response => response.json())
                        .then(data => {
                            if (data.results && data.results.length > 0) {
                                var components = data.results[0].components;

                                // Получаем название улицы и номер дома
                                var street = components.road || '';
                                var houseNumber = components.house_number || '';
                                // Обновляем адрес в блоке
                                newAddressInput.value = street + ', ' + houseNumber;
                            } else {
                                // Если нет информации о адресе, очищаем блок
                                console.error('Не удалось получить адрес по координатам.');
                            }
                        })
                        .catch(error => {
                            console.error('Ошибка при выполнении запроса к геокодеру:', error);
                        });
                }
                ymaps.ready(init);
            });
        document.addEventListener('DOMContentLoaded', function () {
            $('#address-dialog').hide();
            $('#map-dialog').hide();
            $('#user-data-dialog').hide();
            const restaurantItems = document.querySelectorAll('.restaurant-item');
            const typeLinks = document.querySelectorAll('.div a');
            const searchInput = document.querySelector('.text-field__input');
            const searchButton = document.querySelector('.btn.btn-primary');
            const restaurantBlock = document.querySelector('.restaurant-block');
            const noResultsMessage = document.createElement('h2');
            noResultsMessage.textContent = 'Ресторан не найден';
            noResultsMessage.style.display = 'none';
            restaurantBlock.appendChild(noResultsMessage);
            const h1Label = document.createElement('span');
            const h1 = document.querySelector('#main-title');
            h1.appendChild(h1Label);

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

            const uid = getCookie('uid');
            $("#user_add_address").attr("action", "/user_add_address/" + uid);
            if (uid) {
                const userDataForm = document.getElementById('user-data-form');
                if (userDataForm) {
                    userDataForm.action = `/update_user_data/${uid}`;
                }
            }


            typeLinks.forEach(link => {
                link.addEventListener('click', function (event) {
                    event.preventDefault();
                    const selectedType = this.dataset.type.toLowerCase();
                    const searchQuery = searchInput.value.trim().toLowerCase();

                    typeLinks.forEach(typeLink => {
                        const typeLinkType = typeLink.dataset.type.toLowerCase();
                        if (selectedType === '0' || typeLinkType === selectedType) {
                            typeLink.classList.add('selected-type');
                        } else {
                            typeLink.classList.remove('selected-type');
                        }
                    });

                    restaurantItems.forEach(item => {
                        const restaurantName = item.querySelector('h2').textContent.trim().toLowerCase();
                        const itemType = item.dataset.type.toLowerCase();

                        if ((itemType === '0' || itemType === selectedType) &&
                            (restaurantName.includes(searchQuery) || itemType === searchQuery)) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    });

                    updateNoResultsMessage();
                    updateH1Label(selectedType);
                });
            });

            searchButton.addEventListener('click', function (event) {
                event.preventDefault();
                const searchQuery = searchInput.value.trim().toLowerCase();
                const selectedType = document.querySelector('.div a.selected-type').dataset.type.toLowerCase();

                restaurantItems.forEach(item => {
                    const restaurantName = item.querySelector('h2').textContent.trim().toLowerCase();
                    const itemType = item.dataset.type.toLowerCase();

                    if ((itemType === '0' || itemType === selectedType) &&
                        (restaurantName.includes(searchQuery) || itemType === searchQuery)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });

                updateNoResultsMessage();
            });

            function updateNoResultsMessage() {
                const visibleItems = Array.from(restaurantItems).filter(item => item.style.display !== 'none');
                if (visibleItems.length === 0) {
                    noResultsMessage.style.display = 'block';
                } else {
                    noResultsMessage.style.display = 'none';
                }
            }

            function updateH1Label(selectedType) {
                if (selectedType === '0') {
                    h1Label.textContent = '';
                } else {
                    let selectedLinkText = '';
                    for (const link of typeLinks) {
                        if (link.dataset.type.toLowerCase() === selectedType) {
                            selectedLinkText = link.textContent.trim();
                            break;
                        }
                    }
                    h1Label.textContent = ` - ${selectedLinkText}`;
                }
            }

        });
        $("#my-address-btn").on("click", function() {
            // Создаем диалоговое окно с заданным текстом
            $("#dialog-all-address").dialog({
              title: "Сохранённые адреса",
              modal: true,
              close: function() {
                $(this).dialog("close");
              }
            })
          });
        var avatarElement = $('#avatar, #avatar-custom, #avatar-anonim');

         $("#logout-btn").on("click", function() {
            // Очищаем cookie с идентификатором пользователя
            document.cookie = "uid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

            // Перезагружаем страницу
            location.reload();
        });

        avatarElement.click(function () {
            var menu = $(this).next('.menu'); // Используйте .next(), чтобы найти следующий элемент с классом 'menu'
            if (menu.is(':visible')) {
                menu.hide();
            } else {
                menu.show();
            }
        });

        $(document).click(function (event) {
            if (!avatarElement.is(event.target) && !avatarElement.next('.menu').is(event.target)) {
                avatarElement.next('.menu').hide();
            }
        });

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

        document.addEventListener('click', function (event) {
            if (event.target !== document.getElementById('savedAddressesBtn') && event.target !== document.getElementById('menu-address')) {
                hideMenu('menu-address');
            }
        });
        document.getElementById('savedAddressesBtn').addEventListener('click', function () {
                    toggleMenuDisplay('menu-address');
                });
        function toggleMenuDisplay(menuId) {
            var menu = document.getElementById(menuId);
            if (menu.style.display === 'block') {
                hideMenu(menuId);
            } else {
                showMenu(menuId);
            }
        }

        function showMenu(menuId) {
            var menu = document.getElementById(menuId);
            if (menu) {
                menu.style.display = 'block';
            }
        }

        function hideMenu(menuId) {
            var menu = document.getElementById(menuId);
            if (menu) {
                menu.style.display = 'none';
            }
        }
        document.getElementById('typedataSuggestions').addEventListener('input', function(event) {
            const inputValue = event.target.value;
            const commaIndex = inputValue.indexOf(',');

            if (commaIndex === -1) {
                const streetName = inputValue.split(' ')[0];
                if (streetName) {
                    const restOfAddress = inputValue.substring(streetName.length).trim();
                    event.target.value = `${streetName}, ${restOfAddress}`;
                }
            }
        });

        function handleImageUpload() {
                    const inputPhotoEdit = document.getElementById(`photo_client`);
                    const imagePreviewEdit = document.getElementById(`image-preview`);
                    const imagePreviewContainerEdit = document.getElementById(`image-preview-container`);

                    const file = inputPhotoEdit.files[0];

                    if (file) {
                        const reader = new FileReader();

                        reader.onload = function (e) {
                            imagePreviewEdit.src = e.target.result;
                            imagePreviewEdit.style.display = 'block';
                            imagePreviewContainerEdit.style.display = 'block';
                        };

                        reader.readAsDataURL(file);
                    }
                };

        document.getElementById('my-data-btn').addEventListener('click', function() {
                    const dialog = $("#user-data-dialog");
                    dialog.show();

                    if (!dialog.dialog('instance')) {
                        dialog.dialog({
                            autoOpen: false,
                            width: 'auto',
                            modal: true
                        });
                    }
                    dialog.dialog('open');
        });

        document.getElementById('close-data-dialog').addEventListener('click', function() {
            const dialog = $("#user-data-dialog");
            dialog.dialog('close');
        });


        function formatAddress(address) {
                const firstCommaIndex = address.indexOf(',');
                if (firstCommaIndex !== -1) {
                    const secondCommaIndex = address.indexOf(',', firstCommaIndex + 1);
                    if (secondCommaIndex !== -1) {
                        return address.substring(0, secondCommaIndex).trim();
                    }
                }
                return address.trim();
            }

            document.getElementById('menu-address').addEventListener('click', function (event) {
                const target = event.target;
                if (target.tagName === 'LABEL' && !target.classList.contains('add-address')) {
                    const selectedAddress = target.textContent;
                    document.getElementById('savedAddressesBtn').textContent = selectedAddress;
                }
            });
            document.addEventListener('DOMContentLoaded', function () {
                // Выбранный адрес из cookie
                var selectedAddress = getCookie("selectedAddress");

                // При загрузке страницы установить выбранный адрес
                if (selectedAddress) {
                    // Проверка наличия выбранного адреса в списке
                    var addressInList = document.querySelectorAll('.dropdown-item[data-type="user-address"]');
                    var addressInListArray = Array.from(addressInList).map(function (item) {
                        return item.innerText;
                    });

                    if (!addressInListArray.includes(selectedAddress)) {
                        // Удаление адреса из cookie, так как его нет в списке
                        setCookie("selectedAddress", "", -1); // Устанавливаем срок действия cookie в прошлое
                    } else {
                        // Установить адрес в кнопку
                        document.getElementById("savedAddressesBtn").innerText = selectedAddress;
                    }
                }

                // Обработчик события для выбора адреса
                function selectAddress(address) {
                    // Сохранить выбранный адрес в cookie
                    setCookie("selectedAddress", address, 30); // 30 days expiration (adjust as needed)

                    // Изменить текст кнопки
                    document.getElementById("savedAddressesBtn").innerText = address;
                }
                // Функция для установки cookie
                function setCookie(name, value, days) {
                    var expires = "";
                    if (days) {
                        var date = new Date();
                        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                        expires = "; expires=" + date.toUTCString();
                    }
                    document.cookie = name + "=" + value + expires + "; path=/";
                }

                // Обработчик события для выбора адреса
                document.addEventListener('click', function (event) {
                    var target = event.target;
                    if (target.getAttribute('data-type') === 'user-address') {
                        var address = target.innerText;
                        selectAddress(address);
                    }
                });

                // Обработчик события для кнопки удаления адреса
                document.addEventListener('click', function (event) {
                    var target = event.target;
                    if (target.classList.contains('delete-address-btn')) {
                        var addressId = target.getAttribute('data-address-id');
                        var address = target.getAttribute('data-address');
                        deleteAddress(addressId, address);
                    }
                });
            });

            function deleteAddress(addressId, address) {
                const csrftoken = getCookie('csrftoken');

                fetch(`/delete_address/${addressId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json'
                    },
                })
                    .then(response => {
                        if (response.ok) {
                            const deletedItem = document.querySelector(`[data-address-id="${addressId}"]`);
                            if (deletedItem) {
                                deletedItem.remove();
                            }

                            // Проверка, соответствует ли текущий текст кнопки удаленному адресу
                            const savedAddressBtn = document.getElementById("savedAddressesBtn");
                            if (savedAddressBtn.innerText === address) {
                                // Заменить текст на другой, например, текст по умолчанию
                                savedAddressBtn.innerText = "Укажите адрес";
                                document.cookie = 'selectedAddress' + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                            }

                            // Закрытие диалога
                            const dialog = $("#dialog-all-address");
                            dialog.dialog('close');
                            window.location.replace('/');
                        } else {
                            console.error('Network response was not ok');
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting address:', error);

                        // Печать дополнительной информации об ошибке
                        console.error('Error details:', error.message, error.stack);
                    });
            }
           function toggleCartDisplay() {
                var cartElement = document.getElementById('cart');
                if (cartElement.style.display === 'block') {
                    hideCart();
                } else {
                    showCart();
                }
            }

            function showCart() {
                var cartElement = document.getElementById('cart');
                if (cartElement) {
                    cartElement.style.display = 'block';
                }
            }

            function hideCart() {
                var cartElement = document.getElementById('cart');
                if (cartElement) {
                    cartElement.style.display = 'none';
                }
            }

            document.getElementById('cart-btn').addEventListener('click', function () {
                toggleCartDisplay();
            });
            function removeItem(dishId) {
                // Remove the item from the cart displayed on the page
                var itemElement = document.querySelector('.cart p[data-dish-id="' + dishId + '"]');
                if (itemElement) {
                    itemElement.remove();
                }

                // Remove the item from the cart data in memory
                var updatedCart = [];
                for (var i = 0; i < cart.length; i++) {
                    if (cart[i][0].id !== dishId) {
                        updatedCart.push(cart[i]);
                    }
                }
                cart = updatedCart;

                // Update the orderedDishes cookie
                updateOrderedDishesCookie(dishId);

                // Update the total cost
                updateTotalCost();
            }

            function updateOrderedDishesCookie(dishId) {
                var orderedDishes = getCookieMassiv('orderedDishes');

                orderedDishes = orderedDishes.filter(function (dish) {
                    return dish.id !== dishId;
                });

                document.cookie = 'orderedDishes=' + JSON.stringify(orderedDishes) + '; path=/';
            }

            function getCookieMassiv(name) {
                var cookies = document.cookie.split(';');

                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();

                    if (cookie.startsWith(name + '=')) {
                        var cookieValue = decodeURIComponent(cookie.substring(name.length + 1));

                        try {
                            return JSON.parse(cookieValue);
                        } catch (error) {
                            console.error('Error parsing JSON from cookie:', error);
                            return null;
                        }
                    }
                }

                return null;
            }

            function updateTotalCost() {
                // Update the total cost displayed on the page
                var totalCostElement = document.querySelector('.cart p[data-total-cost]');
                if (totalCostElement) {
                    var totalCost = calculateTotalCost();
                    totalCostElement.innerHTML = 'Total Cost: ' + totalCost;
                }
            }

            function calculateTotalCost() {
                // Calculate the total cost based on the updated cart data
                var totalCost = 0;
                for (var i = 0; i < cart.length; i++) {
                    totalCost += cart[i][0].quantity * parseFloat(cart[i][0].cost);
                }
                return totalCost;
            }