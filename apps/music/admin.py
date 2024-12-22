from django.contrib import admin

from .models import Music, MusicCategory, MusicVersion

class MusicAdmin(admin.ModelAdmin):
    list_display = ('id', 'music_title', 'author', 'music_tone',)
    list_display_links = ('id', 'music_title', 'author',)
    search_fields = ('music_title', 'author', 'category')
    list_filter = ('music_title', 'author', 'category')
    list_per_page = 10
    ordering = ('music_title',)

admin.site.register(Music, MusicAdmin)


class MusicVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'version_author', 'version_title', 'music',)
    list_display_links = ('id', 'version_author', 'version_title',)
    search_fields = ('version_author', 'version_title', 'music',)
    list_filter = ('version_author', 'version_title', 'music',)
    list_per_page = 10
    ordering = ('version_author',)

admin.site.register(MusicVersion, MusicVersionAdmin)


class MusicCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    list_display_links = ('category_name',)
    search_fields = ('category_name',)
    list_filter = ('category_name',)
    list_per_page = 10
    ordering = ('category_name',)

admin.site.register(MusicCategory, MusicCategoryAdmin)
