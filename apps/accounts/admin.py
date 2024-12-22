from django.contrib import admin

from .models import Member


class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'availability', 'user',)
    list_display_links = ('name',)
    search_fields = ('name', 'availability', 'function',)
    list_filter = ('name', 'availability', 'function',)
    list_per_page = 10
    ordering = ('name',)

admin.site.register(Member, MemberAdmin)
