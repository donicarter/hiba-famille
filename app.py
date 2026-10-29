import flet as ft
import os, json, hashlib
from datetime import datetime

FICHIER="depenses_hiba.json"
PIN_HASH = "5f4dcc3b5aa765d61d8327deb882cf99" # PIN = password (à changer)

def check_pin(pin):
    return hashlib.md5(pin.encode()).hexdigest() == PIN_HASH

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
    page.title="HIBA SECURE"; page.theme_mode=ft.ThemeMode.DARK; page.padding=15
    page.scroll=ft.ScrollMode.AUTO
    
    # ECRAN DE CONNEXION
    pin_field=ft.TextField(label="Code PIN",password=True,width=200)
    msg=ft.Text("",color=ft.Colors.RED_300)
    depenses=[]
    
    def login(e):
        if not check_pin(pin_field.value):
            msg.value="PIN incorrect"; page.update(); return
        page.controls.clear()
        construire_app()
    
    def construire_app():
        nonlocal depenses
        depenses=charger()
        txt_hiba=ft.Text(size=20,weight="bold",color=ft.Colors.PINK_300)
        txt_perso=ft.Text(size=20,weight="bold",color=ft.Colors.ORANGE_300)
        txt_maison=ft.Text(size=20,weight="bold",color=ft.Colors.BLUE_300)
        chart_hiba=ft.PieChart(sections=[],sections_space=2,center_space_radius=30,height=150)
        leg_hiba=ft.Text("",size=11,color=ft.Colors.GREY_400)
        chart_perso=ft.PieChart(sections=[],sections_space=2,center_space_radius=30,height=150)
        leg_perso=ft.Text("",size=11,color=ft.Colors.GREY_400)
        chart_maison=ft.PieChart(sections=[],sections_space=2,center_space_radius=30,height=150)
        leg_maison=ft.Text("",size=11,color=ft.Colors.GREY_400)
        h_in=ft.TextField(label="Entrée HIBA",width=170,keyboard_type=ft.KeyboardType.NUMBER)
        h_in_q=ft.TextField(label="Source",width=170)
        h_out=ft.TextField(label="Sortie HIBA",width=170,keyboard_type=ft.KeyboardType.NUMBER)
        h_out_q=ft.TextField(label="Quoi",width=170)
        p_in=ft.TextField(label="Entrée Perso",width=170,keyboard_type=ft.KeyboardType.NUMBER)
        p_in_q=ft.TextField(label="Source",width=170)
        p_out=ft.TextField(label="Sortie Perso",width=170,keyboard_type=ft.KeyboardType.NUMBER)
        p_out_q=ft.TextField(label="Quoi",width=170)
        m_in=ft.TextField(label="Entrée Maison",width=170,keyboard_type=ft.KeyboardType.NUMBER)
        m_in_q=ft.TextField(label="Source",width=170)
        m_out=ft.TextField(label="Sortie Maison",width=170,keyboard_type=ft.KeyboardType.NUMBER)
        m_out_q=ft.TextField(label="Quoi",width=170)
        col=ft.Column()
        def maj():
            h_ent=sum(d["montant"] for d in depenses if d.get("type")=="h_in")
            h_sort=sum(d["montant"] for d in depenses if d.get("type")=="h_out")
            p_ent=sum(d["montant"] for d in depenses if d.get("type")=="p_in")
            p_sort=sum(d["montant"] for d in depenses if d.get("type")=="p_out")
            m_ent=sum(d["montant"] for d in depenses if d.get("type")=="m_in")
            m_sort=sum(d["montant"] for d in depenses if d.get("type")=="m_out")
            h_solde=h_ent-h_sort; p_solde=p_ent-p_sort; m_solde=m_ent-m_sort
            txt_hiba.value=f"HIBA: {h_solde} FCFA"; txt_perso.value=f"PERSO: {p_solde} FCFA"; txt_maison.value=f"MAISON: {m_solde} FCFA"
            tot_h=h_ent+h_sort
            if tot_h>0:
                secs=[]
                if h_ent>0: secs.append(ft.PieChartSection(value=h_ent,color=ft.Colors.GREEN_400,title=f"+{h_ent}",title_style=ft.TextStyle(size=10,color="white"),radius=55))
                if h_sort>0: secs.append(ft.PieChartSection(value=h_sort,color=ft.Colors.PINK_400,title=f"-{h_sort}",title_style=ft.TextStyle(size=10,color="white"),radius=50))
                chart_hiba.sections=secs
            tot_p=p_ent+p_sort
            if tot_p>0:
                secs=[]
                if p_ent>0: secs.append(ft.PieChartSection(value=p_ent,color=ft.Colors.GREEN_400,title=f"+{p_ent}",title_style=ft.TextStyle(size=10,color="white"),radius=55))
                if p_sort>0: secs.append(ft.PieChartSection(value=p_sort,color=ft.Colors.ORANGE_400,title=f"-{p_sort}",title_style=ft.TextStyle(size=10,color="white"),radius=50))
                chart_perso.sections=secs
            tot_m=m_ent+m_sort
            if tot_m>0:
                secs=[]
                if m_ent>0: secs.append(ft.PieChartSection(value=m_ent,color=ft.Colors.GREEN_400,title=f"+{m_ent}",title_style=ft.TextStyle(size=10,color="white"),radius=55))
                if m_sort>0: secs.append(ft.PieChartSection(value=m_sort,color=ft.Colors.BLUE_400,title=f"-{m_sort}",title_style=ft.TextStyle(size=10,color="white"),radius=50))
                chart_maison.sections=secs
            col.controls.clear()
            for d in reversed(depenses):
                idx=len(depenses)-1-list(reversed(depenses)).index(d)
                def mk(i=idx):
                    def de(e): depenses.pop(i); sauvegarder(depenses); maj()
                    return de
                t=d.get("type"); pref=t; colr=ft.Colors.WHITE
                col.controls.append(ft.Row([ft.Text(f"{pref}: {d['quoi']} {d['montant']}",color=colr,size=12,expand=True),ft.IconButton(icon=ft.Icons.DELETE,icon_color=ft.Colors.RED_300,icon_size=16,on_click=mk())]))
            page.update()
        def add(t_in_q, t_in, typ):
            if not t_in_q.value or not t_in.value: return
            try: m=int(t_in.value)
            except: return
            if m<=0 or m>10000000: return # validation anti-injection
            depenses.append({"quoi":t_in_q.value.strip()[:30],"montant":m,"type":typ,"date":datetime.now().strftime("%d/%m")}); sauvegarder(depenses); t_in_q.value=""; t_in.value=""; maj()
        def add_out(t_out_q, t_out, typ):
            if not t_out_q.value or not t_out.value: return
            try: m=int(t_out.value)
            except: return
            if m<=0 or m>10000000: return
            depenses.append({"quoi":t_out_q.value.strip()[:30],"montant":m,"type":typ,"date":datetime.now().strftime("%d/%m")}); sauvegarder(depenses); t_out_q.value=""; t_out.value=""; maj()
        page.add(
            ft.Text("🔒 HIBA SECURE",size=22,weight="bold"),
            ft.Container(content=ft.Column([txt_hiba,txt_perso,txt_maison]),bgcolor=ft.Colors.GREY_900,padding=10,border_radius=10),
            ft.Text("1. HIBA 💖",color=ft.Colors.PINK_300,weight="bold"), ft.Row([h_in_q,h_in]), ft.ElevatedButton("Entrée HIBA",on_click=lambda e: add(h_in_q,h_in,"h_in")),
            ft.Row([h_out_q,h_out]), ft.ElevatedButton("Sortie HIBA",on_click=lambda e: add_out(h_out_q,h_out,"h_out")),
            ft.Divider(),
            ft.Text("2. PERSO 👤",color=ft.Colors.ORANGE_300,weight="bold"), ft.Row([p_in_q,p_in]), ft.ElevatedButton("Entrée Perso",on_click=lambda e: add(p_in_q,p_in,"p_in")),
            ft.Row([p_out_q,p_out]), ft.ElevatedButton("Sortie Perso",on_click=lambda e: add_out(p_out_q,p_out,"p_out")),
            ft.Divider(),
            ft.Text("3. MAISON 🏠",color=ft.Colors.BLUE_300,weight="bold"), ft.Row([m_in_q,m_in]), ft.ElevatedButton("Entrée Maison",on_click=lambda e: add(m_in_q,m_in,"m_in")),
            ft.Row([m_out_q,m_out]), ft.ElevatedButton("Sortie Maison",on_click=lambda e: add_out(m_out_q,m_out,"m_out")),
            ft.Divider(), col,
            ft.Text("📊 Graphiques en bas"), chart_hiba, chart_perso, chart_maison
        )
        maj()
    
    # Page login
    page.add(ft.Column([ft.Text("🔒 HIBA - Accès sécurisé",size=24,weight="bold"), ft.Text("Entre ton code PIN pour accéder à tes 3 budgets"), pin_field, ft.ElevatedButton("Se connecter",bgcolor=ft.Colors.PINK_400,color="white",on_click=login), msg],horizontal_alignment=ft.CrossAxisAlignment.CENTER))

port=int(os.environ.get("PORT",8550))
try: ft.app(target=main,view=ft.WEB_BROWSER,port=port)
except:
    try: ft.app(target=main,view=ft.AppView.WEB_BROWSER,port=port)
    except: ft.app(target=main,port=port)
