from rest_framework import serializers

from .models import Music, MusicCategory, MusicVersion


class MusicSerializers(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = '__all__'


class MusicCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = MusicCategory
        fields = '__all__'


class MusicVersionSerializers(serializers.ModelSerializer):
    class Meta:
        model = MusicVersion
        fields = '__all__'
