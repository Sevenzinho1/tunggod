# 🪽 Tung Bot — Setup

## 1. Instale as dependências

```bash
pip install discord.py pytz
```

---

## 2. Crie o bot no Discord Developer Portal

1. Acesse https://discord.com/developers/applications
2. Clique em **New Application** → dê um nome
3. Vá em **Bot** → clique em **Reset Token** e copie o token
4. Ainda em **Bot**, ative os seguintes **Privileged Gateway Intents**:
   - ✅ SERVER MEMBERS INTENT
   - ✅ GUILD MODERATION (ou Ban Members)
5. Vá em **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `View Audit Log`, `Embed Links`, `Read Message History`
6. Copie a URL gerada e convide o bot para o seu servidor

---

## 3. Suba a imagem do Tung

- Faça upload da imagem `images.jpg` em qualquer serviço de hospedagem de imagens, por exemplo:
  - https://imgur.com → faça upload e copie o link direto (termina em `.jpg`)
  - Ou envie a imagem em um canal do Discord e copie o link
- Cole a URL no campo `IMAGEM_TUNG` dentro de `tung_bot.py`

---

## 4. Configure o arquivo

Abra `tung_bot.py` e preencha as 3 variáveis no topo:

```python
TOKEN = "seu_token_aqui"
CANAL_GERAL_NOME = "geral"        # nome exato do canal (sem #)
IMAGEM_TUNG = "https://..."       # URL da imagem
```

---

## 5. Execute o bot

```bash
python tung_bot.py
```

---

## Eventos cobertos

| Evento | Mensagem |
|---|---|
| Membro banido | 🔨 Banido |
| Membro expulso (kick) | 👢 Expulso (Kick) |
| Membro saiu voluntariamente | 🚪 Saiu do servidor |

O horário segue sempre o **fuso horário de Brasília (GMT-3)**.
