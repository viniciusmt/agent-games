import requests
import pandas as pd
import os
from time import sleep
from dotenv import load_dotenv

def get_access_token(client_id, client_secret, region="us"):
    """
    Autentica com a API da Blizzard e retorna o token de acesso.
    
    Args:
        client_id (str): ID do cliente da API Blizzard
        client_secret (str): Segredo do cliente da API Blizzard
        region (str): Região da API (padrão: "us")
        
    Returns:
        str: Token de acesso
    """
    url = f"https://{region}.battle.net/oauth/token"
    try:
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(client_id, client_secret))
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Erro ao obter token de acesso: {e}")
        raise Exception(f"Erro na autenticação com a API da Blizzard: {e}")

def get_character_data(region, realm_slug, character_name, token):
    """
    Obtém dados básicos de um personagem.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        realm_slug (str): Slug do reino
        character_name (str): Nome do personagem
        token (str): Token de acesso
        
    Returns:
        dict: Informações básicas do personagem
    """
    url = f"https://{region}.api.blizzard.com/profile/wow/character/{realm_slug}/{character_name.lower()}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"profile-{region}", "locale": "en_US"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "Character Name": data.get("name"),
            "Realm": data.get("realm", {}).get("name"),
            "Level": data.get("level"),
            "Gender": data.get("gender", {}).get("name"),
            "Faction": data.get("faction", {}).get("name"),
            "Race": data.get("race", {}).get("name"),
            "Class": data.get("character_class", {}).get("name"),
            "Specialization": data.get("active_spec", {}).get("name"),
            "Title": data.get("active_title", {}).get("name", ""),
            "Achievement Points": data.get("achievement_points", 0),
            "Average Item Level": data.get("average_item_level", 0),
            "Equipped Item Level": data.get("equipped_item_level", 0),
            "Last Login": data.get("last_login_timestamp"),
            "Guild Name": data.get("guild", {}).get("name", "N/A"),
            "Realm Slug": realm_slug
        }
    except Exception as e:
        print(f"Erro ao obter dados do personagem {character_name}: {e}")
        return None

def get_character_statistics(region, realm_slug, character_name, token):
    """
    Obtém estatísticas de um personagem.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        realm_slug (str): Slug do reino
        character_name (str): Nome do personagem
        token (str): Token de acesso
        
    Returns:
        dict: Estatísticas do personagem
    """
    url = f"https://{region}.api.blizzard.com/profile/wow/character/{realm_slug}/{character_name.lower()}/statistics"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"profile-{region}", "locale": "en_US"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "Health": data.get("health", 0),
            "Power": data.get("power", 0),
            "Power Type": data.get("power_type", {}).get("name", "N/A"),
            "Strength": data.get("strength", {}).get("effective", 0),
            "Agility": data.get("agility", {}).get("effective", 0),
            "Intellect": data.get("intellect", {}).get("effective", 0),
            "Stamina": data.get("stamina", {}).get("effective", 0),
            "Armor": data.get("armor", {}).get("effective", 0),
            "Versatility": data.get("versatility", 0),
            "Melee Crit": data.get("melee_crit", {}).get("value", 0),
            "Melee Haste": data.get("melee_haste", {}).get("value", 0),
            "Mastery": data.get("mastery", {}).get("value", 0),
            "Spell Power": data.get("spell_power", 0),
            "Spell Crit": data.get("spell_crit", {}).get("value", 0),
            "Dodge": data.get("dodge", {}).get("value", 0),
            "Parry": data.get("parry", {}).get("value", 0),
            "Block": data.get("block", {}).get("value", 0)
        }
    except Exception as e:
        print(f"Erro ao obter estatísticas do personagem {character_name}: {e}")
        return {}

