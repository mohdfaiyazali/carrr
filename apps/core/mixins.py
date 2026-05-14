from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from apps.users.models import User


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in [User.Role.MANAGER, User.Role.ADMIN] or self.request.user.is_superuser
