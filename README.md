# Prescrição UPA – Aparecida de Goiânia

Aplicação web para geração de prescrições médicas e evoluções de enfermaria da UPA 24h de Aparecida de Goiânia.

## Deploy no Render (gratuito)

### 1. Crie uma conta no GitHub
Acesse https://github.com e crie uma conta gratuita se ainda não tiver.

### 2. Crie um repositório
- Clique em "New repository"
- Nome: `prescricao-upa`
- Marque "Public"
- Clique em "Create repository"

### 3. Faça upload dos arquivos
- Clique em "uploading an existing file"
- Arraste todos os arquivos desta pasta (app.py, requirements.txt, Procfile, e a pasta static/ com index.html e logo.png)
- Clique em "Commit changes"

### 4. Deploy no Render
- Acesse https://render.com e crie uma conta gratuita (pode entrar com o GitHub)
- Clique em "New +" → "Web Service"
- Conecte seu repositório GitHub `prescricao-upa`
- Configure:
  - **Name**: prescricao-upa
  - **Runtime**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app`
  - **Instance Type**: Free
- Clique em "Create Web Service"

### 5. Acesse
Após ~2 minutos o Render fornece um link tipo:
`https://prescricao-upa.onrender.com`

Salve esse link no favoritos do navegador. Funciona em qualquer computador ou celular.

## Estrutura
```
upa_app/
├── app.py              # Backend Flask
├── requirements.txt    # Dependências Python
├── Procfile            # Comando de start para o Render
└── static/
    ├── index.html      # Frontend
    └── logo.png        # Logo da Prefeitura de Aparecida
```
