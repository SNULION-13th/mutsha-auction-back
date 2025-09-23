from django.contrib import admin
from .models import Point

# Register your models here.
@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ['id', 'price', 'point']
    list_filter = ['point']
    search_fields = ['price']
