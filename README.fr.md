# Morgan

[English](README.md) | **Français**

Morgan est une newsletter tech quotidienne et personnalisée, publiée sur Discord.

Chaque jour, Morgan récupère les articles des dernières 24 h depuis des flux RSS, demande à un LLM de sélectionner et de résumer ceux qui te concernent, puis poste le résultat dans un salon Discord.

Tes préférences (qui tu es, tes sujets, le format, les sources) vivent dans un simple fichier texte, `profile.md`, que tu écris comme tu veux.

## Prérequis

- Python 3.10 ou plus récent
- Une clé API Gemini (gratuite) : <https://aistudio.google.com/apikey>
- Un serveur Discord sur lequel tu peux ajouter un bot

## Installation

```bash
git clone git@github.com:Alioune4/Morgan.git
cd Morgan
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
cp profile.example.md profile.md
```

## Créer le bot Discord

1. Va sur <https://discord.com/developers/applications> et clique sur **New Application**.
2. Dans l'onglet **Bot**, clique sur **Reset Token** et copie le token : c'est ton `DISCORD_TOKEN`.
3. Dans l'onglet **OAuth2 → URL Generator**, coche le scope `bot`, puis les permissions **View Channels** et **Send Messages**.
4. Ouvre l'URL générée et ajoute le bot à ton serveur.
5. Dans Discord, active le mode développeur (**Paramètres → Avancés → Mode développeur**), puis fais un clic droit sur le salon de ton choix → **Copier l'identifiant du salon** : c'est ton `DISCORD_CHANNEL_ID`.

## Configuration

### `.env`

```
GEMINI_API_KEY=ta-clé-gemini
DISCORD_TOKEN=le-token-du-bot
DISCORD_CHANNEL_ID=l-id-du-salon
```

Options :

- `LLM_MODEL` : le modèle à utiliser, au format [LiteLLM](https://docs.litellm.ai/docs/providers) (par défaut `gemini/gemini-3.5-flash`). Pour un autre fournisseur, ajoute aussi sa clé API dans `.env`.
- `PROFILE_PATH` : le chemin du profil (par défaut `profile.md` à la racine).

Ne commite jamais `.env` : il est déjà dans le `.gitignore`.

### `profile.md`

C'est là que tu personnalises ta newsletter. Écris-le librement : il est donné tel quel à l'IA.

- Décris qui tu es (métier, niveau, stack) : l'IA s'en sert pour juger ce qui te concerne.
- Liste ce qui t'intéresse et ce que tu ne veux pas voir.
- Précise le format souhaité (langue, longueur, présentation).
- Dans la section `## Sources`, mets une URL de flux RSS par ligne. Tu peux ajouter un commentaire après l'URL.

Pour suivre une chaîne YouTube, utilise `https://www.youtube.com/feeds/videos.xml?channel_id=<ID de la chaîne>`.

`profile.md` est ignoré par git : il reste privé.

## Lancer

Pour voir la newsletter dans le terminal sans rien publier :

```bash
venv/bin/python src/main.py --dry-run
```

Pour la publier sur Discord :

```bash
venv/bin/python src/main.py
```

## Envoi automatique chaque jour

### Avec GitHub Actions (recommandé)

Pas besoin de garder une machine allumée : le workflow `.github/workflows/newsletter.yml` lance Morgan tous les jours à 8 h, heure de Paris.

1. Forke le dépôt.
2. Dans **Settings → Secrets and variables → Actions**, crée ces secrets, ou fais-le avec la CLI `gh` :

   ```bash
   gh secret set GEMINI_API_KEY
   gh secret set DISCORD_TOKEN
   gh secret set DISCORD_CHANNEL_ID
   gh secret set PROFILE < profile.md
   ```

   `PROFILE` contient tout ton `profile.md`. Pense à le remettre à jour avec la même commande quand tu modifies ton profil.
3. Optionnel : pour changer de modèle, crée une variable (pas un secret) `LLM_MODEL`.
4. Dans l'onglet **Actions**, active les workflows s'ils sont désactivés sur ton fork.
5. Pour tester, lance **Daily newsletter → Run workflow** : par défaut, l'option `dry_run` est cochée et la newsletter s'affiche dans les logs sans être publiée.

L'heure de déclenchement de GitHub peut avoir quelques minutes de retard. Sur un dépôt public sans activité pendant 60 jours, GitHub désactive les tâches planifiées : il suffit de les réactiver depuis l'onglet **Actions**.

### Avec cron

Avec cron (Linux, macOS ou WSL), pour un envoi tous les jours à 8 h :

```bash
crontab -e
```

puis ajoute la ligne suivante, en adaptant le chemin :

```
0 8 * * * cd /chemin/vers/Morgan && { echo "=== $(date)"; venv/bin/python src/main.py; } >> logs/morgan.log 2>&1
```

Crée le dossier `logs/` avant (`mkdir logs`). Les erreurs éventuelles seront dans `logs/morgan.log`.

L'heure suit le fuseau horaire de la machine. La machine doit être allumée à 8 h : si elle est éteinte, l'envoi du jour est sauté. Sous WSL, la distribution doit aussi être lancée, avec systemd activé (`systemd=true` dans `/etc/wsl.conf`).

## Structure

```
src/
  main.py                  point d'entrée : RSS → IA → Discord
  user_profile.py          lecture du profil et de ses sources
  rss/get_daily_feed.py    récupération et nettoyage des articles des dernières 24 h
  ai/                      génération de la newsletter via LiteLLM
  discord_bot/bot.py       envoi dans le salon, découpé en messages de 2000 caractères
  contract_objects/        structure d'un article
```
