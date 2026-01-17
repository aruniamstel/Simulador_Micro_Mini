import os
import json
import time
import keyboard

# Definição dos Temas (ANSI Escape Codes)
TEMAS = {
    "Clássico": {"fonte": "\033[37m", "fundo": "\033[40m", "reset": "\033[0m"},
    "Vintage":  {"fonte": "\033[30m", "fundo": "\033[42m", "reset": "\033[0m"},
    "Color":    {"fonte": "\033[30m", "fundo": "\033[47m", "reset": "\033[0m"}
}

CONFIG_FILE = "settings.json"
PIN_FILE = "pin.txt"

class ConfigManager:
    def __init__(self):
        self.config = self.carregar_config()
        self.tema_atual = self.config.get("tema", "Clássico")

    def carregar_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {"tema": "Clássico", "pin_ativo": False}

    def salvar_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    def obter_estilo(self):
        """Retorna a string de escape do tema atual."""
        t = TEMAS.get(self.tema_atual, TEMAS["Clássico"])
        return t["fundo"] + t["fonte"]

    def selecionar_tema(self):
        import SYSTEM
        opcoes = list(TEMAS.keys())
        idx = 0
        while True:
            conteudo = [f"{'-> ' if i == idx else '   '}{t}" for i, t in enumerate(opcoes)]
            SYSTEM.renderizar_tela_fixa("TEMAS", conteudo, barra_status_esq="Selecionar", barra_status_dir="Voltar")
            
            tecla = SYSTEM.obter_entrada_tecla()
            if tecla == "up": idx = (idx - 1) % len(opcoes)
            elif tecla == "down": idx = (idx + 1) % len(opcoes)
            elif tecla == "ok":
                self.tema_atual = opcoes[idx]
                self.config["tema"] = self.tema_atual
                self.salvar_config()
                return "MENU_PRINCIPAL"
            elif tecla == "aux_dir": return "SUBMENU"

    def gerenciar_pin(self):
        import SYSTEM
        if os.path.exists(PIN_FILE):
            SYSTEM.renderizar_tela_fixa("SEGURANÇA", ["PIN está ATIVO", "", "Deseja desativar?"], barra_status_esq="Sim", barra_status_dir="Não")
            if SYSTEM.obter_entrada_tecla() == "aux_esq":
                os.remove(PIN_FILE)
                self.config["pin_ativo"] = False
                self.salvar_config()
                SYSTEM.renderizar_tela_fixa("INFO", ["", SYSTEM.centralizar("PIN Desativado")], barra_status_esq="", barra_status_dir="")
                time.sleep(1.5)
            return "SUBMENU"
        else:
            SYSTEM.renderizar_tela_fixa("SEGURANÇA", ["PIN Desativado", "", "Deseja ativar?"], barra_status_esq="Sim", barra_status_dir="Não")
            if SYSTEM.obter_entrada_tecla() == "aux_esq":
                pin = ""
                while len(pin) < 5:
                    SYSTEM.renderizar_tela_fixa("NOVO PIN", ["Digite o PIN:", f"[{pin.ljust(8, '*')}]", "", "Mínimo 4 dígitos"], barra_status_esq="OK", barra_status_dir="Sair")
                    ev = keyboard.read_event(suppress=True)
                    if ev.event_type == keyboard.KEY_DOWN:
                        if ev.name.isdigit() and len(pin) < 8: pin += ev.name
                        elif ev.name == "backspace": pin = pin[:-1]
                        elif ev.name == "page up" and len(pin) >= 4:
                            with open(PIN_FILE, "w") as f: f.write(pin)
                            self.config["pin_ativo"] = True
                            self.salvar_config()
                            return "SUBMENU"
                        elif ev.name == "page down": return "SUBMENU"
            return "SUBMENU"

    def verificar_pin_boot(self):
        import SYSTEM
        if not os.path.exists(PIN_FILE): return True
        with open(PIN_FILE, "r") as f: pin_correto = f.read().strip()
        
        tentativa = ""
        while True:
            SYSTEM.renderizar_tela_fixa("SEGURANÇA", ["", "INSIRA O PIN", f"[{tentativa.ljust(8, '*')}]", ""], barra_status_esq="OK", barra_status_dir="Apagar")
            ev = keyboard.read_event(suppress=True)
            if ev.event_type == keyboard.KEY_DOWN:
                if ev.name.isdigit() and len(tentativa) < 8: tentativa += ev.name
                elif ev.name == "backspace": tentativa = tentativa[:-1]
                elif ev.name == "page up":
                    if tentativa == pin_correto: return True
                    else: 
                        tentativa = ""
                        SYSTEM.renderizar_tela_fixa("ERRO", ["", SYSTEM.centralizar("PIN INCORRETO")], barra_status_esq="", barra_status_dir="")
                        time.sleep(1.5)
        
    def resetar_confirmacao(self):
        import SYSTEM
        SYSTEM.renderizar_tela_fixa("RESET", ["", "Apagar todas as", "configurações?", ""], barra_status_esq="Sim", barra_status_dir="Não")
        if SYSTEM.obter_entrada_tecla() == "aux_esq":
            SYSTEM.renderizar_tela_fixa("RESET", ["", SYSTEM.centralizar("A reiniciar..."), "", ""], barra_status_esq="", barra_status_dir="")
            
            # Remove ficheiros
            if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            if os.path.exists(PIN_FILE): os.remove(PIN_FILE)
            
            # Reset variáveis locais
            self.config = {"tema": "Clássico", "pin_ativo": False}
            self.tema_atual = "Clássico"
            
            time.sleep(2)
            return "MENU_PRINCIPAL"
        return "SUBMENU"

config_manager = ConfigManager()