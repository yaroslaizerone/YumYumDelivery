from yum_deliv.views import database
from django.shortcuts import render


def init(request):
    feed = (
        database.collection("user_feedback")
        .stream()
    )
    feedbacks = [feedback.to_dict() for feedback in feed]

    context = {
        'feedbacks': feedbacks
    }

    return render(request, 'Operator.html', context)