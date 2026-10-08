"""
Sincronização de produtos Omie -> Tray.

Regras:
  - Só entram produtos ativos e marcados para marketplace/e-commerce no Omie
    (os mesmos do Omie.Hub).
  - Produto sem marca, ou de marca que não tem categoria na Tray, não entra.
  - Produto do Omie que não existe na Tray: é criado na Tray.
  - Produto que já existe na Tray: só são preenchidos campos que estão vazios
    na Tray (referência, EAN, NCM, peso, medidas, marca). Nada que já tenha
    valor é sobrescrito.
  - Imagens: produto criado, ou existente na Tray com ZERO imagens, recebe as
    fotos cadastradas no Omie. Produto que já tem alguma imagem nunca é tocado.

Vínculo Omie <-> Tray: codigo (Omie) = reference (Tray); se não achar, EAN.

Modos (variável MODO):
  incremental  produtos alterados no Omie nos últimos minutos, em ciclos a
               cada INTERVALO_SEG segundos durante DURACAO_SEG segundos.
  completo     varre todo o catálogo do Omie (carga inicial / conferência).

Com DRY_RUN=1 nada é gravado na Tray: só mostra o que seria feito.
"""
import os
import sys
import time
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import html
import unicodedata

import requests

TRAY_URL = os.environ.get("TRAY_URL", "https://www.artigos180cosmeticos.com.br/web_api").rstrip("/")
OMIE_URL = "https://app.omie.com.br/api/v1"

MODO = os.environ.get("MODO", "incremental")
DRY_RUN = os.environ.get("DRY_RUN", "1") == "1"
DURACAO_SEG = int(os.environ.get("DURACAO_SEG", "0"))
INTERVALO_SEG = int(os.environ.get("INTERVALO_SEG", "60"))
JANELA_MIN = int(os.environ.get("JANELA_MIN", "10"))
MAX_ESCRITAS = int(os.environ.get("MAX_ESCRITAS", "100000"))
CATEGORIA_PADRAO = os.environ.get("CATEGORIA_PADRAO_ID", "")
LIMITE_OMIE = int(os.environ.get("LIMITE_OMIE", "0"))
# Local de estoque do Omie usado para o estoque na Tray ("Artigos - Loja").
# O campo quantidade_estoque da listagem de produtos não serve: vem zerado.
LOCAL_ESTOQUE = int(os.environ.get("LOCAL_ESTOQUE_OMIE", "2423153066"))  # 0 = sem limite (útil para testes)

BRT = timezone(timedelta(hours=-3))


def log(msg):
    print(f"[{datetime.now(BRT):%H:%M:%S}] {msg}", flush=True)


def vazio(valor):
    if valor is None:
        return True
    texto = str(valor).strip()
    if texto == "":
        return True
    try:
        return float(texto.replace(",", ".")) == 0
    except ValueError:
        return False


# ---------------------------------------------------------------- Tray

