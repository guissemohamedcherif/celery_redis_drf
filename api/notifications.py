# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.html import strip_tags
from mimetypes import MimeTypes
from backend.settings import EMAIL_HOST_PASSWORD, EMAIL_HOST_USER,APP_NAME

connection = get_connection(
    username=EMAIL_HOST_USER,
    password=EMAIL_HOST_PASSWORD,
    fail_silently=False,
)
FROM_EMAIL = APP_NAME+' <'+EMAIL_HOST_USER+'>'


class Notif():

    def send_email(subject, to, template_src, context_dict={}, file=None):
        if file:
            mime = MimeTypes()
            file_type = mime.guess_type(file.url)
            # render with dynamic value
            html_content = render_to_string(template_src, context_dict)
            # Strip the html tag. So people can see the pure text at least.
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL,
                                         [to], connection=connection)
            msg.attach(file.name, file.read(), file_type[0])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            # render with dynamic value
            html_content = render_to_string(template_src, context_dict)
            # Strip the html tag. So people can see the pure text at least.
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, FROM_EMAIL,
                                         [to], connection=connection)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
