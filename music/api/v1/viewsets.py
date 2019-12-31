import os
from django.http import Http404
from rest_framework import permissions
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
import datetime
from rest_framework import permissions
from music.models import Album, Song
from music.serializers import AlbumSerializer, SongSerializer
from datetime import datetime, timedelta
# from apscheduler.schedulers.background import BackgroundScheduler

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated]