import os
import shutil
from datetime import datetime
import time

class FileManager:
    def __init__(self):
        self.raiz_simulada = os.path.join(os.getcwd(), "Telefone")
        if not os.path.exists(self.raiz_simulada):
            os.makedirs(self.raiz_simulada)
            
        self.diretorio_atual = self.raiz_simulada
        self.selecao_idx = 0
        self.filtro_arquivos = []
        self.arquivo_em_copia = None # Para a lógica de copiar/colar

    def atualizar_lista(self):
        try:
            conteudo = os.listdir(self.diretorio_atual)
            pastas = [f for f in conteudo if os.path.isdir(os.path.join(self.diretorio_atual, f))]
            arquivos = [f for f in conteudo if os.path.isfile(os.path.join(self.diretorio_atual, f))]
            self.filtro_arquivos = sorted(pastas) + sorted(arquivos)
        except Exception:
            self.diretorio_atual = self.raiz_simulada
            self.atualizar_lista()

    # --- Telas de Diálogo e Input ---

    def tela_confirmacao(self, mensagem):
        import SYSTEM
        while True:
            linhas = ["", SYSTEM.centralizar(mensagem), "", "", ""]
            SYSTEM.renderizar_tela_fixa("CONFIRMAR?", linhas, barra_status_esq="Confirma", barra_status_dir="Cancelar")
            tecla = SYSTEM.obter_entrada_tecla()
            if tecla == "aux_esq" or tecla == "ok": return True
            if tecla == "aux_dir": return False

    def tela_input(self, titulo, prompt):
        import SYSTEM
        import keyboard
        nome = ""
        while True:
            linhas = [prompt, "", f"> {nome}_", "", ""]
            SYSTEM.renderizar_tela_fixa(titulo, linhas, barra_status_esq="Criar", barra_status_dir="Cancelar")
            
            # Captura de teclado bruto para o nome
            evento = keyboard.read_event(suppress=True)
            if evento.event_type == keyboard.KEY_DOWN:
                if evento.name == 'page up': return nome if nome else None # Aux Esq
                if evento.name == 'page down': return None # Aux Dir
                if evento.name == 'backspace': nome = nome[:-1]
                if evento.name == 'space': nome += " "
                if len(evento.name) == 1: nome += evento.name
            time.sleep(0.05)

    def visualizar_txt(self, nome_item):
        import SYSTEM
        caminho = os.path.join(self.diretorio_atual, nome_item)
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                linhas_texto = f.readlines()
            
            # Formatação básica para caber na tela
            conteudo_formatado = [l.strip()[:20] for l in linhas_texto[:9]]
            while True:
                SYSTEM.renderizar_tela_fixa(nome_item[:15].upper(), conteudo_formatado, barra_status_esq="", barra_status_dir="Voltar")
                if SYSTEM.obter_entrada_tecla() == "aux_dir": break
        except Exception:
            SYSTEM.renderizar_tela_fixa("ERRO", ["Não foi possível", "ler o arquivo"], barra_status_dir="OK")
            time.sleep(1.5)

    # --- Funções de Menu ---

    def menu_opcoes(self, nome_item):
        import SYSTEM
        opcoes = {"1": "Adicionar Pasta", "2": "Renomear", "3": "Copiar", "4": "Apagar", "5": "Info"}
        sel_op = 0
        chaves = sorted(opcoes.keys())
        
        while True:
            linhas = [f"{'->' if i == sel_op else '  '}{k}. {opcoes[k]}" for i, k in enumerate(chaves)]
            SYSTEM.renderizar_tela_fixa("OPÇÕES", linhas, barra_status_esq="Selecionar", barra_status_dir="Voltar")
            tecla = SYSTEM.obter_entrada_tecla()
            
            if tecla == "up": sel_op = (sel_op - 1) % len(chaves)
            elif tecla == "down": sel_op = (sel_op + 1) % len(chaves)
            elif tecla == "aux_dir": return
            elif tecla == "ok" or tecla == "aux_esq":
                escolha = chaves[sel_op]
                caminho_item = os.path.join(self.diretorio_atual, nome_item)

                if escolha == "1": # Adicionar Pasta
                    nome_nova = self.tela_input("NOVA PASTA", "Digite o nome:")
                    if nome_nova: os.makedirs(os.path.join(self.diretorio_atual, nome_nova), exist_ok=True)
                
                elif escolha == "3": # Copiar
                    self.arquivo_em_copia = caminho_item
                    SYSTEM.renderizar_tela_fixa("COPIAR", ["", "Arquivo copiado!", "Escolha o destino", "e pressione OK"], barra_status_dir="OK")
                    time.sleep(1.5)

                elif escolha == "4": # Apagar
                    if os.path.isdir(caminho_item):
                        SYSTEM.renderizar_tela_fixa("AVISO", [SYSTEM.centralizar("Pastas são"), SYSTEM.centralizar("apenas leitura")], barra_status_dir="OK")
                        time.sleep(1.5)
                    else:
                        if self.tela_confirmacao("Apagar arquivo?"):
                            os.remove(caminho_item)
                
                elif escolha == "5":
                    self.exibir_info(nome_item)
                
                return

    def iniciar(self):
        import SYSTEM
        while True:
            self.atualizar_lista()
            pode_voltar = self.diretorio_atual != self.raiz_simulada
            
            # UI dinâmicas se estiver em modo de "Colar"
            status_esq = "Opções" if not self.arquivo_em_copia else "COLAR"
            
            conteudo_tela = []
            if pode_voltar:
                conteudo_tela.append(f"{'->' if self.selecao_idx == 0 else '  '} [..] Voltar")
            
            start_idx = 1 if pode_voltar else 0
            for i, item in enumerate(self.filtro_arquivos):
                idx_real = i + start_idx
                prefixo = "->" if self.selecao_idx == idx_real else "  "
                icone = "📁" if os.path.isdir(os.path.join(self.diretorio_atual, item)) else "📄"
                conteudo_tela.append(f"{prefixo}{icone}{item[:15]}")

            titulo = os.path.basename(self.diretorio_atual) if pode_voltar else "Memória"
            SYSTEM.renderizar_tela_fixa(f"📁 {titulo}", conteudo_tela, barra_status_esq=status_esq, barra_status_dir="Sair")
            
            tecla = SYSTEM.obter_entrada_tecla()
            
            if tecla == "up": self.selecao_idx = (self.selecao_idx - 1) % len(conteudo_tela) if conteudo_tela else 0
            elif tecla == "down": self.selecao_idx = (self.selecao_idx + 1) % len(conteudo_tela) if conteudo_tela else 0
            elif tecla == "aux_dir": return "MENU_PRINCIPAL"
            
            elif tecla == "aux_esq":
                if self.arquivo_em_copia:
                    # Lógica de colar
                    if self.tela_confirmacao("Colar aqui?"):
                        nome_base = os.path.basename(self.arquivo_em_copia)
                        shutil.copy2(self.arquivo_em_copia, os.path.join(self.diretorio_atual, nome_base))
                        self.arquivo_em_copia = None
                elif self.filtro_arquivos:
                    if not (pode_voltar and self.selecao_idx == 0):
                        item_nome = self.filtro_arquivos[self.selecao_idx - start_idx]
                        self.menu_opcoes(item_nome)
            
            elif tecla == "ok":
                if pode_voltar and self.selecao_idx == 0:
                    self.diretorio_atual = os.path.dirname(self.diretorio_atual)
                    self.selecao_idx = 0
                elif self.filtro_arquivos:
                    item_nome = self.filtro_arquivos[self.selecao_idx - start_idx]
                    caminho_item = os.path.join(self.diretorio_atual, item_nome)
                    if os.path.isdir(caminho_item):
                        self.diretorio_atual = caminho_item
                        self.selecao_idx = 0
                    elif item_nome.lower().endswith('.txt'):
                        self.visualizar_txt(item_nome)
                    else:
                        self.exibir_info(item_nome)

    def exibir_info(self, nome_item):
        import SYSTEM
        caminho = os.path.join(self.diretorio_atual, nome_item)
        stats = os.stat(caminho)
        dt_criacao = datetime.fromtimestamp(stats.st_ctime).strftime('%d/%m/%Y')
        extensao = "Pasta" if os.path.isdir(caminho) else nome_item.split('.')[-1].upper()
        conteudo = [f"Nome: {nome_item[:12]}", f"Tipo: {extensao}", f"Criado: {dt_criacao}", "", "Local:", f"\\Telefone\\{nome_item[:10]}"]
        SYSTEM.renderizar_tela_fixa("INFO", conteudo, barra_status_esq="", barra_status_dir="OK")
        SYSTEM.obter_entrada_tecla()

def abrir_gerenciador():
    fm = FileManager()
    return fm.iniciar()