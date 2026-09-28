from django.contrib import admin

from .models import RestaurantSettings, SpecialOpeningHours, WeeklyOpeningHours


@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identité", {"fields": ("name", "tagline")} ),
        (
            "Coordonnées publiques",
            {
                "fields": (
                    "address",
                    "postal_code",
                    "city",
                    "public_phone",
                    "public_email",
                )
            },
        ),
        (
            "Règles de réservation",
            {
                "fields": (
                    "capacity",
                    "reservation_duration_minutes",
                    "slot_interval_minutes",
                    "modification_cutoff_hours",
                    "max_online_party_size",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not RestaurantSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(WeeklyOpeningHours)
class WeeklyOpeningHoursAdmin(admin.ModelAdmin):
    list_display = ("weekday", "opens_at", "closes_at")
    list_filter = ("weekday",)
    ordering = ("weekday", "opens_at")


@admin.register(SpecialOpeningHours)
class SpecialOpeningHoursAdmin(admin.ModelAdmin):
    list_display = ("date", "closed", "opens_at", "closes_at", "description")
    list_filter = ("closed",)
    ordering = ("date",)
