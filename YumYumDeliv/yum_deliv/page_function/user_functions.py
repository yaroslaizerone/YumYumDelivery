import os
import datetime

from yum_deliv.views import check_file_exists
from yum_deliv.views import storage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from yum_deliv.views import database, config, db, takeOrders, randomAlphanumericString, homepageContext


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
        # except Exception as e:
        #     return HttpResponse(f"An error occurred: {str(e)}")

    return HttpResponse("Invalid request method")


def userAddress(request, uid):
    id = randomAlphanumericString(10)
    entrance = request.POST.get('entrance')
    flat = request.POST.get('flat')
    floor = request.POST.get('floor')
    intercom = request.POST.get('intercom')
    streetAndNumber = request.POST.get('address')

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
            folder_path = 'user_feedback'
            photo_urls = []

            for file in uploaded_files:
                file_name = os.path.join(folder_path, file.name)
                file_path = f"{folder_path}%5C{file.name}"

                # Check if the file already exists
                if check_file_exists(file_path):
                    # Use the existing file URL instead of uploading a new one
                    download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_path}%2Fuser_feedback%5C{file_name}?alt=media"

                else:
                    # Upload the file to Firebase Storage
                    upload = storage.child(file_name).put(file)
                    photo_url = upload.get("downloadTokens")
                    download_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/{file_path}%2Fuser_feedback%5C{file.name}?alt=media&token={photo_url}"
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