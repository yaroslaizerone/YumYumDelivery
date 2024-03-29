import logging
import json
import datetime
import os
import random
import string
import firebase_admin
import pyrebase

from django.http import JsonResponse
from requests.exceptions import HTTPError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import credentials, firestore

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


def homepageContext(request):
    rests = database.collection("restaurant").stream()
    type_rests = database.collection("type_rest").stream()

    types = [type_rest.to_dict() for type_rest in type_rests]
    restaurants = [res.to_dict() for res in rests]
    context = {
        "restaurants": restaurants,
        "type_rests": types,
    }
    uid = request.COOKIES.get('uid')
    if uid is None:
        context['user'] = None
        return context
    users = (
        database.collection("client-data")
        .where("uid", "==", uid)
        .stream()
    )
    users_data = [us.to_dict() for us in users]
    if users_data:
        context['user'] = users_data
    address = database.collection("user_address").stream()
    adrs = [ad.to_dict() for ad in address]
    context['address'] = adrs

    for rest in restaurants:
        cart = []
        cost_cart = 0
        ordered_dishes_key = f'orderDishes-"{rest["url_address"]}"-{uid}'
        ordered_dishes = request.COOKIES.get(ordered_dishes_key)

        if ordered_dishes:
            ordered_dishes_data = json.loads(ordered_dishes)

            for order in ordered_dishes_data:
                dish_id = int(order["id"])

                dish = (
                    database.collection("dishes")
                    .where("id", "==", dish_id)
                    .limit(1)
                    .stream()
                )
                select_dish = [dish.to_dict() for dish in dish]

                if select_dish:
                    dish_data = select_dish[0]
                    dish_data['quantity'] = order['quantity']
                    cart.append(dish_data)
                    cost_cart += order['quantity'] * float(dish_data["cost"])
            context[f'cart-{rest["url_address"]}'] = cart
            context[f'cost_cart-{rest["url_address"]}'] = cost_cart
    return context


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
            if user_role == '1':
                response = redirect('/')
                response.set_cookie('uid', uid)
            elif user_role == '2' or user_role == '5' or user_role == '6':
                    role = (
                        database.collection("role")
                        .where("id", "==", int(user_role))
                        .stream()
                    )
                    role_data = []
                    for rol in role:
                        role_data.append(rol.to_dict())
                    for r in role_data:
                       return redirect('adminRest', rest_slug=r['role'])
            elif user_role == '3':
                return redirect('/operator_panel/')
            elif user_role == '4':
                return redirect(f'/couriers_panel/{uid}')
            else:
                logger.info(user_role)
                return HttpResponse("Some default response or redirect")

                response.set_cookie('uid', uid)
            return response
        except Exception as e:
            message = f"Invalid Credentials!! Please Check your Data. Error: {str(e)}"
            return render(request, "Login.html", {"message": message})


# TODO Удалять при выходе
def logOut(request):
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
    context = restContext(rest_slug)
    return render(request, 'RestAdmin.html', context)


def restContext(slug):
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
        .where('url_address', '==', slug)
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
        .where("restaurant", "==", int(rest[0]['id']))
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


def checkFileExists(file_path):
    try:
        # Check if the file exists in Firebase Storage
        storage.child(file_path).get_metadata()
        return True
    except Exception as e:
        # The file does not exist or an error occurred
        return False


def placeOrder(request):
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


def ordered(request, url_rest):
    restaurant = (
        database.collection("restaurant")
        .where("url_address", "==", url_rest)
        .stream()
    )

    rest = [restauran.to_dict() for restauran in restaurant]

    context = {
        'restaurant': rest,
    }
    return render(request, 'PlaceOrder.html', context)


def payOfOrder(request, url_rest):
    if request.method == "POST":
        collection_reference = db.collection('orders')
        documents = collection_reference.get()
        id = len(documents) + 1

        user_cookie = request.COOKIES.get('uid')
        user = None

        rest_current = (
            database.collection("restaurant")
            .where('url_address', '==', url_rest)
            .stream()
        )
        rest = [res.to_dict() for res in rest_current]

        if user_cookie:
            user = user_cookie
            dishes, id_rest, summa = orderedTake(request, url_rest)
            flat = request.POST.get('flatNumber')
            street = request.POST.get('street')
            entrance = request.POST.get('entrance')
            intercom = request.POST.get('intercom')
            floor = request.POST.get('floor')
            comment = request.POST.get('comments')
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            data_time = formatted_datetime

        new_order = {'id': id, 'user': user, 'dishes': dishes,
                     'restaurant': id_rest, 'order_status': "Заказ оформлен",
                     'summa': summa, 'courier': 1, "flat": flat,
                     "street": street, "entrance": entrance,
                     "intercom": intercom, "data_time": data_time,
                     "floor": floor, "comment": comment
                     }
        context = {
            'restaurant': rest,
            'order': new_order,
        }

        return render(request, 'PayOfOrder.html', context)


def publicOrder(request):
    if request.method == 'POST':
        order_data = request.POST.get('orderData')
        decoded_data = str(order_data).replace('&#x27;', "'")
        order_dict = eval(decoded_data)

        db.collection("orders").add(order_dict)

        return redirect("/")


def orderedTake(request, url_rest):
    dishes = []
    summa = 0
    uid = request.COOKIES.get('uid')
    cookie_key = f'cart-"{url_rest}"-{uid}'
    ordered_dishes_cookie = request.COOKIES.get(cookie_key)
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


def condition(doc_data, slug):
    return 'id' in doc_data and doc_data['url_address'] == slug


def orders(request, uid):
    context = takeOrders(uid)
    return render(request, 'UserOrders.html', context)


def takeOrders(uid):
    orders_request = (
        database.collection("orders")
        .where("user", "==", uid)
        .stream()
    )
    orders_user = [orders.to_dict() for orders in orders_request]
    context = {
        "orders": orders_user,
        "uid": uid,
    }
    return context


def randomAlphanumericString(length):
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )


def uploadPhoto(photo):
        upload = storage.child(photo.name).put(photo)
        photo_url = upload.get("downloadTokens")
        download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{photo.name}?alt=media&token={photo_url}"
        return download_url
