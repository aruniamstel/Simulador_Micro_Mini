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
    # O loop principal agora trata a supressão de teclas
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
    limpar_tela()
    renderizar_saudacao (iniciando=False)
    print("\nDesligando...")
    # CRÍTICO: Libera todos os ganchos do teclado para evitar travamento do SO.
    keyboard.unhook_all() 

# --- Funções de Tela Genéricas ---

def renderizar_tela_fixa(titulo, conteudo_linhas, barra_status_esq="Opções", barra_status_dir="Voltar"):
    """
    Desenha a moldura e insere o conteúdo em posições fixas.
    Retorna a lista de linhas da tela pronta para impressão.
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
    
    # Loop interno para esta tela
    while True:
        renderizar_tela_fixa(titulo, conteudo, barra_status_esq="Opções", barra_status_dir="Voltar")
        
        tecla = obter_entrada_tecla()
        
        if tecla == "aux_dir" or tecla == "0": # Pg Dn ou 0 para Voltar
            return "MENU_PRINCIPAL"
        
        # Lógica de discagem rápida (apenas como exemplo de uso)
        if tecla in ["1", "2", "3", "4"]:
            renderizar_tela_fixa(titulo, conteudo + ["Ligando..."], barra_status_dir="Cancelar")
            time.sleep(1)
        
        # Pequeno atraso para evitar leitura dupla
        time.sleep(0.1) 

def exibir_relogio():
    """Gerencia a tela do Relógio Digital."""
    titulo = "⌚ RELÓGIO"
    
    # Loop interno para esta tela
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
            centralizar("Voltar: Pg Dn/0")
        ]
        
        renderizar_tela_fixa(titulo, conteudo, barra_status_esq="Opções", barra_status_dir="Voltar")
        
        tecla = obter_entrada_tecla()
        
        if tecla == "aux_dir" or tecla == "0": # Pg Dn ou 0 para Voltar
            return "MENU_PRINCIPAL"

        # Espera um pouco, mas não bloqueia indefinidamente como no menu
        time.sleep(0.5) 

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

# --- Funções de Navegação e Renderização de Menu ---

def imprimir_moldura_vazia(mensagem=""):
    """Imprime a moldura vazia do celular."""
    limpar_tela()
    FRAME_VAZIO [5] = B_V + centralizar(mensagem) + B_V
    for linha in FRAME_VAZIO:   
        print(linha)          


def renderizar_saudacao(iniciando: bool):
    """
    Imprime a moldura da tela com uma mensagem de saudação ou despedida.
    
    :param iniciando: Se True, mostra "Bem-vindo!", simulando a inicialização. 
                      Se False, mostra "Até a próxima! desligando...", simulando o desligamento.
    """

    if iniciando:
        titulo = "ITAC Micro Mini"
        mensagem = centralizar("Bem-vindo!")
        #renderizar_tela_fixa("", mensagem, "", "") # Tela em branco
        imprimir_moldura_vazia()
        
        # Conteúdo centrado na tela (4ª linha da moldura)
        conteudo_linhas = [""] * 3 + [mensagem] + [""] * 5 

        time.sleep (3)  # Segundos para a saudação de inicialização
        
        print("\nINICIANDO O SISTEMA...")
    else:
        titulo = "ITAC Micro Mini"
        mensagem = centralizar("até a próxima!")
        mensagem2 = centralizar("desligando...")
        #renderizar_tela_fixa("", mensagem, "", "") # Tela em branco
        
        # Conteúdo centrado na tela (4ª e 5ª linha da moldura)
        conteudo_linhas = [""] * 3 + [mensagem] + [mensagem2] + [""] * 4
        
        print("\nENCERRANDO O SISTEMA...")

        time.sleep(2)  # Segundos para a mensagem de desligamento

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
        
    # Renderiza na moldura fixa (barra_status_dir agora diz "OK" para indicar seleção)
    renderizar_tela_fixa(titulo_menu, conteudo_linhas, barra_status_esq="Menu", barra_status_dir="OK")


# --- Loop Principal de Execução ---

def iniciar_simulador():
    """Função principal para iniciar o loop de execução do simulador."""
    
    menu_atual = MENU_PRINCIPAL
    selecao_atual_indice = 0
    chaves_atuais = sorted(menu_atual.keys())
    titulo_atual = "MENU PRINCIPAL"
    
    simulador_ativo = True

    renderizar_saudacao (iniciando=True)
    
    while simulador_ativo:
        
        # 1. Renderizar a tela atual
        renderizar_menu(menu_atual, selecao_atual_indice, titulo_atual)
        
        # 2. Ler a tecla pressionada
        tecla = obter_entrada_tecla()
        
        # 3. Processar a Tecla
        
        if tecla == "down":
            selecao_atual_indice = (selecao_atual_indice + 1) % len(chaves_atuais)
        elif tecla == "up":
            selecao_atual_indice = (selecao_atual_indice - 1) % len(chaves_atuais)
            
        elif tecla.isdigit():
            # Tenta selecionar diretamente por número
            if tecla in menu_atual:
                try:
                    selecao_atual_indice = chaves_atuais.index(tecla)
                except ValueError:
                    pass 
        
        # Tecla de Ação (OK / Espaço) ou número selecionado:
        if tecla == "ok" or (tecla.isdigit() and tecla in chaves_atuais):
            
            chave_selecionada = chaves_atuais[selecao_atual_indice]
            item_selecionado = menu_atual[chave_selecionada]
            
            # Tratamento de Opção 0 (Sair ou Voltar)
            if chave_selecionada == "0":
                if item_selecionado["funcao"] is sair_do_simulador:
                    sair_do_simulador()
                    simulador_ativo = False
                    break
                
                # Trata "Voltar" (volta para o menu principal se for um submenu)
                elif menu_atual != MENU_PRINCIPAL:
                    menu_atual = MENU_PRINCIPAL
                    chaves_atuais = sorted(menu_atual.keys())
                    selecao_atual_indice = 0
                    titulo_atual = "MENU PRINCIPAL"
                    continue
                
                continue 

            # Ação principal (OK/Seleção)
            
            # 1. Tem Submenu: Entra no Submenu
            if item_selecionado.get("submenu") is not None:
                menu_atual = item_selecionado["submenu"]
                chaves_atuais = sorted(menu_atual.keys())
                selecao_atual_indice = 0
                titulo_atual = item_selecionado["titulo"]
                
            # 2. Tem Função: Executa a Função
            elif item_selecionado["funcao"] is not None:
                # Chama a função, que tem seu próprio loop e retorna o próximo estado
                proximo_estado = item_selecionado["funcao"]() 
                
                if proximo_estado == "MENU_PRINCIPAL":
                    # Retorna ao estado do menu principal
                    menu_atual = MENU_PRINCIPAL
                    chaves_atuais = sorted(menu_atual.keys())
                    selecao_atual_indice = 0
                    titulo_atual = "MENU PRINCIPAL"
            
            # 3. Não tem Função nem Submenu: Nenhuma Ação
            else:
                renderizar_tela_fixa("INFO", [f"'{item_selecionado['titulo']}'", "Não implementado"], barra_status_dir="OK")
                time.sleep(1) 
        
        time.sleep(0.05) 

if __name__ == "__main__":
    iniciar_simulador()
