import os
import time
import keyboard 
from datetime import datetime
import FileManager
import Messages
import ConfigManager

# --- Constantes da Tela ---
CELULAR_W = 22 # Largura da tela (colunas)
CELULAR_H = 15 # Altura da tela (linhas)

# Caracteres de borda (compatíveis com UTF-8)
B_TL, B_TR, B_BL, B_BR = '╔', '╗', '╚', '╝'
B_H, B_V, B_S = '═', '║', ' '

# Moldura da tela
FRAME_SUPERIOR = B_TL + B_H * (CELULAR_W - 2) + B_TR
FRAME_INFERIOR = B_BL + B_H * (CELULAR_W - 2) + B_BR
FRAME_LINHA_VAZIA = B_V + B_S * (CELULAR_W - 2) + B_V

FRAME_VAZIO = (
    [FRAME_SUPERIOR] + 
    [FRAME_LINHA_VAZIA] * (CELULAR_H - 2) + 
    [FRAME_INFERIOR]
)

# --- Funções Auxiliares de Sistema ---

def limpar_tela():
    if os.name == 'nt': os.system('cls')
    else: os.system('clear')

def centralizar(texto, largura=CELULAR_W - 2):
    return texto.center(largura)

def obter_entrada_tecla():
    while True:
        evento = keyboard.read_event(suppress=True)
        if evento.event_type == keyboard.KEY_DOWN:
            tecla_pressionada = evento.name.lower()
            
            # Atalho Global de Desligar (Tecla / ou ?)
            if tecla_pressionada == '/':
                return "desligar_global"

            for nome_logico, nome_tecla in MAPA_TECLAS.items():
                if tecla_pressionada == nome_tecla:
                    return nome_logico
            
            if tecla_pressionada.isdigit() and tecla_pressionada in MAPA_TECLAS:
                 return tecla_pressionada

def sair_do_simulador():
    renderizar_saudacao(iniciando=False)
    print("\nDesligando...")
    keyboard.unhook_all()
    os._exit(0) # Força a saída do script

# --- Funções de Tela Genéricas ---

def renderizar_tela_fixa(titulo, conteudo_linhas, barra_status_esq="Opções", barra_status_dir="Voltar"):
    tela = FRAME_VAZIO[:]
    titulo_centralizado = centralizar(titulo)
    tela[1] = B_V + titulo_centralizado + B_V
    tela[2] = B_V + '-' * (CELULAR_W - 2) + B_V

    for i, linha in enumerate(conteudo_linhas):
        if i < 9:
            linha_formatada = linha.ljust(CELULAR_W - 2)
            tela[i + 3] = B_V + linha_formatada + B_V

    tela[12] = B_V + B_H * (CELULAR_W - 2) + B_V
    status_esq = barra_status_esq[:10].ljust(10)
    status_dir = barra_status_dir[:10].rjust(10)
    tela[13] = B_V + status_esq + status_dir + B_V

    limpar_tela()
    estilo = ConfigManager.config_manager.obter_estilo()
    reset = "\033[0m"
    print(estilo + '\n'.join(tela) + reset)
    #print('\n'.join(tela))

# --- Funcionalidades Específicas ---

def exibir_camera():
    """Novidade: Exibe aviso de cartão de memória."""
    renderizar_tela_fixa("📷 CÂMERA", [
        "", "",
        centralizar("ERRO:"),
        centralizar("Inserir cart."),
        centralizar("de memória"),
        "", ""
    ], barra_status_esq="", barra_status_dir="Voltar")
    time.sleep(2)
    return "MENU_PRINCIPAL"

def exibir_indisponivel(nome_recurso):
    """Novidade: Mensagem para recursos ainda não implementados."""
    renderizar_tela_fixa("INFO", [
        "", "",
        centralizar(f"'{nome_recurso}'"),
        centralizar("recurso"),
        centralizar("indisponível"),
        "", ""
    ], barra_status_esq="", barra_status_dir="OK")
    time.sleep(1.5)
    return "MENU_PRINCIPAL"

def exibir_agenda():
    titulo = "📞 AGENDA"
    conteudo = ["1. João", "2. Maria", "3. Pedro", "4. Ana", "", "Use 1-9 para atalho"]
    while True:
        renderizar_tela_fixa(titulo, conteudo, barra_status_esq="Opções", barra_status_dir="Voltar")
        tecla = obter_entrada_tecla()
        if tecla == "desligar_global": sair_do_simulador()
        if tecla == "aux_dir" or tecla == "0": return "MENU_PRINCIPAL"
        if tecla in ["1", "2", "3", "4"]:
            renderizar_tela_fixa(titulo, conteudo + [centralizar("Ligando...")], barra_status_dir="Cancelar")
            time.sleep(1)
        time.sleep(0.1) 

