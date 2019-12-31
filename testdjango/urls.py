# from django.urls import path, include
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
# from django.conf.urls.static import static


urlpatterns = [
    # url(r'', ''),
    url(r'^admin/', admin.site.urls),
    url(r'^music/', include('music.music_urls')),

]


