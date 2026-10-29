# Sistema de Confeitaria (Django)

Projeto reconstruído a partir do código enviado. Usa SQLite e pode rodar gratuitamente no Windows.

## 1. Instale Python
Instale Python 3.11+ e marque "Add Python to PATH".

## 2. Abra o PowerShell nesta pasta e execute

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Se o PowerShell bloquear a ativação, execute antes:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 3. Abra no navegador
- Site: http://127.0.0.1:8000/
- Administração: http://127.0.0.1:8000/admin/
- Painel: http://127.0.0.1:8000/painel/
- Produção: http://127.0.0.1:8000/producao/

## Primeiro uso
Entre em /admin/, cadastre Ingredientes, Produtos e as receitas de cada produto. Depois os produtos ativos aparecerão no cardápio.

## Observação
O arquivo original não continha todos os componentes importados (models.py, services.py, bot.py, settings.py, urls.py etc.). Esses arquivos foram implementados para tornar o projeto executável, mantendo as telas e o fluxo presentes no código enviado.


## Versão 8
Veja `ATUALIZACAO_V8.md` para os módulos de gestão integrada.
