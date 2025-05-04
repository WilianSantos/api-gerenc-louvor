import os
from rest_framework import serializers

from .models import Music, MusicCategory, MusicChord


class MusicCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = MusicCategory
        fields = "__all__"

class MusicChordSerializers(serializers.ModelSerializer):
    class Meta:
        model = MusicChord
        fields = "__all__"

class MusicSerializers(serializers.ModelSerializer):
    category = MusicCategorySerializers(many=True, read_only=True)
    music_chord = MusicChordSerializers(many=True, read_only=True)
    
    # Campos para aceitar apenas IDs no momento da criação/atualização
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=MusicCategory.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    music_chord_ids = serializers.PrimaryKeyRelatedField(
        queryset=MusicChord.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Music
        fields = [
            'id', 'music_title', 'author', 'music_tone', 'music_text',
            'music_link', 'category', 'music_chord', 'created_at', 
            'updated_at', 'category_ids', 'music_chord_ids'
        ]
    
    def create(self, validated_data): 
        category_ids = validated_data.pop('category_ids', [])
        music_chord_ids = validated_data.pop('music_chord_ids', [])
        
        music = Music.objects.create(**validated_data)
        
        if category_ids:
            music.category.set(category_ids)
        if music_chord_ids:
            music.music_chord.set(music_chord_ids)
        
        return music
    
    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        music_chord_ids = validated_data.pop('music_chord_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if category_ids is not None:
            instance.category.set(category_ids)
        
        if music_chord_ids is not None:
            instance.music_chord.set(music_chord_ids)
        
        return instance


class UploadPdfSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, value):
        file = value
        # Validação do tamanho do arquivo (máximo: 10MB)
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise serializers.ValidationError("O arquivo não pode exceder 10 MB.")

        # Validação do tipo de arquivo
        
        valid_extensions = [".pdf"]
        ext = os.path.splitext(file.name)[1].lower()

        if ext not in valid_extensions:
            raise serializers.ValidationError(
                "Tipo de arquivo não permitido. Carregue apenas PDF"
            )
        
        return file

