from django.contrib import admin

from .models import Member, MemberFunctions


class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'availability', 'user',)
    list_display_links = ('name',)
    search_fields = ('name', 'availability', 'function',)
    list_filter = ('name', 'availability', 'function',)
    list_per_page = 10
    ordering = ('name',)

admin.site.register(Member, MemberAdmin)


class MemberFunctionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'functions_name',)
    list_display_links = ('functions_name',)
    search_fields = ('functions_name',)
    list_filter = ('functions_name',)
    list_per_page = 10
    ordering = ('functions_name',)

admin.site.register(MemberFunctions, MemberFunctionsAdmin)
