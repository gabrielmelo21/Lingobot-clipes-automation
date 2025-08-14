import os
import json
import glob

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
    # O `*` no final significa que pegaremos todos os arquivos dentro da pasta.
    target_folder = "clipes/Cultura-mundial/*"

    # 2. Caminho para o arquivo de catálogo JSON
    json_catalog_path = "clipes_json/videos.json"
    
    # 3. Pasta de destino no Firebase Storage
    firebase_destination_folder = "lingobot-clipes/"

    print("--- 🚀 INICIANDO PIPELINE DE PROCESSAMENTO EM LOTE ---")

    # --- ETAPA 0: INICIALIZAÇÃO E VERIFICAÇÃO ---
    try:
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

            # Verifica se o vídeo já foi processado
            if original_filename in processed_videos:
                print(f"\n--- ⏭️ Pulando '{original_filename}' (já processado). ---")
                continue

            print(f"\n--- ▶️ Processando novo vídeo: {original_filename} ---")
            
            # Define o nome do arquivo editado temporário
            base, ext = os.path.splitext(video_path)
            video_editado_path = f"{base}_edited{ext}"

            # ETAPA 1: Edição
            edited_file = edit_and_prepare_video(video_path, video_editado_path)

            if edited_file:
                # ETAPA 2: Upload (com o nome do arquivo original)
                firebase_url = upload_video_to_firebase(
                    edited_file, 
                    firebase_destination_folder, 
                    remote_filename=original_filename
                )

                if firebase_url:
                    # ETAPA 3: Geração de Metadados com IA
                    generate_and_save_metadata(firebase_url, original_filename)
                
                # ETAPA 4: Limpeza
                try:
                    os.remove(edited_file)
                    print(f"✅ Arquivo temporário '{edited_file}' removido.")
                except OSError as e:
                    print(f"❌ Erro ao remover arquivo temporário: {e}")

    except Exception as e:
        print(f"❌ Um erro crítico ocorreu no pipeline: {e}")

    print("\n--- ✨ PIPELINE EM LOTE CONCLUÍDO ✨ ---")
