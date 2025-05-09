# simple_discord_mcp.py
import os
import sys
import json
import traceback
from mcp.server.fastmcp import FastMCP
from discord_api import DiscordAPI

# Inicializa o FastMCP
mcp = FastMCP("discord-simple")

# Obtém o token do Discord das variáveis de ambiente
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    print("ERRO: DISCORD_TOKEN não encontrado nas variáveis de ambiente!", file=sys.stderr)
    sys.exit(1)

# Inicializa a API do Discord
discord_api = DiscordAPI(DISCORD_TOKEN)

@mcp.tool()
def send_discord_message(channel_id: str, content: str) -> dict:
    """
    Envia uma mensagem para um canal específico do Discord.
    
    Args:
        channel_id: ID do canal do Discord
        content: Conteúdo da mensagem
        
    Returns:
        dict: Resultado da operação
    """
    try:
        result = discord_api.send_message(channel_id, content)
        if "error" in result:
            return {"success": False, "error": result["error"]}
        return {"success": True, "message": "Mensagem enviada com sucesso"}
    except Exception as e:
        print(f"Erro em send_discord_message: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_discord_messages(channel_id: str, limit: int = 10) -> dict:
    """
    Obtém as mensagens recentes de um canal do Discord.
    
    Args:
        channel_id: ID do canal do Discord
        limit: Número máximo de mensagens a obter (padrão: 10)
        
    Returns:
        dict: Mensagens do canal
    """
    try:
        result = discord_api.get_channel_messages(channel_id, limit)
        if isinstance(result, dict) and "error" in result:
            return {"success": False, "error": result["error"]}
        
        # Simplificar as mensagens para retornar apenas os dados importantes
        simplified_messages = []
        for msg in result:
            simplified_messages.append({
                "id": msg.get("id"),
                "content": msg.get("content"),
                "author": {
                    "id": msg.get("author", {}).get("id"),
                    "username": msg.get("author", {}).get("username"),
                    "bot": msg.get("author", {}).get("bot", False)
                },
                "timestamp": msg.get("timestamp")
            })
        
        return {"success": True, "messages": simplified_messages}
    except Exception as e:
        print(f"Erro em get_discord_messages: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_discord_channels(guild_id: str) -> dict:
    """
    Obtém os canais de um servidor do Discord.
    
    Args:
        guild_id: ID do servidor do Discord
        
    Returns:
        dict: Canais do servidor
    """
    try:
        result = discord_api.get_guild_channels(guild_id)
        if isinstance(result, dict) and "error" in result:
            return {"success": False, "error": result["error"]}
        
        # Simplificar os canais para retornar apenas os dados importantes
        simplified_channels = []
        for channel in result:
            simplified_channels.append({
                "id": channel.get("id"),
                "name": channel.get("name"),
                "type": channel.get("type"),
                "parent_id": channel.get("parent_id")
            })
        
        return {"success": True, "channels": simplified_channels}
    except Exception as e:
        print(f"Erro em get_discord_channels: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    try:
        print("Iniciando servidor MCP simples para Discord...", file=sys.stderr)
        mcp.run()
    except Exception as e:
        print(f"Erro ao executar o servidor: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)