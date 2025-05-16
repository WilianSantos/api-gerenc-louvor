from rest_framework import serializers

from .models import Playlist


class PlaylistSerializers(serializers.ModelSerializer):
    playlist_link_display = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = "__all__"

    def get_playlist_link_display(self, obj):
        return obj.get_playlist_link_display()
