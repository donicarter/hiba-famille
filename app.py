import flet as ft
import os, json
from datetime import datetime
FICHIER="depenses_hiba.json"
def charger():
    if os.path.exists(FICHIER):
        try:
            with open(FICHIER,"r",encoding="utf-8") as f:
                data=json.load(f)
                return data if isinstance(data,list) else data.get("depenses",[])
        except: return []
    return []
def sauvegarder(d):
    with open(FICHIER,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False)
def main(page: ft.Page):
    page.title="HIBA"; page.theme_mode=ft.ThemeMode.DARK; page.padding=20; page.scroll=ft.ScrollMode.AUTO
    depenses=charger()
    txt_hiba=ft.Text(size=30,weight="bold",color=ft.Colors.PINK_300)
    txt_resume=ft.Text(size=14,color=ft.Colors.GREY_400)
    txt_perso=ft.Text(size=14,color=ft.Colors.GREY_400)
    champ_quoi=ft.TextField(label="Quoi ? (perso)",width=350)
    champ_montant=ft.TextField(label="Montant perso",width=350,keyboard_type=ft.KeyboardType.NUMBER)
    champ_maison_quoi=ft.TextField(label="Quoi maison ? (loyer, courant)",width=350)
    champ_maison_montant=ft.TextField(label="Montant maison",width=350,keyboard_type=ft.KeyboardType.NUMBER)
    champ_source=ft.TextField(label="Source argent",width=350)
    champ_ajout=ft.TextField(label="Montant a ajouter",width=350,keyboard_type=ft.KeyboardType.NUMBER)
    col=ft.Column(); chart=ft.PieChart(sections=[],sections_space=2,center_space_radius=35,height=200); leg=ft.Text("",size=12,color=ft.Colors.GREY_400)
    def maj():
        tp=sum(d["montant"] for d in depenses if d.get("type")=="depense")
        tm=sum(d["montant"] for d in depenses if d.get("type")=="maison")
        ta=sum(d["montant"] for d in depenses if d.get("type")=="ajout")
        hiba=ta-tm  # <-- ICI : HIBA = seulement Entrees - Maison
        txt_hiba.value=f"HIBA (Maison): {hiba} FCFA"
        txt_hiba.color=ft.Colors.GREEN_300 if hiba>=20000 else ft.Colors.ORANGE if hiba>=0 else ft.Colors.RED_300
        txt_resume.value=f"HIBA = Entrees +{ta} - Maison {tm} = {hiba}"
        txt_perso.value=f"Perso a part: -{tp} FCFA (ne touche pas HIBA)"
        tot=ta+tm
        if tot>0:
            chart.sections=[
                ft.PieChartSection(value=ta,color=ft.Colors.GREEN_400,title=f"{ta}",title_style=ft.TextStyle(size=11,color="white",weight="bold"),radius=65),
                ft.PieChartSection(value=tm if tm>0 else 0.01,color=ft.Colors.BLUE_400,title=f"Maison {tm}" if tm>0 else "",title_style=ft.TextStyle(size=10,color="white"),radius=60),
            ]
            leg.value=f"🟢 Entrees | 🔵 Maison - HIBA uniquement"
        else: chart.sections=[]; leg.value="Ajoute loyer / entrees"
        col.controls.clear()
        for d in reversed(depenses):
            idx=len(depenses)-1-list(reversed(depenses)).index(d)
            def mk(i=idx):
                def de(e): depenses.pop(i); sauvegarder(depenses); maj()
                return de
            t=d.get("type"); pref="🟢 + " if t=="ajout" else "🏠 " if t=="maison" else "🔴 - "; colr=ft.Colors.GREEN_300 if t=="ajout" else ft.Colors.BLUE_300 if t=="maison" else ft.Colors.ORANGE_300
            col.controls.append(ft.Row([ft.Column([ft.Text(f"{pref}{d['quoi']}: {d['montant']} FCFA",color=colr,size=14),ft.Text(f"  {d.get('date','')} [{t}]",color=ft.Colors.GREY_500,size=11)],expand=True,spacing=2),ft.IconButton(icon=ft.Icons.DELETE,icon_color=ft.Colors.RED_300,on_click=mk())]))
        page.update()
    def add_perso(e):
        if not champ_quoi.value or not champ_montant.value: return
        try: m=int(champ_montant.value)
        except: return
        depenses.append({"quoi":champ_quoi.value.strip(),"montant":m,"type":"depense","date":datetime.now().strftime("%d/%m %H:%M")}); sauvegarder(depenses); champ_quoi.value=""; champ_montant.value=""; maj()
    def add_maison(e):
        if not champ_maison_quoi.value or not champ_maison_montant.value: return
        try: m=int(champ_maison_montant.value)
        except: return
        depenses.append({"quoi":champ_maison_quoi.value.strip(),"montant":m,"type":"maison","date":datetime.now().strftime("%d/%m %H:%M")}); sauvegarder(depenses); champ_maison_quoi.value=""; champ_maison_montant.value=""; maj()
    def add_plus(e):
        if not champ_source.value or not champ_ajout.value: return
        try: m=int(champ_ajout.value)
        except: return
        depenses.append({"quoi":champ_source.value.strip(),"montant":m,"type":"ajout","date":datetime.now().strftime("%d/%m %H:%M")}); sauvegarder(depenses); champ_source.value=""; champ_ajout.value=""; maj()
    page.add(ft.Text("HIBA - Budget Famille",size=26,color=ft.Colors.RED_400,weight="bold"),txt_hiba,txt_resume,txt_perso,ft.Container(content=ft.Column([chart,leg],horizontal_alignment=ft.CrossAxisAlignment.CENTER),bgcolor=ft.Colors.GREY_900,border_radius=10,padding=10),ft.Divider(),ft.Text("1. Depenses Maison 🏠 -> compte dans HIBA",weight="bold",color=ft.Colors.BLUE_300),champ_maison_quoi,champ_maison_montant,ft.ElevatedButton("Ajouter maison",bgcolor=ft.Colors.BLUE_400,color="white",on_click=add_maison),ft.Divider(),ft.Text("2. Depenses Perso 🔴 -> NE touche PAS HIBA",weight="bold",color=ft.Colors.ORANGE_300),champ_quoi,champ_montant,ft.ElevatedButton("Ajouter perso (a part)",bgcolor=ft.Colors.ORANGE_400,color="white",on_click=add_perso),ft.Divider(),ft.Text("3. Argent",weight="bold",color=ft.Colors.GREEN_300),champ_source,champ_ajout,ft.ElevatedButton("Ajouter +",bgcolor=ft.Colors.GREEN_400,color="white",on_click=add_plus),ft.Divider(),ft.Text("Historique:",weight="bold"),col); maj()
port=int(os.environ.get("PORT",8550))
try: ft.app(target=main,view=ft.WEB_BROWSER,port=port)
except:
    try: ft.app(target=main,view=ft.AppView.WEB_BROWSER,port=port)
    except: ft.app(target=main,port=port)
