from django.conf.urls import url, include
# from rest_framework.routers import DefaultRouter

urlpatterns = [
    url(r'^v1/', include('music.api.v1.v1_urls')),
    # url(r'^v1/', include('rest_framework_docs.urls')),
]