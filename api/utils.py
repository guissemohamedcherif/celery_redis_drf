# -*- coding: utf-8 -*-

from io import BytesIO
import io
import re
from django.http import HttpResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa
import qrcode
import base64
import requests
import random
import string
from django.utils.text import slugify
import os
from requests.structures import CaseInsensitiveDict
from backend.settings import API_URL, MEDIA_ROOT,APP_NAME
import secrets
# from icecream import ic
import json
from django.core.files import File
from datetime import date
from dotenv import load_dotenv
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext as _
from deep_translator import GoogleTranslator
load_dotenv()
N = 4
C = 7
ANONYM_PASSWORD = os.environ.get("anonym_password")
REGEX = os.environ.get("regex")
OTP_URL = API_URL


class Utils():
    def get_code():
        # return ''.join(random.SystemRandom().choice(string.ascii_uppercase
        # + string.digits) for _ in range(N))
        return (''.join(random.SystemRandom().choice(string.digits)
                        for _ in range(N)))

    def get_random():
        return (''.join(random.SystemRandom().choice(string.ascii_uppercase
                + string.digits) for _ in range(C)))

    def generate_imageqrcode(data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        message_bytes = str(data).encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        data = base64_bytes.decode('ascii')

        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        buffer = io.BytesIO()
        img.save(buffer)
        return buffer

    def send_sms(phone, message):
        payload = {}
        headers = {'Cookie': 'SERVERID=A'}
        URL = OTP_URL+phone+"&msg="+message+"&sender="+APP_NAME
        requests.request("POST", URL, headers=headers, data=payload)

    def send_code(phone, message):
        payload = {}
        headers = {'Cookie': 'SERVERID=A'}
        URL = OTP_URL+phone+"&msg="+message+"&sender="+APP_NAME
        return requests.request("POST", URL, headers=headers, data=payload)

    def my_slugigy(text):
        text = re.sub(r'[?,:!@#~`+=$%^&\\*()\[\]{}<>]', '-', text, re.UNICODE)
        return slugify(text)

    def random_string_generator(size=10, chars=string.digits):
        return ''.join(secrets.choice(chars) for _ in range(size))

    def png_to_base64(image_url):
        response = requests.get(image_url,timeout=120)
        # ic(response)
        # img = Image.open(BytesIO(response.content))
        buffer = BytesIO(response.content)
        # img.save(buffer,format='PNG')
        byte_im = buffer.getvalue()
        base64qr = base64.b64encode(byte_im)
        img_data = base64qr.decode("utf-8")
        return img_data

    def returnFile(filename, image_url):
        buffer = Utils.png_to_base64(image_url)
        path_file = os.path.join(MEDIA_ROOT, filename)
        file_64_decode = base64.b64decode(buffer) 
        file_result = open(path_file, 'wb') 
        file_result.write(file_64_decode)
        f = open(path_file, "rb")
        djangofile = File(f)
        return djangofile

    def encode(code):
        code = str(code)
        # encoding string
        code_enc = code.encode(encoding='utf8')
        # printing the encoded string
        print("The encoded string in base64 format is : ",)
        print(code_enc)
        return code_enc

    def decode(code):
        code = str(code)
        # printing the original decoded string
        code_dec = code.decode('utf8', 'strict')
        print("The decoded string is : ",)
        print(code_dec)
        return code_dec
    
    def doc_code():
        code = str(timezone.now().date()) + "-" + str(Utils.get_code())
        return code

    def calculate_age(birthdate):
        today = date.today()
        age = today.year - birthdate.year - ((today.month,today.day) < (birthdate.month,birthdate.day))
        return age

    def generate_libelle(item,prefix='CONSUL'):
        suffix = str(item.created_at.strftime("%Y%m%d"))+str(item.pk)
        code = Utils.get_random()
        ref = '{}-{}-{}'.format(prefix,code[:3].upper(), suffix)
        return ref
    
    def generate_default_libelle():
        prefix = 'RDV'
        code = Utils.get_code()
        suffix = str(timezone.now().strftime("%Y%m%d"))
        ref = '{}-{}-{}'.format(prefix,code, suffix)
        return ref

    def generate_default_filename():
        prefix = 'temp'
        code = Utils.get_code()
        suffix = str(timezone.now().strftime("%Y%m%d"))
        ref = '{}_{}_{}'.format(prefix,code, suffix)
        return ref

    def generate_default_transaction_code():
        prefix = 'TRANS'
        code = Utils.get_code()
        suffix = str(timezone.now().strftime("%Y%m%d"))
        ref = '{}-{}-{}'.format(prefix,code, suffix)
        return ref

    def generate_imageqrcode(data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        message_bytes = str(data).encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        data = base64_bytes.decode('ascii')
        
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        buffer = io.BytesIO()
        img.save(buffer)
        # filename = 'carnet-%s.png' % (self.beneficiaire.id)
        # filebuffer = InMemoryUploadedFile(buffer, None, filename, 'image/png', buffer.getbuffer().nbytes, None)
        # #self.qrcode.save(filename, filebuffer)
        # self.qrcode.save(filename, filebuffer, False)
        return buffer

    def get_matricule(size=6):
        return (''.join(random.SystemRandom().choice(string.digits) for _ in range(size)))

    def get_mondays(date):
        monday_of_this_week = date - timedelta(days=date.weekday())
        monday_of_next_week = monday_of_this_week + timedelta(days=7)
        return monday_of_this_week, monday_of_next_week

    def translate_errors(serializer_errors):
        translated_errors = {}
        for field_name, field_errors in serializer_errors.items():
            translated_field_errors = []
            for error in field_errors:
                translated_field_errors.append(_(" ".join(error.split())))
            translated_errors[field_name] = " ".join(translated_field_errors)
        return translated_errors

    def translate_errors_array(serializer_errors):
        translator = GoogleTranslator(source='en', target='fr')
        translated_errors = {}

        for field_name, field_errors in serializer_errors.items():
            translated_field_errors = [translator.translate(error) for error in field_errors]
            translated_errors[field_name] = translated_field_errors

        return translated_errors

    def get_order_code(size=6):
        return str("#")+ (''.join(random.SystemRandom().choice(string.digits) for _ in range(size)))