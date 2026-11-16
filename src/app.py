"""
Painel de Ocorrências — janela simples para escolher a planilha e abrir o painel.

Também aceita o caminho da planilha como argumento (arrastar a planilha
sobre o ícone ou "Abrir com" funciona).
"""
import json
import os
import sys
import threading
import tkinter as tk
import traceback
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

from gerar_painel import gerar, recurso

APP = "Painel de Ocorrências"
PASTA = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "PainelOcorrencias"
SAIDA = PASTA / "painel_ocorrencias.html"   # caminho fixo: mantém as marcações de "enviado"
CONFIG = PASTA / "config.json"

AZUL = "#1f8fe5"
FUNDO = "#f6f5f2"
TINTA = "#1d1c1a"
TINTA2 = "#6b675f"


def carregar_cfg():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {}


def salvar_cfg(cfg):
    try:
        PASTA.mkdir(parents=True, exist_ok=True)
        CONFIG.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def abrir_painel():
    webbrowser.open(SAIDA.as_uri())


class App:
    def __init__(self, root):
        self.root = root
        self.cfg = carregar_cfg()
        root.title(APP)
        root.configure(bg=FUNDO)
        root.resizable(False, False)
        try:
            root.iconbitmap(default=str(recurso("trackservices.ico")))
        except Exception:
            pass

        wrap = tk.Frame(root, bg=FUNDO, padx=28, pady=24)
        wrap.pack()

        topo = tk.Frame(wrap, bg=FUNDO)
        topo.pack(fill="x")
        try:
            self.logo = tk.PhotoImage(file=str(recurso("trackservices.png")))
            tk.Label(topo, image=self.logo, bg=FUNDO).pack(side="left", padx=(0, 12))
        except Exception:
            pass
        txt = tk.Frame(topo, bg=FUNDO)
        txt.pack(side="left")
        tk.Label(txt, text=APP, font=("Segoe UI Semibold", 15), fg=TINTA, bg=FUNDO).pack(anchor="w")
        tk.Label(txt, text="TrackServices", font=("Segoe UI", 10), fg=TINTA2, bg=FUNDO).pack(anchor="w")

        tk.Label(
            wrap,
            text="Escolha a planilha \"Análise de Ocorrências\" (.xlsm)\npara gerar o painel da semana.",
            font=("Segoe UI", 10), fg=TINTA2, bg=FUNDO, justify="left",
        ).pack(anchor="w", pady=(18, 14))

        self.btn = tk.Button(
            wrap, text="Escolher planilha…", command=self.escolher,
            font=("Segoe UI Semibold", 11), bg=AZUL, fg="white", activebackground="#1873b8",
            activeforeground="white", relief="flat", padx=18, pady=8, cursor="hand2",
        )
        self.btn.pack(fill="x")

        self.btn_ult = tk.Button(
            wrap, text="Abrir último painel", command=abrir_painel,
            font=("Segoe UI", 10), bg="white", fg=TINTA, relief="solid", bd=1, padx=12, pady=6, cursor="hand2",
        )
        self.btn_ult.pack(fill="x", pady=(8, 0))
        if not SAIDA.exists():
            self.btn_ult.configure(state="disabled")

        self.status = tk.Label(wrap, text=self.texto_ultimo(), font=("Segoe UI", 9), fg=TINTA2, bg=FUNDO,
                               wraplength=320, justify="left")
        self.status.pack(anchor="w", pady=(14, 0))

        root.update_idletasks()
        w, h = root.winfo_width(), root.winfo_height()
        root.geometry(f"+{(root.winfo_screenwidth() - w) // 2}+{(root.winfo_screenheight() - h) // 3}")

    def texto_ultimo(self):
        u = self.cfg.get("ultima")
        return f"Última planilha: {Path(u).name}" if u else ""

    def escolher(self):
        ini = self.cfg.get("pasta") or str(Path.home() / "Documents")
        caminho = filedialog.askopenfilename(
            title="Escolher planilha de ocorrências", initialdir=ini,
            filetypes=[("Planilhas Excel", "*.xlsm *.xlsx"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.processar(caminho)

    def processar(self, caminho):
        self.btn.configure(state="disabled", text="Gerando painel…")
        self.status.configure(text=f"Lendo {Path(caminho).name}…")
        threading.Thread(target=self._gerar, args=(caminho,), daemon=True).start()

    def _gerar(self, caminho):
        try:
            PASTA.mkdir(parents=True, exist_ok=True)
            dados = gerar(caminho, SAIDA)
            self.root.after(0, self._ok, caminho, len(dados["ocorrencias"]))
        except PermissionError:
            self.root.after(0, self._erro, "A planilha está bloqueada. Feche-a no Excel e tente de novo.", "")
        except KeyError as e:
            self.root.after(0, self._erro, f"A planilha não tem a aba esperada: {e}.\n"
                                           "Ela precisa das abas \"0. ANAYLSIS\" e \"99. SETUP\".", "")
        except Exception as e:
            self.root.after(0, self._erro, f"Não foi possível ler a planilha:\n{e}", traceback.format_exc())

    def _ok(self, caminho, n):
        self.cfg.update(ultima=caminho, pasta=str(Path(caminho).parent))
        salvar_cfg(self.cfg)
        self.btn.configure(state="normal", text="Escolher planilha…")
        self.btn_ult.configure(state="normal")
        self.status.configure(text=f"{n} ocorrências lidas de {Path(caminho).name}. Painel aberto no navegador.")
        abrir_painel()

    def _erro(self, msg, detalhe):
        self.btn.configure(state="normal", text="Escolher planilha…")
        self.status.configure(text=self.texto_ultimo())
        if detalhe:
            try:
                (PASTA / "erro.log").write_text(detalhe, encoding="utf-8")
            except Exception:
                pass
        messagebox.showerror(APP, msg)


def main():
    try:  # nitidez em telas com escala
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    app = App(root)
    if len(sys.argv) > 1 and Path(sys.argv[1]).is_file():
        root.after(200, app.processar, sys.argv[1])
    root.mainloop()


if __name__ == "__main__":
    main()
