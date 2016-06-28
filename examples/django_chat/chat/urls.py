from django.conf.urls import (
    url, patterns, include
)

import sdjango

from .views import socket_base


urlpatterns = [
    url(r'^socket\.io', include(sdjango.urls)),
    url(r'^$', socket_base, name='socket_base'),
]
