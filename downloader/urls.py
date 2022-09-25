from django.urls import path

from .views import MajorView, ClassView, FailView, download_class, index_redirect, download_file, AllMajorsView

login_url = '/oidc/authenticate?next=/&fail=/fail'

app_name = 'downloader'
urlpatterns = [
    path('', index_redirect, name='index'),
    path('fail/', FailView.as_view(), name='fail'),
    path('all/', AllMajorsView.as_view(), name='all'),
    path('<slug:slug>/', MajorView.as_view(), name='major'),
    path('<slug:major_slug>/<class_slug>/', ClassView.as_view(), name='class'),
    path('<slug:major_slug>/<class_slug>/<file_name>/download/', download_file, name='download_file'),
    path('<slug:major_slug>/<class_slug>/download/', download_class, name='download_class'),
]
