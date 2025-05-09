import requests
from requests.auth import HTTPBasicAuth
import urllib3
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Desativa o warning de certificado autoassinado (local)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carregar variáveis de ambiente
load_dotenv()

def get_wordpress_credentials():
    """
    Obtém credenciais do WordPress das variáveis de ambiente.
    
    Returns:
        dict: Credenciais do WordPress (url, username, password)
    """
    site_url = os.getenv("WORDPRESS_URL", "https://vgamescom.local")
    username = os.getenv("WORDPRESS_USERNAME", "vinicius")
    app_password = os.getenv("WORDPRESS_APP_PASSWORD", "nC43 23d3 qtxq NJo0 SDOx 3nCc")
    
    return {
        "site_url": site_url,
        "username": username,
        "app_password": app_password
    }

def create_post(title: str, content: str, status: str = "publish", 
                categories: Optional[List[int]] = None, 
                tags: Optional[List[int]] = None,
                featured_media: Optional[int] = None) -> Dict[str, Any]:
    """
    Cria um novo post no WordPress.
    
    Args:
        title (str): Título do post
        content (str): Conteúdo HTML do post
        status (str): Status do post (draft, publish, pending, etc.)
        categories (List[int], optional): Lista de IDs de categorias
        tags (List[int], optional): Lista de IDs de tags
        featured_media (int, optional): ID da mídia destacada
        
    Returns:
        dict: Resposta da API do WordPress
    """
    credentials = get_wordpress_credentials()
    
    auth = HTTPBasicAuth(credentials["username"], credentials["app_password"])
    headers = {
        "User-Agent": "MCP-WordPress-Client/1.0"
    }
    
    post_data = {
        "title": title,
        "content": content,
        "status": status
    }
    
    if categories:
        post_data["categories"] = categories
    
    if tags:
        post_data["tags"] = tags
        
    if featured_media:
        post_data["featured_media"] = featured_media
    
    try:
        response = requests.post(
            f"{credentials['site_url']}/wp-json/wp/v2/posts",
            auth=auth,
            headers=headers,
            json=post_data,
            verify=False
        )
        
        response.raise_for_status()  # Lança exceção para códigos de erro HTTP
        return {
            "success": True,
            "status_code": response.status_code,
            "post_data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def create_page(title: str, content: str, status: str = "publish",
                parent: Optional[int] = None,
                featured_media: Optional[int] = None) -> Dict[str, Any]:
    """
    Cria uma nova página no WordPress.
    
    Args:
        title (str): Título da página
        content (str): Conteúdo HTML da página
        status (str): Status da página (draft, publish, pending, etc.)
        parent (int, optional): ID da página pai (para páginas hierárquicas)
        featured_media (int, optional): ID da mídia destacada
        
    Returns:
        dict: Resposta da API do WordPress
    """
    credentials = get_wordpress_credentials()
    
    auth = HTTPBasicAuth(credentials["username"], credentials["app_password"])
    headers = {
        "User-Agent": "MCP-WordPress-Client/1.0"
    }
    
    page_data = {
        "title": title,
        "content": content,
        "status": status
    }
    
    if parent:
        page_data["parent"] = parent
        
    if featured_media:
        page_data["featured_media"] = featured_media
    
    try:
        response = requests.post(
            f"{credentials['site_url']}/wp-json/wp/v2/pages",
            auth=auth,
            headers=headers,
            json=page_data,
            verify=False
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "page_data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }




def update_page(page_id: int, title: Optional[str] = None, content: Optional[str] = None, 
             status: Optional[str] = None, parent: Optional[int] = None,
             featured_media: Optional[int] = None) -> Dict[str, Any]:
    """
    Atualiza uma página existente no WordPress.
    
    Args:
        page_id (int): ID da página a ser atualizada
        title (str, optional): Novo título da página
        content (str, optional): Novo conteúdo HTML da página
        status (str, optional): Novo status da página (draft, publish, pending, etc.)
        parent (int, optional): ID da página pai (para páginas hierárquicas)
        featured_media (int, optional): ID da mídia destacada
        
    Returns:
        dict: Resposta da API do WordPress
    """
    credentials = get_wordpress_credentials()
    
    auth = HTTPBasicAuth(credentials["username"], credentials["app_password"])
    headers = {
        "User-Agent": "MCP-WordPress-Client/1.0"
    }
    
    # Prepara os dados para atualização
    page_data = {}
    if title is not None:
        page_data["title"] = title
    if content is not None:
        page_data["content"] = content
    if status is not None:
        page_data["status"] = status
    if parent is not None:
        page_data["parent"] = parent
    if featured_media is not None:
        page_data["featured_media"] = featured_media
    
    # Verifica se há dados para atualizar
    if not page_data:
        return {
            "success": False,
            "error": "Nenhum dado fornecido para atualização"
        }
    
    try:
        response = requests.post(
            f"{credentials['site_url']}/wp-json/wp/v2/pages/{page_id}",
            auth=auth,
            headers=headers,
            json=page_data,
            verify=False
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "page_data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def update_post(post_id: int, title: Optional[str] = None, content: Optional[str] = None,
              status: Optional[str] = None, categories: Optional[List[int]] = None,
              tags: Optional[List[int]] = None, featured_media: Optional[int] = None) -> Dict[str, Any]:
    """
    Atualiza um post existente no WordPress.
    
    Args:
        post_id (int): ID do post a ser atualizado
        title (str, optional): Novo título do post
        content (str, optional): Novo conteúdo HTML do post
        status (str, optional): Novo status do post (draft, publish, pending, etc.)
        categories (List[int], optional): Nova lista de IDs de categorias
        tags (List[int], optional): Nova lista de IDs de tags
        featured_media (int, optional): Novo ID da mídia destacada
        
    Returns:
        dict: Resposta da API do WordPress
    """
    credentials = get_wordpress_credentials()
    
    auth = HTTPBasicAuth(credentials["username"], credentials["app_password"])
    headers = {
        "User-Agent": "MCP-WordPress-Client/1.0"
    }
    
    # Prepara os dados para atualização
    post_data = {}
    if title is not None:
        post_data["title"] = title
    if content is not None:
        post_data["content"] = content
    if status is not None:
        post_data["status"] = status
    if categories is not None:
        post_data["categories"] = categories
    if tags is not None:
        post_data["tags"] = tags
    if featured_media is not None:
        post_data["featured_media"] = featured_media
    
    # Verifica se há dados para atualizar
    if not post_data:
        return {
            "success": False,
            "error": "Nenhum dado fornecido para atualização"
        }
    
    try:
        response = requests.post(
            f"{credentials['site_url']}/wp-json/wp/v2/posts/{post_id}",
            auth=auth,
            headers=headers,
            json=post_data,
            verify=False
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "post_data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def upload_media(file_path: str, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Faz upload de um arquivo de mídia para a biblioteca de mídia do WordPress.
    
    Args:
        file_path (str): Caminho para o arquivo local
        title (str, optional): Título para a mídia
        
    Returns:
        dict: Resposta da API do WordPress
    """
    credentials = get_wordpress_credentials()
    
    auth = HTTPBasicAuth(credentials["username"], credentials["app_password"])
    
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Arquivo não encontrado: {file_path}"
            }
        
        # Prepara o nome do arquivo
        filename = os.path.basename(file_path)
        
        # Abre o arquivo em modo binário
        with open(file_path, "rb") as file:
            files = {
                'file': (filename, file)
            }
            
            headers = {
                "User-Agent": "MCP-WordPress-Client/1.0"
            }
            
            # Adiciona título se fornecido
            data = {}
            if title:
                data['title'] = title
            
            response = requests.post(
                f"{credentials['site_url']}/wp-json/wp/v2/media",
                auth=auth,
                headers=headers,
                files=files,
                data=data,
                verify=False
            )
            
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "media_data": response.json()
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def upload_media_from_url(image_url: str, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Faz upload de uma imagem a partir de uma URL para a biblioteca de mídia do WordPress.
    
    Args:
        image_url (str): URL da imagem
        title (str, optional): Título para a mídia
        
    Returns:
        dict: Resposta da API do WordPress
    """
    credentials = get_wordpress_credentials()
    
    auth = HTTPBasicAuth(credentials["username"], credentials["app_password"])
    
    try:
        # Baixa a imagem da URL
        image_response = requests.get(image_url, stream=True)
        image_response.raise_for_status()
        
        # Obtém o nome do arquivo da URL
        filename = os.path.basename(image_url)
        
        headers = {
            "User-Agent": "MCP-WordPress-Client/1.0",
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        
        # Adiciona título se fornecido
        data = {}
        if title:
            data['title'] = title
        
        response = requests.post(
            f"{credentials['site_url']}/wp-json/wp/v2/media",
            auth=auth,
            headers=headers,
            data=data,
            files={'file': (filename, image_response.content)},
            verify=False
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "media_data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_posts(per_page: int = 10, page: int = 1) -> Dict[str, Any]:
    """
    Obtém a lista de posts do WordPress.
    
    Args:
        per_page (int): Número de posts por página
        page (int): Número da página
        
    Returns:
        dict: Lista de posts
    """
    credentials = get_wordpress_credentials()
    
    try:
        response = requests.get(
            f"{credentials['site_url']}/wp-json/wp/v2/posts",
            params={
                "per_page": per_page,
                "page": page
            },
            verify=False
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "posts": response.json(),
            "total_posts": response.headers.get("X-WP-Total"),
            "total_pages": response.headers.get("X-WP-TotalPages")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_pages(per_page: int = 10, page: int = 1) -> Dict[str, Any]:
    """
    Obtém a lista de páginas do WordPress.
    
    Args:
        per_page (int): Número de páginas por página
        page (int): Número da página
        
    Returns:
        dict: Lista de páginas
    """
    credentials = get_wordpress_credentials()
    
    try:
        response = requests.get(
            f"{credentials['site_url']}/wp-json/wp/v2/pages",
            params={
                "per_page": per_page,
                "page": page
            },
            verify=False
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "pages": response.json(),
            "total_pages": response.headers.get("X-WP-Total"),
            "total_page_pages": response.headers.get("X-WP-TotalPages")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_categories() -> Dict[str, Any]:
    """
    Obtém a lista de categorias do WordPress.
    
    Returns:
        dict: Lista de categorias
    """
    credentials = get_wordpress_credentials()
    
    try:
        response = requests.get(
            f"{credentials['site_url']}/wp-json/wp/v2/categories",
            params={
                "per_page": 100
            },
            verify=False
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "categories": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_tags() -> Dict[str, Any]:
    """
    Obtém a lista de tags do WordPress.
    
    Returns:
        dict: Lista de tags
    """
    credentials = get_wordpress_credentials()
    
    try:
        response = requests.get(
            f"{credentials['site_url']}/wp-json/wp/v2/tags",
            params={
                "per_page": 100
            },
            verify=False
        )
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "tags": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
        
        
        import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List, Tuple, Union

def get_wordpress_content(post_id: int, is_page: bool = False) -> Tuple[bool, Union[str, Dict]]:
    """
    Obtém o conteúdo atual de uma página ou post WordPress.
    
    Args:
        post_id (int): ID da página ou post
        is_page (bool): Se True, busca uma página. Se False, busca um post.
        
    Returns:
        Tuple[bool, Union[str, Dict]]: (sucesso, conteúdo ou erro)
    """
    credentials = get_wordpress_credentials()
    
    auth = HTTPBasicAuth(credentials["username"], credentials["app_password"])
    content_type = "pages" if is_page else "posts"
    
    try:
        response = requests.get(
            f"{credentials['site_url']}/wp-json/wp/v2/{content_type}/{post_id}",
            auth=auth,
            verify=False
        )
        
        response.raise_for_status()
        post_data = response.json()
        return True, post_data.get("content", {}).get("rendered", "")
    except Exception as e:
        return False, {"error": str(e)}

def insert_content_paragraph(content_id: int, paragraph_text: str, 
                             position: str = "end", is_page: bool = False) -> Dict[str, Any]:
    """
    Insere um parágrafo em uma página ou post existente.
    
    Args:
        content_id (int): ID da página ou post
        paragraph_text (str): Texto do parágrafo a ser inserido
        position (str): Posição onde inserir ('start', 'end', ou 'after:tag_id')
        is_page (bool): Se True, atualiza uma página. Se False, atualiza um post.
        
    Returns:
        dict: Resultado da operação
    """
    # Obter conteúdo atual
    success, content = get_wordpress_content(content_id, is_page)
    if not success:
        return content  # Retorna o erro
    
    # Formatar o parágrafo
    paragraph_html = f"<p>{paragraph_text}</p>"
    
    # Inserir o parágrafo na posição especificada
    new_content = _insert_at_position(content, paragraph_html, position)
    
    # Atualizar o conteúdo
    if is_page:
        return update_page(content_id, content=new_content)
    else:
        return update_post(content_id, content=new_content)

def insert_content_image(content_id: int, image_url: str, alt_text: str = "", 
                         caption: str = "", position: str = "end", 
                         is_page: bool = False) -> Dict[str, Any]:
    """
    Insere uma imagem em uma página ou post existente.
    
    Args:
        content_id (int): ID da página ou post
        image_url (str): URL da imagem ou ID da mídia
        alt_text (str): Texto alternativo para a imagem
        caption (str): Legenda da imagem
        position (str): Posição onde inserir ('start', 'end', ou 'after:tag_id')
        is_page (bool): Se True, atualiza uma página. Se False, atualiza um post.
        
    Returns:
        dict: Resultado da operação
    """
    # Obter conteúdo atual
    success, content = get_wordpress_content(content_id, is_page)
    if not success:
        return content  # Retorna o erro
    
    # Se for um ID de mídia ao invés de URL
    if str(image_url).isdigit():
        image_html = f'<!-- wp:image {{"id":{image_url}}} -->'
        if caption:
            image_html += f'<figure class="wp-block-image"><img src="" alt="{alt_text}" class="wp-image-{image_url}"/><figcaption>{caption}</figcaption></figure>'
        else:
            image_html += f'<figure class="wp-block-image"><img src="" alt="{alt_text}" class="wp-image-{image_url}"/></figure>'
        image_html += '<!-- /wp:image -->'
    else:
        # Formatar a imagem
        if caption:
            image_html = f'<figure class="wp-block-image"><img src="{image_url}" alt="{alt_text}" /><figcaption>{caption}</figcaption></figure>'
        else:
            image_html = f'<figure class="wp-block-image"><img src="{image_url}" alt="{alt_text}" /></figure>'
    
    # Inserir a imagem na posição especificada
    new_content = _insert_at_position(content, image_html, position)
    
    # Atualizar o conteúdo
    if is_page:
        return update_page(content_id, content=new_content)
    else:
        return update_post(content_id, content=new_content)

def insert_content_table(content_id: int, table_data: List[List[str]], 
                         has_header: bool = True, position: str = "end", 
                         is_page: bool = False) -> Dict[str, Any]:
    """
    Insere uma tabela em uma página ou post existente.
    
    Args:
        content_id (int): ID da página ou post
        table_data (List[List[str]]): Dados da tabela (lista de linhas, cada linha é uma lista de células)
        has_header (bool): Se True, a primeira linha é tratada como cabeçalho
        position (str): Posição onde inserir ('start', 'end', ou 'after:tag_id')
        is_page (bool): Se True, atualiza uma página. Se False, atualiza um post.
        
    Returns:
        dict: Resultado da operação
    """
    # Obter conteúdo atual
    success, content = get_wordpress_content(content_id, is_page)
    if not success:
        return content  # Retorna o erro
    
    # Construir o HTML da tabela
    table_html = '<table class="wp-block-table"><tbody>'
    
    for i, row in enumerate(table_data):
        if i == 0 and has_header:
            table_html += '<thead><tr>'
            for cell in row:
                table_html += f'<th>{cell}</th>'
            table_html += '</tr></thead><tbody>'
        else:
            table_html += '<tr>'
            for cell in row:
                table_html += f'<td>{cell}</td>'
            table_html += '</tr>'
    
    table_html += '</tbody></table>'
    
    # Inserir a tabela na posição especificada
    new_content = _insert_at_position(content, table_html, position)
    
    # Atualizar o conteúdo
    if is_page:
        return update_page(content_id, content=new_content)
    else:
        return update_post(content_id, content=new_content)

def insert_content_heading(content_id: int, heading_text: str, level: int = 2, 
                           position: str = "end", is_page: bool = False) -> Dict[str, Any]:
    """
    Insere um cabeçalho em uma página ou post existente.
    
    Args:
        content_id (int): ID da página ou post
        heading_text (str): Texto do cabeçalho
        level (int): Nível do cabeçalho (1-6)
        position (str): Posição onde inserir ('start', 'end', ou 'after:tag_id')
        is_page (bool): Se True, atualiza uma página. Se False, atualiza um post.
        
    Returns:
        dict: Resultado da operação
    """
    # Validar o nível do cabeçalho
    if level < 1 or level > 6:
        return {"success": False, "error": "Nível de cabeçalho deve estar entre 1 e 6"}
    
    # Obter conteúdo atual
    success, content = get_wordpress_content(content_id, is_page)
    if not success:
        return content  # Retorna o erro
    
    # Formatar o cabeçalho
    heading_html = f'<h{level}>{heading_text}</h{level}>'
    
    # Inserir o cabeçalho na posição especificada
    new_content = _insert_at_position(content, heading_html, position)
    
    # Atualizar o conteúdo
    if is_page:
        return update_page(content_id, content=new_content)
    else:
        return update_post(content_id, content=new_content)

def insert_content_list(content_id: int, list_items: List[str], list_type: str = "ul", 
                        position: str = "end", is_page: bool = False) -> Dict[str, Any]:
    """
    Insere uma lista em uma página ou post existente.
    
    Args:
        content_id (int): ID da página ou post
        list_items (List[str]): Itens da lista
        list_type (str): Tipo de lista ('ul' para não ordenada, 'ol' para ordenada)
        position (str): Posição onde inserir ('start', 'end', ou 'after:tag_id')
        is_page (bool): Se True, atualiza uma página. Se False, atualiza um post.
        
    Returns:
        dict: Resultado da operação
    """
    # Validar o tipo de lista
    if list_type not in ['ul', 'ol']:
        return {"success": False, "error": "Tipo de lista deve ser 'ul' ou 'ol'"}
    
    # Obter conteúdo atual
    success, content = get_wordpress_content(content_id, is_page)
    if not success:
        return content  # Retorna o erro
    
    # Formatar a lista
    list_html = f'<{list_type}>'
    for item in list_items:
        list_html += f'<li>{item}</li>'
    list_html += f'</{list_type}>'
    
    # Inserir a lista na posição especificada
    new_content = _insert_at_position(content, list_html, position)
    
    # Atualizar o conteúdo
    if is_page:
        return update_page(content_id, content=new_content)
    else:
        return update_post(content_id, content=new_content)

def insert_content_quote(content_id: int, quote_text: str, citation: str = "", 
                         position: str = "end", is_page: bool = False) -> Dict[str, Any]:
    """
    Insere uma citação em uma página ou post existente.
    
    Args:
        content_id (int): ID da página ou post
        quote_text (str): Texto da citação
        citation (str): Fonte da citação
        position (str): Posição onde inserir ('start', 'end', ou 'after:tag_id')
        is_page (bool): Se True, atualiza uma página. Se False, atualiza um post.
        
    Returns:
        dict: Resultado da operação
    """
    # Obter conteúdo atual
    success, content = get_wordpress_content(content_id, is_page)
    if not success:
        return content  # Retorna o erro
    
    # Formatar a citação
    quote_html = f'<blockquote class="wp-block-quote"><p>{quote_text}</p>'
    if citation:
        quote_html += f'<cite>{citation}</cite>'
    quote_html += '</blockquote>'
    
    # Inserir a citação na posição especificada
    new_content = _insert_at_position(content, quote_html, position)
    
    # Atualizar o conteúdo
    if is_page:
        return update_page(content_id, content=new_content)
    else:
        return update_post(content_id, content=new_content)

def insert_content_code(content_id: int, code: str, language: str = "", 
                        position: str = "end", is_page: bool = False) -> Dict[str, Any]:
    """
    Insere um bloco de código em uma página ou post existente.
    
    Args:
        content_id (int): ID da página ou post
        code (str): Código a ser inserido
        language (str): Linguagem do código (para destacar sintaxe)
        position (str): Posição onde inserir ('start', 'end', ou 'after:tag_id')
        is_page (bool): Se True, atualiza uma página. Se False, atualiza um post.
        
    Returns:
        dict: Resultado da operação
    """
    # Obter conteúdo atual
    success, content = get_wordpress_content(content_id, is_page)
    if not success:
        return content  # Retorna o erro
    
    # Formatar o bloco de código
    language_class = f' class="language-{language}"' if language else ''
    code_html = f'<pre><code{language_class}>{code}</code></pre>'
    
    # Inserir o código na posição especificada
    new_content = _insert_at_position(content, code_html, position)
    
    # Atualizar o conteúdo
    if is_page:
        return update_page(content_id, content=new_content)
    else:
        return update_post(content_id, content=new_content)

def insert_content_html(content_id: int, html_content: str, 
                        position: str = "end", is_page: bool = False) -> Dict[str, Any]:
    """
    Insere HTML personalizado em uma página ou post existente.
    
    Args:
        content_id (int): ID da página ou post
        html_content (str): Conteúdo HTML a ser inserido
        position (str): Posição onde inserir ('start', 'end', ou 'after:tag_id')
        is_page (bool): Se True, atualiza uma página. Se False, atualiza um post.
        
    Returns:
        dict: Resultado da operação
    """
    # Obter conteúdo atual
    success, content = get_wordpress_content(content_id, is_page)
    if not success:
        return content  # Retorna o erro
    
    # Inserir o HTML na posição especificada
    new_content = _insert_at_position(content, html_content, position)
    
    # Atualizar o conteúdo
    if is_page:
        return update_page(content_id, content=new_content)
    else:
        return update_post(content_id, content=new_content)

def _insert_at_position(content: str, new_html: str, position: str) -> str:
    """
    Insere conteúdo HTML em uma posição específica.
    
    Args:
        content (str): Conteúdo HTML atual
        new_html (str): Novo HTML a ser inserido
        position (str): Posição onde inserir ('start', 'end', ou 'after:id')
        
    Returns:
        str: Conteúdo HTML atualizado
    """
    # Se o conteúdo estiver vazio, apenas retorne o novo HTML
    if not content or content.strip() == "":
        return new_html
    
    # Inserir no início
    if position.lower() == "start":
        return new_html + content
    
    # Inserir no final (padrão)
    if position.lower() == "end" or not position:
        return content + new_html
    
    # Inserir após um elemento específico (by ID)
    if position.lower().startswith("after:"):
        element_id = position[6:]  # Remove 'after:'
        soup = BeautifulSoup(content, 'html.parser')
        target_element = soup.find(id=element_id)
        
        if target_element:
            # Criar novo elemento com BeautifulSoup
            new_soup = BeautifulSoup(new_html, 'html.parser')
            
            # Inserir após o elemento alvo
            target_element.insert_after(new_soup)
            return str(soup)
        else:
            # Se não encontrar o ID, insere no final
            return content + new_html
    
    # Inserir após um padrão de texto (menos confiável)
    if position.lower().startswith("aftertext:"):
        search_text = position[10:]  # Remove 'aftertext:'
        parts = content.split(search_text, 1)
        
        if len(parts) > 1:
            return parts[0] + search_text + new_html + parts[1]
        else:
            # Se não encontrar o texto, insere no final
            return content + new_html
    
    # Para qualquer outra posição desconhecida, insere no final
    return content + new_html