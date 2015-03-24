from django.contrib import admin
from codingchallenge.models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "id")

# Register your models here.
admin.site.register(Category, CategoryAdmin)