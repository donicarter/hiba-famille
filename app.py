import flet as ft
import os
import json

FICHIER = "depenses_hiba.json"
FOND_DEPART = 86500

def charger():
    if os.path.exists(FICHIER):
        try:
            with open(FICHIER, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def sauvegarder(depenses):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(depenses, f, ensure_ascii=False)

def main(page: ft.Page):
    page.title = "HIBA - Budget Famille"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    depenses = charger()

    txt_fond = ft.Text(f"Fond de depart: {FOND_DEPART} FCFA", size=18, weight="bold")
    txt_total = ft.Text(size=18)
    txt_reste = ft.Text(size=20, weight="bold", color=ft.Colors.GREEN)

    champ_quoi = ft.TextField(label="Quoi ? (ex: riz)", width=300)
    champ_montant = ft.TextField(label="Montant FCFA", width=300, keyboard_type=ft.KeyboardType.NUMBER)

    col_historique = ft.Column()

    def mettre_a_jour():
        total = sum(d["montant"] for d in depenses)
        reste = FOND_DEPART - total
        txt_total.value = f"Total depenses: {total} FCFA"
        txt_reste.value = f"Reste: {reste} FCFA"
        txt_reste.color = ft.Colors.GREEN if reste >= 0 else ft.Colors.RED
        
        col_historique.controls.clear()
        for d in reversed(depenses):
            col_historique.controls.append(
                ft.Text(f"- {d['quoi']}: {d['montant']} FCFA")
            )
        page.update()

    def ajouter(e):
        if not champ_quoi.value or not champ_montant.value:
            return
        try:
            montant = int(champ_montant.value)
        except:
            return
        depenses.append({"quoi": champ_quoi.value, "montant": montant})
        sauvegarder(depenses)
        champ_quoi.value = ""
        champ_montant.value = ""
        mettre_a_jour()

    btn = ft.ElevatedButton("Ajouter depense", bgcolor=ft.Colors.PINK_300, on_click=ajouter)

    page.add(
        ft.Text("HIBA - Budget Famille", size=24, color=ft.Colors.RED_400, weight="bold"),
        txt_fond,
        txt_total,
        txt_reste,
        ft.Divider(),
        champ_quoi,
        champ_montant,
        btn,
        ft.Divider(),
        ft.Text("Historique:", weight="bold"),
        col_historique
    )
    mettre_a_jour()

port = int(os.environ.get("PORT", 8550))
try:
    ft.app(target=main, view=ft.WEB_BROWSER, port=port)
except:
    try:
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
    except:
        ft.app(target=main, port=port)
