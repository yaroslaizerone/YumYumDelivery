import os

from yum_deliv.views import database, db, condition, restContext, storage, checkFileExists, config, homepageContext
from django.shortcuts import render, redirect

from yum_deliv.views import uploadPhoto


def addDish(request, rest_slug):
    if request.method == 'POST':
        collection_reference = db.collection('dishes')
        documents = collection_reference.get()
        id = len(documents) + 1
        name = request.POST.get('name')
        description = request.POST.get('description')
        dish_type = int(request.POST.get('type-food'))
        weight = request.POST.get('weight')
        cost = request.POST.get('cost')
        calories = request.POST.get('calories')
        proteins = request.POST.get('proteins')
        carbohydrates = request.POST.get('carbohydrates')
        fats = request.POST.get('fats')

        # Получение id ресторана
        restaurant_request = (
            database.collection("role")
            .where("role", "==", rest_slug)
            .stream()
        )
        restaurant = [rest.to_dict()['id_rest'] for rest in restaurant_request]

        # Получение фото
        uploaded_files = request.FILES
        photo = uploaded_files.get('photo_dish')

        data = {"id": id, "name": name, "description": description,
                "dish_type": dish_type, "weight": weight,
                "cost": cost, "calories": calories,
                "proteins": proteins, "carbohydrates": carbohydrates,
                "fats": fats, "restaurant": restaurant[0]}

        if photo:
            data['image'] = uploadPhoto(photo)

        database.collection("dishes").add(data)

    context = restContext(rest_slug)
    render(request, 'RestAdmin.html', context)
    return redirect('adminRest', rest_slug=rest_slug)


def restaurant(request, url_rest):
    # Получать типы блюд, которые есть в ресторане.
    rest_id = (
        database.collection("restaurant")
        .where("url_address", "==", url_rest)
        .stream()
    )
    restaurant = [rest.to_dict() for rest in rest_id]
    menu = (
        database.collection("dishes")
        .where("restaurant", "==", restaurant[0]['id'])
        .stream()
    )
    cart = request.session.get('cart', [])
    dishes = [dish.to_dict() for dish in menu]
    type_dish = []
    for dish in dishes:
        if dish['dish_type'] in type_dish:
            continue
        else:
            type_dish.append(dish['dish_type'])
    list_type_dishes = []
    for type in type_dish:
        type_dish_db = (
            database.collection("type_dishes")
            .where("id", "==", type)
            .stream()
        )
        list_type = [type_d.to_dict() for type_d in type_dish_db]
        list_type_dishes.append({"name": list_type[0]['type'], "id": list_type[0]['id']})

    user_context = homepageContext(request)
    context = {
        "type_dishes": list_type_dishes,
        "restaurant": restaurant,
        "url_rest": url_rest,
        "dishes": dishes,
        "cart": cart
    }
    context.update(user_context)
    return render(request, 'Resataurant.html', context)


def republic(request, rest_slug):
    if request.method == 'POST':
        name_rest = request.POST.get('name_rest')
        type_rest = int(request.POST.get('type-rest'))
        representative = request.POST.get('representative')
        avg_time_cook = request.POST.get('avg_time_cook')
        url = request.POST.get('url_address')
        start_time = request.POST.get('start-work')
        end_time = request.POST.get('end-work')
        address = request.POST.get('address_rest')

        new_data_rest = {
            'address': address,
            'avg_time_cook': int(avg_time_cook),
            'end_work': end_time,
            'start_work': start_time,
            'name': name_rest,
            'representative': representative,
            'type': type_rest,
            'url_address': url
        }

        # Получение фото
        uploaded_files = request.FILES
        photo = uploaded_files.get('photo_rest')

        if photo:
            new_data_rest['image'] = uploadPhoto(photo)

        # Получение id ресторана
        restaurant_request = (
            database.collection("restaurant")
            .where("url_address", "==", rest_slug)
        )
        docs = restaurant_request.stream()
        for doc in docs:
            doc_data = doc.to_dict()
            if condition(doc_data, rest_slug):
                document_id = doc.id
                database.collection("restaurant").document(document_id).update(new_data_rest)

    context = restContext(rest_slug)
    return render(request, 'RestAdmin.html', context)


def deleteDish(request, rest, dish_id):
    if request.method == 'POST':
        dish_request = (
            database.collection("dishes")
            .where("id", "==", int(dish_id))
        )
        docs = dish_request.stream()
        for doc in docs:
            document_id = doc.id
            db.collection("dishes").document(document_id).delete()
        return redirect('adminRest', rest_slug=rest)


def editDish(request, rest, dish_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        dish_type = int(request.POST.get('type-food'))
        weight = request.POST.get('weight')
        cost = request.POST.get('cost')
        calories = request.POST.get('calories')
        proteins = request.POST.get('proteins')
        carbohydrates = request.POST.get('carbohydrates')
        fats = request.POST.get('fats')

        # Get file data (photo)
        uploaded_files = request.FILES
        photo = uploaded_files.get('photo_dish')

        # Check if a photo has been uploaded
        if photo:
            download_url = uploadPhoto(photo)
        else:
            download_url = None

        data = {
            "name": name,
            "description": description,
            "dish_type": dish_type,
            "weight": weight,
            "cost": cost,
            "calories": calories,
            "proteins": proteins,
            "carbohydrates": carbohydrates,
            "fats": fats
        }

        # Include photo in data if download_url is not None
        if download_url:
            data["photo"] = download_url

        # Update the dish data
        dish_request = (
            database.collection("dishes")
            .where("id", "==", int(dish_id))
        )
        docs = dish_request.stream()
        for doc in docs:
            document_id = doc.id
            database.collection("dishes").document(document_id).update(data)

        return redirect('adminRest', rest_slug=rest)


def changeStatus(request, rest, order_id):
    if request.method == "POST":
        status_value = request.POST.get('status')
        data = {
            'order_status': status_value
        }
        # Update the dish data
        dish_request = (
            database.collection("orders")
            .where("id", "==", int(order_id))
        )
        docs = dish_request.stream()
        for doc in docs:
            document_id = doc.id
            database.collection("orders").document(document_id).update(data)

        return redirect('adminRest', rest_slug=rest)
