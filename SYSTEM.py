import os
import time
import keyboard 
from datetime import datetime

# --- Constantes da Tela ---
CELULAR_W = 22 # Largura da tela (colunas)
CELULAR_H = 15 # Altura da tela (linhas)

# Caracteres de borda (compatíveis com UTF-8)
B_TL = '╔' # Top Left
B_TR = '╗' # Top Right
B_BL = '╚' # Bottom Left
B_BR = '╝' # Bottom Right
B_H  = '═' # Horizontal
B_V  = '║' # Vertical
B_S  = ' ' # Espaço interno

# Moldura da tela (15 linhas, 22 colunas)
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
    """Limpa a tela do terminal."""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def centralizar(texto, largura=CELULAR_W - 2):
    """Centraliza o texto dentro da largura da tela interna."""
    return texto.center(largura)

def obter_entrada_tecla():
    """Espera por uma tecla válida ser pressionada e retorna seu nome lógico."""
    while True:
        evento = keyboard.read_event(suppress=True)
        if evento.event_type == keyboard.KEY_DOWN:
            tecla_pressionada = evento.name.lower()
            
            for nome_logico, nome_tecla in MAPA_TECLAS.items():
                if tecla_pressionada == nome_tecla:
                    return nome_logico
            
            if tecla_pressionada.isdigit() and tecla_pressionada in MAPA_TECLAS:
                 return tecla_pressionada

def sair_do_simulador():
    """Função para sair do simulador e liberar o controle do teclado."""
    # A renderizar_saudacao(False) será chamada pelo loop principal antes de sair
    print("\nDesligando...")
    # CRÍTICO: Libera todos os ganchos do teclado para evitar travamento do SO.
    keyboard.unhook_all() 

# --- Funções de Tela Genéricas ---

def renderizar_tela_fixa(titulo, conteudo_linhas, barra_status_esq="Opções", barra_status_dir="Voltar"):
    """
    Desenha a moldura e insere o conteúdo em posições fixas.
    """
    tela = FRAME_VAZIO[:] # Cria uma cópia da moldura vazia

    # Linha 1: Título Centralizado
    titulo_centralizado = centralizar(titulo)
    tela[1] = B_V + titulo_centralizado + B_V
    
    # Linha 2: Separador visual
    tela[2] = B_V + '-' * (CELULAR_W - 2) + B_V

    # Linhas 3 a 11: Conteúdo principal (9 linhas disponíveis)
    for i, linha in enumerate(conteudo_linhas):
        if i < 9: # Limita a 9 linhas de conteúdo
            linha_formatada = linha.ljust(CELULAR_W - 2)
            tela[i + 3] = B_V + linha_formatada + B_V

    # Linha 12: Separador para barra de status
    tela[12] = B_V + B_H * (CELULAR_W - 2) + B_V

    # Linha 13: Barra de Status (Pg Up / Pg Dn)
    # 20 caracteres disponíveis: 10 para cada lado
    status_esq = barra_status_esq[:10].ljust(10)
    status_dir = barra_status_dir[:10].rjust(10)
    tela[13] = B_V + status_esq + status_dir + B_V

    # Imprime a tela final
    limpar_tela()
    print('\n'.join(tela))


def exibir_agenda():
    """Gerencia a tela da Agenda de Contatos."""
    titulo = "📞 AGENDA"
    conteudo = [
        "1. João",
        "2. Maria",
        "3. Pedro",
        "4. Ana",
        "",
        "Use 1-9 para atalho"
    ]
    
    while True:
        renderizar_tela_fixa(titulo, conteudo, barra_status_esq="Opções", barra_status_dir="Voltar")
        
        tecla = obter_entrada_tecla()
        
        if tecla == "aux_dir" or tecla == "0": # Pg Dn ou 0 para Voltar
            return "TELA_ESPERA" # Retorna para a tela de espera
        
        if tecla in ["1", "2", "3", "4"]:
            renderizar_tela_fixa(titulo, conteudo + [centralizar("Ligando...")], barra_status_dir="Cancelar")
            time.sleep(1)
        
        time.sleep(0.1) 

