from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured


def major_check(user, major, strict_match=False):
    if user.is_authenticated:
        if strict_match:
            if user.major == major:
                return True
        else:
            if user.major.split('-')[0] == major.split('-')[0]:
                return True
    return False


class MajorRequiredMixin(AccessMixin):
    major = None
    strict_match = False

    def get_permission_denied_message(self):
        return f"Du gehörst nicht zum Studiengang {self.get_major_required().upper()}"

    def get_major_required(self, **kwargs):
        if self.major is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the "
                f"major attribute. Define "
                f"{self.__class__.__name__}.major, or override "
                f"{self.__class__.__name__}.get_major_required()."
            )

    def dispatch(self, request, *args, **kwargs):
        if major_check(request.user, self.get_major_required(**kwargs), self.strict_match):
            # noinspection PyUnresolvedReferences
            return super().dispatch(request, *args, **kwargs)
        return self.handle_no_permission()
