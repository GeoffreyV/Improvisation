import os
import re
import shutil
import urllib.parse  # Pour encoder correctement les noms de fichiers dans les liens

# Dossiers d'entrée (Obsidian) et de sortie (GitHub Pages)
DOSSIER_ORIGINAL = "notes"  # Dossier où sont tes notes pour Obsidian
DOSSIER_GITHUB = "output"  # Dossier où seront stockées les versions modifiées

# Expressions régulières pour détecter les liens Obsidian
LIEN_OBSIDIAN = re.compile(r"(?<!\!)\[\[([^\]]+)\]\]")  # [[Nom de la Note]]
APERCU_OBSIDIAN = re.compile(r"!\[\[([^\]]+)\]\]")  # ![[Nom de la Note]]

# Expression régulière pour détecter les callouts [!type]
CALLOUT_OBSIDIAN = re.compile(r"^\[!(\w+)\](.*)", re.MULTILINE)

# Mapping des callouts vers des classes CSS
CALLOUT_MAPPING = {
    "note": "callout-note",
    "success": "callout-success",
    "warning": "callout-warning",
    "danger": "callout-danger",
    "tip": "callout-tip",
    "info": "callout-info"
}

def normaliser_nom_fichier(nom):
    """
    Transforme 'Nom de la Note' en 'Nom-de-la-Note.md'
    et encode les caractères spéciaux pour les liens Markdown.
    """
    nom_sans_espace = nom.replace(" ", "-")  # Remplace les espaces par des tirets
    nom_nettoye = re.sub(r"[^\w\-]", "", nom_sans_espace)  # Supprime les caractères spéciaux
    return nom_nettoye + ".md"

def convertir_liens_obsidian(texte):
    """ Remplace [[Nom de la Note]] par [Nom de la Note](Nom-de-la-Note.md) """
    texte = LIEN_OBSIDIAN.sub(lambda match: f"[{match.group(1)}]({urllib.parse.quote(normaliser_nom_fichier(match.group(1)))})", texte)
    texte = APERCU_OBSIDIAN.sub(lambda match: f"{{% include_relative {normaliser_nom_fichier(match.group(1))} %}}", texte)
    return texte

def convertir_callouts(texte):
    """ Remplace [!type] par un bloc HTML stylisé pour GitHub Pages """
    def remplacer(match):
        callout_type = match.group(1).lower()  # Convertir en minuscule
        contenu = match.group(2).strip()  # Contenu après le callout

        # Vérifier si le type de callout est connu
        css_class = CALLOUT_MAPPING.get(callout_type, "callout-default")

        return f"""
<div class="{css_class}">
    <strong>{callout_type.capitalize()}</strong>
    <p>{contenu}</p>
</div>
        """.strip()

    return CALLOUT_OBSIDIAN.sub(remplacer, texte)

def traiter_fichier(chemin_fichier, dossier_sortie):
    """ Convertit les liens Obsidian et les callouts dans un fichier Markdown """
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        contenu = fichier.read()

    contenu_converti = convertir_liens_obsidian(contenu)
    contenu_converti = convertir_callouts(contenu_converti)

    # Définir le chemin de sortie
    chemin_sortie = chemin_fichier.replace(DOSSIER_ORIGINAL, dossier_sortie, 1)
    os.makedirs(os.path.dirname(chemin_sortie), exist_ok=True)

    # Écrire le fichier converti
    with open(chemin_sortie, "w", encoding="utf-8") as fichier:
        fichier.write(contenu_converti)

    print(f"✅ Converti : {chemin_sortie}")

def copier_notes(dossier_entree, dossier_sortie):
    """ Copie tous les fichiers Markdown en conservant l'arborescence et applique la conversion """
    if os.path.exists(dossier_sortie):
        shutil.rmtree(dossier_sortie)  # Supprime l'ancien dossier output pour tout recréer
    os.makedirs(dossier_sortie, exist_ok=True)

    for racine, _, fichiers in os.walk(dossier_entree):
        for fichier in fichiers:
            print(f"📄 Copie : {fichier}")
            if fichier.endswith(".md"):
                print(f"📄 Traitement : {fichier}")
                chemin_fichier = os.path.join(racine, fichier)
                traiter_fichier(chemin_fichier, dossier_sortie)

# Exécution du script
copier_notes(DOSSIER_ORIGINAL, DOSSIER_GITHUB)
