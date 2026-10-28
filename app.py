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
    page.scroll = "auto"
    page.padding = 20

    titre = ft.Text("HIBA - Budget Famille", size=24, weight="bold", color="#E91E63")
    txt_fond = ft.Text(f"Fond de depart: {fond} FCFA", size=16)
    total_dep = sum([x["montant"] for x in depenses])
    txt_total = ft.Text(f"Total depenses: {total_dep} FCFA", size=16)
    txt_reste = ft.Text(f"Reste: {fond - total_dep} FCFA", size=18, weight="bold", color="green")

    label_input = ft.TextField(label="Quoi ? (ex: riz)", width=300)
    montant_input = ft.TextField(label="Montant FCFA", width=300, keyboard_type="number")
    
    liste = ft.Column()

    def refresh_list():
        liste.controls.clear()
        for item in reversed(depenses):
            liste.controls.append(ft.Text(f"- {item['label']}: {item['montant']} FCFA"))
        total = sum([x["montant"] for x in depenses])
        txt_total.value = f"Total depenses: {total} FCFA"
        txt_reste.value = f"Reste: {fond - total} FCFA"
        page.update()

    def ajouter(e):
        try:
            m = int(montant_input.value)
            l = label_input.value
            if l and m:
                depenses.append({"label": l, "montant": m})
                save()
                refresh_list()
                page.snack_bar = ft.SnackBar(ft.Text(f"Ajoute {m} FCFA"))
                page.snack_bar.open = True
                montant_input.value = ""
                label_input.value = ""
                page.update()
        except:
            pass

    refresh_list()

    page.add(ft.Column([
        titre, txt_fond, txt_total, txt_reste,
        ft.Divider(),
        label_input, montant_input,
        ft.ElevatedButton("Ajouter depense", on_click=ajouter, bgcolor="#E91E63", color="white"),
        ft.Divider(),
        ft.Text("Historique:", weight="bold"),
        liste
    ]))
port = int(os.environ.get("PORT", 8550))
ft.app(target=main, view=ft.WEB_BROWSER, port=port)
