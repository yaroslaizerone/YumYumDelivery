import logging
import os
import json
import datetime

from django.http import JsonResponse, HttpResponseServerError
from requests.exceptions import HTTPError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

logger = logging.getLogger(__name__)
config = {
    "apiKey": "AIzaSyCMk-jWD8RgFoFQSvMfDrjP25qmPwiQK0Q",
    "authDomain": "yumyumdelivery-12ebb.firebaseapp.com",
    "databaseURL": "https://console.firebase.google.com/project/yumyumdelivery-12ebb",
    "projectId": "yumyumdelivery-12ebb",
    "storageBucket": "yumyumdelivery-12ebb.appspot.com",
    "messagingSenderId": "772726972796",
    "appId": "1:772726972796:web:0eb1ae51194aee6b7204f9"
}

cred = credentials.Certificate('firebase_config.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firestore.client()
storage = firebase.storage()


def signIn(request):
    return render(request, "Login.html")


def home(request):
    try:
        uid = request.COOKIES.get('uid')
        users = (
            database.collection("client-data")
            .where("uid", "==", uid)
            .stream()
        )
        user = [us.to_dict() for us in users]
        rests = database.collection("restaurant").stream()
        type_rests = database.collection("type_rest").stream()

        types = [type_rest.to_dict() for type_rest in type_rests]
        restaurants = [res.to_dict() for res in rests]
        context = {
            "restaurants": restaurants,
            "type_rests": types,
            "user": user,
        }
        return render(request, "Homepage.html", context)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return HttpResponseServerError("Internal Server Error", content_type="text/plain")


# TODO Добавить cookie при авторизации
def postsignIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        pasw = request.POST.get('pass')
        try:
            user = authe.sign_in_with_email_and_password(email, pasw)
            uid = user['localId']

            roles = (
                database.collection("authentication")
                .where("uid", "==", uid)
                .stream()
            )
            role_data = []
            for role in roles:
                role_data.append(role.to_dict())
            user_role = role_data[0]['role']
            # TODO Переделать на if, так как case для каждого администратора не напишешь
            if user_role == '1':
                response = redirect('/')
            elif user_role == '2':
                role = (
                    database.collection("role")
                    .where("id", "==", 2)
                    .stream()
                )
                role_data = []
                for rol in role:
                    role_data.append(rol.to_dict())
                for r in role_data:
                    response = redirect('adminRest', rest_slug=r['role'])
            else:
                logger.info(user_role)
                return HttpResponse("Some default response or redirect")

            response.set_cookie('uid', uid)
            return response
        except Exception as e:
            message = f"Invalid Credentials!! Please Check your Data. Error: {str(e)}"
            return render(request, "Login.html", {"message": message})


# TODO Удалять при выходе
def logout(request):
    try:
        del request.session['uid']
    except:
        pass
    return render(request, "Login.html")


def signUp(request):
    return render(request, "Registration.html")


def postsignUp(request):
    logger.info("Registration attempt")
    email = request.POST.get('email')
    password = request.POST.get('pass')
    pass_repeat = request.POST.get('pass-repeat')

    if pass_repeat != password:
        logger.info("Пароли не совпадают")
        messages.info(request, 'Пароли не совпадают.')
        return render(request, "Registration.html")

    try:
        # Create a new user with the given email and password
        user = authe.create_user_with_email_and_password(email, password)
        uid = user['localId']
        idtoken = user['idToken']

        # Set the 'uid' in the session
        request.session['uid'] = str(idtoken)

        try:
            # Save user information to your database (consider using a transaction)
            data = {"uid": uid, "role": 1}
            database.collection("authentication").add(data)  # Use add() to auto-generate document ID
            logger.info("User saved to database successfully")
            return render(request, "Login.html", {"message": "Registration successful."})
        except Exception as db_error:
            # Log the database error
            logger.error(f"Error saving user to database: {db_error}")
            return render(request, "Registration.html", {"message": "Error saving user to database."})

    except HTTPError as auth_error:
        # Log the authentication error
        logger.error(f"Authentication error: {auth_error}")
        return render(request, "Registration.html", {"message": "Authentication error."})


def reset(request):
    return render(request, "Reset.html")


def postReset(request):
    email = request.POST.get('email')
    try:
        authe.send_password_reset_email(email)
        message = "A email to reset password is successfully sent"
        return render(request, "Login.html", {"msg": message})
    except:
        message = "Something went wrong, Please check the email you provided is registered or not"
        return render(request, "Login.html", {"msg": message})


def adminRest(request, rest_slug):
    context = rest_context(rest_slug)
    return render(request, 'RestAdmin.html', context)


# Вспомогательный метод
def rest_context(slug):
    types_dishes = (
        database.collection("type_dishes")
        .stream()
    )
    type_rests = (
        database.collection("type_rest")
        .stream()
    )
    types_data_dish = [type.to_dict() for type in types_dishes]
    type_data_rests = [type.to_dict() for type in type_rests]
    rest_current = (
        database.collection("restaurant")
        .where('url_adress', '==', slug)
        .stream()
    )
    rest = [res.to_dict() for res in rest_current]
    orders_retaraunt = (
        database.collection("orders")
        .where("restaurant", "==", rest[0]['id'])
        .stream()
    )
    orders = [order.to_dict() for order in orders_retaraunt]
    menu = (
        database.collection("dishes")
        .where("restaurant", "==", rest[0]['id'])
        .stream()
    )
    dishes = [dish.to_dict() for dish in menu]
    context = {
        "categories_dish": types_data_dish,
        "categories_rest": type_data_rests,
        "rest_slug": slug,
        "rest": rest,
        'orders': orders,
        'dishes': dishes
    }
    return context


def check_file_exists(file_path):
    try:
        # Check if the file exists in Firebase Storage
        storage.child(file_path).get_metadata()
        return True
    except Exception as e:
        # The file does not exist or an error occurred
        return False


def add_dish(request, rest_slug):
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
        .where("url_adress", "==", url_rest)
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


def place_order(request):
    context = {
        'dish_names': [],
        'dish_photo': [],
        'dish_cost': [],
        'dish_quantity': [],
    }
    logger.info("method: " + request.method)

    if request.method == "POST":
        data = json.loads(request.body)

        for item in data:
            dish_name = item["name"]
            dish_photo = item["photo"]
            dish_cost = item["cost"]
            dish_quantity = item["quantity"]
            context['dish_names'].append(dish_name)
            context['dish_photo'].append(dish_photo)
            context['dish_cost'].append(dish_cost)
            context['dish_quantity'].append(dish_quantity)

        # Вернуть JSON-ответ с URL для перенаправления и данными context
        response_data = {
            'redirect_url': '/place_order/ordered/',
            'context': context
        }
        return JsonResponse(response_data)

    # Вернуть ошибку для неверного метода
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def ordered(request):
    # TODO Вынести в один метод
    dishes, id_rest, summa = ordered_take(request)

    restaurant = (
        database.collection("restaurant")
        .where("id", "==", id_rest)
        .stream()
    )

    name_rest = [name.to_dict() for name in restaurant]

    context = {
        'dishes': dishes,
        'rest_name': name_rest,
    }
    return render(request, 'PlaceOrder.html', context)


def payOfOrder(request):
    if request.method == "POST":
        collection_reference = db.collection('orders')
        documents = collection_reference.get()
        id = len(documents) + 1

        user_cookie = request.COOKIES.get('uid')
        user = None

        if user_cookie:
            user = user_cookie
            dishes, id_rest, summa = ordered_take(request)
            house = request.POST.get('houseNumber')
            street = request.POST.get('street')
            entrance = request.POST.get('entrance')
            intercom = request.POST.get('intercom')
            floor = request.POST.get('floor')
            comment = request.POST.get('comments')
            data_time = datetime.datetime.now()

        new_order = {'id': id, 'user': user, 'dishes': dishes,
                     'restaurant': id_rest, 'order_status': "Заказ оформлен",
                     'summa': summa, 'courier': 1, "house": house,
                     "street": street, "entrance": entrance,
                     "intercom": intercom, "data_time": data_time,
                     "floor": floor, "comment": comment
                     }
        database.collection("orders").add(new_order)
        context = {
            'order': dishes,
        }

    return render(request, 'PayOfOrder.html', context)


def ordered_take(request):
    dishes = []
    summa = 0
    ordered_dishes_cookie = request.COOKIES.get('orderedDishes')
    ordered_dishes_data = None

    if ordered_dishes_cookie:
        ordered_dishes_data = json.loads(ordered_dishes_cookie)

    if ordered_dishes_data:
        for odd in ordered_dishes_data:
            dishes_firebase = (
                database.collection("dishes")
                .where("id", "==", int(odd['id']))
                .stream()
            )
            for dish in dishes_firebase:
                object_cart = dish.to_dict()
                object_cart['quantity'] = odd['quantity']
                summa = summa + int(object_cart['quantity']) * int(object_cart['cost'])
                dishes.append(object_cart)

    first_dish = dishes[0]
    id_rest = first_dish['restaurant']
    return dishes, id_rest, summa


def republuc(request, rest_slug):
    if request.method == 'POST':
        name_rest = request.POST.get('name_rest')
        type_rest = int(request.POST.get('type-rest'))
        representative = request.POST.get('representative')
        avg_time_cook = request.POST.get('avg_time_cook')
        url = request.POST.get('url_adress')
        start_time = request.POST.get('start-work')
        end_time = request.POST.get('end-work')
        adress = request.POST.get('adress_rest')

        new_data_rest = {
            'adress': adress,
            'avg_time_cook': int(avg_time_cook),
            'end_work': end_time,
            'start_work': start_time,
            'name': name_rest,
            'representative': representative,
            'type': type_rest,
            'url_adress': url
        }

        # Получение фото
        uploaded_files = request.FILES
        photo = uploaded_files.get('photo_rest')

        if photo:
            dict_path = 'rest_photo'
            file_name = os.path.join(dict_path, photo.name)
            file_path = f"{dict_path}%5C{photo.name}"

            if check_file_exists(file_path):
                new_data_rest['image'] = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_path}%2Frest_photo%5C{file_name}?alt=media"
            else:
                upload = storage.child(file_name).put(photo)
                photo_url = upload.get("downloadTokens")
                download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_path}%2Frest_photo%5C{photo.name}?alt=media&token={photo_url}"
                new_data_rest['image'] = download_url

        # Получение id ресторана
        restaurant_request = (
            database.collection("restaurant")
            .where("url_adress", "==", rest_slug)
        )
        docs = restaurant_request.stream()
        for doc in docs:
            doc_data = doc.to_dict()
            if condition(doc_data, rest_slug):
                document_id = doc.id
                database.collection("restaurant").document(document_id).update(new_data_rest)

    context = rest_context(rest_slug)
    return render(request, 'RestAdmin.html', context)