def get_character_equipment(region, realm_slug, character_name, token):
    """
    Obtém equipamentos de um personagem.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        realm_slug (str): Slug do reino
        character_name (str): Nome do personagem
        token (str): Token de acesso
        
    Returns:
        list: Lista de equipamentos do personagem
    """
    url = f"https://{region}.api.blizzard.com/profile/wow/character/{realm_slug}/{character_name.lower()}/equipment"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"profile-{region}", "locale": "en_US"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        equipment_list = []
        for item in data.get("equipped_items", []):
            equipment_list.append({
                "Name": item.get("name"),
                "Slot": item.get("slot", {}).get("name"),
                "Item Level": item.get("level", {}).get("value"),
                "Quality": item.get("quality", {}).get("name"),
                "Item ID": item.get("item", {}).get("id")
            })
        
        return equipment_list
    except Exception as e:
        print(f"Erro ao obter equipamentos do personagem {character_name}: {e}")
        return []

def get_character_achievements(region, realm_slug, character_name, token, max_achievements=50):
    """
    Obtém conquistas de um personagem.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        realm_slug (str): Slug do reino
        character_name (str): Nome do personagem
        token (str): Token de acesso
        max_achievements (int): Número máximo de conquistas a retornar
        
    Returns:
        list: Lista de conquistas do personagem
    """
    url = f"https://{region}.api.blizzard.com/profile/wow/character/{realm_slug}/{character_name.lower()}/achievements"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"profile-{region}", "locale": "en_US"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        achievements_list = []
        for achievement in data.get("achievements", [])[:max_achievements]:
            achievements_list.append({
                "ID": achievement.get("id"),
                "Name": achievement.get("achievement", {}).get("name"),
                "Description": achievement.get("achievement", {}).get("description"),
                "Completed Timestamp": achievement.get("completed_timestamp"),
                "Points": achievement.get("achievement", {}).get("points", 0)
            })
        
        return achievements_list
    except Exception as e:
        print(f"Erro ao obter conquistas do personagem {character_name}: {e}")
        return []

def get_guild_data(region, realm_slug, guild_name, token):
    """
    Obtém informações sobre uma guilda.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        realm_slug (str): Slug do reino
        guild_name (str): Nome da guilda
        token (str): Token de acesso
        
    Returns:
        dict: Informações sobre a guilda
    """
    url = f"https://{region}.api.blizzard.com/data/wow/guild/{realm_slug}/{guild_name.lower()}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"profile-{region}", "locale": "en_US"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "Guild Name": data.get("name"),
            "Realm": data.get("realm", {}).get("name"),
            "Faction": data.get("faction", {}).get("name"),
            "Created Timestamp": data.get("created_timestamp"),
            "Achievement Points": data.get("achievement_points", 0),
            "Member Count": data.get("member_count", 0)
        }
    except Exception as e:
        print(f"Erro ao obter dados da guilda {guild_name}: {e}")
        return None

def get_guild_members(region, realm_slug, guild_name, token):
    """
    Obtém lista de membros de uma guilda.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        realm_slug (str): Slug do reino
        guild_name (str): Nome da guilda
        token (str): Token de acesso
        
    Returns:
        list: Lista de membros da guilda
    """
    url = f"https://{region}.api.blizzard.com/data/wow/guild/{realm_slug}/{guild_name.lower()}/roster"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"profile-{region}", "locale": "en_US"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        members_list = []
        for member in data.get("members", []):
            character = member.get("character", {})
            members_list.append({
                "Name": character.get("name"),
                "Realm": character.get("realm", {}).get("name"),
                "Level": character.get("level"),
                "Class": character.get("playable_class", {}).get("name"),
                "Race": character.get("playable_race", {}).get("name"),
                "Rank": member.get("rank", 0)
            })
        
        return members_list
    except Exception as e:
        print(f"Erro ao obter membros da guilda {guild_name}: {e}")
        return []

