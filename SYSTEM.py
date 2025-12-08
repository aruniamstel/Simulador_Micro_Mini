import os
import time
import keyboard # Importa a biblioteca para leitura de teclas
from datetime import datetime

# --- Funções do Aparelho ---

def exibir_agenda():
    """Exibe a tela da Agenda de Contatos."""
    print("\n" + "="*40)
    print("      📞 Agenda de Contatos")
    print("="*40)
    print("1: João (9999-0001)")
    print("2: Maria (9999-0002)")
    print("...")
    print("\n[Pg Up] Opções | [Pg Dn] Ligar")
    return "AGENDA" # Mantém no estado AGENDA

def exibir_relogio():
    """Exibe um relógio digital na tela."""
    agora = datetime.now()
    hora_formatada = agora.strftime("%H:%M:%S")
    data_formatada = agora.strftime("%d/%m/%Y")
    
    print("\n" + "="*40)
    print("          ⌚ Relógio Digital")
    print("="*40)
    print(f"       {data_formatada}")
    print(f"       *** {hora_formatada} ***")
    print("\n[Pg Up] Opções | [Pg Dn] Voltar")
    # Não pausa, a atualização deve ser feita no loop, mas por simplicidade, apenas exibe.
    return "RELOGIO" # Mantém no estado RELOGIO

def menu_principal_funcao():
    """Função de entrada para o menu principal."""
    return "MENU_PRINCIPAL"

def sair_do_simulador():
    """Função para sair do simulador."""
    print("\nDesligando...")
    # Não precisa de return, o loop principal irá parar.

# --- Estrutura de Menus e Mapeamento de Teclas ---

# Mapeamento do seu layout de teclas para os nomes usados pela biblioteca `keyboard`
MAPA_TECLAS = {
    "up": "up",        # Cima
    "down": "down",    # Baixo
    "left": "left",    # Esquerda
    "right": "right",  # Direita
    "ok": "space",     # Espaço para OK
    "aux_esq": "page up",  # Pg Up para botão auxiliar esquerdo
    "aux_dir": "page down",# Pg Dn para botão auxiliar direito
    "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
    "5": "5", "6": "6", "7": "7", "8": "8", "9": "9"
}

# Estrutura de menu completa (usando as funções acima)
MENU_PRINCIPAL = {
    "1": {
        "titulo": "Mensagens",
        "submenu": {
            "1": {"titulo": "Nova Mensagem", "funcao": None},
            "2": {"titulo": "Caixa de Entrada", "funcao": None},
            "0": {"titulo": "Voltar", "funcao": menu_principal_funcao}
        },
        "funcao": None
    },
    "2": {
        "titulo": "Agenda",
        "funcao": exibir_agenda, # Opção que executa uma função diretamente
        "submenu": None # Sem submenu, executa a função acima
    },
    "3": {
        "titulo": "Ferramentas",
        "submenu": {
            "1": {"titulo": "Alarme", "funcao": None},
            "2": {"titulo": "Relógio digital", "funcao": exibir_relogio},
            "0": {"titulo": "Voltar", "funcao": menu_principal_funcao}
        },
        "funcao": None
    },
    "0": {"titulo": "Sair", "funcao": sair_do_simulador, "submenu": None}
}

# --- Funções de Navegação e Renderização ---

def limpar_tela():
    """Limpa a tela do terminal."""
    # Para Windows
    if os.name == 'nt':
        os.system('cls')
    # Para Unix/Linux/Mac
    else:
        os.system('clear')

def renderizar_menu(menu, selecao_atual, titulo_menu="MENU PRINCIPAL"):
    """
    Renderiza o menu atual na tela.
    `selecao_atual` é o item do menu atualmente selecionado (destacado).
    """
    limpar_tela()
    print("=" * 40)
    print(f"      📱 ITAC  MICRO MINI S40 SYSTEM - {titulo_menu.upper()}")
    print("=" * 40)

    # Ordena as chaves para garantir a ordem (e.g., 1, 2, 3, 0)
    chaves_ordenadas = sorted(menu.keys())
    
    for i, chave in enumerate(chaves_ordenadas):
        item = menu[chave]
        prefixo = "->" if i == selecao_atual else "  "
        
        # Determina o título a ser exibido
        if "submenu" in item and item["submenu"] is not None:
            titulo = item["titulo"] + " >"
        else:
            titulo = item["titulo"]
            
        print(f"{prefixo} {chave}. {titulo}")

    print("\n--- TECLAS ---")
    print("Cima/Baixo: Navegar | Espaço: OK | 0: Voltar/Sair")
    print("Pg Up/Pg Dn: Auxiliares")
    print("------------------")

def obter_entrada_tecla():
    """
    Espera por uma tecla válida ser pressionada e retorna seu nome.
    Simula o comportamento de `getch()`.
    """
    while True:
        # Espera por qualquer tecla pressionada
        evento = keyboard.read_event(suppress=True)
        if evento.event_type == keyboard.KEY_DOWN:
            tecla_pressionada = evento.name.lower()
            
            # Verifica se a tecla pressionada faz parte do nosso mapa
            for nome_logico, nome_tecla in MAPA_TECLAS.items():
                if tecla_pressionada == nome_tecla:
                    return nome_logico # Retorna o nome lógico (ex: 'up', '1', 'ok')
            
            # Trata teclas numéricas que não estão explicitamente no MAPA_TECLAS como '1', '2', etc.
            if tecla_pressionada.isdigit() and tecla_pressionada in MAPA_TECLAS:
                 return tecla_pressionada
            
            # Se for 'enter' e estiver simulando 'input', podemos ignorar ou tratar.
            # Aqui, apenas ignoramos outras teclas não mapeadas.

