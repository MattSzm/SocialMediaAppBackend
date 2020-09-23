#from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title='TwitterClone API',
        default_version='v1',
        description='API created by Mateusz Szmal',
        contact=openapi.Contact(url='https://github.com/MattSzm/SocialMediaAppBackend'),
        license=openapi.License(name='BSD License'),
    ),
    public=True
)

urlpatterns = [
    path('api/user/', include('user.urls', namespace='user')),
    path('api/tweet/', include('tweet.urls', namespace='tweet')),
    path('api/auth/', include('auth.urls', namespace='auth')),
    path('api/activity/', include('activity.urls', namespace='activity')),
    path('apischema/', schema_view.with_ui(
                'redoc', cache_timeout=0), name='api_schema'),
    # path('admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
