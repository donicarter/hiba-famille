import flet as ft
import os
import json

FICHIER = "depenses_hiba.json"
FOND_DEPART = 69000  # <-- ton nouveau fond

def charger():
    if os.path.exists(FICHIER):
        try:
            with open(FICHIER, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list): # ancien format
                    return {"fond": FOND_DEPART, "depenses": data}
                # Si ancien fond 86500, on le met à 69000
                if data.get("fond") == 86500:
                    data["fond"] = FOND_DEPART
                return data
        except:
            pass
    return {"fond": FOND_DEPART, "depenses": []}

def sauvegarder(fond, depenses):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump({"fond": fond, "depenses": depenses}, f, ensure_ascii=False)

def main(page: ft.Page):
    page.title = "HIBA - Budget Famille"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    data = charger()
    fond = data["fond"]
    depenses = data["depenses"]

    txt_fond = ft.Text(size=17, weight="bold")
    txt_total_dep = ft.Text(size=17)
    txt_total_ajout = ft.Text(size=17, color=ft.Colors.GREEN_300)
    txt_reste = ft.Text(size=22, weight="bold")

    # Champs depense
    champ_quoi = ft.TextField(label="Quoi ? (ex: riz, transport)", width=350)
    champ_montant = ft.TextField(label="Montant depense", width=350, keyboard_type=ft.KeyboardType.NUMBER)
    
    # Champs ajout argent
    champ_source = ft.TextField(label="Source argent (ex: salaire)", width=350)
    champ_ajout = ft.TextField(label="Montant a ajouter", width=350, keyboard_type=ft.KeyboardType.NUMBER)

    col_historique = ft.Column()

    def mettre_a_jour():
        total_dep = sum(d["montant"] for d in depenses if d["type"]=="depense")
        total_ajout = sum(d["montant"] for d in depenses if d["type"]=="ajout")
        reste = fond + total_ajout - total_dep

        txt_fond.value = f"Fond de depart: {fond} FCFA"
        txt_total_dep.value = f"Total depenses: {total_dep} FCFA"
        txt_total_ajout.value = f"Total argent ajoute: +{total_ajout} FCFA"
        txt_reste.value = f"Reste: {reste} FCFA"
        txt_reste.color = ft.Colors.GREEN if reste >= 20000 else ft.Colors.ORANGE if reste >=0 else ft.Colors.RED
        
        col_historique.controls.clear()
        for idx, d in enumerate(reversed(depenses)):
            vrai_idx = len(depenses) - 1 - idx
            def make_delete(i=vrai_idx):
                def delete(e):
                    depenses.pop(i)
                    sauvegarder(fond, depenses)
                    mettre_a_jour()
                return delete
            
            is_ajout = d["type"]=="ajout"
            prefix = "🟢 + " if is_ajout else "🔴 - "
            couleur = ft.Colors.GREEN_300 if is_ajout else ft.Colors.WHITE
            ligne = ft.Row([
                ft.Text(f"{prefix}{d['quoi']}: {d['montant']} FCFA", expand=True, color=couleur),
                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_300, on_click=make_delete())
            ])
            col_historique.controls.append(ligne)
        page.update()

    def ajouter_depense(e):
        if not champ_quoi.value or not champ_montant.value: return
        try: montant = int(champ_montant.value)
        except: return
        depenses.append({"quoi": champ_quoi.value.strip(), "montant": montant, "type": "depense"})
        sauvegarder(fond, depenses)
        champ_quoi.value = ""; champ_montant.value = ""
        mettre_a_jour()

    def ajouter_argent(e):
        if not champ_source.value or not champ_ajout.value: return
        try: montant = int(champ_ajout.value)
        except: return
        depenses.append({"quoi": champ_source.value.strip(), "montant": montant, "type": "ajout"})
        sauvegarder(fond, depenses)
        champ_source.value = ""; champ_ajout.value = ""
        mettre_a_jour()

    page.add(
        ft.Text("HIBA - Budget Famille", size=26, color=ft.Colors.RED_400, weight="bold"),
        txt_fond,
        txt_total_dep,
        txt_total_ajout,
        txt_reste,
        ft.Divider(),
        ft.Text("1. Depense", weight="bold", color=ft.Colors.RED_200),
        champ_quoi, champ_montant,
        ft.ElevatedButton("Ajouter depense", bgcolor=ft.Colors.RED_400, color="white", on_click=ajouter_depense),
        ft.Divider(),
        ft.Text("2. Ajouter de l'argent", weight="bold", color=ft.Colors.GREEN_300),
        champ_source, champ_ajout,
        ft.ElevatedButton("Ajouter +", bgcolor=ft.Colors.GREEN_400, color="white", on_click=ajouter_argent),
        ft.Divider(),
        ft.Text("Historique (vert=ajout, blanc=depense):", weight="bold"),
        col_historique
    )
    mettre_a_jour()

port = int(os.environ.get("PORT", 8550))
try: ft.app(target=main, view=ft.WEB_BROWSER, port=port)
except:
    try: ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
    except: ft.app(target=main, port=port)
