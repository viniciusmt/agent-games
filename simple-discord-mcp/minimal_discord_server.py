import os
import sys
import json
import requests
import time

# Token do Discord (obtido das variáveis de ambiente)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    print("ERRO: DISCORD_TOKEN não encontrado nas variáveis de ambiente!", file=sys.stderr)
    sys.exit(1)

# Configuração da API do Discord
DISCORD_API_BASE = "https://discord.com/api/v10"
HEADERS = {
    "Authorization": f"Bot {DISCORD_TOKEN}",
    "Content-Type": "application/json"
}

# Variáveis para o protocolo MCP
SERVER_CAPABILITIES = {
    "tools": {
        "send_message": {
            "description": "Envia uma mensagem para um canal do Discord",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "ID do canal do Discord"
                    },
                    "content": {
                        "type": "string",
                        "description": "Conteúdo da mensagem"
                    }
                },
                "required": ["channel_id", "content"]
            }
        },
        "get_messages": {
            "description": "Obtém mensagens recentes de um canal do Discord",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "ID do canal do Discord"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Número máximo de mensagens (padrão: 10)"
                    }
                },
                "required": ["channel_id"]
            }
        }
    }
}

# Funções da API do Discord
def send_discord_message(channel_id, content):
    """Envia uma mensagem para um canal específico do Discord."""
    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
    data = {"content": content}
    
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        print(f"Mensagem enviada com sucesso para o canal {channel_id}", file=sys.stderr)
        return {"success": True, "message": "Mensagem enviada com sucesso"}
    except Exception as e:
        print(f"Erro ao enviar mensagem: {str(e)}", file=sys.stderr)
        return {"success": False, "error": str(e)}

def get_discord_messages(channel_id, limit=10):
    """Obtém as mensagens recentes de um canal."""
    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages?limit={limit}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        messages = response.json()
        print(f"Obtidas {len(messages)} mensagens do canal {channel_id}", file=sys.stderr)
        
        simplified_messages = []
        for msg in messages:
            simplified_messages.append({
                "id": msg.get("id"),
                "content": msg.get("content"),
                "author": {
                    "username": msg.get("author", {}).get("username"),
                    "bot": msg.get("author", {}).get("bot", False)
                },
                "timestamp": msg.get("timestamp")
            })
        
        return {"success": True, "messages": simplified_messages}
    except Exception as e:
        print(f"Erro ao obter mensagens: {str(e)}", file=sys.stderr)
        return {"success": False, "error": str(e)}

# Implementação do protocolo MCP
def handle_initialize(params):
    return {
        "serverInfo": {
            "name": "Discord Simple Server",
            "version": "1.0.0"
        },
        "capabilities": SERVER_CAPABILITIES
    }

def handle_invoke(params):
    method = params.get("method")
    arguments = params.get("arguments", {})
    
    if method == "send_message":
        channel_id = arguments.get("channel_id")
        content = arguments.get("content")
        return send_discord_message(channel_id, content)
    elif method == "get_messages":
        channel_id = arguments.get("channel_id")
        limit = arguments.get("limit", 10)
        return get_discord_messages(channel_id, limit)
    else:
        return {"error": f"Método desconhecido: {method}"}

# Loop principal para processar comandos MCP
def main():
    print("Iniciando servidor Discord simples...", file=sys.stderr)
    
    # Lê stdin para comandos MCP
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break  # Fim do input
                
            # Processa o comando JSON
            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})
            
            # Gerar resposta com base no método
            if method == "initialize":
                result = handle_initialize(params)
            elif method == "invoke":
                result = handle_invoke(params)
            else:
                result = {"error": f"Método desconhecido: {method}"}
            
            # Enviar resposta
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except Exception as e:
            print(f"Erro ao processar comando: {e}", file=sys.stderr)
            # Se possível, enviar erro formatado conforme protocolo MCP
            if 'request_id' in locals():
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    main()