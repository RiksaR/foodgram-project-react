from django.core.exceptions import ValidationError


def validate_positive_value(value):
    if value == 0:
        raise ValidationError(
            message='Значение этого поля не может равняться нулю!'
        )
