
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

def generate_and_save_metadata(firebase_url: str, original_filename: str, category: str):
    """
    Gera uma descrição de vídeo usando a API Gemini e salva os metadados em um arquivo JSON.

    :param firebase_url: A URL pública do vídeo no Firebase Storage.
    :param original_filename: O nome do arquivo original do vídeo (para contexto).
    :param category: A categoria do vídeo, baseada na pasta de origem.
    :return: True se for bem-sucedido, False caso contrário.
    """
    try:
        print("--- Configurando a API Gemini ---")
        load_dotenv()
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("❌ Erro: A variável de ambiente GEMINI_API_KEY não foi encontrada.")
            return False
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Limpa o nome do arquivo para criar um contexto melhor para a IA
        clean_filename = os.path.basename(original_filename).split('.')[0].replace('-', ' ')

        # Cria o prompt para a IA
        prompt = f"""Your task is to write a very short caption for a TikTok video.
        The video shows a character named Lingobot. The audience is learning intermediate English.
        Based on the filename '{clean_filename}', describe what Lingobot is doing in a simple, clear, and casual sentence.
        The sentence should be around 5 to 7 words long. Use common contractions.

        Example for filename 'making pizza': "Look! Lingobot's making a pizza."
        Example for filename 'running in the park': "Lingobot is going for a run."
        Example for filename 'programming': "He's focused on his coding."""

        print(f"Gerando descrição para: {clean_filename}...")
        response = model.generate_content(prompt)
        video_description = response.text.strip()
        print(f"✅ Descrição gerada: {video_description}")

        # Define o caminho para o arquivo JSON
        json_path = "clipes_json/videos.json"
        
        # Garante que o diretório exista
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        # Lê o conteúdo existente do JSON ou cria uma nova lista
        if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        # Cria a nova entrada de metadados
        new_metadata = {
            "video_url": firebase_url,
            "video_description": video_description,
            "category": category
        }

        # Adiciona a nova entrada à lista
        data.append(new_metadata)

        # Salva a lista atualizada de volta no arquivo JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Metadados salvos em {json_path}")
        return video_description

    except Exception as e:
        print(f"❌ Ocorreu um erro ao gerar ou salvar metadados: {e}")
        return None
