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
    page.title="HIBA"; page.theme_mode=ft.ThemeMode.DARK; page.padding=15; page.scroll=ft.ScrollMode.AUTO
    depenses=charger()
    
    # Textes soldes
    txt_hiba=ft.Text(size=22,weight="bold",color=ft.Colors.PINK_300)
    txt_perso=ft.Text(size=22,weight="bold",color=ft.Colors.ORANGE_300)
    txt_maison=ft.Text(size=22,weight="bold",color=ft.Colors.BLUE_300)
    
    # Champs HIBA
    h_in=ft.TextField(label="Entrée HIBA",width=170,keyboard_type=ft.KeyboardType.NUMBER)
    h_in_q=ft.TextField(label="Source",width=170)
    h_out=ft.TextField(label="Sortie HIBA",width=170,keyboard_type=ft.KeyboardType.NUMBER)
    h_out_q=ft.TextField(label="Quoi",width=170)
    
    # Champs PERSO
    p_in=ft.TextField(label="Entrée Perso",width=170,keyboard_type=ft.KeyboardType.NUMBER)
    p_in_q=ft.TextField(label="Source",width=170)
    p_out=ft.TextField(label="Sortie Perso",width=170,keyboard_type=ft.KeyboardType.NUMBER)
    p_out_q=ft.TextField(label="Quoi",width=170)
    
    # Champs MAISON
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
        
        h_solde=h_ent-h_sort
        p_solde=p_ent-p_sort
        m_solde=m_ent-m_sort
        
        txt_hiba.value=f"HIBA: {h_solde} FCFA (+{h_ent} / -{h_sort})"
        txt_perso.value=f"PERSO: {p_solde} FCFA (+{p_ent} / -{p_sort})"
        txt_maison.value=f"MAISON: {m_solde} FCFA (+{m_ent} / -{m_sort})"
        
        col.controls.clear()
        for d in reversed(depenses):
            idx=len(depenses)-1-list(reversed(depenses)).index(d)
            def mk(i=idx):
                def de(e): depenses.pop(i); sauvegarder(depenses); maj()
                return de
            t=d.get("type")
            if t=="h_in": pref="💰 HIBA + "; colr=ft.Colors.GREEN_300
            elif t=="h_out": pref="💸 HIBA - "; colr=ft.Colors.PINK_300
            elif t=="p_in": pref="💰 PERSO + "; colr=ft.Colors.GREEN_300
            elif t=="p_out": pref="💸 PERSO - "; colr=ft.Colors.ORANGE_300
            elif t=="m_in": pref="💰 MAISON + "; colr=ft.Colors.GREEN_300
            else: pref="💸 MAISON - "; colr=ft.Colors.BLUE_300
            
            col.controls.append(ft.Row([ft.Column([ft.Text(f"{pref}{d['quoi']}: {d['montant']}",color=colr,size=13),ft.Text(f"  {d.get('date','')}",color=ft.Colors.GREY_500,size=10)],expand=True,spacing=1),ft.IconButton(icon=ft.Icons.DELETE,icon_color=ft.Colors.RED_300,icon_size=18,on_click=mk())]))
        page.update()
    
    def add(t_in_q, t_in, typ):
        if not t_in_q.value or not t_in.value: return
        try: m=int(t_in.value)
        except: return
        depenses.append({"quoi":t_in_q.value.strip(),"montant":m,"type":typ,"date":datetime.now().strftime("%d/%m %H:%M")}); sauvegarder(depenses); t_in_q.value=""; t_in.value=""; maj()
    
    def add_out(t_out_q, t_out, typ):
        if not t_out_q.value or not t_out.value: return
        try: m=int(t_out.value)
        except: return
        depenses.append({"quoi":t_out_q.value.strip(),"montant":m,"type":typ,"date":datetime.now().strftime("%d/%m %H:%M")}); sauvegarder(depenses); t_out_q.value=""; t_out.value=""; maj()

    page.add(
        ft.Text("3 Budgets Séparés",size=26,color=ft.Colors.WHITE,weight="bold"),
        ft.Container(content=ft.Column([txt_hiba,txt_perso,txt_maison],spacing=5),bgcolor=ft.Colors.GREY_900,padding=12,border_radius=10),
        ft.Divider(),
        # HIBA
        ft.Text("1. HIBA 💖",weight="bold",color=ft.Colors.PINK_300),
        ft.Row([h_in_q,h_in]), ft.ElevatedButton("Ajouter Entrée HIBA",bgcolor=ft.Colors.GREEN_700,color="white",on_click=lambda e: add(h_in_q,h_in,"h_in")),
        ft.Row([h_out_q,h_out]), ft.ElevatedButton("Ajouter Sortie HIBA",bgcolor=ft.Colors.PINK_400,color="white",on_click=lambda e: add_out(h_out_q,h_out,"h_out")),
        ft.Divider(),
        # PERSO
        ft.Text("2. PERSO 👤",weight="bold",color=ft.Colors.ORANGE_300),
        ft.Row([p_in_q,p_in]), ft.ElevatedButton("Ajouter Entrée Perso",bgcolor=ft.Colors.GREEN_700,color="white",on_click=lambda e: add(p_in_q,p_in,"p_in")),
        ft.Row([p_out_q,p_out]), ft.ElevatedButton("Ajouter Sortie Perso",bgcolor=ft.Colors.ORANGE_400,color="white",on_click=lambda e: add_out(p_out_q,p_out,"p_out")),
        ft.Divider(),
        # MAISON
        ft.Text("3. MAISON 🏠",weight="bold",color=ft.Colors.BLUE_300),
        ft.Row([m_in_q,m_in]), ft.ElevatedButton("Ajouter Entrée Maison",bgcolor=ft.Colors.GREEN_700,color="white",on_click=lambda e: add(m_in_q,m_in,"m_in")),
        ft.Row([m_out_q,m_out]), ft.ElevatedButton("Ajouter Sortie Maison",bgcolor=ft.Colors.BLUE_400,color="white",on_click=lambda e: add_out(m_out_q,m_out,"m_out")),
        ft.Divider(),
        ft.Text("Historique:",weight="bold"),
        col
    )
    maj()

port=int(os.environ.get("PORT",8550))
try: ft.app(target=main,view=ft.WEB_BROWSER,port=port)
except:
    try: ft.app(target=main,view=ft.AppView.WEB_BROWSER,port=port)
    except: ft.app(target=main,port=port)
