from django.urls import path
from user import api

app_name = 'user'

urlpatterns = [
    path('<uuid:uuid>/', api.UserDetail.as_view(), name='user_detail')
]