from random import sample
from apps.music.models import Music 
from apps.playlist.models import Playlist # ajuste o caminho se necessário

# IDs das playlists fornecidas (sem None e únicos)
playlist_ids = list(set([46, 4, 15, 20, 16, 8, 14, 12, 11, 5, 13, 10, 17, 2, 3, 9, 7, 6]))

# Buscar músicas existentes
musics = list(Music.objects.all()[:100])  # limite por segurança
music_ids = [m.id for m in musics]

if len(music_ids) < 6:
    raise ValueError("É necessário ter ao menos 6 músicas no banco de dados.")

for playlist_id in playlist_ids:
    try:
        playlist = Playlist.objects.get(id=playlist_id)
        num_to_add = 5 + (playlist_id % 2)  # alterna entre 5 e 6
        selected_music_ids = sample(music_ids, num_to_add)
        playlist.music.set(selected_music_ids)
        playlist.save()
        print(f"Playlist {playlist_id} atualizada com músicas: {selected_music_ids}")
    except Playlist.DoesNotExist:
        print(f"Playlist {playlist_id} não encontrada.")
    except Exception as e:
        print(f"Erro com playlist {playlist_id}: {str(e)}")
