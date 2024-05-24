from celery import shared_task
from backend.settings import APP_NAME
from django.conf import settings
from django.utils import timezone
from api.notifications import Notif as notify
from api.models import *

@shared_task
def mail_sender(user):
    user = User.objects.get(id=user['id'])
    content = f"Congratulations! Your account has just been created on {APP_NAME} ! 🎉🎉"
    subject = f"Welcome 🎉 on  {APP_NAME}"
    to = user.email
    template_src = 'mail_notification.html'
    name = f"{user.first_name} {user.last_name}" 
    context = {
        "user_type": user.user_type,
        "email": to,
        "name": name,
        "settings": settings,
        "id": "false",
        "content": content,
        "year": timezone.now().year
        }
    notify.send_email(subject, to, template_src, context)
    return "DONE !"


@shared_task
def admin_mail_sender():
    admins = User.objects.filter(user_type=SUPERADMIN)
    content = "Hello admins"
    subject = "Admin Mailer"
    for admin in admins:
        to = admin.email
        template_src = 'mail_notification.html'
        context = {
            "user_type": admin.user_type,
            "email": to,
            "settings": settings,
            "id": "false",
            "content": content,
            "year": timezone.now().year
            }
        notify.send_email(subject, to, template_src, context)
    return "DONE !"