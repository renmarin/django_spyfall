from django.contrib import admin

from .models import Places, Roles

# Register your models here.


class RolesInline(admin.TabularInline):
    model = Roles
    extra = 3


class PlacesAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['place']}),
    ]
    inlines = [RolesInline]

admin.site.register(Places, PlacesAdmin)
