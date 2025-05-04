from django.contrib import admin

from .models import LineupMember, PraiseLineup


@admin.register(PraiseLineup)
class PraiseLineupAdmin(admin.ModelAdmin):
    list_display = ("lineup_date", "lineup_event", "playlist")
    list_filter = ("lineup_date",)


@admin.register(LineupMember)
class LineupMemberAdmin(admin.ModelAdmin):
    list_display = ("lineup", "member", "function", "created_at", 'get_member_display', 'get_function_display')
    list_filter = ("function", "lineup__lineup_date")
