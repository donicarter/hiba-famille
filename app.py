import flet as ft
import os
import json

DATA_FILE = "hiba_data.json"

try:
    with open(DATA_FILE, "r") as f:
        d = json.load(f)
        fond = d.get("fond", 86500)
        depenses = d.get("depenses", [])
except:
    fond = 86500
    depenses = []

def save():
    with open(DATA_FILE, "w") as f:
        json.dump({"fond": fond, "depenses": depenses}, f)

def main(page: ft.Page):
    page.title = "HIBA - Budget Famille"
    page.bgcolor = "#FFF0F5"
    page.padding = 15
    page.scroll = "auto"

    total = sum(x["montant"] for x in depenses)
    reste = fond - total

    titre = ft.Text("HIBA - Budget Famille", size=24, weight="bold", color="#E91E63")
    txt_fond = ft.Text(f"FOND DISPO {fond} FCFA", size=18, weight="bold")
    txt_total = ft.Text(f"Depense: {total} FCFA")
    txt_reste = ft.Container(ft.Text(f"RESTE: {reste} FCFA", size=20, weight="bold", color="blue"), bgcolor="white", padding=15, border_radius=10)

    label_input = ft.TextField(label="Pour quoi ?", hint_text="ex: marche")
    montant_input = ft.TextField(label="Montant", keyboard_type=ft.KeyboardType.NUMBER)

    liste = ft.Column([ft.Text(f"{x['label']}: {x['montant']} FCFA") for x in depenses])

    def ajouter(e):
        global fond
        if montant_input.value and label_input.value:
            try:
                m = int(montant_input.value)
                depenses.append({"label": label_input.value, "montant": m})
                save()
                page.snack_bar = ft.SnackBar(ft.Text(f"Ajoute {m} FCFA"))
                page.snack_bar.open = True
                montant_input.value = ""
                label_input.value = ""
                page.update()
            except:
                pass

    page.add(ft.Column([
        titre, txt_fond, txt_total, txt_reste,
        ft.Divider(),
        label_input, montant_input,
        ft.ElevatedButton("Ajouter depense", on_click=ajouter, bgcolor="#E91E63", color="white"),
        ft.Divider(),
        ft.Text("Historique:", weight="bold"),
        liste
    ]))

port = int(os.environ.get("PORT", 8502))
ft.app(target=main, view=ft.WEB_BROWSER, port=port, host="0.0.0.0")
