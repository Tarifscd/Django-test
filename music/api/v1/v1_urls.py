from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework import routers, serializers, viewsets
from music.api.v1 import viewsets
from music import views

router = DefaultRouter()
router.register('albums', viewsets.AlbumViewSet)
router.register('songs', viewsets.SongViewSet)
# router.register('keyvalues', viewsets.KeyvalueList, 'keyvalues')

# urlpatterns = router.urls
urlpatterns = [
    url(r'^', include(router.urls)),
    # url(r'^keyvalues/', viewsets.KeyvalueList.as_view()),
]