def get_auction_house_data(region, connected_realm_id, token, categories=None, limit=100):
    """
    Obtém dados do leilão (mercado) de um reino conectado.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        connected_realm_id (int): ID do reino conectado
        token (str): Token de acesso
        categories (list): Lista de IDs de categorias para filtrar (opcional)
        limit (int): Limite de resultados
        
    Returns:
        list: Lista de itens do leilão
    """
    url = f"https://{region}.api.blizzard.com/data/wow/connected-realm/{connected_realm_id}/auctions"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"dynamic-{region}", "locale": "en_US"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        auctions = data.get("auctions", [])
        
        # Filtra por categorias se especificado
        if categories:
            filtered_auctions = [a for a in auctions if a.get("item", {}).get("id") in categories]
            auctions = filtered_auctions
        
        # Limita o número de resultados
        auctions = auctions[:limit]
        
        auction_list = []
        for auction in auctions:
            price = auction.get("price") / 10000  # Convertendo de copper para gold
            auction_list.append({
                "Item ID": auction.get("item", {}).get("id"),
                "Item Name": auction.get("item", {}).get("name", "Unknown"),
                "Quantity": auction.get("quantity", 1),
                "Price (Gold)": price,
                "Time Left": auction.get("time_left")
            })
        
        return auction_list
    except Exception as e:
        print(f"Erro ao obter dados do leilão para o reino {connected_realm_id}: {e}")
        return []

def get_item_data(region, item_id, token):
    """
    Obtém dados de um item específico.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        item_id (int): ID do item
        token (str): Token de acesso
        
    Returns:
        dict: Informações sobre o item
    """
    url = f"https://{region}.api.blizzard.com/data/wow/item/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"static-{region}", "locale": "en_US"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "Item ID": data.get("id"),
            "Name": data.get("name"),
            "Quality": data.get("quality", {}).get("name"),
            "Level": data.get("level"),
            "Required Level": data.get("required_level"),
            "Item Class": data.get("item_class", {}).get("name"),
            "Item Subclass": data.get("item_subclass", {}).get("name"),
            "Inventory Type": data.get("inventory_type", {}).get("name"),
            "Purchase Price": data.get("purchase_price", 0) / 10000,  # Convertendo para gold
            "Sell Price": data.get("sell_price", 0) / 10000,  # Convertendo para gold
            "Is Equippable": data.get("is_equippable", False),
            "Is Stackable": data.get("is_stackable", False)
        }
    except Exception as e:
        print(f"Erro ao obter dados do item {item_id}: {e}")
        return None

def get_connected_realm_id(region, realm_name, token):
    """
    Obtém o ID do reino conectado para um dado nome de reino.
    
    Args:
        region (str): Região do servidor (us, eu, etc.)
        realm_name (str): Nome do reino
        token (str): Token de acesso
        
    Returns:
        int: ID do reino conectado
    """
    url = f"https://{region}.api.blizzard.com/data/wow/search/connected-realm"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "namespace": f"dynamic-{region}",
        "locale": "en_US",
        "_page": 1,
        "_pageSize": 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        for result in data.get("results", []):
            realms = result.get("data", {}).get("realms", [])
            for realm in realms:
                if realm.get("name", {}).get("en_US", "").lower() == realm_name.lower():
                    return result.get("data", {}).get("id")
        
        # Se não encontrou, tenta buscar pelo slug
        for result in data.get("results", []):
            realms = result.get("data", {}).get("realms", [])
            for realm in realms:
                if realm.get("slug", "").lower() == realm_name.lower():
                    return result.get("data", {}).get("id")
        
        print(f"Não foi possível encontrar o ID do reino conectado para {realm_name}")
        return None
    except Exception as e:
        print(f"Erro ao buscar ID do reino conectado para {realm_name}: {e}")
        return None

