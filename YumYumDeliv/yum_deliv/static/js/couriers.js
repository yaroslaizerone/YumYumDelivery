function getOrder(orderID, uid) {
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