def exibir_relogio():
    titulo = "⌚ RELÓGIO"
    while True:
        agora = datetime.now()
        conteudo = ["", centralizar(agora.strftime("%d/%m/%Y")), "", centralizar(agora.strftime("%H:%M:%S")), "", "", centralizar("Voltar: botão direito")]
        renderizar_tela_fixa(titulo, conteudo, barra_status_esq="Opções", barra_status_dir="Voltar")
        tecla = obter_entrada_tecla()
        if tecla == "desligar_global": sair_do_simulador()
        if tecla == "aux_dir" or tecla == "0": return "MENU_PRINCIPAL"
        time.sleep(0.5) 

# --- Funções de Transição e Espera ---

def entrar_no_menu(): return "MENU_PRINCIPAL"
def entrar_na_agenda(): return exibir_agenda()

def renderizar_tela_espera():
    data_hora = datetime.now().strftime("%H:%M")
    data_completa = datetime.now().strftime("%d/%m/%Y")
    titulo = "📶📶📶   🔋🔋🔋"
    conteudo_linhas = ["", centralizar(data_hora), centralizar(data_completa), "", "", "", centralizar("Press. OK para Menu")]
    renderizar_tela_fixa(titulo, conteudo_linhas, barra_status_esq="Menu", barra_status_dir="Agenda")
    return "TELA_ESPERA" 

def tela_ligacao(numero_discado=""):
    titulo = "CHAMADA"
    while True:
        conteudo = [""] * 3 + [centralizar(numero_discado)] + [""] * 5
        renderizar_tela_fixa(titulo, conteudo, barra_status_esq="Ligar", barra_status_dir="Apagar")
        tecla = obter_entrada_tecla()
        if tecla == "desligar_global": sair_do_simulador()
        if tecla.isdigit() and len(numero_discado) < (CELULAR_W - 3):
            numero_discado += tecla
            continue
        elif tecla == "aux_dir":
            if numero_discado: numero_discado = numero_discado[:-1]
            else: return "TELA_ESPERA"
            continue
        elif tecla == "aux_esq":
            if numero_discado:
                renderizar_tela_fixa("ERRO", [centralizar("Insira o Cartão SIM")], centralizar("Cartão SIM"))
                time.sleep(2)
                continue
            else:
                renderizar_tela_fixa("INFO", [centralizar("Número vazio")], barra_status_dir="OK")
                time.sleep(1)
                continue
        elif tecla == "ok": return "TELA_ESPERA"
        time.sleep(0.05)

# --- Estrutura de Menus e Grade ---

MAPA_TECLAS = {
    "up": "up", "down": "down", "left": "left", "right": "right",
    "ok": "space", "aux_esq": "page up", "aux_dir": "page down",
    "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
    "5": "5", "6": "6", "7": "7", "8": "8", "9": "9"
}

# Definição dos itens da grade 3x3
ESTRUTURA_GRADE = [
    {"titulo": "Agenda", "icone": "👥", "ref": "2"},
    {"titulo": "Mensagens", "icone": "✉️", "ref": "1"},
    {"titulo": "Ligações", "icone": "📞", "ref": "ligacoes"},
    {"titulo": "Câmera", "icone": "📷", "ref": "camera"},
    {"titulo": "Rádio", "icone": "📻", "ref": "radio"},
    {"titulo": "Gerenc. Arq", "icone": "📁", "ref": "arquivos", "funcao": FileManager.abrir_gerenciador},
    {"titulo": "Config.", "icone": "⚙️", "ref": "4"},
    {"titulo": "Serviços", "icone": "🌐", "ref": "servicos"},
    {"titulo": "Ferramentas", "icone": "🛠️", "ref": "3"}
]

