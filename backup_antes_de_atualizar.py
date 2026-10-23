"""Cria um backup local do projeto e do SQLite antes de uma atualização.
Uso: python backup_antes_de_atualizar.py
"""
from pathlib import Path
from datetime import datetime
import shutil

raiz=Path(__file__).resolve().parent
destino=raiz.parent / f"backup_confeitaria_{datetime.now():%Y%m%d_%H%M%S}"
ignorar=shutil.ignore_patterns('__pycache__','.git','staticfiles','*.pyc')
shutil.copytree(raiz,destino,ignore=ignorar)
print(f'Backup criado em: {destino}')
