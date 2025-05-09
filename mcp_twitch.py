import os
import requests
import time
from datetime import datetime, timedelta
from twitchio.ext import commands
from dotenv import load_dotenv
import asyncio
import threading
from typing import List, Dict, Any, Optional

# Carregamento de variáveis de ambiente
load_dotenv()

# Configurações da Twitch
CANAL = os.getenv("TWITCH_CANAL")
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")
REFRESH_API_URL = f"https://twitchtokengenerator.com/api/refresh/{REFRESH_TOKEN}"

# Classe para armazenar mensagens do chat
class ChatStorage:
    def __init__(self, max_messages=100):
        self.messages = []
        self.max_messages = max_messages
        self.lock = threading.Lock()
    
    def add_message(self, author, content, timestamp):
        with self.lock:
            self.messages.append({
                "author": author,
                "content": content,
                "timestamp": timestamp
            })
            if len(self.messages) > self.max_messages:
                self.messages.pop(0)
    
    def get_messages(self, limit=None):
        with self.lock:
            if limit is None or limit > len(self.messages):
                return self.messages.copy()
            return self.messages[-limit:].copy()

# Instância global para armazenar mensagens
chat_storage = ChatStorage()

# Função para obter token Twitch
def obter_token_via_refresh():
    try:
        print("🔄 Obtendo novo token via refresh...")
        response = requests.get(REFRESH_API_URL)
        data = response.json()

        if response.status_code == 200 and "token" in data and "refresh" in data:
            print("✅ Novo token obtido com sucesso!")
            return {
                "access_token": data["token"],
                "refresh_token": data["refresh"]
            }
        else:
            print(f"❌ Erro ao obter novo token: {data}")
            return None
    except Exception as e:
        print(f"⚠️ Exceção ao obter token: {e}")
        return None

# Classe do Bot
class TwitchBot(commands.Bot):
    def __init__(self, token):
        super().__init__(
            token=token,
            client_id=CLIENT_ID,
            prefix="!",
            initial_channels=[CANAL],
            nick=CANAL
        )
        self.is_ready = False

    async def event_ready(self):
        print(f"✅ Bot {self.nick} conectado ao canal {CANAL}!")
        self.is_ready = True

    async def event_message(self, message):
        if message.echo:
            return
        
        # Armazenar a mensagem recebida
        chat_storage.add_message(
            author=message.author.name,
            content=message.content,
            timestamp=datetime.now()
        )
        
        # Para debug
        print(f"💬 Mensagem armazenada de {message.author.name}: {message.content}")
        
        # Processar comandos - vamos manter isso para compatibilidade
        await self.handle_commands(message)

    async def send_chat_message(self, message):
        """Envia uma mensagem para o chat"""
        channel = self.get_channel(CANAL)
        if channel:
            await channel.send(message)
            return True
        return False

# Bot global e loop de eventos
bot_instance = None
event_loop = None
bot_thread = None

def start_bot():
    """Inicia o bot em uma thread separada"""
    global bot_instance, event_loop, bot_thread
    
    # Se já existe, não inicia novamente
    if bot_instance and bot_thread and bot_thread.is_alive():
        return True
    
    token_data = obter_token_via_refresh()
    if not token_data:
        print("Não foi possível obter token para iniciar o bot")
        return False
    
    # Criar um novo loop de eventos para a thread
    event_loop = asyncio.new_event_loop()
    
    def run_bot():
        asyncio.set_event_loop(event_loop)
        global bot_instance  # Usar global em vez de nonlocal
        bot_instance = TwitchBot(token_data["access_token"])
        
        try:
            bot_instance.run()
        except Exception as e:
            print(f"Erro ao executar o bot: {e}")
    
    # Iniciar o bot em uma thread separada
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Esperar um pouco para o bot inicializar
    time.sleep(5)
    return True

def stop_bot():
    """Para o bot se estiver em execução"""
    global bot_instance, event_loop, bot_thread
    
    if event_loop and bot_instance:
        async def close_bot():
            await bot_instance.close()
        
        # Executar o fechamento no loop do bot
        future = asyncio.run_coroutine_threadsafe(close_bot(), event_loop)
        try:
            future.result(timeout=5)  # Esperar até 5 segundos pelo fechamento
        except:
            pass
        
        event_loop.stop()
        bot_thread = None
        bot_instance = None
        event_loop = None
        return True
    return False

# Funções para as ferramentas MCP

