import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de endpoints da API Twitch
TWITCH_TOKEN_URL = os.getenv('TWITCH_TOKEN_URL', 'https://id.twitch.tv/oauth2/token')
TWITCH_API_BASE_URL = os.getenv('TWITCH_API_BASE_URL', 'https://api.twitch.tv/helix')

def get_twitch_auth_token(client_id, client_secret):
    """
    Obtém token de autenticação da API da Twitch.
    
    Args:
        client_id (str): Client ID da aplicação registrada na Twitch
        client_secret (str): Client Secret da aplicação registrada na Twitch
        
    Returns:
        str: Token de acesso ou None se falhar
    """
    response = requests.post(TWITCH_TOKEN_URL, {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    })
    
    if response.status_code != 200:
        print(f"Falha ao obter token: {response.status_code} - {response.text}")
        return None
        
    return response.json()['access_token']

def search_game_ids(game_names, client_id, client_secret):
    """
    Função para buscar game IDs na Twitch com base em uma lista de nomes de jogos.
    
    Args:
        game_names (list): Lista de nomes de jogos para buscar
        client_id (str): Client ID da aplicação registrada na Twitch
        client_secret (str): Client Secret da aplicação registrada na Twitch
        
    Returns:
        pd.DataFrame: DataFrame com os dados dos jogos encontrados, incluindo IDs
    """
    # Obter token de acesso
    access_token = get_twitch_auth_token(client_id, client_secret)
    if not access_token:
        return pd.DataFrame(columns=['id', 'name', 'box_art_url'])
    
    # Headers para a API
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    
    # Lista para armazenar os dados dos jogos
    all_games = []
    
    # Buscar IDs para cada jogo pelo nome
    for game_name in game_names:
        url = f'{TWITCH_API_BASE_URL}/games?name={game_name}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            games = response.json().get('data', [])
            for game in games:
                all_games.append(game)
        else:
            print(f"Erro ao buscar game ID para '{game_name}': {response.status_code} - {response.text}")
    
    # Converter para DataFrame
    if all_games:
        df = pd.DataFrame(all_games)
    else:
        df = pd.DataFrame(columns=['id', 'name', 'box_art_url'])
    
    return df

def get_twitch_channel_data_bulk(channel_names, client_id, client_secret):
    """
    Obtém informações de múltiplos canais da Twitch, incluindo textos de setup.
    
    Args:
        channel_names (list): Lista de nomes de canais da Twitch
        client_id (str): Client ID da aplicação registrada na Twitch
        client_secret (str): Client Secret da aplicação registrada na Twitch
        
    Returns:
        pd.DataFrame: DataFrame contendo informações de todos os canais
    """
    # Obter token de acesso
    access_token = get_twitch_auth_token(client_id, client_secret)
    if not access_token:
        return pd.DataFrame()
    
    # Configurar cabeçalhos da API
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    
    # Para armazenar dados de todos os canais
    all_channel_data = []
    
    for channel_name in channel_names:
        try:
            # Buscar dados básicos do canal pela API
            url = f'{TWITCH_API_BASE_URL}/users?login={channel_name}'
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Erro ao buscar dados do canal '{channel_name}': {response.status_code}")
                continue
                
            data = response.json().get('data', [])
            if not data:
                print(f"Canal '{channel_name}' não encontrado.")
                continue
                
            # Extrair informações básicas do canal
            channel_info = data[0]
            
            # Adicionar `view_count` corretamente (API de streams)
            streams_url = f"{TWITCH_API_BASE_URL}/streams?user_id={channel_info['id']}"
            streams_response = requests.get(streams_url, headers=headers)
            
            if streams_response.status_code == 200:
                stream_data = streams_response.json().get('data', [])
                if stream_data:
                    channel_info['view_count'] = stream_data[0].get('viewer_count', 0)
                else:
                    channel_info['view_count'] = 0  # Offline ou sem visualizações
            else:
                channel_info['view_count'] = 0
            
            # Scraping para obter textos de setup
            setup_texts = []
            try:
                about_url = f"https://www.twitch.tv/{channel_name}/about"
                about_response = requests.get(about_url)
                
                if about_response.status_code == 200:
                    soup = BeautifulSoup(about_response.text, 'html.parser')
                    panels = soup.find_all('div', class_='panel-description')  # Atualizar classe conforme necessário
                    setup_texts = [panel.get_text(strip=True) for panel in panels]
                else:
                    print(f"Erro ao acessar página 'About' do canal '{channel_name}': {about_response.status_code}")
            except Exception as e:
                print(f"Erro ao realizar scraping para o canal '{channel_name}': {e}")
            
            # Adicionar informações dos textos de setup ao canal
            channel_info['setup_texts'] = setup_texts
            
            # Armazenar informações do canal
            all_channel_data.append(channel_info)
        
        except Exception as e:
            print(f"Erro ao processar canal '{channel_name}': {e}")
    
    # Transformar todos os dados em um DataFrame
    df_canais_twitch = pd.DataFrame(all_channel_data) if all_channel_data else pd.DataFrame()
    return df_canais_twitch

