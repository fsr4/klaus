import io
import os.path
import zipfile

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, FileResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.template import loader
from django.views.generic import DetailView, TemplateView

from downloader.auth_check import MajorRequiredMixin, major_check
from filecollection.models import Major, class_slug_to_name, class_name_prettify, storage

match_major = False


class FailView(TemplateView):
    template_name = 'fail.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        error = request.GET.get('error')
        self.extra_context = {'error': error}
        return super().get(request, *args, **kwargs)


def forbidden_handler(request, exception=None):
    return HttpResponseForbidden(loader.render_to_string('403.html', {'error': exception}))


def index_redirect(request: HttpRequest):
    if request.user.is_authenticated:
        major = request.user.major
        return HttpResponseRedirect(f'/{major}')
    return HttpResponseRedirect('/oidc/authenticate?next=/&fail=/fail')


class AllMajorsView(LoginRequiredMixin, TemplateView):
    template_name = 'all.html'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'majors': Major.objects.all()
        })
        return super().get_context_data(**kwargs)


class MajorView(MajorRequiredMixin if match_major else LoginRequiredMixin, DetailView):
    model = Major
    template_name = 'major.html'

    def get_major_required(self, **kwargs):
        return self.kwargs.get('slug')


class ClassView(MajorRequiredMixin if match_major else LoginRequiredMixin, TemplateView):
    template_name = 'class.html'

    def get_major_required(self, **kwargs):
        return self.kwargs.get('major_slug')

    def get_context_data(self, **kwargs):
        major_slug = self.kwargs.get('major_slug')
        class_slug = self.kwargs.get('class_slug')
        major = Major.objects.get(slug=major_slug)
        class_name = class_name_prettify(class_slug_to_name(class_slug))
        files = major.get_class_files(class_slug)
        print(files)
        kwargs.update({
            'files': files,
            'major': major,
            'class_name': class_name,
        })
        return super().get_context_data(**kwargs)


@login_required
def download_file(request: HttpRequest, major_slug: str, class_slug: str, file_name: str):
    # Check permissions
    if match_major and not major_check(request.user, major_slug, False):
        raise PermissionDenied('You may only download files from your own major')

    major = Major.objects.get(slug=major_slug)
    files = major.get_class_files(class_slug)

    exam_file = next(filter(lambda f: f.name == file_name, files), None)
    if exam_file is None:
        return HttpResponseNotFound(f'file {file_name} does not exist')

    return FileResponse(open(storage.path(exam_file.path), 'rb'), filename=exam_file.name)


@login_required
def download_class(request: HttpRequest, major_slug: str, class_slug: str):
    # Check permissions
    if match_major and not major_check(request.user, major_slug, False):
        raise PermissionDenied('You may only download files from your own major')

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
