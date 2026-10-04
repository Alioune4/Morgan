import os
from typing import List

from litellm import completion

from contract_objects.ai_daily_input import RSSEntryEssentials


DEFAULT_MODEL = "gemini/gemini-3.5-flash"

SYSTEM_PROMPT = """Tu es le rédacteur d'une newsletter tech quotidienne et personnelle, publiée sur Discord.
Voici le profil du lecteur, écrit par lui-même. Suis ses préférences de sujets, de format et de langue.

<profil>
{profile}
</profil>

Règles :
- Ne garde que les articles vraiment pertinents pour ce lecteur. Le nombre varie selon les jours : mieux vaut 3 bons articles que 10 moyens.
- Si plusieurs articles parlent du même sujet, fusionne-les en un seul point.
- Regroupe les articles par thème avec des titres `## Thème`.
- Mets chaque lien entre chevrons <https://...> pour éviter les aperçus Discord.
- Markdown compatible Discord : pas de tableaux, pas de titres `#` de niveau 1.
- N'invente rien qui ne figure pas dans les articles.
- Réponds uniquement avec la newsletter, sans phrase d'introduction ni commentaire sur le format."""


def request_personalized_newsletter(entries: List[RSSEntryEssentials], profile: str) -> str:
    response = completion(
        model=os.getenv("LLM_MODEL") or DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(profile=profile)},
            {"role": "user", "content": format_entries(entries)},
        ],
        num_retries=3,
    )
    return response.choices[0].message.content


def format_entries(entries: List[RSSEntryEssentials]) -> str:
    blocks = []
    for entry in entries:
        lines = [f"Titre : {entry.title}", f"Lien : {entry.link}"]
        if entry.tags:
            lines.append(f"Tags : {', '.join(entry.tags)}")
        text = entry.summary or entry.content
        if text:
            lines.append(f"Résumé : {text}")
        blocks.append("\n".join(lines))
    return "\n\n---\n\n".join(blocks)
