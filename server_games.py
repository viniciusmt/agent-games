import sys
import traceback
import os
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv


try:
    from mcp.server.fastmcp import FastMCP
    
    # Certifica-se de que o diretório atual está no path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    print(f"Adicionado ao sys.path: {current_dir}", file=sys.stderr)
    
    # Importando o módulo steam
    try:
        import steam
        print("Módulo steam importado com sucesso", file=sys.stderr)
    except ImportError as e:
        print(f"Erro ao importar steam: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    
    # Importando o módulo wow
    try:
        import wow
        print("Módulo wow importado com sucesso", file=sys.stderr)
    except ImportError as e:
        print(f"Erro ao importar wow: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    
    # Importando o módulo data_twitch para funções da Twitch
    try:
        import data_twitch
        print("Módulo data_twitch importado com sucesso", file=sys.stderr)
    except ImportError as e:
        print(f"Erro ao importar data_twitch: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    
    # Importando o módulo BigQuery
    try:
        import bq
        print("Módulo BigQuery importado com sucesso", file=sys.stderr)
    except ImportError as e:
        print(f"Erro ao importar bq: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        # Adicione estas importações no início do arquivo, junto com as outras importações
    try:
        import wordpress
        print("Módulo wordpress importado com sucesso", file=sys.stderr)
    except ImportError as e:
        print(f"Erro ao importar wordpress: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    if not STEAM_API_KEY:
        print("AVISO: STEAM_API_KEY não encontrada nas variáveis de ambiente!", file=sys.stderr)
    
    BLIZZARD_CLIENT_ID = os.getenv("BLIZZARD_CLIENT_ID")
    BLIZZARD_CLIENT_SECRET = os.getenv("BLIZZARD_CLIENT_SECRET")
    if not BLIZZARD_CLIENT_ID or not BLIZZARD_CLIENT_SECRET:
        print("AVISO: Credenciais da Blizzard não encontradas nas variáveis de ambiente!", file=sys.stderr)
    
    # Usando as novas credenciais fornecidas para a Twitch
    TWITCH_CLIENT_ID = os.getenv("TWITCH_API_CLIENT_ID", "xeea2lir92l9lu67uiqca539nghwza")
    TWITCH_CLIENT_SECRET = os.getenv("TWITCH_API_CLIENT_SECRET", "hdynaddspbdua06shhwndd4ptif1qh")
    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        print("AVISO: Credenciais da Twitch não encontradas nas variáveis de ambiente!", file=sys.stderr)
    
    # Inicializa o FastMCP
    mcp = FastMCP("games-agent")
    
    # Ferramentas Steam
    @mcp.tool()
    def steam_game_data(
        app_ids: List[int],
        language: str = "portuguese",
        max_reviews: int = 50
    ) -> dict:
        """
        Obtém dados detalhados de jogos da Steam.
        
        Args:
            app_ids: Lista de IDs de jogos na Steam
            language: Idioma para as descrições e reviews (padrão: portuguese)
            max_reviews: Número máximo de reviews a serem coletados
            
        Returns:
            dict: Informações detalhadas dos jogos
        """
        try:
            result = steam.get_steam_game_data(app_ids, language, max_reviews)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em steam_game_data: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def current_players(
        app_id: int
    ) -> dict:
        """
        Obtém o número atual de jogadores para um jogo específico.
        
        Args:
            app_id: ID do jogo na Steam
            
        Returns:
            dict: Número atual de jogadores
        """
        try:
            result = steam.get_current_players(app_id)
            return {"success": True, "data": {"current_players": result}}
        except Exception as e:
            print(f"Erro em current_players: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def historical_data(
        app_ids: List[int]
    ) -> dict:
        """
        Obtém dados históricos de jogadores para jogos da Steam.
        
        Args:
            app_ids: Lista de IDs de jogos na Steam
            
        Returns:
            dict: Dados históricos de jogadores
        """
        try:
            result = steam.get_historical_data_for_games(app_ids)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em historical_data: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def game_reviews(
        app_ids: List[int],
        language: str = "portuguese",
        max_reviews: int = 50
    ) -> dict:
        """
        Obtém avaliações de jogos da Steam.
        
        Args:
            app_ids: Lista de IDs de jogos na Steam
            language: Idioma das avaliações (padrão: portuguese)
            max_reviews: Número máximo de avaliações por jogo
            
        Returns:
            dict: Avaliações de jogos
        """
        try:
            result = steam.get_steam_game_reviews(app_ids, language, max_reviews)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em game_reviews: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def recent_games(
        app_ids: List[int],
        num_players: int = 10
    ) -> dict:
        """
        Obtém jogos recentes jogados por usuários que avaliaram jogos específicos.
        
        Args:
            app_ids: Lista de IDs de jogos na Steam
            num_players: Número de jogadores a analisar
            
        Returns:
            dict: Jogos recentes populares entre jogadores
        """
        try:
            result = steam.get_recent_games_for_multiple_apps(app_ids, STEAM_API_KEY, num_players)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em recent_games: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    # Ferramentas World of Warcraft
    @mcp.tool()
    def wow_character_info(
        character_name: str,
        realm: str,
        region: str = "us"
    ) -> dict:
        """
        Obtém informações detalhadas de um personagem de World of Warcraft.
        
        Args:
            character_name: Nome do personagem
            realm: Nome do reino (servidor)
            region: Região do servidor (padrão: "us")
            
        Returns:
            dict: Informações detalhadas do personagem (perfil, estatísticas, equipamentos e conquistas)
        """
        try:
            result = wow.get_complete_character_info(
                BLIZZARD_CLIENT_ID, 
                BLIZZARD_CLIENT_SECRET, 
                region, 
                realm, 
                character_name
            )
            return result
        except Exception as e:
            print(f"Erro em wow_character_info: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def wow_search_characters(
        names: List[str],
        realm: str,
        region: str = "us"
    ) -> dict:
        """
        Pesquisa múltiplos personagens de World of Warcraft.
        
        Args:
            names: Lista de nomes de personagens
            realm: Nome do reino (servidor)
            region: Região do servidor (padrão: "us")
            
        Returns:
            dict: Informações básicas dos personagens encontrados
        """
        try:
            result = wow.search_characters(
                BLIZZARD_CLIENT_ID, 
                BLIZZARD_CLIENT_SECRET, 
                region, 
                realm, 
                names
            )
            return result
        except Exception as e:
            print(f"Erro em wow_search_characters: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def wow_guild_info(
        guild_name: str,
        realm: str,
        region: str = "us"
    ) -> dict:
        """
        Obtém informações detalhadas de uma guilda de World of Warcraft.
        
        Args:
            guild_name: Nome da guilda
            realm: Nome do reino (servidor)
            region: Região do servidor (padrão: "us")
            
        Returns:
            dict: Informações da guilda, incluindo lista de membros
        """
        try:
            result = wow.get_guild_info(
                BLIZZARD_CLIENT_ID, 
                BLIZZARD_CLIENT_SECRET, 
                region, 
                realm, 
                guild_name
            )
            return result
        except Exception as e:
            print(f"Erro em wow_guild_info: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def wow_search_guilds(
        guild_names: List[str],
        realm: str,
        region: str = "us"
    ) -> dict:
        """
        Pesquisa múltiplas guildas de World of Warcraft.
        
        Args:
            guild_names: Lista de nomes de guildas
            realm: Nome do reino (servidor)
            region: Região do servidor (padrão: "us")
            
        Returns:
            dict: Informações básicas das guildas encontradas
        """
        try:
            result = wow.search_guilds(
                BLIZZARD_CLIENT_ID, 
                BLIZZARD_CLIENT_SECRET, 
                region, 
                realm, 
                guild_names
            )
            return result
        except Exception as e:
            print(f"Erro em wow_search_guilds: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def wow_auction_data(
        realm: str,
        region: str = "us",
        limit: int = 100
    ) -> dict:
        """
        Obtém dados do leilão (mercado) de World of Warcraft.
        
        Args:
            realm: Nome do reino (servidor)
            region: Região do servidor (padrão: "us")
            limit: Número máximo de itens a retornar (padrão: 100)
            
        Returns:
            dict: Dados do leilão, incluindo preços e informações de itens
        """
        try:
            result = wow.get_auction_data(
                BLIZZARD_CLIENT_ID, 
                BLIZZARD_CLIENT_SECRET, 
                region, 
                realm, 
                limit=limit
            )
            return result
        except Exception as e:
            print(f"Erro em wow_auction_data: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
            
    # Ferramentas Twitch
    @mcp.tool()
    def twitch_search_games(
        game_names: List[str]
    ) -> dict:
        """
        Busca IDs de jogos na Twitch com base em seus nomes.
        
        Args:
            game_names: Lista de nomes de jogos para buscar
            
        Returns:
            dict: Informações dos jogos encontrados
        """
        try:
            result = data_twitch.search_game_ids(game_names, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em twitch_search_games: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def twitch_get_channels(
        channel_names: List[str]
    ) -> dict:
        """
        Obtém informações de múltiplos canais da Twitch.
        
        Args:
            channel_names: Lista de nomes de canais da Twitch
            
        Returns:
            dict: Informações dos canais
        """
        try:
            result = data_twitch.get_twitch_channel_data_bulk(channel_names, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em twitch_get_channels: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
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
            result = data_twitch.get_twitch_game_data(game_name, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
            return {"success": "error" not in result, "data": result}
        except Exception as e:
            print(f"Erro em twitch_get_game_info: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def twitch_get_live_streams(
        game_ids: List[str],
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
            result = data_twitch.get_live_streams_for_games(game_ids, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, language, limit)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em twitch_get_live_streams: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
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
            result = data_twitch.get_top_games(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, limit)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em twitch_get_top_games: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    # Novas Ferramentas BigQuery
    @mcp.tool()
    def bq_list_datasets(
        project_id: Optional[str] = None
    ) -> dict:
        """
        Lista todos os datasets disponíveis no projeto do BigQuery.
        
        Args:
            project_id: ID do projeto (opcional, usa o projeto padrão se não for fornecido)
            
        Returns:
            dict: Lista de datasets disponíveis
        """
        try:
            result = bq.list_datasets(project_id)
            return {"success": True, "data": result}
        except Exception as e:
            print(f"Erro em bq_list_datasets: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def bq_list_tables(
        dataset_id: str,
        project_id: Optional[str] = None
    ) -> dict:
        """
        Lista todas as tabelas de um dataset específico no BigQuery.
        
        Args:
            dataset_id: ID do dataset
            project_id: ID do projeto (opcional, usa o projeto padrão se não for fornecido)
            
        Returns:
            dict: Lista de tabelas do dataset
        """
        try:
            result = bq.list_tables(dataset_id, project_id)
            return {"success": True, "data": result}
        except Exception as e:
            print(f"Erro em bq_list_tables: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def bq_execute_query(
        query: str
    ) -> dict:
        """
        Executa uma query SQL no BigQuery.
        
        Args:
            query: Query SQL a ser executada
            
        Returns:
            dict: Resultado da query em formato DataFrame
        """
        try:
            result = bq.execute_query(query)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em bq_execute_query: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def bq_get_table_data(
        table_id: str,
        dataset_id: str,
        project_id: Optional[str] = None,
        limit: int = 1000
    ) -> dict:
        """
        Obtém dados de uma tabela específica do BigQuery.
        
        Args:
            table_id: ID da tabela
            dataset_id: ID do dataset
            project_id: ID do projeto (opcional, usa o projeto padrão se não for fornecido)
            limit: Limite de linhas a retornar (padrão: 1000)
            
        Returns:
            dict: Dados da tabela
        """
        try:
            result = bq.get_table_data(table_id, dataset_id, project_id, limit)
            return {"success": True, "data": result.to_dict("records")}
        except Exception as e:
            print(f"Erro em bq_get_table_data: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def bq_insert_rows(
        table_id: str,
        dataset_id: str,
        rows_data: List[Dict[str, Any]],
        project_id: Optional[str] = None
    ) -> dict:
        """
        Insere novas linhas em uma tabela do BigQuery.
        
        Args:
            table_id: ID da tabela
            dataset_id: ID do dataset
            rows_data: Lista de dicionários com os dados a serem inseridos
            project_id: ID do projeto (opcional, usa o projeto padrão se não for fornecido)
            
        Returns:
            dict: Resultado da operação
        """
        try:
            result = bq.insert_rows(table_id, dataset_id, rows_data, project_id)
            return result
        except Exception as e:
            print(f"Erro em bq_insert_rows: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def bq_replace_table(
        table_id: str,
        dataset_id: str,
        data: Union[List[Dict[str, Any]], Dict[str, List[Any]]],
        project_id: Optional[str] = None
    ) -> dict:
        """
        Substitui uma tabela existente por novos dados ou cria uma nova tabela.
        
        Args:
            table_id: ID da tabela
            dataset_id: ID do dataset
            data: Dados para a nova tabela (lista de dicionários ou dicionário com listas)
            project_id: ID do projeto (opcional, usa o projeto padrão se não for fornecido)
            
        Returns:
            dict: Resultado da operação
        """
        try:
            result = bq.replace_table(table_id, dataset_id, data, None, project_id)
            return result
        except Exception as e:
            print(f"Erro em bq_replace_table: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    @mcp.tool()
    def bq_create_dataset(
        dataset_id: str,
        project_id: Optional[str] = None,
        location: str = "US"
    ) -> dict:
        """
        Cria um novo dataset no BigQuery.
        
        Args:
            dataset_id: ID do dataset a ser criado
            project_id: ID do projeto (opcional, usa o projeto padrão se não for fornecido)
            location: Localização dos dados (padrão: "US")
            
        Returns:
            dict: Resultado da operação
        """
        try:
            result = bq.create_dataset(dataset_id, project_id, location)
            return result
        except Exception as e:
            print(f"Erro em bq_create_dataset: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
    
    
    # Ferramentas WordPress
    @mcp.tool()
    def wp_create_post(
        title: str,
        content: str,
        status: str = "publish",
        categories: Optional[List[int]] = None,
        tags: Optional[List[int]] = None,
        featured_media: Optional[int] = None
    ) -> dict:
        """
        Cria um novo post no WordPress.
        
        Args:
            title: Título do post
            content: Conteúdo HTML do post
            status: Status do post (draft, publish, pending, etc.)
            categories: Lista de IDs de categorias (opcional)
            tags: Lista de IDs de tags (opcional)
            featured_media: ID da mídia destacada (opcional)
            
        Returns:
            dict: Resposta da API do WordPress
        """
        try:
            result = wordpress.create_post(title, content, status, categories, tags, featured_media)
            return result
        except Exception as e:
            print(f"Erro em wp_create_post: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_create_page(
        title: str,
        content: str,
        status: str = "publish",
        parent: Optional[int] = None,
        featured_media: Optional[int] = None
    ) -> dict:
        """
        Cria uma nova página no WordPress.
        
        Args:
            title: Título da página
            content: Conteúdo HTML da página
            status: Status da página (draft, publish, pending, etc.)
            parent: ID da página pai (opcional)
            featured_media: ID da mídia destacada (opcional)
            
        Returns:
            dict: Resposta da API do WordPress
        """
        try:
            result = wordpress.create_page(title, content, status, parent, featured_media)
            return result
        except Exception as e:
            print(f"Erro em wp_create_page: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_upload_media(
        file_path: str,
        title: Optional[str] = None
    ) -> dict:
        """
        Faz upload de um arquivo de mídia para a biblioteca de mídia do WordPress.
        
        Args:
            file_path: Caminho para o arquivo local
            title: Título para a mídia (opcional)
            
        Returns:
            dict: Resposta da API do WordPress
        """
        try:
            result = wordpress.upload_media(file_path, title)
            return result
        except Exception as e:
            print(f"Erro em wp_upload_media: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_upload_media_from_url(
        image_url: str,
        title: Optional[str] = None
    ) -> dict:
        """
        Faz upload de uma imagem a partir de uma URL para a biblioteca de mídia do WordPress.
        
        Args:
            image_url: URL da imagem
            title: Título para a mídia (opcional)
            
        Returns:
            dict: Resposta da API do WordPress
        """
        try:
            result = wordpress.upload_media_from_url(image_url, title)
            return result
        except Exception as e:
            print(f"Erro em wp_upload_media_from_url: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_get_posts(
        per_page: int = 10,
        page: int = 1
    ) -> dict:
        """
        Obtém a lista de posts do WordPress.
        
        Args:
            per_page: Número de posts por página (padrão: 10)
            page: Número da página (padrão: 1)
            
        Returns:
            dict: Lista de posts
        """
        try:
            result = wordpress.get_posts(per_page, page)
            return result
        except Exception as e:
            print(f"Erro em wp_get_posts: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_get_pages(
        per_page: int = 10,
        page: int = 1
    ) -> dict:
        """
        Obtém a lista de páginas do WordPress.
        
        Args:
            per_page: Número de páginas por página (padrão: 10)
            page: Número da página (padrão: 1)
            
        Returns:
            dict: Lista de páginas
        """
        try:
            result = wordpress.get_pages(per_page, page)
            return result
        except Exception as e:
            print(f"Erro em wp_get_pages: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_get_categories() -> dict:
        """
        Obtém a lista de categorias do WordPress.
        
        Returns:
            dict: Lista de categorias
        """
        try:
            result = wordpress.get_categories()
            return result
        except Exception as e:
            print(f"Erro em wp_get_categories: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_get_tags() -> dict:
        """
        Obtém a lista de tags do WordPress.
        
        Returns:
            dict: Lista de tags
        """
        try:
            result = wordpress.get_tags()
            return result
        except Exception as e:
            print(f"Erro em wp_get_tags: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
        
    # Adicione estas ferramentas após as funções WordPress existentes no server_games.py

    @mcp.tool()
    def wp_update_page(
        page_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
        parent: Optional[int] = None,
        featured_media: Optional[int] = None
    ) -> dict:
        """
        Atualiza uma página existente no WordPress.
        
        Args:
            page_id: ID da página a ser atualizada
            title: Novo título da página (opcional)
            content: Novo conteúdo HTML da página (opcional)
            status: Novo status da página (draft, publish, pending, etc.) (opcional)
            parent: ID da página pai (opcional)
            featured_media: ID da mídia destacada (opcional)
            
        Returns:
            dict: Resposta da API do WordPress
        """
        try:
            import wordpress
            result = wordpress.update_page(
                page_id=page_id,
                title=title,
                content=content,
                status=status,
                parent=parent,
                featured_media=featured_media
            )
            return result
        except Exception as e:
            print(f"Erro em wp_update_page: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_update_post(
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
        categories: Optional[List[int]] = None,
        tags: Optional[List[int]] = None,
        featured_media: Optional[int] = None
    ) -> dict:
        """
        Atualiza um post existente no WordPress.
        
        Args:
            post_id: ID do post a ser atualizado
            title: Novo título do post (opcional)
            content: Novo conteúdo HTML do post (opcional)
            status: Novo status do post (draft, publish, pending, etc.) (opcional)
            categories: Nova lista de IDs de categorias (opcional)
            tags: Nova lista de IDs de tags (opcional)
            featured_media: Novo ID da mídia destacada (opcional)
            
        Returns:
            dict: Resposta da API do WordPress
        """
        try:
            import wordpress
            result = wordpress.update_post(
                post_id=post_id,
                title=title,
                content=content,
                status=status,
                categories=categories,
                tags=tags,
                featured_media=featured_media
            )
            return result
        except Exception as e:
            print(f"Erro em wp_update_post: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
        
        
        
    
    # Adicione estas funções de ferramenta ao arquivo server_games.py

    @mcp.tool()
    def wp_insert_paragraph(
        content_id: int,
        paragraph_text: str,
        position: str = "end",
        is_page: bool = False
    ) -> dict:
        """
        Insere um parágrafo em uma página ou post existente do WordPress.
        
        Args:
            content_id: ID da página ou post
            paragraph_text: Texto do parágrafo a ser inserido
            position: Posição onde inserir ('start', 'end', ou 'after:tag_id')
            is_page: Se True, atualiza uma página. Se False, atualiza um post.
            
        Returns:
            dict: Resultado da operação
        """
        try:
            import wordpress
            result = wordpress.insert_content_paragraph(
                content_id=content_id,
                paragraph_text=paragraph_text,
                position=position,
                is_page=is_page
            )
            return result
        except Exception as e:
            print(f"Erro em wp_insert_paragraph: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_insert_image(
        content_id: int,
        image_url: str,
        alt_text: str = "",
        caption: str = "",
        position: str = "end",
        is_page: bool = False
    ) -> dict:
        """
        Insere uma imagem em uma página ou post existente do WordPress.
        
        Args:
            content_id: ID da página ou post
            image_url: URL da imagem ou ID da mídia
            alt_text: Texto alternativo para a imagem
            caption: Legenda da imagem
            position: Posição onde inserir ('start', 'end', ou 'after:tag_id')
            is_page: Se True, atualiza uma página. Se False, atualiza um post.
            
        Returns:
            dict: Resultado da operação
        """
        try:
            import wordpress
            result = wordpress.insert_content_image(
                content_id=content_id,
                image_url=image_url,
                alt_text=alt_text,
                caption=caption,
                position=position,
                is_page=is_page
            )
            return result
        except Exception as e:
            print(f"Erro em wp_insert_image: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_insert_table(
        content_id: int,
        table_data: List[List[str]],
        has_header: bool = True,
        position: str = "end",
        is_page: bool = False
    ) -> dict:
        """
        Insere uma tabela em uma página ou post existente do WordPress.
        
        Args:
            content_id: ID da página ou post
            table_data: Dados da tabela (lista de linhas, cada linha é uma lista de células)
            has_header: Se True, a primeira linha é tratada como cabeçalho
            position: Posição onde inserir ('start', 'end', ou 'after:tag_id')
            is_page: Se True, atualiza uma página. Se False, atualiza um post.
            
        Returns:
            dict: Resultado da operação
        """
        try:
            import wordpress
            result = wordpress.insert_content_table(
                content_id=content_id,
                table_data=table_data,
                has_header=has_header,
                position=position,
                is_page=is_page
            )
            return result
        except Exception as e:
            print(f"Erro em wp_insert_table: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_insert_heading(
        content_id: int,
        heading_text: str,
        level: int = 2,
        position: str = "end",
        is_page: bool = False
    ) -> dict:
        """
        Insere um cabeçalho em uma página ou post existente do WordPress.
        
        Args:
            content_id: ID da página ou post
            heading_text: Texto do cabeçalho
            level: Nível do cabeçalho (1-6)
            position: Posição onde inserir ('start', 'end', ou 'after:tag_id')
            is_page: Se True, atualiza uma página. Se False, atualiza um post.
            
        Returns:
            dict: Resultado da operação
        """
        try:
            import wordpress
            result = wordpress.insert_content_heading(
                content_id=content_id,
                heading_text=heading_text,
                level=level,
                position=position,
                is_page=is_page
            )
            return result
        except Exception as e:
            print(f"Erro em wp_insert_heading: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_insert_list(
        content_id: int,
        list_items: List[str],
        list_type: str = "ul",
        position: str = "end",
        is_page: bool = False
    ) -> dict:
        """
        Insere uma lista em uma página ou post existente do WordPress.
        
        Args:
            content_id: ID da página ou post
            list_items: Itens da lista
            list_type: Tipo de lista ('ul' para não ordenada, 'ol' para ordenada)
            position: Posição onde inserir ('start', 'end', ou 'after:tag_id')
            is_page: Se True, atualiza uma página. Se False, atualiza um post.
            
        Returns:
            dict: Resultado da operação
        """
        try:
            import wordpress
            result = wordpress.insert_content_list(
                content_id=content_id,
                list_items=list_items,
                list_type=list_type,
                position=position,
                is_page=is_page
            )
            return result
        except Exception as e:
            print(f"Erro em wp_insert_list: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def wp_insert_html(
        content_id: int,
        html_content: str,
        position: str = "end",
        is_page: bool = False
    ) -> dict:
        """
        Insere HTML personalizado em uma página ou post existente do WordPress.
        
        Args:
            content_id: ID da página ou post
            html_content: Conteúdo HTML a ser inserido
            position: Posição onde inserir ('start', 'end', ou 'after:tag_id')
            is_page: Se True, atualiza uma página. Se False, atualiza um post.
            
        Returns:
            dict: Resultado da operação
        """
        try:
            import wordpress
            result = wordpress.insert_content_html(
                content_id=content_id,
                html_content=html_content,
                position=position,
                is_page=is_page
            )
            return result
        except Exception as e:
            print(f"Erro em wp_insert_html: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"success": False, "error": str(e)}
        
    
    # Não precisamos mais registrar ferramentas Twitch separadamente, pois já as implementamos diretamente
    
    if __name__ == "__main__":
        try:
            print("Iniciando MCP server para jogos...", file=sys.stderr)
            mcp.run()
        except Exception as e:
            print(f"Erro ao executar o servidor: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
except Exception as e:
    print(f"Erro global: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)