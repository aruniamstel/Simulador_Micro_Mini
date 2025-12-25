import os
import shutil
from datetime import datetime
import time

class FileManager:
    def __init__(self):
        # 1. Definimos o caminho absoluto para a pasta 'Telefone'
        # Isso garante que ele sempre busque a pasta no local onde o script está
        self.raiz_simulada = os.path.join(os.getcwd(), "Telefone")
        
        # Criar a pasta automaticamente caso ela não exista ainda
        if not os.path.exists(self.raiz_simulada):
            os.makedirs(self.raiz_simulada)
            
        self.diretorio_atual = self.raiz_simulada
        self.selecao_idx = 0
        self.filtro_arquivos = []

    def atualizar_lista(self):
        try:
            conteudo = os.listdir(self.diretorio_atual)
            pastas = [f for f in conteudo if os.path.isdir(os.path.join(self.diretorio_atual, f))]
            arquivos = [f for f in conteudo if os.path.isfile(os.path.join(self.diretorio_atual, f))]
            self.filtro_arquivos = sorted(pastas) + sorted(arquivos)
        except Exception:
            self.diretorio_atual = self.raiz_simulada
            self.atualizar_lista()

    def exibir_info(self, nome_item):
        import SYSTEM
        caminho = os.path.join(self.diretorio_atual, nome_item)
        stats = os.stat(caminho)
        dt_criacao = datetime.fromtimestamp(stats.st_ctime).strftime('%d/%m/%Y')
        extensao = "Pasta" if os.path.isdir(caminho) else nome_item.split('.')[-1].upper()
        
        conteudo = [
            f"Nome: {nome_item[:12]}",
            f"Tipo: {extensao}",
            f"Criado: {dt_criacao}",
            "",
            "Local:",
            f"\\Telefone\\{nome_item[:10]}" # Mostra o caminho simulado
        ]
        SYSTEM.renderizar_tela_fixa("INFO", conteudo, barra_status_esq="", barra_status_dir="OK")
        SYSTEM.obter_entrada_tecla()

    def menu_opcoes(self, nome_item):
        import SYSTEM
        opcoes = {"1": "Adicionar Pasta", "2": "Renomear", "3": "Copiar", "4": "Apagar", "5": "Info"}
        sel_op = 0
        chaves = sorted(opcoes.keys())
        
        while True:
            linhas = [f"{'->' if i == sel_op else '  '}{k}. {opcoes[k]}" for i, k in enumerate(chaves)]
            SYSTEM.renderizar_tela_fixa("OPÇÕES", linhas, barra_status_esq="OK", barra_status_dir="Voltar")
            tecla = SYSTEM.obter_entrada_tecla()
            
            if tecla == "up": sel_op = (sel_op - 1) % len(chaves)
            elif tecla == "down": sel_op = (sel_op + 1) % len(chaves)
            elif tecla == "aux_dir": return
            elif tecla == "ok":
                caminho_item = os.path.join(self.diretorio_atual, nome_item)
                if chaves[sel_op] == "4": # Apagar
                    if os.path.isdir(caminho_item):
                        SYSTEM.renderizar_tela_fixa("AVISO", [SYSTEM.centralizar("Pastas são"), SYSTEM.centralizar("apenas leitura")], barra_status_dir="OK")
                        time.sleep(1.5)
                    else:
                        os.remove(caminho_item)
                elif chaves[sel_op] == "5":
                    self.exibir_info(nome_item)
                return

    def iniciar(self):
        import SYSTEM
        while True:
            self.atualizar_lista()
            
            # Título dinâmico que mostra apenas o nome da pasta atual
            nome_pasta_exibicao = os.path.basename(self.diretorio_atual)
            if self.diretorio_atual == self.raiz_simulada:
                nome_pasta_exibicao = "Memória"
                
            conteudo_tela = []
            
            # 2. LÓGICA DE BLOQUEIO DE RAIZ:
            # Só mostra o [..] se o diretório atual NÃO FOR a raiz simulada
            pode_voltar = self.diretorio_atual != self.raiz_simulada
            
            if pode_voltar:
                conteudo_tela.append(f"{'->' if self.selecao_idx == 0 else '  '} [..] Voltar")
            
            start_idx = 1 if pode_voltar else 0
            
            for i, item in enumerate(self.filtro_arquivos):
                idx_real = i + start_idx
                prefixo = "->" if self.selecao_idx == idx_real else "  "
                icone = "📁" if os.path.isdir(os.path.join(self.diretorio_atual, item)) else "📄"
                conteudo_tela.append(f"{prefixo}{icone}{item[:15]}")

            SYSTEM.renderizar_tela_fixa(f"📁 {nome_pasta_exibicao}", conteudo_tela, barra_status_esq="Opções", barra_status_dir="Sair")
            
            tecla = SYSTEM.obter_entrada_tecla()
            
            if tecla == "up": 
                self.selecao_idx = (self.selecao_idx - 1) % len(conteudo_tela) if conteudo_tela else 0
            elif tecla == "down": 
                self.selecao_idx = (self.selecao_idx + 1) % len(conteudo_tela) if conteudo_tela else 0
            elif tecla == "aux_dir": 
                return "MENU_PRINCIPAL"
            elif tecla == "aux_esq" and self.filtro_arquivos:
                if not (pode_voltar and self.selecao_idx == 0):
                    item_nome = self.filtro_arquivos[self.selecao_idx - start_idx]
                    self.menu_opcoes(item_nome)
            elif tecla == "ok":
                if pode_voltar and self.selecao_idx == 0:
                    self.diretorio_atual = os.path.dirname(self.diretorio_atual)
                    self.selecao_idx = 0
                elif self.filtro_arquivos:
                    item_nome = self.filtro_arquivos[self.selecao_idx - start_idx]
                    caminho_novo = os.path.join(self.diretorio_atual, item_nome)
                    if os.path.isdir(caminho_novo):
                        self.diretorio_atual = caminho_novo
                        self.selecao_idx = 0
                    else:
                        self.exibir_info(item_nome)

def abrir_gerenciador():
    fm = FileManager()
    return fm.iniciar()