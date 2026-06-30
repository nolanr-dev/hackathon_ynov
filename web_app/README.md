# TechCorp AI — Interface Chat (DEV WEB)

Interface web Streamlit connectée à Ollama pour discuter avec le modèle **Phi-3.5-Financial**.

## Prérequis

- Python 3.10+
- Accès réseau à un serveur Ollama (le serveur d'inférence, fourni par la filière INFRA) :
  - soit le serveur partagé de l'équipe INFRA (par défaut `http://10.70.0.50:11434`, modèle `phi3.5-financial`) — accessible uniquement depuis le **VLAN Étudiant Ynov (10.70.0.0/24)**, donc être connecté à ce réseau/VPN est indispensable,
  - soit une instance [Ollama](https://ollama.com/download) installée et démarrée en local.

## 1. Installer les dépendances Python

Depuis le dossier `web_app/` :

```bash
pip install -r requirements.txt
```

## 2. Configurer le serveur Ollama

Par défaut, l'interface se connecte au serveur partagé `http://10.70.0.50:11434` — aucune installation locale d'Ollama n'est nécessaire. Vérifier qu'il répond :

```bash
Invoke-RestMethod -Uri http://10.70.0.50:11434/api/tags
```

Pour pointer vers un autre serveur (par exemple une instance Ollama locale sur `http://localhost:11434`), définir la variable d'environnement `OLLAMA_BASE_URL` avant de lancer Streamlit :

```bash
# PowerShell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
```

> Si vous utilisez une instance locale, démarrez-la avec `ollama serve` puis créez le modèle custom avec `ollama create phi3.5-financial -f ollama_server/Modelfile` (Modelfile fourni par INFRA).

## 3. Lancer l'interface

Toujours depuis `web_app/` :

```bash
streamlit run app.py
```

L'interface s'ouvre dans le navigateur sur `http://localhost:8501`.

## Tout en une fois (récap)

```bash
cd web_app
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Les paramètres d'inférence (température, max tokens) sont réglables directement dans la barre latérale de l'interface, sous **Paramètres**. Le modèle utilisé est `phi3.5-financial` par défaut (`backend_api.DEFAULT_MODEL`) ; si ce modèle n'est pas trouvé sur le serveur ciblé, l'app bascule automatiquement sur le premier modèle disponible.

## Dépannage

| Problème | Solution |
|---|---|
| Badge "Ollama · hors ligne" dans la sidebar, ou erreur `ConnectTimeoutError` lors de l'envoi d'un message | Le serveur partagé INFRA (`10.70.0.50:11434`) n'est accessible que depuis le **VLAN Étudiant Ynov (10.70.0.0/24)** — vérifier la connexion réseau/VPN, puis tester `Invoke-RestMethod -Uri http://10.70.0.50:11434/api/version` |
| Le modèle `phi3.5-financial` n'apparaît pas dans la liste | Choisir un modèle disponible dans le sélecteur, ou lancer `ollama create phi3.5-financial -f ollama_server/Modelfile` sur le serveur ciblé |
| `ModuleNotFoundError: streamlit` | Relancer `pip install -r requirements.txt` dans l'environnement Python utilisé |
| Port 8501 déjà utilisé | `streamlit run app.py --server.port 8502` |

## Structure du projet

```
web_app/
├── app.py                   # point d'entrée (streamlit run app.py)
├── backend_api.py           # client Ollama + persistance de l'historique
├── state.py                 # état de session Streamlit
├── requirements.txt
├── .streamlit/config.toml   # thème sombre
├── assets/techcorp_logo.png
├── data/conversations.json  # historique des conversations (persisté)
└── components/
    ├── styles.py            # CSS de l'interface
    ├── sidebar.py            # branding, statut Ollama, historique, paramètres
    ├── chat.py                # affichage des messages, suggestions, envoi
    └── cyber_security.py      # bandeau d'audit sécurité (backdoor identifiée par CYBER)
```
