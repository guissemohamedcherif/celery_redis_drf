import os
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

'''
This regex assumes that you have a clean string,
you should clean the string for spaces and other characters
'''
message = 'This field must be number only'
code = 'Invalid field'
textvalidator = r'^[A-Za-z0-9-À-ÿ? ,_\':"-]{6,100000000}$'
alphavalidator = r'^[A-Za-z0-9-À-ÿ? ,_\':.@#-]+$'
isalphavalidator = RegexValidator(alphavalidator,
                                  message, code)
isnumbervalidator = RegexValidator(r'[\d,+]', message, code)
isalphatextvalidator = RegexValidator(textvalidator, message, code)


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Only .pdf,.jpg,' +
                              '.png,.jpeg, file is supported')


def validate_pdf_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.' +
                              'Only .pdf file is supported')


def validate_many_extensions(value):
    ext = value.name.split('.')  # [0] returns value before and after a point
    if len(ext) > 2:
        raise ValidationError('Unsupported file. Two many extensions detected')


pwdmessage = ("Le mot de passe doit avoir au moins au minimum 8 caractères," +
              "1 caractère en majuscule, 1 caractère en minuscule," +
              "1 nombre et 1 caractère spéciale")
ispasswordvalidator = RegexValidator(r'[A-Za-z0-9@#$%^&+=]{8,}',
                                     message=pwdmessage, code='Invalid name')
