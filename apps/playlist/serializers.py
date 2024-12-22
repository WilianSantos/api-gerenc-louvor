from rest_framework import serializers

from .models import Playlist


class PlaylistSerializers(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'