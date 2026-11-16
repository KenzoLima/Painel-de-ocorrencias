"""
Gera o painel semanal de ocorrências a partir da planilha "Análise de Ocorrências".

Uso:
    python gerar_painel.py "Análise de Ocorrências - 9-11.xlsm"  [saida.html]

Lê:
  - aba "0. ANAYLSIS"  -> ocorrências (cliente, placa, tipo, dias, observação, ação, não notificar)
  - aba "99. SETUP"    -> contatos dos clientes (colunas CLIENTE / NOME / TELEFONE)
Gera um único arquivo HTML, sem dependências, que abre em qualquer navegador.
"""
import datetime
import json
import re
import sys
from pathlib import Path

import openpyxl

TIPOS = {
    "OFFLINE": {"rotulo": "Offline", "emoji": "📵", "frase": "Equipamento sem comunicação"},
    "CAMERA ABNORMALITY": {"rotulo": "Câmera com falha", "emoji": "📷", "frase": "Câmera sem imagem"},
    "CONSUMO CHIP": {"rotulo": "Consumo de chip alto", "emoji": "📶", "frase": "Consumo de dados acima do previsto"},
    "SEM CONSUMO": {"rotulo": "Operando sem consumo", "emoji": "💤", "frase": "Veículo rodando sem enviar dados"},
    "STORAGE DOES NOT EXIST": {"rotulo": "Cartão SD ausente", "emoji": "💾", "frase": "Cartão de memória não detectado"},
}


def txt(v):
    return "" if v is None else str(v).strip()


def ler(caminho):
    wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)

    ws = wb["0. ANAYLSIS"]
    atualizacao = ws["I2"].value
    if isinstance(atualizacao, datetime.datetime):
        atualizacao = atualizacao.date().isoformat()

    ocorrencias = []
    for row in ws.iter_rows(min_row=5, values_only=True):
        cliente, tipo = txt(row[2]), txt(row[6]).upper()
        if not cliente or not tipo:
            continue
        inicio = row[7]
        if isinstance(inicio, datetime.datetime):
            inicio = inicio.date().isoformat()
        try:
            dias = round(float(row[8]))
        except (TypeError, ValueError):
            dias = None
        obs = txt(row[9])
        item = {
            "cliente": cliente,
            "placa": txt(row[3]),
            "serial": txt(row[4]),
            "tipo": tipo,
            "inicio": txt(inicio),
            "dias": dias,
            "obs": obs,
            "acao": txt(row[10]),
            "naoNotificar": txt(row[11]).upper() == "X",
        }
        m = re.search(r"PROPORCIONAL:\s*(\d+)%\s*ATUAL:\s*(\d+)%", obs)
        if m:
            item["esperado"], item["atual"] = int(m.group(1)), int(m.group(2))
        m = re.search(r"CHANNEL NUMBER\s+(\d+)", obs)
        if m:
            item["canal"] = int(m.group(1))
        ocorrencias.append(item)

    contatos = {}
    ws = wb["99. SETUP"]
    for row in ws.iter_rows(min_row=2, values_only=True):
        cliente = txt(row[8])
        if cliente and cliente not in contatos:
            contatos[cliente] = {"nome": txt(row[9]), "telefone": re.sub(r"\D", "", txt(row[10]))}

    return {"atualizacao": txt(atualizacao), "ocorrencias": ocorrencias, "contatos": contatos, "tipos": TIPOS}


def recurso(nome):
    # no .exe (PyInstaller) os arquivos ficam em sys._MEIPASS
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / nome
    return Path(__file__).resolve().parent.parent / "assets" / nome


def gerar(entrada, saida):
    dados = ler(entrada)
    modelo = recurso("painel_modelo.html").read_text(encoding="utf-8")
    payload = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    Path(saida).write_text(modelo.replace("/*__DADOS__*/null", payload), encoding="utf-8")
    return dados


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    entrada = Path(sys.argv[1])
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "output" / "painel_ocorrencias.html"
    dados = gerar(entrada, saida)
    print(f"{len(dados['ocorrencias'])} ocorrências -> {saida}")


if __name__ == "__main__":
    main()
