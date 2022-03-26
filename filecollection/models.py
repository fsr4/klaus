import os
import re

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.db import models
from django.db.models.signals import post_init

from .apps import FileCollectionConfig

app_name = FileCollectionConfig.name
storage = StaticFilesStorage(location=app_name + '/static/' + app_name, base_url=app_name + '/')


def class_name_prettify(class_name: str) -> str:
    return re.sub(r"(\w)([A-Z]|(?<=[a-z])[1-3])", r"\1 \2", re.sub("_", " - ", class_name))


def class_name_to_slug(class_name: str) -> str:
    return re.sub(r"(\w)([A-Z]|(?<=[a-z])[1-3])", r"\1-\2", re.sub("_", "---", class_name)).lower()


def class_slug_to_name(class_slug: str) -> str:
    return re.sub("--", "_", re.sub(
        r"-[a-z0-9]",
        lambda pattern: pattern.group(0).replace("-", "").upper(),
        class_slug.capitalize()
    ))


class Major(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=10, unique=True)

    def __str__(self):
        return self.name

    @property
    def classes(self):
        return Klass.list_from_major(self)

    def get_class_files(self, class_slug: str):
        return ExamFile.list_from_class(self, class_slug_to_name(class_slug))


def init_major_directory(**kwargs):
    major = kwargs.get('instance')
    path = storage.path(major.name)
    os.makedirs(path, exist_ok=True)


post_init.connect(init_major_directory, Major)


class Klass:
    def __init__(self, major, name):
        super().__init__()
        self.major = major
        self.name = name
        self.slug = class_name_to_slug(name)
        self.pretty_name = class_name_prettify(name)
        self.element_count = len(storage.listdir(os.path.join(self.major.name, self.name))[1])

    def __str__(self) -> str:
        return self.pretty_name

    @staticmethod
    def list_from_major(major: Major):
        dir_list = storage.listdir(major.name)
        return [Klass(major, class_name) for class_name in sorted(dir_list[0])]


class ExamFile:
    def __init__(self, major, class_name, file_name):
        super().__init__()
        self.major = major
        self.class_name = class_name
        self.name = file_name
        self.path = os.path.join(self.major.name, self.class_name, self.name)
        self.url = storage.url(self.path)

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def list_from_class(major: Major, class_name: str):
        dir_list = storage.listdir(os.path.join(major.name, class_name))
        return [ExamFile(major, class_name, file) for file in sorted(dir_list[1])]
