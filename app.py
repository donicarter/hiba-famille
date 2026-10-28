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
    txt_reste = ft.Text(size=20, weight="bold")

    champ_quoi = ft.TextField(label="Quoi ? (ex: riz, transport)", width=300)
    champ_montant = ft.TextField(label="Montant FCFA", width=300, keyboard_type=ft.KeyboardType.NUMBER)

    col_historique = ft.Column()

    def mettre_a_jour():
        total = sum(d["montant"] for d in depenses)
        reste = FOND_DEPART - total
        txt_total.value = f"Total depenses: {total} FCFA"
        txt_reste.value = f"Reste: {reste} FCFA"
        txt_reste.color = ft.Colors.GREEN if reste >= 20_000 else ft.Colors.ORANGE if reste >=0 else ft.Colors.RED
        
        col_historique.controls.clear()
        for idx, d in enumerate(reversed(depenses)):
            vrai_idx = len(depenses) - 1 - idx
            def make_delete(i=vrai_idx):
                def delete(e):
                    depenses.pop(i)
                    sauvegarder(depenses)
                    mettre_a_jour()
                return delete
            
            ligne = ft.Row([
                ft.Text(f"{d['quoi']}: {d['montant']} FCFA", expand=True),
                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_300, on_click=make_delete())
            ])
            col_historique.controls.append(ligne)
        page.update()

    def ajouter(e):
        if not champ_quoi.value or not champ_montant.value:
            return
        try:
            montant = int(champ_montant.value)
        except:
            return
        depenses.append({"quoi": champ_quoi.value.strip(), "montant": montant})
        sauvegarder(depenses)
        champ_quoi.value = ""
        champ_montant.value = ""
        mettre_a_jour()

    def tout_effacer(e):
        depenses.clear()
        sauvegarder(depenses)
        mettre_a_jour()

    btn_ajouter = ft.ElevatedButton("Ajouter depense", bgcolor=ft.Colors.PINK_300, color="white", on_click=ajouter)
    btn_clear = ft.TextButton("Tout effacer", icon=ft.Icons.WARNING, on_click=tout_effacer)

    page.add(
        ft.Text("HIBA - Budget Famille", size=26, color=ft.Colors.RED_400, weight="bold"),
        txt_fond,
        txt_total,
        txt_reste,
        ft.Divider(),
        champ_quoi,
        champ_montant,
        ft.Row([btn_ajouter, btn_clear]),
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
