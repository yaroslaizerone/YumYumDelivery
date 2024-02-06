import os
import datetime

from yum_deliv.views import checkFileExists
from yum_deliv.views import storage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from yum_deliv.views import database, config, db, takeOrders,\
    randomAlphanumericString, homepageContext, uploadPhoto


def updateUserData(request, uid):
    if request.method == 'POST':
        # try:
            user_data = {
                'name': request.POST.get('name'),
                'surname': request.POST.get('surname'),
                'middle_name': request.POST.get('middle-name'),
            }

            uploaded_files = request.FILES
            photo_client = uploaded_files.get('photo_client')

            if photo_client:
                download_url = uploadPhoto(photo_client)

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
        # except Exception as e:
        #     return HttpResponse(f"An error occurred: {str(e)}")

    return HttpResponse("Invalid request method")


def userAddress(request, uid):
    id = randomAlphanumericString(10)
    entrance = request.POST.get('entrance')
    flat = request.POST.get('flat')
    floor = request.POST.get('floor')
    intercom = request.POST.get('intercom')
    streetAndNumber = request.POST.get('address-user')

    data = {
        "id": id,
        "entrance": entrance,
        "flat": flat,
        "floor": floor,
        "intercom": intercom,
        "streetAndNumber": streetAndNumber,
        "uid": uid,
    }

    database.collection("user_address").add(data)

    return redirect('/')


def deleteAddress(request, addressID):
    address_request = (
        database.collection("user_address")
        .where("id", "==", addressID)
    )

    address_docs = address_request.stream()

    for doc in address_docs:
        document_id = doc.id
        database.collection("user_address").document(document_id).delete()

    context = homepageContext(request)
    return render(request, "Homepage.html", context)


def createSupport(request, uid):
    if request.method == 'POST':
        # Получение данных из формы
        order_id = request.POST.get('orderId')
        email = request.POST.get('email')
        reason = request.POST.get('reason')
        comment = request.POST.get('comment')
        uploaded_files = request.FILES.getlist('attachment')
        datetime_feedback = datetime.datetime.now()
        id = randomAlphanumericString(10)

        # Данные для сохранения в Firestore
        data = {
            'order_id': order_id,
            'email': email,
            'reason': reason,
            'comment': comment,
            'datetime_feedback': datetime_feedback,
            'id': id,
        }

        # Проверка, если есть загруженные файлы
        if uploaded_files:
            # Папка для сохранения файлов user_feedback
            photo_urls = []

            for file in uploaded_files:
                download_url = uploadPhoto(file)
                photo_urls.append(download_url)
            else:
                # No new photo uploaded, check if preview image exists
                preview_image_id = f'feedback_{order_id}'
                if request.POST.get(preview_image_id):
                    # Use the existing photo URL
                    download_url = request.POST.get(preview_image_id)
            if download_url:
                # Добавление URL фотографий в параметр "photo" через точку с запятой
                data['photo'] = ';'.join(photo_urls)

        # Сохранение данных в Firestore
        db.collection('user_feedback').add(data)

        context = takeOrders(uid)
        return render(request, 'UserOrders.html', context)


def deleteOrder(request, uid, order_id):
    if request.method == 'DELETE':
        dish_request = (
            database.collection("orders")
            .where("id", "==", int(order_id))
        )
        docs = dish_request.stream()
        for doc in docs:
            document_id = doc.id
            db.collection("orders").document(document_id).delete()
    context = takeOrders(uid)
    return render(request, 'UserOrders.html', context)