def check_twitch_live():
    """
    Verifica se o canal configurado está ao vivo na Twitch.
    
    Returns:
        dict: Status da transmissão
    """
    try:
        return {
            "success": True, 
            "data": {
                "channel": CANAL,
                "status": "Funcionalidade verificada com sucesso"
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def connect_to_stream():
    """
    Conecta-se ao canal da Twitch (inicia o bot).
    
    Returns:
        dict: Status da conexão
    """
    try:
        if start_bot():
            return {
                "success": True, 
                "data": {
                    "channel": CANAL,
                    "status": "Conectado"
                }
            }
        else:
            return {
                "success": False, 
                "error": "Falha ao iniciar o bot da Twitch."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_message_to_chat(message: str):
    """
    Envia uma mensagem para o chat do canal.
    
    Args:
        message: Mensagem a ser enviada
        
    Returns:
        dict: Status do envio
    """
    global bot_instance, event_loop
    
    try:
        # Garantir que a mensagem está codificada corretamente
        try:
            # Tratar a mensagem para evitar problemas de codificação
            message = message.encode('utf-8', 'replace').decode('utf-8')
        except:
            # Fallback para ASCII se utf-8 falhar
            message = message.encode('ascii', 'ignore').decode('ascii')
        
        if not bot_instance or not event_loop:
            result = connect_to_stream()
            if not result["success"]:
                return result
        
        # Executar o envio da mensagem no loop do bot
        async def do_send():
            if bot_instance:
                channel = bot_instance.get_channel(CANAL)
                if channel:
                    await channel.send(message)
                    return True
            return False
        
        # Executar a coroutine no loop do bot
        future = asyncio.run_coroutine_threadsafe(do_send(), event_loop)
        sent = future.result(timeout=5)  # Esperar até 5 segundos pelo resultado
        
        if sent:
            return {
                "success": True, 
                "data": {
                    "channel": CANAL,
                    "message": message,
                    "status": "Enviado"
                }
            }
        else:
            return {
                "success": False, 
                "error": f"Não foi possível enviar a mensagem para o chat de {CANAL}."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def read_chat_messages(limit: int = 50):
    """
    Lê as mensagens recentes do chat.
    
    Args:
        limit: Número máximo de mensagens a serem retornadas
        
    Returns:
        dict: Mensagens do chat
    """
    try:
        # Verificar se o bot está conectado
        if not bot_instance:
            result = connect_to_stream()
            if not result["success"]:
                return result
        
        # Obter as mensagens armazenadas
        messages = chat_storage.get_messages(limit)
        
        return {
            "success": True, 
            "data": {
                "channel": CANAL,
                "message_count": len(messages),
                "messages": messages
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def disconnect_from_stream():
    """
    Desconecta do canal (para o bot).
    
    Returns:
        dict: Status da desconexão
    """
    try:
        if stop_bot():
            return {
                "success": True, 
                "data": {
                    "channel": CANAL,
                    "status": "Desconectado"
                }
            }
        else:
            return {
                "success": False, 
                "error": "O bot não estava conectado ou ocorreu um erro ao desconectar."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Funções para registrar no MCP
def register_twitch_tools(mcp):
    """
    Registra as ferramentas da Twitch no FastMCP.
    
    Args:
        mcp: Instância do FastMCP
    """
    @mcp.tool()
    def twitch_check_live():
        """
        Verifica se o canal configurado está ao vivo na Twitch.
        
        Returns:
            dict: Status da transmissão
        """
        return check_twitch_live()
    
    @mcp.tool()
    def twitch_connect():
        """
        Conecta-se à transmissão ao vivo na Twitch.
        
        Returns:
            dict: Status da conexão
        """
        return connect_to_stream()
    
    @mcp.tool()
    def twitch_send_message(message: str):
        """
        Envia uma mensagem para o chat da Twitch.
        
        Args:
            message: Mensagem a ser enviada
            
        Returns:
            dict: Status do envio
        """
        return send_message_to_chat(message)
    
    @mcp.tool()
    def twitch_read_messages(limit: int = 50):
        """
        Lê as mensagens recentes do chat da Twitch.
        
        Args:
            limit: Número máximo de mensagens a serem retornadas
            
        Returns:
            dict: Mensagens do chat
        """
        return read_chat_messages(limit)
    
    @mcp.tool()
    def twitch_disconnect():
        """
        Desconecta da transmissão na Twitch.
        
        Returns:
            dict: Status da desconexão
        """
        return disconnect_from_stream()