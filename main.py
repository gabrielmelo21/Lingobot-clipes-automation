import os
import json
import glob
import shutil

# Importa as funções de cada etapa do nosso pipeline
from edit_video_pre_upload import edit_and_prepare_video
from video_upload_to_firebase_automation import setup_firebase, upload_video_to_firebase
from generate_video_metadata import generate_and_save_metadata

def get_processed_videos(json_path: str) -> set:
    """Lê o arquivo JSON e retorna um conjunto com os nomes dos vídeos já processados."""
    processed_videos = set()
    if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for entry in data:
                # Extrai o nome do arquivo da URL para a verificação
                if 'video_url' in entry and entry['video_url']:
                    filename = os.path.basename(entry['video_url'])
                    processed_videos.add(filename)
    return processed_videos

if __name__ == "__main__":
    # --- CONFIGURAÇÃO ---
    # 1. Defina a pasta que contém os vídeos a serem processados.
    target_folder = "clipes/Viajando/*"

    # 2. Caminho para o arquivo de catálogo JSON
    json_catalog_path = "clipes_json/videos.json"
    
    # 3. Pasta de destino no Firebase Storage
    firebase_destination_folder = "lingobot-clipes/"

    # 4. Pasta para salvar cópias locais dos vídeos editados
    local_edited_folder = "clipes_editados"

    print("--- 🚀 INICIANDO PIPELINE DE PROCESSAMENTO EM LOTE ---")

    # --- ETAPA 0: INICIALIZAÇÃO E VERIFICAÇÃO ---
    try:
        # Garante que a pasta de clipes editados exista
        os.makedirs(local_edited_folder, exist_ok=True)

        # Inicializa o Firebase uma única vez
        setup_firebase()
        
        # Pega a lista de vídeos que já foram processados e estão no JSON
        processed_videos = get_processed_videos(json_catalog_path)
        print(f"Encontrados {len(processed_videos)} vídeos já catalogados.")

        # Pega todos os arquivos de vídeo da pasta de destino
        video_files_to_process = glob.glob(target_folder)
        print(f"Encontrados {len(video_files_to_process)} arquivos de vídeo na pasta de origem.")

        # --- LOOP DE PROCESSAMENTO ---
        for video_path in video_files_to_process:
            original_filename = os.path.basename(video_path)

            if original_filename in processed_videos:
                print(f"\n--- ⏭️ Pulando '{original_filename}' (já processado). ---")
                continue

            print(f"\n--- ▶️ Processando novo vídeo: {original_filename} ---")
            
            base, ext = os.path.splitext(video_path)
            video_editado_path = f"{base}_edited{ext}"

            edited_file = edit_and_prepare_video(video_path, video_editado_path)

            if edited_file:
                firebase_url = upload_video_to_firebase(
                    edited_file,
                    firebase_destination_folder,
                    remote_filename=original_filename
                )

                video_description = None  # Inicializa a descrição como None
                if firebase_url:
                    category = os.path.basename(os.path.dirname(video_path))
                    print(f"Extraindo categoria: {category}")
                    # Gera metadados e captura a descrição retornada
                    video_description = generate_and_save_metadata(firebase_url, original_filename, category)

                # ETAPA FINAL: Mover arquivo e salvar descrição
                try:
                    category_folder_name = os.path.basename(os.path.dirname(video_path))
                    video_folder_name = os.path.splitext(original_filename)[0]

                    final_destination_folder = os.path.join(local_edited_folder, category_folder_name, video_folder_name)
                    os.makedirs(final_destination_folder, exist_ok=True)

                    # Move o vídeo editado
                    destination_path = os.path.join(final_destination_folder, os.path.basename(edited_file))
                    shutil.move(edited_file, destination_path)
                    print(f"✅ Arquivo de vídeo salvo em: '{destination_path}'")

                    # Salva o arquivo de descrição, se a descrição foi gerada
                    if video_description:
                        description_filename = f"{video_folder_name}_description.txt"
                        description_path = os.path.join(final_destination_folder, description_filename)
                        with open(description_path, 'w', encoding='utf-8') as f:
                            f.write(video_description)
                        print(f"✅ Arquivo de descrição salvo em: '{description_path}'")

                except Exception as e:
                    print(f"❌ Erro ao mover o arquivo ou salvar a descrição: {e}")

    except Exception as e:
        print(f"❌ Um erro crítico ocorreu no pipeline: {e}")

    print("\n--- ✨ PIPELINE EM LOTE CONCLUÍDO ✨ ---")