import flet as ft
import os
import json
from datetime import datetime

FICHIER = "depenses_hiba.json"

def charger():
    if os.path.exists(FICHIER):
        try:
            with open(FICHIER, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "depenses" in data:
                    return data["depenses"]
                return []
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

    txt_hiba = ft.Text(size=28, weight="bold", color=ft.Colors.PINK_300)
    txt_resume = ft.Text(size=16, color=ft.Colors.GREY_400)

    champ_quoi = ft.TextField(label="Quoi ? (ex: riz, transport)", width=350)
    champ_montant = ft.TextField(label="Montant depense", width=350, keyboard_type=ft.KeyboardType.NUMBER)
    
    champ_source = ft.TextField(label="Source argent (ex: salaire)", width=350)
    champ_ajout = ft.TextField(label="Montant a ajouter", width=350, keyboard_type=ft.KeyboardType.NUMBER)

    col_historique = ft.Column()

    def mettre_a_jour():
        total_dep = sum(d["montant"] for d in depenses if d.get("type","depense")=="depense")
        total_ajout = sum(d["montant"] for d in depenses if d.get("type")=="ajout")
        hiba = total_ajout - total_dep

        txt_hiba.value = f"HIBA: {hiba} FCFA"
        txt_hiba.color = ft.Colors.GREEN_300 if hiba >= 20000 else ft.Colors.ORANGE if hiba >=0 else ft.Colors.RED_300
        txt_resume.value = f"Entrees: +{total_ajout} | Depenses: -{total_dep}"
        
        col_historique.controls.clear()
        for idx, d in enumerate(reversed(depenses)):
            vrai_idx = len(depenses) - 1 - idx
            def make_delete(i=vrai_idx):
                def delete(e):
                    depenses.pop(i)
                    sauvegarder(depenses)
                    mettre_a_jour()
                return delete
            
            is_ajout = d.get("type")=="ajout"
            prefix = "🟢 + " if is_ajout else "🔴 - "
            couleur = ft.Colors.GREEN_300 if is_ajout else ft.Colors.WHITE
            date_str = d.get("date", "")
            
            ligne = ft.Row([
                ft.Column([
                    ft.Text(f"{prefix}{d['quoi']}: {d['montant']} FCFA", color=couleur, size=15),
                    ft.Text(f"  {date_str}", color=ft.Colors.GREY_500, size=11) if date_str else ft.Text("")
                ], expand=True, spacing=2),
                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_300, on_click=make_delete())
            ])
            col_historique.controls.append(ligne)
        page.update()

    def ajouter_depense(e):
        if not champ_quoi.value or not champ_montant.value: return
        try: montant = int(champ_montant.value)
        except: return
        date_now = datetime.now().strftime("%d/%m %H:%M")
        depenses.append({"quoi": champ_quoi.value.strip(), "montant": montant, "type": "depense", "date": date_now})
        sauvegarder(depenses)
        champ_quoi.value = ""; champ_montant.value = ""
        mettre_a_jour()

    def ajouter_argent(e):
        if not champ_source.value or not champ_ajout.value: return
        try: montant = int(champ_ajout.value)
        except: return
        date_now = datetime.now().strftime("%d/%m %H:%M")
        depenses.append({"quoi": champ_source.value.strip(), "montant": montant, "type": "ajout", "date": date_now})
        sauvegarder(depenses)
        champ_source.value = ""; champ_ajout.value = ""
        mettre_a_jour()

    page.add(
        ft.Text("HIBA - Budget Famille", size=26, color=ft.Colors.RED_400, weight="bold"),
        txt_hiba,
        txt_resume,
        ft.Divider(),
        ft.Text("1. Depense", weight="bold", color=ft.Colors.RED_200),
        champ_quoi, champ_montant,
        ft.ElevatedButton("Ajouter depense", bgcolor=ft.Colors.RED_400, color="white", on_click=ajouter_depense),
        ft.Divider(),
        ft.Text("2. Ajouter de l'argent", weight="bold", color=ft.Colors.GREEN_300),
        champ_source, champ_ajout,
        ft.ElevatedButton("Ajouter +", bgcolor=ft.Colors.GREEN_400, color="white", on_click=ajouter_argent),
        ft.Divider(),
        ft.Text("Historique avec dates:", weight="bold"),
        col_historique
    )
    mettre_a_jour()

port = int(os.environ.get("PORT", 8550))
try: ft.app(target=main, view=ft.WEB_BROWSER, port=port)
except:
    try: ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
    except: ft.app(target=main, port=port)
