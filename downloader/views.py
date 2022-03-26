import io
import os.path
import zipfile

from django.http import HttpRequest, FileResponse
from django.views.generic import DetailView, TemplateView
from oauth2_provider.views.mixins import ProtectedResourceMixin

from filecollection.models import Major, class_slug_to_name, class_name_prettify, storage


class MajorView(ProtectedResourceMixin, DetailView):
    model = Major
    template_name = 'major.html'


class ClassView(ProtectedResourceMixin, TemplateView):
    template_name = 'class.html'

    def get_context_data(self, **kwargs):
        major_slug = self.kwargs.get('major_slug')
        class_slug = self.kwargs.get('class_slug')
        major = Major.objects.get(slug=major_slug)
        class_name = class_name_prettify(class_slug_to_name(class_slug))
        files = major.get_class_files(class_slug)
        kwargs.update({
            'files': files,
            'major': major,
            'class_name': class_name,
        })
        return super().get_context_data(**kwargs)


def download(request: HttpRequest, major_slug: str, class_slug: str):
    class_name = class_slug_to_name(class_slug)
    major = Major.objects.get(slug=major_slug)
    file_dir = storage.path(os.path.join(major.name, class_name))

    # Create ZIP file
    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED)
    for file in storage.listdir(file_dir)[1]:
        zip_file.write(os.path.join(file_dir, file), arcname=os.path.join(class_name, file))
    zip_file.close()

    buffer.seek(0)
    return FileResponse(buffer, filename=class_name + '.zip')
