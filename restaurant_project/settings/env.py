import os

from django.core.exceptions import ImproperlyConfigured


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


def env_value(
    name: str,
    default: str | None = None,
    *,
    required: bool = False,
) -> str:
    value = os.environ.get(name)
    if value is not None and value.strip():
        return value.strip()
    if required:
        raise ImproperlyConfigured(
            f"The environment variable {name} is required."
        )
    return "" if default is None else default


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default

    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ImproperlyConfigured(
        f"The environment variable {name} must be a boolean value."
    )


def env_list(name: str, default: tuple[str, ...] = ()) -> list[str]:
    value = os.environ.get(name)
    if value is None:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]
