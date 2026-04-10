# 🐸 Corrida dos Sapos — UI Local

Interface web para acompanhar a corrida em tempo real no navegador, com o Python rodando as threads no backend via **Flask + Server-Sent Events**.

---

## 📁 Estrutura do projeto

```
corrida_sapos/
├── app.py
├── requirements.txt
└── templates/
    └── index.html
```

---

## ⚙️ Instalação

### 1. Crie e ative o ambiente virtual

```bash
# Criar
python -m venv venv

# Ativar — Windows
venv\Scripts\activate

# Ativar — Linux/macOS
source venv/bin/activate
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

> Só é necessário instalar o **Flask**. As threads (`threading`), `random`, `time`, `json` e `queue` são da biblioteca padrão do Python.

---

## ▶️ Como rodar

```bash
python app.py
```

Depois abra no navegador:

```
http://localhost:5000
```

Clique em **Iniciar corrida** e acompanhe os sapos em tempo real.

---

## 🧠 Como funciona

```
Navegador  ──── GET /         ──►  Flask renderiza index.html
           ──── GET /iniciar  ──►  Flask cria 4 threads (uma por sapo)
           ──── GET /stream   ──►  EventSource recebe progresso em tempo real
                                   via Server-Sent Events (SSE)
```

Cada sapo roda em sua própria thread Python e envia eventos para uma `queue.Queue`. O endpoint `/stream` lê essa fila e transmite os dados para o navegador, que atualiza as barras sem precisar recarregar a página.

---

## ✏️ Customizações

Edite o topo de `app.py`:

| Variável | Padrão | O que muda |
|---|---|---|
| `DISTANCIA_TOTAL` | `50` | Comprimento da pista |
| `SAPOS` | 4 sapos | Adicione/remova dicionários na lista |

Em cada sapo você pode trocar `nome`, `emoji` e `cor` (hex).
