# TechCorp AI — Interface Chat (DEV WEB)

Interface web Streamlit connectée à Ollama pour discuter avec le modèle **Phi-3.5-Financial**.

## Prérequis

- Python 3.10+
- Accès réseau à un serveur Ollama (le serveur d'inférence, fourni par la filière INFRA) :
  - soit le serveur partagé de l'équipe INFRA (par défaut `http://10.70.0.179:11434`),
  - soit une instance [Ollama](https://ollama.com/download) installée et démarrée en local.

## 1. Installer les dépendances Python

Depuis le dossier `web_app/` :

```bash
pip install -r requirements.txt
```

## 2. Configurer le serveur Ollama

Par défaut, l'interface se connecte au serveur partagé `http://10.70.0.179:11434` — aucune installation locale d'Ollama n'est nécessaire. Vérifier qu'il répond :

```bash
Invoke-RestMethod -Uri http://10.70.0.179:11434/api/tags
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

Les paramètres d'inférence (modèle, température, max tokens) sont réglables directement dans la barre latérale de l'interface, sous **Paramètres**. Si aucun modèle `phi3.5-financial` n'est trouvé, le sélecteur liste automatiquement les modèles disponibles sur le serveur Ollama (par exemple `phi3.5:latest` sur le serveur partagé INFRA).

## Dépannage

| Problème | Solution |
|---|---|
| Badge "Ollama · hors ligne" dans la sidebar | Vérifier la connectivité réseau vers le serveur Ollama configuré (`OLLAMA_BASE_URL`, par défaut `http://10.70.0.179:11434/api/version`) |
| Le modèle `phi3.5-financial` n'apparaît pas dans la liste | Normal si ce modèle custom n'a pas été créé sur le serveur cible ; choisir un modèle disponible (ex. `phi3.5:latest`) dans le sélecteur, ou lancer `ollama create phi3.5-financial -f ollama_server/Modelfile` sur ce serveur |
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
