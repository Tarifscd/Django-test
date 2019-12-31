"""conf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



urlpatterns = [
    url(r'^lged/', include('lged.urls', 'lged')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^', include('lged.urls')),
    # url(r'^accounts/',include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)
    urlpatterns = urlpatterns + static(settings.NODE_MODULES_URL, document_root=settings.NODE_MODULES_ROOT, show_indexes=True)

    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