def get_twitch_game_data(game_name, client_id, client_secret):
    """
    Função para obter informações de um jogo na Twitch pelo nome.
    
    Args:
        game_name (str): Nome do jogo
        client_id (str): Client ID da aplicação registrada na Twitch
        client_secret (str): Client Secret da aplicação registrada na Twitch
        
    Returns:
        dict: Dados do jogo ou mensagem de erro
    """
    # Obter token de acesso
    access_token = get_twitch_auth_token(client_id, client_secret)
    if not access_token:
        return {"error": "Falha ao obter token de autenticação"}
    
    # Buscar dados do jogo pelo nome
    url = f'{TWITCH_API_BASE_URL}/games?name={game_name}'
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    
    # Verificar se a chamada foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        if not data.get('data'):
            return {"error": f"Jogo '{game_name}' não encontrado na Twitch"}
        return data
    else:
        return {"error": f"Erro ao buscar dados do jogo: {response.status_code} - {response.text}"}

def get_live_streams_for_games(game_ids, client_id, client_secret, language='pt', limit=100):
    """
    Função para buscar streams ao vivo para uma lista de jogos, filtrando por idioma.
    
    Args:
        game_ids (list): Lista de IDs dos jogos na Twitch
        client_id (str): Client ID da aplicação registrada na Twitch
        client_secret (str): Client Secret da aplicação registrada na Twitch
        language (str): Código do idioma para filtrar as streams (padrão: 'pt')
        limit (int): Limite de streams a retornar por jogo (padrão: 100)
        
    Returns:
        pd.DataFrame: DataFrame com os dados das streams ao vivo
    """
    # Obter token de acesso
    access_token = get_twitch_auth_token(client_id, client_secret)
    if not access_token:
        return pd.DataFrame()
    
    # Headers para a API
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    
    # Lista para armazenar os dados
    all_streams = []
    
    # Buscar streams para cada jogo
    for game_id in game_ids:
        url = f'{TWITCH_API_BASE_URL}/streams?game_id={game_id}&language={language}&first={limit}'
        
        # Implementar paginação para obter mais resultados
        pagination_cursor = None
        streams_count = 0
        
        while streams_count < limit:
            paginated_url = url
            if pagination_cursor:
                paginated_url += f'&after={pagination_cursor}'
                
            response = requests.get(paginated_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                streams = data.get('data', [])
                
                if not streams:
                    break  # Não há mais streams
                
                # Adicionar o ID do jogo aos dados da stream
                for stream in streams:
                    stream['game_id'] = game_id
                
                all_streams.extend(streams)
                streams_count += len(streams)
                
                # Verificar se há mais páginas
                pagination_cursor = data.get('pagination', {}).get('cursor')
                if not pagination_cursor:
                    break
            else:
                print(f"Erro ao buscar streams para game_id={game_id}: {response.status_code} - {response.text}")
                break
    
    # Converter para DataFrame
    if all_streams:
        df = pd.DataFrame(all_streams)
    else:
        df = pd.DataFrame(columns=['game_id', 'user_id', 'user_name', 'title', 'viewer_count', 'language'])
    
    return df

def get_top_games(client_id, client_secret, first=100):
    """
    Obtém a lista dos jogos mais populares na Twitch.
    
    Args:
        client_id (str): Client ID da aplicação registrada na Twitch
        client_secret (str): Client Secret da aplicação registrada na Twitch
        first (int): Número de jogos a retornar (padrão: 100)
        
    Returns:
        pd.DataFrame: DataFrame com os jogos mais populares
    """
    # Obter token de acesso
    access_token = get_twitch_auth_token(client_id, client_secret)
    if not access_token:
        return pd.DataFrame()
    
    # Headers para a API
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    
    # URL para obter os jogos mais populares
    url = f'{TWITCH_API_BASE_URL}/games/top?first={first}'
    
    # Implementar paginação para obter mais resultados
    all_games = []
    pagination_cursor = None
    games_count = 0
    
    while games_count < first:
        paginated_url = url
        if pagination_cursor:
            paginated_url += f'&after={pagination_cursor}'
            
        response = requests.get(paginated_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('data', [])
            
            if not games:
                break  # Não há mais jogos
            
            all_games.extend(games)
            games_count += len(games)
            
            # Verificar se há mais páginas
            pagination_cursor = data.get('pagination', {}).get('cursor')
            if not pagination_cursor:
                break
        else:
            print(f"Erro ao buscar jogos populares: {response.status_code} - {response.text}")
            break
    
    # Converter para DataFrame
    if all_games:
        df = pd.DataFrame(all_games)
    else:
        df = pd.DataFrame(columns=['id', 'name', 'box_art_url'])
    
    return df

def register_twitch_tools(mcp):
    """
    Registra as ferramentas da Twitch no MCP.
    
    Args:
        mcp: Instância do FastMCP
    """
    # Carregando variáveis de ambiente
    load_dotenv()
    
    # Usando as novas credenciais fornecidas
    TWITCH_CLIENT_ID = os.getenv("TWITCH_API_CLIENT_ID", "xeea2lir92l9lu67uiqca539nghwza")
    TWITCH_CLIENT_SECRET = os.getenv("TWITCH_API_CLIENT_SECRET", "hdynaddspbdua06shhwndd4ptif1qh")
    
    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        print("AVISO: Credenciais da Twitch não encontradas nas variáveis de ambiente!")
        return
    
    @mcp.tool()
    def twitch_search_games(
        game_names: list
    ) -> dict:
        """
        Busca IDs de jogos na Twitch com base em seus nomes.
        
        Args:
            game_names: Lista de nomes de jogos para buscar
            
        Returns:
            dict: Informações dos jogos encontrados
        """
        try:
            result = search_game_ids(game_names, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def twitch_get_channels(
        channel_names: list
    ) -> dict:
        """
        Obtém informações de múltiplos canais da Twitch.
        
        Args:
            channel_names: Lista de nomes de canais da Twitch
            
        Returns:
            dict: Informações dos canais
        """
        try:
            result = get_twitch_channel_data_bulk(channel_names, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def twitch_get_game_info(
        game_name: str
    ) -> dict:
        """
        Obtém informações detalhadas de um jogo na Twitch.
        
        Args:
            game_name: Nome do jogo
            
        Returns:
            dict: Informações do jogo
        """
        try:
            result = get_twitch_game_data(game_name, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
            return {"success": "error" not in result, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def twitch_get_live_streams(
        game_ids: list,
        language: str = "pt",
        limit: int = 100
    ) -> dict:
        """
        Busca streams ao vivo para uma lista de jogos.
        
        Args:
            game_ids: Lista de IDs dos jogos na Twitch
            language: Código do idioma para filtrar as streams (padrão: 'pt')
            limit: Limite de streams a retornar por jogo (padrão: 100)
            
        Returns:
            dict: Dados das streams ao vivo
        """
        try:
            result = get_live_streams_for_games(game_ids, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, language, limit)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def twitch_get_top_games(
        limit: int = 100
    ) -> dict:
        """
        Obtém a lista dos jogos mais populares na Twitch.
        
        Args:
            limit: Número de jogos a retornar (padrão: 100)
            
        Returns:
            dict: Lista dos jogos mais populares
        """
        try:
            result = get_top_games(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, limit)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            return {"success": False, "error": str(e)}