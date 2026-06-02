import os
import json
import requests
import time

def gerar_novo_token_tray():
    """
    Gera o token de acesso para a API da Tray utilizando as credenciais
    armazenadas de forma segura nas variáveis de ambiente do GitHub.
    """
    url_auth = "https://1501119.commercesuite.com.br/web_api/auth"
    
    # As chaves agora são puxadas de forma automática e segura do GitHub Secrets
    payload_form = {
        "consumer_key": os.environ.get("CONSUMER_KEY"),
        "consumer_secret": os.environ.get("CONSUMER_SECRET"),
        "code": os.environ.get("CODE_TRAY")
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    print("🔑 Autenticando o aplicativo no formato correto (Form URL Encoded)...")
    
    try:
        response = requests.post(url_auth, headers=headers, data=payload_form)
        
        if response.status_code in [200, 201]:
            dados = response.json()
            token_gerado = dados.get("access_token")
            print("✅ Sucesso absoluto! Novo Token de acesso gerado e validado!")
            return token_gerado
        else:
            print(f"⚠️ Resposta da API ao gerar token: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao conectar com a API da Tray: {str(e)}")
        return None