def get_complete_character_info(client_id, client_secret, region, realm, character_name):
    """
    Obtém informações completas de um personagem (perfil, estatísticas, equipamentos e conquistas).
    
    Args:
        client_id (str): ID do cliente da API Blizzard
        client_secret (str): Segredo do cliente da API Blizzard
        region (str): Região do servidor (us, eu, etc.)
        realm (str): Nome do reino
        character_name (str): Nome do personagem
        
    Returns:
        dict: Informações completas do personagem
    """
    try:
        token = get_access_token(client_id, client_secret, region)
        
        # Obter dados básicos do personagem
        character_info = get_character_data(region, realm, character_name, token)
        if not character_info:
            return {"success": False, "error": f"Personagem {character_name}@{realm} não encontrado"}
        
        # Obter estatísticas
        stats = get_character_statistics(region, realm, character_name, token)
        
        # Obter equipamentos
        equipment = get_character_equipment(region, realm, character_name, token)
        
        # Obter conquistas
        achievements = get_character_achievements(region, realm, character_name, token, max_achievements=20)
        
        return {
            "success": True,
            "data": {
                "profile": character_info,
                "statistics": stats,
                "equipment": equipment,
                "achievements": achievements
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_guild_info(client_id, client_secret, region, realm, guild_name):
    """
    Obtém informações completas de uma guilda (perfil e membros).
    
    Args:
        client_id (str): ID do cliente da API Blizzard
        client_secret (str): Segredo do cliente da API Blizzard
        region (str): Região do servidor (us, eu, etc.)
        realm (str): Nome do reino
        guild_name (str): Nome da guilda
        
    Returns:
        dict: Informações completas da guilda
    """
    try:
        token = get_access_token(client_id, client_secret, region)
        
        # Obter dados da guilda
        guild_info = get_guild_data(region, realm, guild_name, token)
        if not guild_info:
            return {"success": False, "error": f"Guilda {guild_name}@{realm} não encontrada"}
        
        # Obter membros da guilda
        members = get_guild_members(region, realm, guild_name, token)
        
        return {
            "success": True,
            "data": {
                "guild_info": guild_info,
                "members": members
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_auction_data(client_id, client_secret, region, realm, limit=100):
    """
    Obtém dados do leilão (mercado) para um reino.
    
    Args:
        client_id (str): ID do cliente da API Blizzard
        client_secret (str): Segredo do cliente da API Blizzard
        region (str): Região do servidor (us, eu, etc.)
        realm (str): Nome do reino
        limit (int): Limite de resultados
        
    Returns:
        dict: Dados do leilão
    """
    try:
        token = get_access_token(client_id, client_secret, region)
        
        # Obter ID do reino conectado
        connected_realm_id = get_connected_realm_id(region, realm, token)
        if not connected_realm_id:
            return {"success": False, "error": f"Não foi possível encontrar o reino {realm}"}
        
        # Obter dados do leilão
        auctions = get_auction_house_data(region, connected_realm_id, token, limit=limit)
        
        # Adicionar detalhes dos itens para os primeiros 10 itens (para não sobrecarregar a API)
        detailed_items = []
        for auction in auctions[:10]:
            item_id = auction.get("Item ID")
            item_details = get_item_data(region, item_id, token)
            if item_details:
                auction["Item Details"] = item_details
                detailed_items.append(auction)
        
        return {
            "success": True,
            "data": {
                "auctions": auctions,
                "detailed_items": detailed_items
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_characters(client_id, client_secret, region, realm, names):
    """
    Pesquisa múltiplos personagens.
    
    Args:
        client_id (str): ID do cliente da API Blizzard
        client_secret (str): Segredo do cliente da API Blizzard
        region (str): Região do servidor (us, eu, etc.)
        realm (str): Nome do reino
        names (list): Lista de nomes de personagens
        
    Returns:
        dict: Informações dos personagens
    """
    try:
        token = get_access_token(client_id, client_secret, region)
        
        results = []
        for name in names:
            character_info = get_character_data(region, realm, name, token)
            if character_info:
                results.append(character_info)
            sleep(0.5)  # Para evitar rate limiting
        
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_guilds(client_id, client_secret, region, realm, guild_names):
    """
    Pesquisa múltiplas guildas.
    
    Args:
        client_id (str): ID do cliente da API Blizzard
        client_secret (str): Segredo do cliente da API Blizzard
        region (str): Região do servidor (us, eu, etc.)
        realm (str): Nome do reino
        guild_names (list): Lista de nomes de guildas
        
    Returns:
        dict: Informações das guildas
    """
    try:
        token = get_access_token(client_id, client_secret, region)
        
        results = []
        for name in guild_names:
            guild_info = get_guild_data(region, realm, name, token)
            if guild_info:
                # Obter apenas o número de membros, não a lista completa
                members_count = guild_info.get("Member Count", 0)
                guild_info["Members Count"] = members_count
                results.append(guild_info)
            sleep(0.5)  # Para evitar rate limiting
        
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}