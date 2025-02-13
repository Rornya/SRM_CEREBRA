from django.contrib import admin
from .models import NewsPost

class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    actions = ['make_published', 'make_unpublished']

    def make_published(self, request, queryset):
        queryset.update(is_published=True)

    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)

    make_published.short_description = "Опубликовать выбранные посты"
    make_unpublished.short_description = "Снять с публикации выбранные посты"

admin.site.register(NewsPost, NewsPostAdmin)
