from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.forbidden'
handler500 = 'core.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('orders.urls', namespace='orders')),
    path('api/', include('api.urls', namespace='api')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
