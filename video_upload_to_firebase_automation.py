
import os
import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv


def setup_firebase():
    """Carrega as variáveis de ambiente e inicializa o app Firebase."""
    load_dotenv()

    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")

    if not cred_path or not bucket_name:
        raise ValueError("As variáveis de ambiente GOOGLE_APPLICATION_CREDENTIALS e FIREBASE_STORAGE_BUCKET devem ser definidas.")

    # Inicializa o app Firebase
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': bucket_name
    })
    print("Firebase app inicializado com sucesso!")


def upload_video_to_firebase(local_file_path: str, remote_folder: str, remote_filename: str = None):
    """
    Faz o upload de um arquivo de vídeo para uma pasta específica no Firebase Storage.

    :param local_file_path: O caminho para o arquivo de vídeo local.
    :param remote_folder: O nome da pasta no Firebase Storage onde o vídeo será salvo.
    :param remote_filename: (Opcional) O nome do arquivo no storage. Se não for fornecido, usa o nome do arquivo local.
    :return: A URL pública do vídeo no Firebase Storage ou None se o upload falhar.
    """
    if not os.path.exists(local_file_path):
        print(f"Erro: O arquivo local '{local_file_path}' não foi encontrado.")
        return None

    try:
        bucket = storage.bucket()
        
        # Usa o nome de arquivo remoto fornecido ou o nome do arquivo local como padrão
        destination_name = remote_filename if remote_filename else os.path.basename(local_file_path)
        remote_path = f"{remote_folder}{destination_name}" # Garante que a barra seja tratada corretamente

        blob = bucket.blob(remote_path)

        print(f"Iniciando o upload de '{local_file_path}' para '{remote_path}'...")
        
        # Faz o upload do arquivo
        blob.upload_from_filename(local_file_path)

        # Torna o arquivo público (opcional, mas necessário para obter uma URL de acesso direto)
        blob.make_public()

        print("Upload concluído com sucesso!")
        print(f"URL pública: {blob.public_url}")
        return blob.public_url

    except Exception as e:
        print(f"Ocorreu um erro durante o upload: {e}")
        return None


if __name__ == "__main__":
    # --- CONFIGURAÇÃO E TESTE ---
    try:
        setup_firebase()

        # 1. Escolha o vídeo que deseja enviar
        video_para_teste = "VIDEO_FINAL_COMPLETO.mp4" # Você pode trocar para qualquer vídeo da sua pasta 'clipes'

        # 2. Escolha a pasta de destino no Firebase Storage
        pasta_destino = "videos_de_teste"

        # 3. Executa o upload
        upload_video_to_firebase(video_para_teste, pasta_destino)

    except ValueError as e:
        print(f"Erro de configuração: {e}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")