def exibir_relogio():
    """Gerencia a tela do Relógio Digital."""
    titulo = "⌚ RELÓGIO"
    
    while True:
        agora = datetime.now()
        hora_formatada = agora.strftime("%H:%M:%S")
        data_formatada = agora.strftime("%d/%m/%Y")
        
        conteudo = [
            "",
            centralizar(data_formatada),
            "",
            centralizar(hora_formatada),
            "",
            "",
            centralizar("Voltar: botão direito")
        ]
        
        renderizar_tela_fixa(titulo, conteudo, barra_status_esq="Opções", barra_status_dir="Voltar")
        
        tecla = obter_entrada_tecla()
        
        if tecla == "aux_dir" or tecla == "0": # Pg Dn ou 0 para Voltar
            return "MENU_PRINCIPAL"

        time.sleep(0.5) 

# --- Funções de Transição e Telas Específicas ---

def entrar_no_menu():
    """Função para transição de TELA_ESPERA para MENU_PRINCIPAL."""
    return "MENU_PRINCIPAL"

def entrar_na_agenda():
    """Função para transição de TELA_ESPERA para AGENDA."""
    # A função exibir_agenda contém um loop interno e retorna o próximo estado
    proximo_estado = exibir_agenda()
    return proximo_estado # Deve retornar "TELA_ESPERA" se for para lá

def renderizar_tela_espera():
    """
    Renderiza a tela de espera clássica com informações de status e atalhos.
    """
    data_hora = datetime.now().strftime("%H:%M")
    data_completa = datetime.now().strftime("%d/%m/%Y")
    
    # Simulação de Status
    nivel_bateria = "🔋🔋🔋" # 3 barras de 4
    nivel_rede = "📶📶📶" # 3 barras de 4
    
    # Linha do Título: Rede e Bateria
    titulo = f"{nivel_rede}   {nivel_bateria}"
    
    # Conteúdo principal (Horário e Data)
    conteudo_linhas = [
        "",
        centralizar(data_hora),
        centralizar(data_completa),
        "",
        "",
        "",
        centralizar("Press. OK para Menu")
    ]
    
    # Renderiza na moldura (Atalhos Menu e Agenda)
    renderizar_tela_fixa(
        titulo, 
        conteudo_linhas, 
        barra_status_esq="Menu", 
        barra_status_dir="Agenda"
    )
    
    return "TELA_ESPERA" # Retorna o estado atual

def tela_ligacao(numero_discado=""):
    """
    Gerencia a tela de discagem. Permite ao usuário digitar números, apagar 
    e tentar ligar.
    """
    titulo = "CHAMADA"
    
    while True:
        # Linha 4: Mostra o número discado
        # Certifica que o número discado está centralizado
        conteudo = [""] * 3 + [centralizar(numero_discado)] + [""] * 5
        
        # O botão auxiliar direito é 'Apagar'
        renderizar_tela_fixa(
            titulo, 
            conteudo, 
            barra_status_esq="Ligar", 
            barra_status_dir="Apagar"
        )
        
        tecla = obter_entrada_tecla()
        
        # 1. Tratar teclas numéricas (1-9, 0)
        if tecla.isdigit() and len(numero_discado) < (CELULAR_W - 3): # Limita o tamanho
            numero_discado += tecla
            continue

        # 2. Tratar Apagar (Pg Dn / aux_dir)
        elif tecla == "aux_dir":
            if numero_discado:
                numero_discado = numero_discado[:-1] # Remove o último caractere
            else:
                # Se o número estiver vazio, volta para a Tela de Espera
                return "TELA_ESPERA"
            continue

        # 3. Tratar Ligar (Pg Up / aux_esq)
        elif tecla == "aux_esq":
            if numero_discado:
                # Requisito: Exibe a mensagem de erro "insira o Cartão SIM"
                renderizar_tela_fixa("ERRO", [centralizar("Insira o")], centralizar("Cartão SIM"))
                time.sleep(2)
                # Volta para a tela de ligação para continuar ou apagar
                continue
            else:
                # Se não houver número, exibe um erro
                renderizar_tela_fixa("INFO", [centralizar("Número vazio")], barra_status_dir="OK")
                time.sleep(1)
                continue

        # 4. Tratar OK (Espaço) - Volta para a Tela de Espera
        elif tecla == "ok":
            return "TELA_ESPERA"
        
        time.sleep(0.05)


