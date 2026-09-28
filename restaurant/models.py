from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class RestaurantSettings(models.Model):
    name = models.CharField(max_length=120, default="Restaurant Osaka")
    tagline = models.CharField(max_length=180, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=12, blank=True)
    city = models.CharField(max_length=100, blank=True)
    public_phone = models.CharField(max_length=30, blank=True)
    public_email = models.EmailField(blank=True)
    capacity = models.PositiveSmallIntegerField(
        default=20,
        validators=[MinValueValidator(1)],
    )
    reservation_duration_minutes = models.PositiveSmallIntegerField(
        default=90,
        validators=[MinValueValidator(30)],
    )
    slot_interval_minutes = models.PositiveSmallIntegerField(
        default=30,
        validators=[MinValueValidator(5)],
    )
    modification_cutoff_hours = models.PositiveSmallIntegerField(default=2)
    max_online_party_size = models.PositiveSmallIntegerField(
        default=8,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = "configuration du restaurant"
        verbose_name_plural = "configuration du restaurant"

    @classmethod
    def load(cls):
        config, _ = cls.objects.get_or_create(pk=1)
        return config

    def save(self, *args, **kwargs):
        self.pk = 1
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class WeeklyOpeningHours(models.Model):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    WEEKDAYS = (
        (MONDAY, "Lundi"),
        (TUESDAY, "Mardi"),
        (WEDNESDAY, "Mercredi"),
        (THURSDAY, "Jeudi"),
        (FRIDAY, "Vendredi"),
        (SATURDAY, "Samedi"),
        (SUNDAY, "Dimanche"),
    )

    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    opens_at = models.TimeField()
    closes_at = models.TimeField()

    class Meta:
        ordering = ("weekday", "opens_at")
        constraints = [
            models.UniqueConstraint(
                fields=("weekday", "opens_at", "closes_at"),
                name="unique_weekly_service",
            )
        ]
        verbose_name = "horaire hebdomadaire"
        verbose_name_plural = "horaires hebdomadaires"

    def clean(self):
        super().clean()
        errors = {}
        if self.opens_at and self.closes_at and self.closes_at <= self.opens_at:
            errors["closes_at"] = "L'heure de fermeture doit suivre l'ouverture."

        if self.weekday is not None and self.opens_at and self.closes_at:
            overlaps = type(self).objects.filter(
                weekday=self.weekday,
                opens_at__lt=self.closes_at,
                closes_at__gt=self.opens_at,
            )
            if self.pk:
                overlaps = overlaps.exclude(pk=self.pk)
            if overlaps.exists():
                errors["opens_at"] = "Ce service chevauche un horaire existant."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.get_weekday_display()} "
            f"{self.opens_at.strftime('%H:%M')}–{self.closes_at.strftime('%H:%M')}"
        )
