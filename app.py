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
                if isinstance(data, list): return data
                if isinstance(data, dict) and "depenses" in data: return data["depenses"]
                return []
        except: return []
    return []

def sauvegarder(depenses):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(depenses, f, ensure_ascii=False)

def extraire_mois(date_str):
    if not date_str: return None
    try:
        if "/" in date_str and len(date_str.split("/"))==3: # 28/10/2025 07:22
            dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        else: # 28/10 07:22
            dt = datetime.strptime(date_str, "%d/%m %H:%M")
            dt = dt.replace(year=datetime.now().year)
        return dt.strftime("%m/%Y")
    except:
        return None

def main(page: ft.Page):
    page.title = "HIBA - Budget Famille"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    depenses = charger()

    txt_hiba = ft.Text(size=28, weight="bold", color=ft.Colors.PINK_300)
    txt_resume = ft.Text(size=16, color=ft.Colors.GREY_400)

    champ_quoi = ft.TextField(label="Quoi ? (ex: riz)", width=350)
    champ_montant = ft.TextField(label="Montant depense", width=350, keyboard_type=ft.KeyboardType.NUMBER)
    champ_source = ft.TextField(label="Source argent", width=350)
    champ_ajout = ft.TextField(label="Montant a ajouter", width=350, keyboard_type=ft.KeyboardType.NUMBER)

    col_historique = ft.Column()
    chart = ft.PieChart(sections=[], sections_space=2, center_space_radius=40, height=200)
    txt_chart_legend = ft.Text("", size=13, color=ft.Colors.GREY_400)

    filtre_mois = ft.Dropdown(label="Filtrer par mois", value="Tous", width=350, options=[ft.dropdown.Option("Tous")])

    def mettre_a_jour(e=None):
        # Mettre à jour liste des mois disponibles
        mois_uniques = set()
        for d in depenses:
            m = extraire_mois(d.get("date",""))
            if m: mois_uniques.add(m)
        # Reconstruire options
        options = [ft.dropdown.Option("Tous")]
        for m in sorted(mois_uniques, reverse=True):
            options.append(ft.dropdown.Option(m))
        filtre_mois.options = options

        # Filtrer selon choix
        choix = filtre_mois.value
        if choix == "Tous" or not choix:
            filtrees = depenses
        else:
            filtrees = [d for d in depenses if extraire_mois(d.get("date","")) == choix]

        total_dep = sum(d["montant"] for d in filtrees if d.get("type","depense")=="depense")
        total_ajout = sum(d["montant"] for d in filtrees if d.get("type")=="ajout")
        hiba = total_ajout - total_dep

        txt_hiba.value = f"HIBA: {hiba} FCFA" + (f" ({choix})" if choix!="Tous" else "")
        txt_hiba.color = ft.Colors.GREEN_300 if hiba >= 20000 else ft.Colors.ORANGE if hiba >=0 else ft.Colors.RED_300
        txt_resume.value = f"Entrees: +{total_ajout} | Depenses: -{total_dep}"

        total = total_ajout + total_dep
        if total > 0:
            chart.sections = [
                ft.PieChartSection(value=total_ajout, color=ft.Colors.GREEN_400, title=f"+{total_ajout}", title_style=ft.TextStyle(size=12, color="white", weight="bold"), radius=60),
                ft.PieChartSection(value=total_dep if total_dep>0 else 0.01, color=ft.Colors.RED_400, title=f"-{total_dep}" if total_dep>0 else "", title_style=ft.TextStyle(size=12, color="white"), radius=60),
            ]
            txt_chart_legend.value = f"🟢 {int(total_ajout/total*100)}% Entrees | 🔴 {int(total_dep/total*100)}% Depenses"
        else:
            chart.sections = []
            txt_chart_legend.value = "Pas de donnees pour ce mois"

        col_historique.controls.clear()
        for idx, d in enumerate(reversed(filtrees)):
            # trouver vrai index dans depenses globales pour suppression
            # on cherche par identite
            try:
                vrai_idx = len(depenses) - 1 - list(reversed(depenses)).index(d)
                # plus simple: on prend l'objet et on trouve sa position
                # mais on utilise une recherche par contenu
                vrai_idx = depenses.index(d)
            except:
                vrai_idx = 0
            def make_delete(i=vrai_idx):
                def delete(ev):
                    depenses.pop(i)
                    sauvegarder(depenses)
                    mettre_a_jour()
                return delete
            is_ajout = d.get("type")=="ajout"
            prefix = "🟢 + " if is_ajout else "🔴 - "
            couleur = ft.Colors.GREEN_300 if is_ajout else ft.Colors.WHITE
            ligne = ft.Row([
                ft.Column([
                    ft.Text(f"{prefix}{d['quoi']}: {d['montant']} FCFA", color=couleur, size=14),
                    ft.Text(f"  {d.get('date','')}", color=ft.Colors.GREY_500, size=11)
                ], expand=True, spacing=2),
                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_300, on_click=make_delete())
            ])
            col_historique.controls.append(ligne)
        page.update()

    filtre_mois.on_change = mettre_a_jour

    def ajouter_depense(e):
        if not champ_quoi.value or not champ_montant.value: return
        try: montant = int(champ_montant.value)
        except: return
        date_now = datetime.now().strftime("%d/%m/%Y %H:%M")
        depenses.append({"quoi": champ_quoi.value.strip(), "montant": montant, "type": "depense", "date": date_now})
        sauvegarder(depenses)
        champ_quoi.value = ""; champ_montant.value = ""
        mettre_a_jour()

    def ajouter_argent(e):
        if not champ_source.value or not champ_ajout.value: return
        try: montant = int(champ_ajout.value)
        except: return
        date_now = datetime.now().strftime("%d/%m/%Y %H:%M")
        depenses.append({"quoi": champ_source.value.strip(), "montant": montant, "type": "ajout", "date": date_now})
        sauvegarder(depenses)
        champ_source.value = ""; champ_ajout.value = ""
        mettre_a_jour()

    page.add(
        ft.Text("HIBA - Budget Famille", size=26, color=ft.Colors.RED_400, weight="bold"),
        txt_hiba,
        txt_resume,
        filtre_mois,
        ft.Container(content=ft.Column([chart, txt_chart_legend], horizontal_alignment=ft.CrossAxisAlignment.CENTER), bgcolor=ft.Colors.GREY_900, border_radius=10, padding=10),
        ft.Divider(),
        ft.Text("1. Depense", weight="bold", color=ft.Colors.RED_200),
        champ_quoi, champ_montant,
        ft.ElevatedButton("Ajouter depense", bgcolor=ft.Colors.RED_400, color="white", on_click=ajouter_depense),
        ft.Divider(),
        ft.Text("2. Ajouter de l'argent", weight="bold", color=ft.Colors.GREEN_300),
        champ_source, champ_ajout,
        ft.ElevatedButton("Ajouter +", bgcolor=ft.Colors.GREEN_400, color="white", on_click=ajouter_argent),
        ft.Divider(),
        ft.Text("Historique:", weight="bold"),
        col_historique
    )
    mettre_a_jour()

port = int(os.environ.get("PORT", 8550))
try: ft.app(target=main, view=ft.WEB_BROWSER, port=port)
except:
    try: ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
    except: ft.app(target=main, port=port)
