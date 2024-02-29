from django.urls import path, include
from django.conf import settings

urlpatterns = []

## If you are using the extended_accounts app
urlpatterns += [
    path(
        "extended_accounts/",
        include("extended_accounts.urls", namespace="extended_accounts"),
    )
]
## Use this setting to correctly visualize your images in development django templates.
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
