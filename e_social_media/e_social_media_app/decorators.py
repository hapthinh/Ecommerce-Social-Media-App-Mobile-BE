from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from .serializers import PostReactionSerializer

authorization = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            description='Token for authentication (Nhớ thêm Bearer nha)',
            required=True
        )
    ],
    order=['Authorization', 'header']
)

