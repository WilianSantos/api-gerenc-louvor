from rest_framework import serializers

from .models import LineupMember, PraiseLineup


class PraiseLineupSerializers(serializers.ModelSerializer):
    playlist_display = serializers.SerializerMethodField()
    playlist_link_display = serializers.SerializerMethodField()
    class Meta:
        model = PraiseLineup
        fields = "__all__"

    def get_playlist_display(self, obj):
        return obj.get_playlist_display()

    def get_playlist_link_display(self, obj):
        return obj.get_playlist_link_display()


class LineupMemberSerializers(serializers.ModelSerializer):
    member_display = serializers.SerializerMethodField()
    function_display = serializers.SerializerMethodField()

    class Meta:
        model = LineupMember
        fields = "__all__"

    def get_member_display(self, obj):
        return obj.get_member_display()

    def get_function_display(self, obj):
        return obj.get_function_display()

    
