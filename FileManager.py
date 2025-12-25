import os
import shutil
from datetime import datetime
import time
import winsound  # <--- Nativo do Windows! Não precisa de PIP.

class FileManager:
    def __init__(self):
        # Define a raiz na pasta 'Telefone' dentro da pasta dos scripts
        self.raiz_simulada = os.path.join(os.getcwd(), "Telefone")
        
        # Cria a estrutura inicial se não existir
        if not os.path.exists(self.raiz_simulada):
            os.makedirs(os.path.join(self.raiz_simulada, "Toques"))
            os.makedirs(os.path.join(self.raiz_simulada, "Fotos"))
            
        self.diretorio_atual = self.raiz_simulada
        self.selecao_idx = 0
        self.filtro_arquivos = []
        self.arquivo_em_copia = None

    def atualizar_lista(self):
        try:
            conteudo = os.listdir(self.diretorio_atual)
            pastas = [f for f in conteudo if os.path.isdir(os.path.join(self.diretorio_atual, f))]
            arquivos = [f for f in conteudo if os.path.isfile(os.path.join(self.diretorio_atual, f))]
            self.filtro_arquivos = sorted(pastas) + sorted(arquivos)
        except Exception:
            self.diretorio_atual = self.raiz_simulada
            self.atualizar_lista()

    # --- Utilitários de Som e Diálogo ---

    def tocar_toque(self, nome_item):
        import SYSTEM
        caminho = os.path.join(self.diretorio_atual, nome_item)
        
        try:
            # SND_FILENAME: toca um arquivo / SND_ASYNC: não trava o programa enquanto toca
            winsound.PlaySound(caminho, winsound.SND_FILENAME | winsound.SND_ASYNC)
            
            while True:
                linhas = [
                    "",
                    SYSTEM.centralizar("Reproduzindo..."),
                    SYSTEM.centralizar(f"🎵 {nome_item[:15]}"),
                    "",
                    SYSTEM.centralizar("Sair: Botão Dir.")
                ]
                SYSTEM.renderizar_tela_fixa("PLAYER", linhas, barra_status_esq="", barra_status_dir="Parar")
                
                tecla = SYSTEM.obter_entrada_tecla()
                if tecla == "aux_dir" or tecla == "ok":
                    winsound.PlaySound(None, winsound.SND_PURGE) # Para o som imediatamente
                    break
        except Exception:
            SYSTEM.renderizar_tela_fixa("ERRO", [SYSTEM.centralizar("O arquivo deve"), SYSTEM.centralizar("ser .WAV")], barra_status_dir="OK")
            time.sleep(1.5)

    def visualizar_txt(self, nome_item):
        import SYSTEM
        caminho = os.path.join(self.diretorio_atual, nome_item)
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                linhas = [l.strip()[:20] for l in f.readlines()[:9]]
            while True:
                SYSTEM.renderizar_tela_fixa(nome_item[:15].upper(), linhas, barra_status_esq="", barra_status_dir="Sair")
                if SYSTEM.obter_entrada_tecla() == "aux_dir": break
        except Exception:
            pass

    def tela_confirmacao(self, mensagem):
        import SYSTEM
        while True:
            linhas = ["", SYSTEM.centralizar(mensagem), "", ""]
            SYSTEM.renderizar_tela_fixa("CONFIRMAR?", linhas, barra_status_esq="Sim", barra_status_dir="Não")
            tecla = SYSTEM.obter_entrada_tecla()
            if tecla == "aux_esq": return True
            if tecla == "aux_dir": return False

    # --- Menu de Opções ---

    def menu_opcoes(self, nome_item):
        import SYSTEM
        opcoes = {"1": "Adicionar Pasta", "2": "Copiar", "3": "Apagar", "4": "Info"}
        sel = 0
        chaves = sorted(opcoes.keys())
        
        while True:
            linhas = [f"{'->' if i == sel else '  '}{k}. {opcoes[k]}" for i, k in enumerate(chaves)]
            SYSTEM.renderizar_tela_fixa("OPÇÕES", linhas, barra_status_esq="OK", barra_status_dir="Voltar")
            tecla = SYSTEM.obter_entrada_tecla()
            
            if tecla == "up": sel = (sel - 1) % len(chaves)
            elif tecla == "down": sel = (sel + 1) % len(chaves)
            elif tecla == "aux_dir": return
            elif tecla == "ok" or tecla == "aux_esq":
                escolha = chaves[sel]
                caminho_item = os.path.join(self.diretorio_atual, nome_item)

                if escolha == "1": # Adicionar Pasta (Simples)
                    nova = os.path.join(self.diretorio_atual, "Nova Pasta")
                    os.makedirs(nova, exist_ok=True)
                elif escolha == "2": # Copiar
                    self.arquivo_em_copia = caminho_item
                elif escolha == "3": # Apagar
                    if not os.path.isdir(caminho_item):
                        if self.tela_confirmacao("Apagar arquivo?"):
                            os.remove(caminho_item)
                return

    # --- Loop Principal ---

    def iniciar(self):
        import SYSTEM
        while True:
            self.atualizar_lista()
            pode_voltar = self.diretorio_atual != self.raiz_simulada
            
            conteudo_tela = []
            if pode_voltar:
                conteudo_tela.append(f"{'->' if self.selecao_idx == 0 else '  '} [..] Voltar")
            
            start_idx = 1 if pode_voltar else 0
            for i, item in enumerate(self.filtro_arquivos):
                idx_real = i + start_idx
                prefixo = "->" if self.selecao_idx == idx_real else "  "
                
                # Ícones
                ext = item.lower()
                icone = "📁" if os.path.isdir(os.path.join(self.diretorio_atual, item)) else "📄"
                if ext.endswith('.wav'): icone = "🎵"
                
                conteudo_tela.append(f"{prefixo}{icone}{item[:15]}")

            status_esq = "COLAR" if self.arquivo_em_copia else "Opções"
            titulo = os.path.basename(self.diretorio_atual) if pode_voltar else "Memória"
            
            SYSTEM.renderizar_tela_fixa(f"📁 {titulo}", conteudo_tela, barra_status_esq=status_esq, barra_status_dir="Sair")
            
            tecla = SYSTEM.obter_entrada_tecla()
            
            if tecla == "up": self.selecao_idx = (self.selecao_idx - 1) % len(conteudo_tela) if conteudo_tela else 0
            elif tecla == "down": self.selecao_idx = (self.selecao_idx + 1) % len(conteudo_tela) if conteudo_tela else 0
            elif tecla == "aux_dir": return "MENU_PRINCIPAL"
            
            elif tecla == "aux_esq":
                if self.arquivo_em_copia:
                    if self.tela_confirmacao("Colar aqui?"):
                        shutil.copy2(self.arquivo_em_copia, os.path.join(self.diretorio_atual, os.path.basename(self.arquivo_em_copia)))
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
                    elif item_nome.lower().endswith('.wav'):
                        self.tocar_toque(item_nome)
                    elif item_nome.lower().endswith('.txt'):
                        self.visualizar_txt(item_nome)

def abrir_gerenciador():
    fm = FileManager()
    return fm.iniciar()