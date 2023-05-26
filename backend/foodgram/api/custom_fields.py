import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.Field):
    """Кастомное поле для преобразования формата Base64"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            file_name = f'{uuid.uuid4().hex}.{ext}'

            decoded_image = base64.b64decode(imgstr)
            return ContentFile(decoded_image, name=file_name)
        return super().to_internal_value(data)

    def to_representation(self, value):
        if value and hasattr(value, 'url'):
            return value.url
        return value
