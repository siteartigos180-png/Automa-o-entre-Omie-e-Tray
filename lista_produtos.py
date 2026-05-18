import requests
import os
import time

def auditoria_catalogo_completo_tray():
    url_base = "https://artigos180cosmeticosemoveis.corpsuite.com.br/web_api/products"
    
    consumer_key = os.getenv('CONSUMER_KEY', '').strip()
    consumer_secret = os.getenv('CONSUMER_SECRET', '').strip()
    
    pagina = 1
    total_produtos = 0
    
    print("🚀 INICIANDO CONFERÊNCIA AUTOMATIZADA: ATUALIZAÇÃO OMIE -> TRAY...")
    print("-" * 110)
    print(f"{'ID':<6} | {'SKU (Ref)':<15} | {'EAN (Barras)':<15} | {'Peso (Tray)':<12} | {'Nome do Produto'}")
    print("-" * 110)
    
    while True:
        params = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "page": pagina,
            "limit": 50
        }
        
        resposta = requests.get(url_base, params=params)
        
        if resposta.status_code == 200:
            dados = response_json = resposta.json()
            produtos_pagina = dados.get('Products', [])
            
            if not produtos_pagina:
                break
                
            for p in produtos_pagina:
                prod = p.get('Product', p)
                
                # Coletando as variáveis exatas do manual que a Juliana encontrou
                sku = prod.get('reference') or "Sem SKU"
                ean = prod.get('ean') or "Sem EAN"
                peso = prod.get('weight')
                
                # Formatando a exibição do peso
                p_exibir = f"{peso}g" if peso and str(peso) != "0" else "Vazio (0g)"
                nome_reduzido = prod.get('name', '')[:45]
                
                print(f"{prod.get('id'):<6} | {sku:<15} | {ean:<15} | {p_exibir:<12} | {nome_reduzido}")
                total_produtos += 1
                
            pagina += 1
            time.sleep(0.2)
        else:
            print(f"\n❌ Erro ao acessar a página {pagina}. Status: {resposta.status_code}")
            break
            
    print("-" * 110)
    print(f"🎉 AUDITORIA CONCLUÍDA! {total_produtos} produtos verificados com sucesso.")

if __name__ == "__main__":
    auditoria_catalogo_completo_tray()
