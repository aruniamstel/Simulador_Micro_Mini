import os
import shutil
from datetime import datetime
import time

# Importamos as funções e constantes do sistema principal


class FileManager:
    def __init__(self):
        # Define o diretório inicial (pode ser a pasta atual do script)
        self.diretorio_atual = os.getcwd()
        self.selecao_idx = 0
        self.filtro_arquivos = []

    def atualizar_lista(self):
        """Lê o conteúdo do diretório atual."""
        try:
            # Lista pastas primeiro, depois arquivos
            conteudo = os.listdir(self.diretorio_atual)
            pastas = [f for f in conteudo if os.path.isdir(os.path.join(self.diretorio_atual, f))]
            arquivos = [f for f in conteudo if os.path.isfile(os.path.join(self.diretorio_atual, f))]
            self.filtro_arquivos = sorted(pastas) + sorted(arquivos)
        except PermissionError:
            SYSTEM.renderizar_tela_fixa("ERRO", [SYSTEM.centralizar("Acesso Negado")], barra_status_dir="OK")
            time.sleep(1.5)
            # Volta um nível se der erro de permissão
            self.diretorio_atual = os.path.dirname(self.diretorio_atual)
            self.atualizar_lista()

    def exibir_info(self, nome_item):
        """Mostra metadados do arquivo/pasta selecionado."""
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
            "Caminho:",
            f"...{caminho[-15:]}"
        ]
        SYSTEM.renderizar_tela_fixa("INFO", conteudo, barra_status_esq="", barra_status_dir="OK")
        SYSTEM.obter_entrada_tecla()

    def menu_opcoes(self, nome_item):
        """Submenu universal de opções."""
        import SYSTEM 
        opcoes = {
            "1": "Adicionar Pasta",
            "2": "Renomear",
            "3": "Copiar",
            "4": "Apagar",
            "5": "Info"
        }
        
        sel_op = 0
        chaves = sorted(opcoes.keys())
        
        while True:
            linhas = []
            for i, k in enumerate(chaves):
                prefixo = "->" if i == sel_op else "  "
                linhas.append(f"{prefixo}{k}. {opcoes[k]}")
            
            SYSTEM.renderizar_tela_fixa("OPÇÕES", linhas, barra_status_esq="OK", barra_status_dir="Voltar")
            tecla = SYSTEM.obter_entrada_tecla()
            
            if tecla == "up": sel_op = (sel_op - 1) % len(chaves)
            elif tecla == "down": sel_op = (sel_op + 1) % len(chaves)
            elif tecla == "aux_dir": return
            elif tecla == "ok":
                escolha = chaves[sel_op]
                caminho_item = os.path.join(self.diretorio_atual, nome_item)
                
                if escolha == "1": # Adicionar Pasta
                    nova_pasta = os.path.join(self.diretorio_atual, f"Nova_Pasta_{int(time.time())}")
                    os.makedirs(nova_pasta, exist_ok=True)
                
                elif escolha == "2": # Renomear (Simples: adiciona prefixo)
                    novo_nome = os.path.join(self.diretorio_atual, f"REN_{nome_item}")
                    os.rename(caminho_item, novo_nome)
                
                elif escolha == "3": # Copiar
                    if os.path.isfile(caminho_item):
                        shutil.copy2(caminho_item, caminho_item + "_copia")
                
                elif escolha == "4": # Apagar
                    if os.path.isdir(caminho_item):
                        SYSTEM.renderizar_tela_fixa("AVISO", [SYSTEM.centralizar("Pastas são"), SYSTEM.centralizar("apenas leitura")], barra_status_dir="OK")
                        time.sleep(1.5)
                    else:
                        os.remove(caminho_item)
                
                elif escolha == "5": # Info
                    self.exibir_info(nome_item)
                
                return # Sai do menu de opções após ação

    def iniciar(self):
        """Loop principal do Gerenciador de Arquivos."""
        import SYSTEM 
        while True:
            self.atualizar_lista()
            titulo = f"📁 {os.path.basename(self.diretorio_atual) or 'Raiz'}"[:20]
            
            conteudo_tela = []
            # Adiciona opção de voltar diretório se não estiver na raiz
            if self.diretorio_atual != os.path.dirname(self.diretorio_atual):
                conteudo_tela.append(f"{'->' if self.selecao_idx == 0 else '  '} [..] Voltar")
            
            start_idx = 1 if "[..]" in str(conteudo_tela) else 0
            
            for i, item in enumerate(self.filtro_arquivos):
                idx_real = i + start_idx
                prefixo = "->" if self.selecao_idx == idx_real else "  "
                icone = "📁" if os.path.isdir(os.path.join(self.diretorio_atual, item)) else "📄"
                conteudo_tela.append(f"{prefixo}{icone}{item[:15]}")

            SYSTEM.renderizar_tela_fixa(titulo, conteudo_tela, barra_status_esq="Opções", barra_status_dir="Sair")
            
            tecla = SYSTEM.obter_entrada_tecla()
            
            if tecla == "up":
                self.selecao_idx = (self.selecao_idx - 1) % len(conteudo_tela)
            elif tecla == "down":
                self.selecao_idx = (self.selecao_idx + 1) % len(conteudo_tela)
            elif tecla == "aux_dir":
                return "MENU_PRINCIPAL"
            elif tecla == "aux_esq":
                # Abre opções para o item selecionado (se não for o botão de voltar [..])
                if not (start_idx == 1 and self.selecao_idx == 0):
                    item_nome = self.filtro_arquivos[self.selecao_idx - start_idx]
                    self.menu_opcoes(item_nome)
            elif tecla == "ok":
                # Lógica de entrar em pasta
                if start_idx == 1 and self.selecao_idx == 0:
                    self.diretorio_atual = os.path.dirname(self.diretorio_atual)
                    self.selecao_idx = 0
                else:
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