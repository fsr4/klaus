from django.urls import path

from .views import MajorView, ClassView, download

app_name = 'downloader'
urlpatterns = [
    path('<slug:slug>/', MajorView.as_view(), name='major'),
    path('<slug:major_slug>/<class_slug>/', ClassView.as_view(), name='class'),
    path('<slug:major_slug>/<class_slug>/download/', download, name='download')
]