MENU_PRINCIPAL = {
    "1": {"titulo": "Mensagens", "submenu": {"1": {"titulo": "Nova Mensagem", "funcao": Messages.nova_mensagem}, "2": {"titulo": "Cx. de Entrada", "funcao": None},  "3": {"titulo": "Enviadas", "funcao": Messages.mensagens_enviadas}}, "funcao": None},
    "2": {"titulo": "Agenda", "funcao": exibir_agenda, "submenu": None},
    "3": {"titulo": "Ferramentas", "submenu": {"1": {"titulo": "Alarme", "funcao": None}, "2": {"titulo": "Relógio digital", "funcao": exibir_relogio}, "3": {"titulo": "Calculadora", "funcao": None}, "4": {"titulo": "Jogos", "funcao": None}, "5": {"titulo": "Navegador WAP", "funcao": None}}, "funcao": None},
    "4": {
        "titulo": "Configurações",
        "submenu": {
            "1": {"titulo": "Perfil", "submenu": {
                "1": {"titulo": "Geral", "funcao": None},
                "2": {"titulo": "Silencioso", "funcao": None},
                "3": {"titulo": "Auricular", "funcao": None},
                "4": {"titulo": "Alto", "funcao": None}
            }},
            "2": {"titulo": "Data e Hora", "submenu": {
                "1": {"titulo": "Definir Data", "funcao": None},
                "2": {"titulo": "Definir Hora", "funcao": None},
                "3": {"titulo": "Fuso horário", "funcao": None},
                "4": {"titulo": "Hora automática", "funcao": None}
            }},
            "3": {"titulo": "Toques", "submenu": {
                "1": {"titulo": "Toque Chamada", "funcao": None},
                "2": {"titulo": "Toque Alarme", "funcao": None},
                "3": {"titulo": "Toque Aviso", "funcao": None},
                "4": {"titulo": "Sons Sistema", "funcao": None}
            }},
            "4": {"titulo": "Tela", "submenu": {
                "1": {"titulo": "Duração Luz", "funcao": None},
                "2": {"titulo": "Brilho", "funcao": None},
                "3": {"titulo": "Saturação", "funcao": None},
                "4": {"titulo": "Cor", "funcao": None},
                "5": {"titulo": "Tema", "funcao": ConfigManager.config_manager.selecionar_tema}
            }},
            "5": {"titulo": "Confs. Avançad.", "submenu": {
                "1": {"titulo": "Sintoniz.Rede", "funcao": None},
                "2": {"titulo": "Memória", "funcao": None},
                "3": {"titulo": "Info Software", "funcao": None},
                "4": {"titulo": "Segurança", "funcao": ConfigManager.config_manager.gerenciar_pin},
                "5": {"titulo": "Aplicativos", "funcao": None},
                "6": {"titulo": "Chamadas", "funcao": None},
                "7": {"titulo": "Idioma", "funcao": None},
                "8": {"titulo": "Sincronizar", "funcao": None},
                "9": {"titulo": "Resetar", "funcao": ConfigManager.config_manager.resetar_confirmacao}
            }}
        },
        "funcao": None
    }
}

TELA_ESPERA_MAPA = {
    "ok": entrar_no_menu, "aux_esq": entrar_no_menu, "aux_dir": entrar_na_agenda,
    "0": tela_ligacao, "1": tela_ligacao, "2": tela_ligacao, "3": tela_ligacao, "4": tela_ligacao, 
    "5": tela_ligacao, "6": tela_ligacao, "7": tela_ligacao, "8": tela_ligacao, "9": tela_ligacao 
}

# --- Funções de Renderização Específicas ---

def renderizar_saudacao(iniciando: bool):
    titulo = "ITAC Micro Mini"
    if iniciando:
        conteudo_linhas = [""] * 3 + [centralizar("Bem-vindo!")] + [""] * 5 
        delay = 2
    else:
        conteudo_linhas = [""] * 3 + [centralizar("até a próxima!")] + [centralizar("desligando...")] + [""] * 4
        delay = 2
    renderizar_tela_fixa(titulo, conteudo_linhas, barra_status_esq="", barra_status_dir="")
    time.sleep(delay)

def renderizar_menu_grade(indice_selecionado):
    """Renderiza a grade 3x3 para o Menu Principal."""
    item_focado = ESTRUTURA_GRADE[indice_selecionado]
    conteudo = [""]
    
    # Renderiza as 3 linhas da grade
    for row in range(3):
        linha_icones = "  "
        for col in range(3):
            idx = row * 3 + col
            icone = ESTRUTURA_GRADE[idx]["icone"]
            if idx == indice_selecionado:
                linha_icones += f" [{icone}] "
            else:
                linha_icones += f"  {icone}  "
        conteudo.append(linha_icones)
        conteudo.append("") # Espaço entre linhas de ícones

    renderizar_tela_fixa(item_focado["titulo"].upper(), conteudo, barra_status_esq="Selecionar", barra_status_dir="Sair")

def renderizar_menu_lista(menu, selecao_atual_indice, titulo_menu):
    conteudo_linhas = []
    chaves_ordenadas = sorted(menu.keys())
    for i, chave in enumerate(chaves_ordenadas):
        item = menu[chave]
        prefixo = "->" if i == selecao_atual_indice else "  "
        titulo = item["titulo"]
        #if item.get("submenu") is not None: titulo += " >"
        conteudo_linhas.append(f"{prefixo}{chave}. {titulo}")
    renderizar_tela_fixa(titulo_menu, conteudo_linhas, barra_status_esq="Opções", barra_status_dir="Voltar")

# --- Loop Principal de Execução ---

