from django.contrib import admin
from .models import Category, Tag, Article, Comment, Announcement

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'text')

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Announcement)