class Tray:
    INTERVALO_MIN = 0.35  # 180 req/min

    def __init__(self):
        self.s = requests.Session()
        self.token = None
        self.refresh = None
        self.expira = None
        self.ultima = 0.0
        self.escritas = 0

    def autenticar(self):
        r = self.s.post(f"{TRAY_URL}/auth", data={
            "consumer_key": os.environ["CONSUMER_KEY"],
            "consumer_secret": os.environ["CONSUMER_SECRET"],
            "code": os.environ["CODE_TRAY"],
        }, timeout=60)
        dados = r.json()
        if "access_token" not in dados:
            raise RuntimeError(f"Falha ao autenticar na Tray: {r.status_code} {dados}")
        self._guardar(dados)
        if self.expira <= datetime.now(BRT) + timedelta(minutes=5):
            self.renovar()
        log(f"Tray autenticada (loja {dados.get('store_id')}, token até {self.expira:%d/%m %H:%M})")

    def renovar(self):
        r = self.s.get(f"{TRAY_URL}/auth", params={"refresh_token": self.refresh}, timeout=60)
        dados = r.json()
        if "access_token" not in dados:
            raise RuntimeError(f"Falha ao renovar token da Tray: {r.status_code} {dados}")
        self._guardar(dados)

    def _guardar(self, dados):
        self.token = dados["access_token"]
        self.refresh = dados["refresh_token"]
        self.expira = datetime.strptime(dados["date_expiration_access_token"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=BRT)

    def req(self, metodo, caminho, params=None, corpo=None):
        if self.expira and self.expira <= datetime.now(BRT) + timedelta(minutes=2):
            self.renovar()
        for tentativa in range(6):
            espera = self.INTERVALO_MIN - (time.time() - self.ultima)
            if espera > 0:
                time.sleep(espera)
            self.ultima = time.time()
            p = dict(params or {}, access_token=self.token)
            try:
                r = self.s.request(metodo, f"{TRAY_URL}{caminho}", params=p,
                                   data=json.dumps(corpo) if corpo is not None else None,
                                   headers={"Content-Type": "application/json"} if corpo is not None else None,
                                   timeout=90)
            except requests.RequestException as e:
                log(f"Tray: erro de conexão ({e}), tentando de novo")
                time.sleep(10 * (tentativa + 1))
                continue
            if r.status_code == 401:
                self.renovar()
                continue
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(min(60, 5 * (tentativa + 1)))
                continue
            return r
        raise RuntimeError(f"Tray {metodo} {caminho}: muitas falhas seguidas")

    def buscar(self, campo, valor):
        if vazio(valor):
            return None
        r = self.req("GET", "/products", {campo: valor, "limit": 5})
        if r.status_code != 200:
            raise RuntimeError(f"Tray: falha ao buscar {campo}={valor}: {r.status_code} {r.text[:200]}")
        produtos = r.json().get("Products", [])
        if len(produtos) > 1:
            log(f"atenção: {len(produtos)} produtos na Tray com {campo}={valor}; usando o primeiro ({produtos[0]['Product']['id']})")
        return produtos[0]["Product"] if produtos else None

    def categoria_da_marca(self, marca):
        """Categoria mais usada pelos produtos dessa marca na Tray."""
        r = self.req("GET", "/products", {"brand": marca, "limit": 50})
        if r.status_code != 200:
            raise RuntimeError(f"Tray: falha ao buscar marca {marca}: {r.status_code}")
        cats = Counter(x["Product"].get("category_id") for x in r.json().get("Products", [])
                       if x["Product"].get("category_id"))
        return cats.most_common(1)[0][0] if cats else None

    def listar_todos(self):
        pagina, todos = 1, []
        while True:
            r = self.req("GET", "/products", {"limit": 50, "page": pagina})
            if r.status_code != 200:
                raise RuntimeError(f"Tray: falha ao listar página {pagina}: {r.status_code} {r.text[:200]}")
            produtos = r.json().get("Products", [])
            if not produtos:
                return todos
            todos += [p["Product"] for p in produtos]
            pagina += 1

    def gravar(self, metodo, caminho, corpo):
        self.escritas += 1
        r = self.req(metodo, caminho, corpo=corpo)
        ok = r.status_code in (200, 201)
        return ok, r


# ---------------------------------------------------------------- Omie

class Omie:
    def __init__(self):
        self.s = requests.Session()

    def call(self, servico, metodo, param):
        corpo = {"call": metodo, "app_key": os.environ["APP_KEY_OMIE"],
                 "app_secret": os.environ["APP_SECRET_OMIE"], "param": [param]}
        for tentativa in range(6):
            try:
                r = self.s.post(f"{OMIE_URL}/{servico}/", json=corpo, timeout=120)
                dados = r.json()
            except Exception as e:
                log(f"Omie: erro de conexão ({e}), tentando de novo")
                time.sleep(10 * (tentativa + 1))
                continue
            if "faultstring" in dados:
                falha = dados["faultstring"]
                if "Não existem registros" in falha:
                    return {}
                if "Consumo redundante" in falha or "bloqueada" in falha.lower() or r.status_code in (425, 429, 500):
                    log(f"Omie: {falha[:120]} — aguardando")
                    time.sleep(30 * (tentativa + 1))
                    continue
                raise RuntimeError(f"Omie {metodo}: {falha}")
            return dados
        raise RuntimeError(f"Omie {metodo}: muitas falhas seguidas")

    def saldos_local(self):
        """Saldo de todos os produtos no local de estoque configurado: {codigo: saldo}."""
        saldos, pagina = {}, 1
        hoje = datetime.now(BRT).strftime("%d/%m/%Y")
        while True:
            dados = self.call("estoque/consulta", "ListarPosEstoque",
                              {"nPagina": pagina, "nRegPorPagina": 500, "dDataPosicao": hoje,
                               "cExibeTodos": "S", "codigo_local_estoque": LOCAL_ESTOQUE})
            for p in dados.get("produtos", []):
                saldos[p["cCodigo"]] = int(float(p.get("nSaldo") or 0))
            if pagina >= dados.get("nTotPaginas", 0):
                return saldos
            pagina += 1

    def saldo_produto(self, codigo_produto):
        dados = self.call("estoque/consulta", "PosicaoEstoque",
                          {"codigo_local_estoque": LOCAL_ESTOQUE, "id_prod": codigo_produto,
                           "data": datetime.now(BRT).strftime("%d/%m/%Y")})
        return int(float(dados.get("saldo") or 0))

    def produtos(self, desde=None):
        pagina = 1
        while True:
            # só produtos ativos e marcados para venda em marketplace/e-commerce (os do Omie.Hub)
            param = {"pagina": pagina, "registros_por_pagina": 100,
                     "apenas_importado_api": "N", "filtrar_apenas_omiepdv": "N",
                     "filtrar_apenas_marketplace": "S", "inativo": "N"}
            if desde:
                param.update({"filtrar_por_data_de": desde.strftime("%d/%m/%Y"),
                              "filtrar_por_hora_de": desde.strftime("%H:%M:%S")})
            dados = self.call("geral/produtos", "ListarProdutos", param)
            for p in dados.get("produto_servico_cadastro", []):
                yield p
            if pagina >= dados.get("total_de_paginas", 0):
                return
            pagina += 1


# ---------------------------------------------------------------- regras

def chave_marca(marca):
    sem_acento = unicodedata.normalize("NFKD", marca or "").encode("ascii", "ignore").decode()
    return " ".join(sem_acento.upper().split())


def ncm_tray(ncm):
    return "".join(c for c in str(ncm or "") if c.isdigit())[:8]


def peso_gramas(p):
    kg = p.get("peso_bruto") or p.get("peso_liq") or 0
    try:
        return int(round(float(kg) * 1000))
    except (TypeError, ValueError):
        return 0


def ficha_omie(p):
    """Campos da ficha da Tray a partir do produto do Omie (sem imagens)."""
    return {
        "reference": str(p.get("codigo") or "").strip(),
        "ean": str(p.get("ean") or "").strip(),
        "ncm": ncm_tray(p.get("ncm")),
        "weight": peso_gramas(p),
        "length": p.get("profundidade") or 0,
        "width": p.get("largura") or 0,
        "height": p.get("altura") or 0,
        "brand": str(p.get("marca") or "").strip(),
    }


def fotos_omie(p):
    """URLs das fotos do produto no Omie (a Tray aceita até 15)."""
    return [i["url_imagem"] for i in (p.get("imagens") or []) if i.get("url_imagem")][:15]


def campos_a_preencher(tray_prod, ficha):
    """Só campos vazios na Tray que o Omie tem preenchidos."""
    return {c: v for c, v in ficha.items() if vazio(tray_prod.get(c)) and not vazio(v)}


class Sincronizador:
    def __init__(self):
        self.tray = Tray()
        self.omie = Omie()
        self.cont = Counter()
        self.cat_por_marca = {}
        self.indice = None  # usado no modo completo
        # fotos já enviadas nesta execução: a Tray leva alguns minutos para
        # processá-las, e nesse meio tempo o produto ainda aparece sem imagem
        self.fotos_enviadas = set()
        self.saldos = None  # modo completo: saldos do local carregados de uma vez

    def preparar_categorias(self, produtos_tray):
        por_marca = defaultdict(Counter)
        for p in produtos_tray:
            if p.get("brand") and p.get("category_id"):
                por_marca[chave_marca(p["brand"])][p["category_id"]] += 1
        self.cat_por_marca = {m: c.most_common(1)[0][0] for m, c in por_marca.items()}

    def estoque_de(self, p):
        """Estoque do produto no local "Artigos - Loja" do Omie."""
        if self.saldos is not None:
            return self.saldos.get(p.get("codigo"), 0)
        return self.saldo_produto(p["codigo_produto"])

    def categoria_para(self, marca):
        chave = chave_marca(marca)
        if chave and chave not in self.cat_por_marca and self.indice is None:
            self.cat_por_marca[chave] = self.tray.categoria_da_marca(marca)
        return self.cat_por_marca.get(chave) or CATEGORIA_PADRAO

    def localizar(self, ficha):
        if self.indice is not None:
            return self.indice["ref"].get(ficha["reference"]) or self.indice["ean"].get(ficha["ean"])
        return self.tray.buscar("reference", ficha["reference"]) or self.tray.buscar("ean", ficha["ean"])

    def processar(self, p):
        if p.get("inativo") == "S":
            self.cont["ignorado_inativo"] += 1
            return
        ficha = ficha_omie(p)
        if not ficha["reference"]:
            self.cont["ignorado_sem_codigo"] += 1
            return
        tray_prod = self.localizar(ficha)

        if tray_prod:
            novos = campos_a_preencher(tray_prod, ficha)
            precisa_fotos = not (tray_prod.get("ProductImage") or []) and bool(fotos_omie(p))
            if novos:
                self.escrever("PUT", f"/products/{tray_prod['id']}", novos,
                              f"preencher {tray_prod['id']} ({ficha['reference']}): {', '.join(novos)}", "preenchido")
            elif not precisa_fotos:
                self.cont["sem_mudanca"] += 1
            if precisa_fotos:
                self.enviar_fotos(tray_prod["id"], p, tray_prod)
            return

        # Confirmação direta na Tray antes de criar (não confia só no índice do modo
        # completo, que pode ficar incompleto se o catálogo mudar durante a leitura).
        if self.indice is not None:
            existente = self.tray.buscar("reference", ficha["reference"]) or self.tray.buscar("ean", ficha["ean"])
            if existente:
                self.indice["ref"][ficha["reference"]] = existente
                self.cont["achado_na_confirmacao"] += 1
                novos = campos_a_preencher(existente, ficha)
                if novos:
                    self.escrever("PUT", f"/products/{existente['id']}", novos,
                                  f"preencher {existente['id']} ({ficha['reference']}): {', '.join(novos)}", "preenchido")
                self.enviar_fotos(existente["id"], p, existente)
                return

        categoria = self.categoria_para(ficha["brand"])
        if not categoria:
            self.cont["sem_categoria"] += 1
            motivo = "sem marca no Omie" if not ficha["brand"] else f"marca {ficha['brand']} sem categoria na Tray"
            log(f"pulado {ficha['reference']} ({motivo})")
            return
        corpo = {k: v for k, v in ficha.items() if not vazio(v)}
        corpo.update({
            "name": html.unescape(p.get("descricao") or "").strip()[:200],
            "price": p.get("valor_unitario") or 0,
            "stock": self.estoque_de(p),
            "category_id": categoria,
            "available": 1,
            "available_in_store": 1,
        })
        novo_id = self.escrever("POST", "/products", corpo, f"criar {ficha['reference']} — {corpo['name']}", "criado")
        if novo_id:
            self.enviar_fotos(novo_id, p)

    def enviar_fotos(self, tray_id, p, tray_prod=None):
        """Envia as fotos do Omie só se o produto não tiver nenhuma imagem na Tray."""
        fotos = fotos_omie(p)
        if not fotos or str(tray_id) in self.fotos_enviadas:
            return
        if tray_prod is not None and (tray_prod.get("ProductImage") or []):
            return
        if tray_prod is None:  # recém-criado: confirma que continua sem imagem
            r = self.tray.req("GET", f"/products/{tray_id}")
            if r.status_code != 200 or (r.json()["Product"].get("ProductImage") or []):
                return
        corpo = {"Images": {f"picture_source_{n}": u for n, u in enumerate(fotos, 1)}}
        if DRY_RUN:
            self.cont["fotos_simulado"] += 1
            return
        if self.tray.escritas >= MAX_ESCRITAS:
            self.cont["adiado_limite"] += 1
            return
        self.tray.escritas += 1
        r = self.tray.req("POST", f"/products/{tray_id}/images", corpo=corpo)
        if r.status_code in (200, 201):
            self.fotos_enviadas.add(str(tray_id))
            self.cont["fotos_enviadas"] += 1
        else:
            self.cont["erro"] += 1
            log(f"ERRO fotos do produto {tray_id}: {r.status_code} {r.text[:200]}")

    def escrever(self, metodo, caminho, campos, descricao, chave):
        if DRY_RUN:
            self.cont[f"{chave}_simulado"] += 1
            if self.cont[f"{chave}_simulado"] <= 20:
                log(f"[simulação] {descricao} -> {campos}")
            return
        if self.tray.escritas >= MAX_ESCRITAS:
            self.cont["adiado_limite"] += 1
            return
        ok, r = self.tray.gravar(metodo, caminho, {"Product": campos})
        if ok:
            self.cont[chave] += 1
            novo_id = r.json().get("id") if metodo == "POST" else None
            if self.indice is not None and metodo == "POST":
                novo = {**campos, "id": r.json().get("id")}
                self.indice["ref"][campos["reference"]] = novo
                if campos.get("ean"):
                    self.indice["ean"][campos["ean"]] = novo
            return novo_id
        else:
            self.cont["erro"] += 1
            log(f"ERRO {descricao}: {r.status_code} {r.text[:300]}")

    def rodar_completo(self):
        log("Lendo catálogo da Tray…")
        todos = self.tray.listar_todos()
        log(f"{len(todos)} produtos na Tray")
        self.preparar_categorias(todos)
        self.indice = {"ref": {}, "ean": {}}
        for p in todos:
            if not vazio(p.get("reference")):
                self.indice["ref"][str(p["reference"]).strip()] = p
            if not vazio(p.get("ean")):
                self.indice["ean"][str(p["ean"]).strip()] = p
        log("Lendo saldos do local de estoque do Omie…")
        self.saldos = self.omie.saldos_local()
        log(f"{len(self.saldos)} saldos no local {LOCAL_ESTOQUE}")
        log("Lendo catálogo do Omie e sincronizando…")
        for n, p in enumerate(self.omie.produtos(), 1):
            self.processar(p)
            if n % 1000 == 0:
                log(f"{n} produtos do Omie processados — {dict(self.cont)}")
            if LIMITE_OMIE and n >= LIMITE_OMIE:
                break

    def rodar_incremental(self):
        inicio_job = time.time()
        desde = datetime.now(BRT) - timedelta(minutes=JANELA_MIN)
        while True:
            ciclo = datetime.now(BRT)
            vistos = 0
            for p in self.omie.produtos(desde=desde):
                vistos += 1
                self.processar(p)
            log(f"ciclo: {vistos} alterados no Omie desde {desde:%d/%m %H:%M:%S} — {dict(self.cont)}")
            desde = ciclo - timedelta(minutes=1)
            if time.time() - inicio_job + INTERVALO_SEG > DURACAO_SEG:
                return
            time.sleep(max(0, INTERVALO_SEG - (datetime.now(BRT) - ciclo).total_seconds()))


def main():
    log(f"Modo {MODO}{' (SIMULAÇÃO — nada será gravado)' if DRY_RUN else ''}")
    s = Sincronizador()
    s.tray.autenticar()
    if MODO == "completo":
        s.rodar_completo()
    else:
        s.rodar_incremental()
    log(f"Resumo: {dict(s.cont)} | escritas na Tray: {s.tray.escritas}")
    if s.cont["erro"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