def iniciar_simulador():
    menu_history = [] 
    menu_atual = MENU_PRINCIPAL
    selecao_grade_idx = 0 # Cursor para a grade
    selecao_lista_idx = 0 # Cursor para submenus
    estado_atual = "TELA_ESPERA" 
    titulo_atual = "MENU PRINCIPAL"

    renderizar_saudacao(iniciando=True)
    # NOVO: Verificação de Segurança antes de ligar
    if not ConfigManager.config_manager.verificar_pin_boot():
        return
    
    while True:
        # 1. Renderização baseada no estado
        if estado_atual == "TELA_ESPERA":
            renderizar_tela_espera() 
        elif estado_atual == "MENU_PRINCIPAL":
            renderizar_menu_grade(selecao_grade_idx)
        else: # Submenus (Lista)
            renderizar_menu_lista(menu_atual, selecao_lista_idx, titulo_atual)
        
        # 2. Entrada
        tecla = obter_entrada_tecla()
        
        # Lógica de Desligamento Global
        if tecla == "desligar_global":
            sair_do_simulador()

        # --- LÓGICA TELA ESPERA ---
        if estado_atual == "TELA_ESPERA":
            if tecla in TELA_ESPERA_MAPA:
                if tecla.isdigit(): proximo = tela_ligacao(numero_discado=tecla)
                else: proximo = TELA_ESPERA_MAPA[tecla]()
                if proximo == "MENU_PRINCIPAL": 
                    estado_atual = "MENU_PRINCIPAL"
                    selecao_grade_idx = 0
            continue 

        # --- LÓGICA MENU PRINCIPAL (GRADE) ---
        if estado_atual == "MENU_PRINCIPAL":
            if tecla == "right": selecao_grade_idx = (selecao_grade_idx + 1) % 9
            elif tecla == "left": selecao_grade_idx = (selecao_grade_idx - 1) % 9
            elif tecla == "down": selecao_grade_idx = (selecao_grade_idx + 3) % 9
            elif tecla == "up": selecao_grade_idx = (selecao_grade_idx - 3) % 9
            elif tecla == "aux_dir": estado_atual = "TELA_ESPERA"
            elif tecla == "ok":
                item_grade = ESTRUTURA_GRADE[selecao_grade_idx]
                ref = item_grade["ref"]
                
                if "funcao" in item_grade and item_grade["funcao"] is not None:
                    res = item_grade["funcao"]()
                    if res == "MENU_PRINCIPAL":
                        estado_atual = "MENU_PRINCIPAL"
                        continue

                if ref == "camera": exibir_camera()
                elif ref in ["ligacoes", "radio", "arquivos", "servicos"]: 
                    exibir_indisponivel(item_grade["titulo"])
                elif ref in MENU_PRINCIPAL:
                    item_alvo = MENU_PRINCIPAL[ref]
                    if item_alvo["submenu"]:
                        menu_history.append({'menu': MENU_PRINCIPAL, 'titulo': "MENU PRINCIPAL"})
                        menu_atual = item_alvo["submenu"]
                        titulo_atual = item_alvo["titulo"]
                        selecao_lista_idx = 0
                        estado_atual = "SUBMENU"
                    elif item_alvo["funcao"]:
                        res = item_alvo["funcao"]()
                        if res == "TELA_ESPERA": estado_atual = "TELA_ESPERA"
            continue

        # --- LÓGICA SUBMENUS (LISTA) ---
        if estado_atual == "SUBMENU":
            chaves = sorted(menu_atual.keys())
            if tecla == "aux_dir":
                hist = menu_history.pop()
                menu_atual = hist['menu']
                titulo_atual = hist['titulo']
                selecao_lista_idx = 0
                if not menu_history: estado_atual = "MENU_PRINCIPAL"
            elif tecla == "down": selecao_lista_idx = (selecao_lista_idx + 1) % len(chaves)
            elif tecla == "up": selecao_lista_idx = (selecao_lista_idx - 1) % len(chaves)
            elif tecla == "ok" or (tecla.isdigit() and tecla in chaves):
                if tecla.isdigit(): selecao_lista_idx = chaves.index(tecla)
                item = menu_atual[chaves[selecao_lista_idx]]
                if item.get("submenu"):
                    menu_history.append({'menu': menu_atual, 'titulo': titulo_atual})
                    menu_atual = item["submenu"]
                    titulo_atual = item["titulo"]
                    selecao_lista_idx = 0
                elif item["funcao"]:
                    res = item["funcao"]()
                    if res == "MENU_PRINCIPAL": 
                        estado_atual = "MENU_PRINCIPAL"
                        menu_history = []
            continue

if __name__ == "__main__":
    iniciar_simulador()