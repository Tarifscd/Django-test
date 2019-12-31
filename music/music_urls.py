from django.conf.urls import url, include
from . import views

app_name = 'music'
urlpatterns = [
    # url(r'^$', views.index, name='index'),
    # url(r'^(?P<album_id>[0-9]+)$', views.detail, name='detail'),
    url(r'^api/', include('music.api.api_urls')),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)$', views.DetailView.as_view(), name='detail'),
    # url(r'album/add/$', views.AlbumCreate.as_view(), name='album-add'),
    # url(r'album/(?P<pk>[0-9]+)/$', views.AlbumUpdate.as_view(), name='album-update'),
    # url(r'album/(?P<pk>[0-9]+)/delete/$', views.AlbumDelete.as_view(), name='album-delete'),
]
# From base.html
# <a href="{% url 'music:album-add' %}">
# <span class="glyphicon glyphicon-plus" aria-hidden="true"></span>&nbsp; Add Album
# </a>

# From index.html
# <form action="{% url 'music:album-delete' album.id %}" method="post" style="display: inline;">
#     {% csrf_token %}
#     <input type="hidden" name="album_id" value="{{ alnum.id }}"/>
#     <button type="submit" class="btn btn-default btn-sm">
#         <span class="icon-trash">Delete</span>
#     </button>
# </form>
