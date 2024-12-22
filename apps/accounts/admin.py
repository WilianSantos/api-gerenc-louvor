from django.contrib import admin

from .models import Member, MemberFunction


class MemberFunctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'function_name',)
    list_display_links = ('id', 'function_name',)
    search_fields = ('function_name',)
    list_filter = ('function_name',)
    list_per_page = 10
    ordering = ('function_name',)

admin.site.register(MemberFunction, MemberFunctionAdmin)


class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'availability', 'user',)
    list_display_links = ('name',)
    search_fields = ('name', 'availability', 'function',)
    list_filter = ('name', 'availability', 'function',)
    list_per_page = 10
    ordering = ('name',)

admin.site.register(Member, MemberAdmin)
