from .models import Shift


def get_active_shift(user):
    """Получает активную смену пользователя."""

    return Shift.objects.filter(waiter=user, is_active=True).first()