# --- Estrutura de Menus e Mapeamento de Teclas ---

MAPA_TECLAS = {
    "up": "up", "down": "down", "left": "left", "right": "right",
    "ok": "space", 
    "aux_esq": "page up",
    "aux_dir": "page down",
    "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
    "5": "5", "6": "6", "7": "7", "8": "8", "9": "9"
}

MENU_PRINCIPAL = {
    "1": {
        "titulo": "Mensagens",
        "submenu": {
            "1": {"titulo": "Nova Mensagem", "funcao": None},
            "2": {"titulo": "Cx. de Entrada", "funcao": None},
            "0": {"titulo": "Voltar", "funcao": None}
        },
        "funcao": None
    },
    "2": {
        "titulo": "Agenda",
        "funcao": exibir_agenda, 
        "submenu": None 
    },
    "3": {
        "titulo": "Ferramentas",
        "submenu": {
            "1": {"titulo": "Alarme", "funcao": None},
            "2": {"titulo": "Relógio digital", "funcao": exibir_relogio},
            "0": {"titulo": "Voltar", "funcao": None}
        },
        "funcao": None
    },
    "0": {"titulo": "Desligar", "funcao": sair_do_simulador, "submenu": None}
}

# Mapeamento de teclas para a TELA_ESPERA
TELA_ESPERA_MAPA = {
    "ok": entrar_no_menu,        # Espaço -> Menu Principal
    "aux_esq": entrar_no_menu,   # Pg Up (Atalho Menu) -> Menu Principal
    "aux_dir": entrar_na_agenda, # Pg Dn (Atalho Agenda) -> Agenda
    # Teclas numéricas para discagem
    "0": tela_ligacao, 
    "1": tela_ligacao, 
    "2": tela_ligacao, 
    "3": tela_ligacao, 
    "4": tela_ligacao, 
    "5": tela_ligacao, 
    "6": tela_ligacao, 
    "7": tela_ligacao, 
    "8": tela_ligacao, 
    "9": tela_ligacao 
}

# --- Funções de Renderização de Menu e Saudação ---

# Ajuste na renderizar_saudacao (removendo a lógica desnecessária de imprimir_moldura_vazia)
def renderizar_saudacao(iniciando: bool):
    """
    Imprime a moldura da tela com uma mensagem de saudação ou despedida.
    """
    titulo = "ITAC Micro Mini"
    
    if iniciando:
        mensagem = centralizar("Bem-vindo!")
        delay = 3
        conteudo_linhas = [""] * 3 + [mensagem] + [""] * 5 
    else:
        mensagem = centralizar("até a próxima!")
        mensagem2 = centralizar("desligando...")
        delay = 2
        conteudo_linhas = [""] * 3 + [mensagem] + [mensagem2] + [""] * 4

    renderizar_tela_fixa(titulo, conteudo_linhas, barra_status_esq="", barra_status_dir="")
    time.sleep(delay)


def renderizar_menu(menu, selecao_atual_indice, titulo_menu="MENU PRINCIPAL"):
    """Prepara o conteúdo do menu para ser inserido na moldura fixa."""
    
    conteudo_linhas = []
    chaves_ordenadas = sorted(menu.keys())
    
    for i, chave in enumerate(chaves_ordenadas):
        item = menu[chave]
        prefixo = "->" if i == selecao_atual_indice else "  "
        
        titulo = item["titulo"]
        if item.get("submenu") is not None:
            titulo += " >"
            
        conteudo_linhas.append(f"{prefixo}{chave}. {titulo}")
        
    renderizar_tela_fixa(titulo_menu, conteudo_linhas, barra_status_esq="Menu", barra_status_dir="Voltar")


# --- Loop Principal de Execução ---

