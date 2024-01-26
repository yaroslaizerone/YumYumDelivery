import os

from yum_deliv.views import database, db, condition, rest_context, storage, check_file_exists
from django.shortcuts import render, redirect

from yum_deliv.views import config


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

        # Check if the file with the same name already exists in Firebase Storage
        if photo:
            dict_path = 'dishes_photo'
            file_name = os.path.join(dict_path, photo.name)
            file_url = dict_path + '%5C' + photo.name

            if check_file_exists(file_url):
                # Use the existing file URL instead of uploading a new one
                download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_url}?alt=media"
            else:
                # Upload the file to Firebase Storage
                upload = storage.child(file_name).put(photo)
                photo_url = upload.get("downloadTokens")
                download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_url}?alt=media&token={photo_url}"

            data = {"id": id, "name": name, "description": description,
                    "dish_type": dish_type, "weight": weight,
                    "cost": cost, "calories": calories,
                    "proteins": proteins, "carbohydrates": carbohydrates,
                    "fats": fats, "restaurant": restaurant[0], "photo": download_url}

            database.collection("dishes").add(data)

    context = rest_context(rest_slug)
    render(request, 'RestAdmin.html', context)
    return redirect('adminRest', rest_slug=rest_slug)


def restaurant(request, url_rest):
    rest_id = (
        database.collection("restaurant")
        .where("url_address", "==", url_rest)
        .stream()
    )
    restaurant_id = [rest.to_dict()['id'] for rest in rest_id]
    menu = (
        database.collection("dishes")
        .where("restaurant", "==", restaurant_id[0])
        .stream()
    )
    cart = request.session.get('cart', [])
    dishes = [dish.to_dict() for dish in menu]
    context = {
        "url_rest": url_rest,
        "dishes": dishes,
        "cart": cart
    }
    return render(request, 'Resataurant.html', context)


def republuc(request, rest_slug):
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
            dict_path = 'rest_photo'
            file_name = os.path.join(dict_path, photo.name)
            file_path = f"{dict_path}%5C{photo.name}"

            if check_file_exists(file_path):
                new_data_rest[
                    'image'] = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_path}%2Frest_photo%5C{file_name}?alt=media"
            else:
                upload = storage.child(file_name).put(photo)
                photo_url = upload.get("downloadTokens")
                download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_path}%2Frest_photo%5C{photo.name}?alt=media&token={photo_url}"
                new_data_rest['image'] = download_url

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

    context = rest_context(rest_slug)
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
            dict_path = 'dishes_photo'
            file_name = os.path.join(dict_path, photo.name)
            file_url = dict_path + '%5C' + photo.name

            # Check if the file already exists
            if check_file_exists(file_url):
                # Use the existing file URL instead of uploading a new one
                download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_url}?alt=media"
            else:
                # Upload the file to Firebase Storage
                upload = storage.child(file_name).put(photo)
                photo_url = upload.get("downloadTokens")
                download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_url}?alt=media&token={photo_url}"
        else:
            # No new photo uploaded, check if preview image exists
            preview_image_id = f'image-preview-edit_{dish_id}'
            if request.POST.get(preview_image_id):
                # Use the existing photo URL
                download_url = request.POST.get(preview_image_id)
            else:
                # No photo uploaded and no preview image, set to None
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