def condition(doc_data, slug):
    return 'id' in doc_data and doc_data['url_adress'] == slug


def delete_dish(request, rest, dish_id):
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


def edit_dish(request, rest, dish_id):
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


def change_status(request, rest, order_id):
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


def update_user_data(request, uid):
    if request.method == 'POST':
        try:
            user_data = {
                'name': request.POST.get('name'),
                'surname': request.POST.get('surname'),
                'middle_name': request.POST.get('middle-name'),
            }

            uploaded_files = request.FILES
            photo_client = uploaded_files.get('photo_client')

            if photo_client:
                dict_path = 'avatars'
                file_name = os.path.join(dict_path, photo_client.name)
                file_path = f"{dict_path}%5C{photo_client.name}"

                # Check if the file already exists
                if check_file_exists(file_path):
                    # Use the existing file URL instead of uploading a new one
                    download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_path}%2Favatars%5C{file_name}?alt=media"

                else:
                    # Upload the file to Firebase Storage
                    upload = storage.child(file_name).put(photo_client)
                    photo_url = upload.get("downloadTokens")
                    download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_path}%2Favatars%5C{photo_client.name}?alt=media&token={photo_url}"
            else:
                # No new photo uploaded, check if preview image exists
                preview_image_id = f'image-preview-edit_{uid}'
                if request.POST.get(preview_image_id):
                    # Use the existing photo URL
                    download_url = request.POST.get(preview_image_id)
                else:
                    # No photo uploaded and no preview image, set to None
                    download_url = None

            if download_url:
                user_data["image"] = download_url
            # Обновление данных пользователя в базе данных
            user_request = (
                database.collection("client-data")
                .where("uid", "==", uid)
            )
            user_docs = user_request.stream()
            for user_doc in user_docs:
                user_doc_id = user_doc.id
                database.collection("client-data").document(user_doc_id).update(user_data)

            return redirect('/')
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}")

    return HttpResponse("Invalid request method")


def orders(request, uid):
    orders_request = (
        database.collection("orders")
        .where("user", "==", uid)
        .stream()
    )
    orders_user = [orders.to_dict() for orders in orders_request]
    context = {
        "orders": orders_user
    }

    return render(request, 'UserOrders.html', context)