def iniciar_simulador():
    """Função principal para iniciar o loop de execução do simulador."""
    
    # Variáveis de Estado
    menu_atual = MENU_PRINCIPAL
    selecao_atual_indice = 0
    chaves_atuais = sorted(menu_atual.keys())
    titulo_atual = "MENU PRINCIPAL"
    
    simulador_ativo = True
    estado_atual = "TELA_ESPERA" # Novo estado inicial

    renderizar_saudacao (iniciando=True)
    
    while simulador_ativo:
        
        # 1. Renderizar a tela atual
        if estado_atual == "TELA_ESPERA":
            renderizar_tela_espera() 
        elif estado_atual == "MENU_PRINCIPAL" or estado_atual.endswith("_SUBMENU"):
            renderizar_menu(menu_atual, selecao_atual_indice, titulo_atual)
        
        # 2. Ler a tecla pressionada
        tecla = obter_entrada_tecla()
        
        # --- LÓGICA DA TELA DE ESPERA ---
        if estado_atual == "TELA_ESPERA":
            if tecla in TELA_ESPERA_MAPA:
                funcao_chamada = TELA_ESPERA_MAPA[tecla]
                
                if tecla.isdigit():
                    # Para números, entra na tela de ligação, passando o primeiro dígito
                    proximo_estado = tela_ligacao(numero_discado=tecla)
                else:
                    # Para atalhos (OK, PgUp, PgDn)
                    proximo_estado = funcao_chamada() 
                
                # Transição de estado após a função retornar
                if proximo_estado == "MENU_PRINCIPAL":
                    estado_atual = "MENU_PRINCIPAL"
                    menu_atual = MENU_PRINCIPAL
                    chaves_atuais = sorted(menu_atual.keys())
                    selecao_atual_indice = 0
                    titulo_atual = "MENU PRINCIPAL"
                elif proximo_estado == "TELA_ESPERA":
                    estado_atual = "TELA_ESPERA"
                
            time.sleep(0.05)
            continue # Volta ao topo do loop da TELA_ESPERA
        
        # --- LÓGICA DO MENU (Existente) ---
        
        if tecla == "down":
            selecao_atual_indice = (selecao_atual_indice + 1) % len(chaves_atuais)
        elif tecla == "up":
            selecao_atual_indice = (selecao_atual_indice - 1) % len(chaves_atuais)
        # ... (restante da lógica de navegação numérica e OK/Espaço)
        
        # Tecla de Ação (OK / Espaço) ou número selecionado:
        if tecla == "ok" or (tecla.isdigit() and tecla in chaves_atuais):
            
            chave_selecionada = chaves_atuais[selecao_atual_indice]
            item_selecionado = menu_atual[chave_selecionada]
            
            # Tratamento de Opção 0 (Desligar ou Voltar)
            if chave_selecionada == "0":
                if item_selecionado["funcao"] is sair_do_simulador:
                    renderizar_saudacao(iniciando=False) 
                    sair_do_simulador()
                    simulador_ativo = False
                    break
                
                elif menu_atual != MENU_PRINCIPAL:
                    menu_atual = MENU_PRINCIPAL
                    chaves_atuais = sorted(menu_atual.keys())
                    selecao_atual_indice = 0
                    titulo_atual = "MENU PRINCIPAL"
                    continue
                
                continue 

            # Ação principal (OK/Seleção)
            if item_selecionado.get("submenu") is not None:
                menu_atual = item_selecionado["submenu"]
                chaves_atuais = sorted(menu_atual.keys())
                selecao_atual_indice = 0
                titulo_atual = item_selecionado["titulo"]
                
            elif item_selecionado["funcao"] is not None:
                proximo_estado = item_selecionado["funcao"]() 
                
                if proximo_estado == "MENU_PRINCIPAL":
                    menu_atual = MENU_PRINCIPAL
                    chaves_atuais = sorted(menu_atual.keys())
                    selecao_atual_indice = 0
                    titulo_atual = "MENU PRINCIPAL"
                elif proximo_estado == "TELA_ESPERA":
                    estado_atual = "TELA_ESPERA" # Transição direta do Menu para a Espera (Agenda)
            
            else:
                renderizar_tela_fixa("INFO", [centralizar("Não implementado")], barra_status_dir="OK")
                time.sleep(1) 
        
        time.sleep(0.05) 

if __name__ == "__main__":
    iniciar_simulador()