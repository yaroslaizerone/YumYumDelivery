from yum_deliv.views import database
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from yum_deliv.views import db


def init(request):
    feed = (
        database.collection("user_feedback")
        .stream()
    )
    feedbacks = [feedback.to_dict() for feedback in feed]

    context = {
        'feedbacks': feedbacks
    }
    # в view.py посмотреть как задать параметры response, чтобы из-за url не отправлялось повторное письмо
    return render(request, 'Operator.html', context)


def sendResponse(request, feedback):
    if request.method == 'POST':
        feed = (
            database.collection("user_feedback")
            .where('id', '==', feedback)
            .stream()
        )

        for doc in feed:
            document_id = doc.id
            db.collection("user_feedback").document(document_id).delete()
        
        email = request.POST.get('email')
        response_text = request.POST.get('responseTextArea')

        send_mail(subject='Ответ поддержки YumYumDelivery',
                  message=response_text,
                  from_email='kolpackov.yarosl@gmail.com',
                  recipient_list=[email],
                  fail_silently=False)
        return redirect('operator_panel/')
