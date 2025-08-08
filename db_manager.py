import json
import os
import datetime

# Define o nome do ficheiro de "banco de dados"
DB_FILE = "database.json"

# --- Funções Internas para Gerir o Ficheiro ---

def _carregar_db():
    """
    Função interna para ler o ficheiro JSON.
    Cria o ficheiro com a estrutura base se ele não existir.
    """
    if not os.path.exists(DB_FILE):
        dados_iniciais = {"ultimo_processo": 0, "ultimo_porte": 0, "processos": {}}
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_iniciais, f, indent=4)
        return dados_iniciais
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _salvar_db(dados):
    """Função interna para escrever no ficheiro JSON."""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- Funções do Fluxo Principal ---

def salvar_processo(dados_processo: dict, message_id: int, channel_id: int):
    """Salva um novo processo no banco de dados e retorna o seu número."""
    db = _carregar_db()
    
    novo_numero_int = db["ultimo_processo"] + 1
    novo_numero_str = f"{novo_numero_int:03d}"
    db["ultimo_processo"] = novo_numero_int
    
    dados_processo["status"] = "Aguardando Avaliação"
    dados_processo["message_id"] = message_id
    dados_processo["channel_id"] = channel_id
    
    db["processos"][novo_numero_str] = dados_processo
    
    _salvar_db(db)
    return novo_numero_str

def encontrar_e_atualizar_laudo(identidade_cidadao: str):
    """Encontra e atualiza um processo para 'Apto no Psicológico'."""
    db = _carregar_db()
    id_limpa = identidade_cidadao.strip()
    for numero_processo, dados_processo in db["processos"].items():
        if dados_processo.get("identidade", "").strip() == id_limpa and dados_processo.get("status") == "Aguardando Avaliação":
            db["processos"][numero_processo]["status"] = "Apto no Psicológico"
            _salvar_db(db)
            return dados_processo
    return None

def encontrar_e_emitir_porte(identidade_cidadao: str):
    """Encontra e atualiza um processo para 'Porte Emitido', gerando um novo número de porte."""
    db = _carregar_db()
    id_limpa = identidade_cidadao.strip()
    for numero_processo, dados_processo in db["processos"].items():
        if dados_processo.get("identidade", "").strip() == id_limpa and dados_processo.get("status") == "Apto no Psicológico":
            novo_porte_int = db.get("ultimo_porte", 0) + 1
            novo_porte_str = f"{novo_porte_int:03d}"
            db["ultimo_porte"] = novo_porte_int
            
            db["processos"][numero_processo]["status"] = "Porte Emitido"
            db["processos"][numero_processo]["numero_porte"] = novo_porte_str
            
            _salvar_db(db)
            
            return dados_processo, novo_porte_str
    return None, None

# --- FUNÇÕES ATUALIZADAS PARA CONSULTA E ADMINISTRAÇÃO ---

def encontrar_processo_por_id(identidade_cidadao: str):
    """Apenas encontra e retorna os dados de um processo pela ID, sem alterar nada."""
    db = _carregar_db()
    id_limpa = identidade_cidadao.strip()
    for numero_processo, dados_processo in db["processos"].items():
        if dados_processo.get("identidade", "").strip() == id_limpa:
            return numero_processo, dados_processo
    return None, None

def revogar_porte_por_id(numero_processo: str, motivo: str, admin_user: str):
    """Muda o status para Revogado e guarda o motivo e o admin."""
    db = _carregar_db()
    if numero_processo in db["processos"]:
        db["processos"][numero_processo]["status"] = "Revogado"
        db["processos"][numero_processo]["log_revogacao"] = {
            "motivo": motivo,
            "admin": admin_user,
            "data": datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
        }
        _salvar_db(db)
        return db["processos"][numero_processo]
    return None

def alterar_nivel_por_id(numero_processo: str, novo_nivel: str, motivo: str, admin_user: str):
    """Altera o nível do porte e guarda um registo da alteração."""
    db = _carregar_db()
    if numero_processo in db["processos"]:
        nivel_antigo = db["processos"][numero_processo]["nivel_porte"]
        db["processos"][numero_processo]["nivel_porte"] = novo_nivel
        db["processos"][numero_processo]["log_alteracao"] = {
            "de_nivel": nivel_antigo,
            "para_nivel": novo_nivel,
            "motivo": motivo,
            "admin": admin_user,
            "data": datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
        }
        _salvar_db(db)
        return db["processos"][numero_processo]
    return None

# --- NOVA FUNÇÃO DE LIMPEZA ---
def limpar_processo_por_id(numero_processo: str):
    """Encontra um processo pelo seu NÚMERO e o remove completamente."""
    db = _carregar_db()
    # Verifica se o processo realmente existe antes de tentar apagar
    if numero_processo in db["processos"]:
        # Remove o processo do dicionário
        processo_removido = db["processos"].pop(numero_processo)
        _salvar_db(db)
        # Retorna os dados do processo que foi removido, para confirmação
        return processo_removido
    return None