# --- Loop Principal de Execução ---

def iniciar_simulador():
    """Função principal para iniciar o loop de execução do simulador."""
    
    # Variáveis de Estado
    estado_atual = "MENU_PRINCIPAL" 
    menu_atual = MENU_PRINCIPAL
    selecao_atual_indice = 0
    
    # A lista de chaves (itens) do menu atual em ordem para indexação
    chaves_atuais = sorted(menu_atual.keys())
    
    # Título para o renderizador
    titulo_atual = "MENU PRINCIPAL"
    
    simulador_ativo = True
    
    while simulador_ativo:
        
        # 1. Renderizar a tela atual (Menu ou Função/Tela)
        if estado_atual == "MENU_PRINCIPAL" or estado_atual.endswith("_SUBMENU"):
            renderizar_menu(menu_atual, selecao_atual_indice, titulo_atual)
        # Se estiver em um estado de função (ex: AGENDA, RELOGIO), não renderiza o menu,
        # mas a função chamada já fez a sua exibição.
        
        # 2. Ler a tecla pressionada
        tecla = obter_entrada_tecla()
        
        # Se estiver em uma tela de função, só o 'aux_dir' (Pg Dn) ou 'aux_esq' (Pg Up)
        # para Voltar/Sair devem ser considerados aqui para simplificar.
        if estado_atual not in ["MENU_PRINCIPAL", "MENSAGENS_SUBMENU", "FERRAMENTAS_SUBMENU"]:
            if tecla == "aux_dir" or tecla == "aux_esq":
                 # Por simplicidade, qualquer tecla auxiliar volta para o menu principal
                 estado_anterior = estado_atual 
                 estado_atual = "MENU_PRINCIPAL"
                 menu_atual = MENU_PRINCIPAL
                 chaves_atuais = sorted(menu_atual.keys())
                 selecao_atual_indice = 0
                 titulo_atual = "MENU PRINCIPAL"
                 continue # Volta para o topo do loop

            # Permite um pequeno atraso para evitar leitura dupla acidental em telas de função
            time.sleep(0.1) 
            continue # Volta para o topo do loop, esperando nova entrada
        
        # 3. Processar a Tecla (Apenas se estiver em um Menu)
        
        if tecla == "down":
            selecao_atual_indice = (selecao_atual_indice + 1) % len(chaves_atuais)
        elif tecla == "up":
            selecao_atual_indice = (selecao_atual_indice - 1) % len(chaves_atuais)
            
        elif tecla.isdigit():
            # Tenta selecionar diretamente por número
            if tecla in menu_atual:
                # Encontra o índice da chave numérica
                try:
                    selecao_atual_indice = chaves_atuais.index(tecla)
                except ValueError:
                    # Chave numérica não encontrada (improvável com `sorted`)
                    pass 
        
        # Tecla de Ação (OK / Espaço) ou número selecionado:
        if tecla == "ok" or tecla.isdigit() and tecla in chaves_atuais:
            
            # Se a tecla for numérica, garante que a seleção_atual_indice está correta
            if tecla.isdigit() and tecla in chaves_atuais:
                chave_selecionada = tecla
            else: # Se for 'ok', usa a seleção atual
                chave_selecionada = chaves_atuais[selecao_atual_indice]
                
            item_selecionado = menu_atual[chave_selecionada]
            
            # Opção 0 (Voltar/Sair)
            if chave_selecionada == "0":
                if item_selecionado["funcao"] is sair_do_simulador:
                    sair_do_simulador()
                    simulador_ativo = False
                    break
                
                # Trata "Voltar" (volta para o menu principal ou estado anterior)
                elif estado_atual.endswith("_SUBMENU"):
                    estado_atual = "MENU_PRINCIPAL"
                    menu_atual = MENU_PRINCIPAL
                    chaves_atuais = sorted(menu_atual.keys())
                    selecao_atual_indice = 0
                    titulo_atual = "MENU PRINCIPAL"
                    continue
                
                # Se for Voltar em outro lugar ou Sair que não seja "0"
                if item_selecionado["funcao"] is not None:
                    item_selecionado["funcao"]()
                    continue

            # Ação principal (OK/Seleção)
            
            # 1. Tem Submenu: Entra no Submenu
            elif item_selecionado["submenu"] is not None:
                estado_atual = chave_selecionada + "_SUBMENU"
                menu_atual = item_selecionado["submenu"]
                chaves_atuais = sorted(menu_atual.keys())
                selecao_atual_indice = 0
                titulo_atual = item_selecionado["titulo"]
                
            # 2. Tem Função: Executa a Função
            elif item_selecionado["funcao"] is not None:
                novo_estado = item_selecionado["funcao"]()
                if novo_estado:
                    # A função retorna o novo estado (ex: "AGENDA")
                    estado_atual = novo_estado
                else:
                    # Se a função não retornar nada (simples execução), volta para o menu
                    pass
            
            # 3. Não tem Função nem Submenu: Nenhuma Ação
            else:
                print(f"Opção '{item_selecionado['titulo']}' não implementada ainda.")
                time.sleep(1) # Pequeno atraso para feedback

        # Permite um pequeno atraso para evitar leitura dupla acidental
        time.sleep(0.1) 
        
    print("Simulador encerrado.")

# --- Execução ---
if __name__ == "__main__":
    iniciar_simulador()
