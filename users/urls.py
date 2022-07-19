from django.urls import path, include

urlpatterns = [
    path('register/', include('dj_rest_auth.registration.urls')),
    path('', include('dj_rest_auth.urls')),
]