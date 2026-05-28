import requests

def gerar_novo_token():
    # Endereço confirmado pelo Mateus e pelo seu print
    url = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/auth"
    
    # O código longo que aparece exatamente no seu print da Tray
    codigo_instalacao = "efcd9cb9fa9715c2f86f634847192d157571e6b3546ddb0d60abca1390f83140"
    
    payload = {
        "code": codigo_instalacao
    }
    
    print("🔑 Tentando gerar um novo Access Token com a Tray...")
    response = requests.post(url, data=payload)
    
    if response.status_code in [200, 201]:
        dados = response.json()
        novo_token = dados.get("access_token")
        print("\n" + "="*50)
        print(f"✅ NOVO ACCESS TOKEN GERADO COM SUCESSO!")
        print(f"👉 COPIE ESTE TEXTO ABAIXO:")
        print(f"\n{novo_token}\n")
        print("="*50)
    else:
        print(f"❌ Erro ao gerar token: {response.status_code} - {response.text}")

if __name__ == "__main__":
    gerar_novo_token()
