
import os
from moviepy.editor import VideoFileClip

# Importa as funções do nosso script de upload
from video_upload_to_firebase_automation import setup_firebase, upload_video_to_firebase

def edit_and_prepare_video(source_path: str, temp_path: str):
    """
    Corta o primeiro 1.5 segundo de um vídeo e o salva em um caminho temporário.

    :param source_path: Caminho do vídeo original.
    :param temp_path: Caminho para salvar o vídeo editado.
    """
    if not os.path.exists(source_path):
        print(f"Erro: O arquivo de origem '{source_path}' não foi encontrado.")
        return False

    try:
        print(f"Carregando o vídeo: {source_path}")
        clip = VideoFileClip(source_path)

        # Corta o vídeo a partir de 1.5 segundos até o final
        print("Cortando o primeiro 1.5 segundo do vídeo...")
        edited_clip = clip.subclip(1.5)

        print(f"Salvando o vídeo editado em: {temp_path}")
        # codec="libx264" e audio_codec="aac" são bons para compatibilidade web
        edited_clip.write_videofile(temp_path, codec="libx264", audio_codec="aac")
        
        clip.close()
        edited_clip.close()
        
        print("Edição concluída.")
        return temp_path

    except Exception as e:
        print(f"Ocorreu um erro durante a edição do vídeo: {e}")
        return None






