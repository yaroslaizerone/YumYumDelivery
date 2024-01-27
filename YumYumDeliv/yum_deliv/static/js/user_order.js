document.addEventListener('DOMContentLoaded', function () {
        var orderListItems = document.querySelectorAll('.order-list');
        var orderDetailsContainer = document.getElementById('order-details');
        var supportModal = document.getElementById('supportModal');
        var orderIdInput = supportModal.querySelector('#orderId');

        orderListItems.forEach(function (item) {
            item.addEventListener('click', function () {
                var orderId = item.getAttribute('data-order-id');
                orderIdInput.value = orderId;

                var orderDetailBlocks = document.querySelectorAll('[id^="od-"]');
                orderDetailBlocks.forEach(function (block) {
                    block.hidden = true;
                });

                var selectedOrderDetailBlock = document.getElementById('od-' + orderId);
                if (selectedOrderDetailBlock) {
                    selectedOrderDetailBlock.hidden = false;
                }
            });
        });

        var attachmentInput = document.getElementById('attachment');
        var attachmentPreview = document.getElementById('attachmentPreview');

        attachmentInput.addEventListener('change', function () {
            attachmentPreview.innerHTML = '';

            for (var i = 0; i < attachmentInput.files.length; i++) {
                var file = attachmentInput.files[i];

                if (file.type.startsWith('image/')) {
                    var reader = new FileReader();
                    reader.onload = function (e) {
                        var img = document.createElement('img');
                        img.src = e.target.result;
                        img.classList.add('img-thumbnail');

                        var deleteButton = document.createElement('button');
                        deleteButton.textContent = 'Удалить';
                        deleteButton.classList.add('btn', 'btn-danger', 'mt-2');
                        deleteButton.addEventListener('click', function () {
                            attachmentInput.value = '';
                            attachmentPreview.innerHTML = '';
                        });

                        var previewBlock = document.createElement('div');
                        previewBlock.appendChild(img);
                        previewBlock.appendChild(deleteButton);

                        attachmentPreview.appendChild(previewBlock);
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    });
function deleteOrder(orderID) {
    const csrftoken = getCookie('csrftoken');
    const uid = getCookie('uid')

    fetch(`/delete_order/${uid}/${orderID}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
    })
        .then(response => {
            if (response.ok) {
                var orderElement = document.getElementById(`od-${orderID}`);
                var orderModelPanel = document.getElementById(`md-${orderID}`)
                if (orderElement && orderModelPanel) {
                    orderElement.remove();
                    orderModelPanel.remove();
                } else {
                    console.error(`Element with id "od-${orderID}" not found`);
                }
            } else {
                console.error('Network response was not ok');
            }
        })
        .catch(error => {
            console.error('Error deleting address:', error);
            console.error('Error details:', error.message, error.stack);
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