import flet as ft
import threading
import datetime
import os

def main(page: ft.Page):
    # --- 1. AYARLAR ---
    page.title = "CepList"
    page.window_width = 400
    page.window_height = 750
    page.padding = 0 
    
    # DİNAMİK DOSYA YOLU (Hata almamak için)
    try:
        program_klasoru = os.path.dirname(os.path.abspath(__file__))
        assets_yolu = os.path.join(program_klasoru, "assets")
        page.assets_dir = assets_yolu
    except:
        page.assets_dir = "assets"

    # --- 2. KURUMSAL KİMLİK ---
    
    # DÜZELTİLDİ: İSİM TEKRAR CEPLIST OLDU
    APP_NAME = "CepList" 
    
    # ŞİRKET ADI
    COMPANY_NAME = "Novus Digital Inc." 
    
    # LOGO AYARI
    LOGO_FILE = "icon.png" 
    BRAND_COLOR = "teal"
    BRAND_TEXT_COLOR = "teal"
    SPLASH_BG = "#1a1a1a"

    # --- 3. TEMA MOTORU ---
    THEMES = {
        "Obsidian": { "bg": "#121212", "surface": "#1e1e1e", "appbar_bg": "#2c2c2c", "primary": "teal", "on_primary": "black", "text_main": "#ffffff", "text_sec": "#b2bec3", "divider": "#2d3436", "icon_bg1": "#2d3436", "icon_bg2": "#636e72" },
        "Snow": { "bg": "#f5f6fa", "surface": "#ffffff", "appbar_bg": "#ffffff", "primary": "#0984e3", "on_primary": "white", "text_main": "#2d3436", "text_sec": "#636e72", "divider": "#dfe6e9", "icon_bg1": "#74b9ff", "icon_bg2": "#a29bfe" },
        "Navy": { "bg": "#0c2461", "surface": "#1e3799", "appbar_bg": "#0a3d62", "primary": "#f6b93b", "on_primary": "black", "text_main": "#ffffff", "text_sec": "#82ccdd", "divider": "#3c6382", "icon_bg1": "#4a69bd", "icon_bg2": "#6a89cc" },
        "Forest": { "bg": "#1e272e", "surface": "#2f3640", "appbar_bg": "#192a56", "primary": "#44bd32", "on_primary": "white", "text_main": "#f5f6fa", "text_sec": "#7f8fa6", "divider": "#353b48", "icon_bg1": "#4cd137", "icon_bg2": "#0097e6" }
    }

    state = { "ekran": "splash", "secili_baslik": "", "gecmis": [], "dil": "TR", "tema": "Obsidian" }

    SOZLUK = {
        "TR": {
            "notlar": "Notlarım", "siparisler": "Alışveriş Listesi",
            "ayarlar": "Ayarlar", "not_klasorleri": "Not Klasörleri", "siparis_listeleri": "Alışveriş Listeleri",
            "yeni_klasor": "Yeni Liste Oluştur", "hata_isim_var": "Bu isim zaten var!",
            "degistir": "Düzenle", "sil": "Sil", "iptal": "İptal", "kaydet": "Kaydet",
            "not_yaz": "Notlarını buraya yaz...", "siparis_ekle": "Ürün adı...", "fiyat_gir": "Fiyat",
            "dil_secimi": "Dil / Language", "tema_secimi": "Tema / Theme",
            # KURUMSAL İMZA
            "gelistirici": f"© 2025 {COMPANY_NAME}", "surum": "Sürüm 1.0.0", 
            "dil_degisti": "Dil güncellendi", "tema_degisti": "Tema güncellendi", "yukleniyor": "Başlatılıyor...",
            "toplam": "TOPLAM", "tl": "TL", "son_islem": ""
        },
        "EN": {
            "notlar": "My Notes", "siparisler": "Shopping List",
            "ayarlar": "Settings", "not_klasorleri": "Note Folders", "siparis_listeleri": "Shopping Lists",
            "yeni_klasor": "Create New List", "hata_isim_var": "Name taken!",
            "degistir": "Edit", "sil": "Delete", "iptal": "Cancel", "kaydet": "Save",
            "not_yaz": "Write details here...", "siparis_ekle": "Product...", "fiyat_gir": "Price",
            "dil_secimi": "Language", "tema_secimi": "Theme",
            # CORPORATE SIGNATURE
            "gelistirici": f"© 2025 {COMPANY_NAME}", "surum": "Version 1.0.0",
            "dil_degisti": "Language updated", "tema_degisti": "Theme updated", "yukleniyor": "Starting...",
            "toplam": "TOTAL", "tl": "$", "son_islem": "Last edited"
        }
    }

    AYLAR_TR = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    GUNLER_TR = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

    # --- YARDIMCI FONKSİYONLAR ---
    def baslat():
        state["dil"] = page.client_storage.get("dil") or "TR"
        state["tema"] = page.client_storage.get("tema") or "Obsidian"
        uygula_tema()

    def uygula_tema():
        tema = THEMES[state["tema"]]
        page.bgcolor = tema["bg"]
        page.theme_mode = ft.ThemeMode.LIGHT if state["tema"] == "Snow" else ft.ThemeMode.DARK

    def c(key): return THEMES[state["tema"]][key]
    def t(key): return SOZLUK[state["dil"]].get(key, "---")
    def db_get(key): return page.client_storage.get(key) or {}
    def db_set(key, val): page.client_storage.set(key, val)

    def tarih_formatla():
        simdi = datetime.datetime.now()
        if state["dil"] == "TR":
            gun = GUNLER_TR[simdi.weekday()]; ay = AYLAR_TR[simdi.month]
            return f"{simdi.day} {ay} {simdi.year}, {gun}"
        else: return simdi.strftime("%d %B %Y, %A")

    def kisa_tarih(): return datetime.datetime.now().strftime("%d.%m %H:%M")
    def tarih_guncelle(baslik, tur):
        key = f"{tur}_tarih"; meta = db_get(key); meta[baslik] = kisa_tarih(); db_set(key, meta)
    def tarih_getir(baslik, tur): return db_get(f"{tur}_tarih").get(baslik, "")

    # --- NAVİGASYON ---
    def git(yeni_ekran):
        if state["ekran"] != yeni_ekran and state["ekran"] != "splash": state["gecmis"].append(state["ekran"])
        state["ekran"] = yeni_ekran; ekrani_ciz()

    def geri_git(e=None):
        if len(state["gecmis"]) > 0: state["ekran"] = state["gecmis"].pop(); ekrani_ciz()

    def splash_gecisi(): git("ana_menu"); 
    try: page.update()
    except: pass

    # --- SAHNELER ---

    def sahne_splash():
        return ft.Container(
            content=ft.Column([
                ft.Image(src=LOGO_FILE, width=150, height=150, fit=ft.ImageFit.CONTAIN, border_radius=20), 
                ft.Container(height=20),
                ft.Text(APP_NAME, size=40, weight="bold", color="white", font_family="Verdana"),
                ft.Container(height=50),
                ft.ProgressBar(width=150, color=BRAND_COLOR, bgcolor="#333333"),
                ft.Container(height=10),
                ft.Text(t("yukleniyor"), color="grey", size=12)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SPLASH_BG, 
            expand=True, alignment=ft.alignment.center
        )

    def sahne_ana_menu():
        txt_saat = ft.Text("", size=32, weight="bold", color=c("text_main"))
        txt_tarih = ft.Text("", size=14, color=c("text_sec"))

        def saat_guncelle():
            if state["ekran"] == "ana_menu":
                try:
                    simdi = datetime.datetime.now()
                    txt_saat.value = simdi.strftime("%H:%M")
                    txt_tarih.value = tarih_formatla()
                    page.update()
                    threading.Timer(1.0, saat_guncelle).start()
                except: return
        saat_guncelle()

        return ft.Column([
            ft.Container(height=30),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon("note_alt_outlined", size=50, color=c("text_main")), 
                        ft.Text(t("notlar"), size=16, weight="bold", color=c("text_main"))
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5), 
                    width=160, height=150, 
                    bgcolor=c("icon_bg1"), 
                    border_radius=20, 
                    shadow=ft.BoxShadow(blur_radius=10, color="#33000000"), 
                    alignment=ft.alignment.center, on_click=lambda _: git("liste_not"), ink=True
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon("shopping_cart_outlined", size=50, color=c("text_main")), 
                        ft.Text(t("siparisler"), size=16, weight="bold", color=c("text_main"))
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=5), 
                    width=160, height=150, 
                    bgcolor=c("icon_bg2"), 
                    border_radius=20, 
                    shadow=ft.BoxShadow(blur_radius=10, color="#33000000"),
                    alignment=ft.alignment.center, on_click=lambda _: git("liste_siparis"), ink=True
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            
            ft.Container(height=15),
            
            ft.Container(
                content=ft.Row([
                    ft.Icon("settings", color=c("text_main")), 
                    ft.Text(t("ayarlar"), size=16, weight="bold", color=c("text_main"))
                ], alignment=ft.MainAxisAlignment.CENTER), 
                width=200, height=50, 
                bgcolor=c("surface"), 
                border=ft.border.all(1, c("divider")), 
                border_radius=25, 
                alignment=ft.alignment.center, on_click=lambda _: git("ayarlar"), ink=True
            ),
            ft.Container(expand=True),
            
            ft.Container(
                content=ft.Column([
                    txt_saat, 
                    txt_tarih
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0), 
                alignment=ft.alignment.center, padding=ft.padding.only(bottom=40)
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    def sahne_liste(tur):
        db_key = "notlar" if tur == "not" else "siparisler"
        veriler = db_get(db_key)
        ikon_turu = "description" if tur == "not" else "shopping_cart"
        
        def detaya_git(baslik): state["secili_baslik"] = baslik; git(f"detay_{tur}")
        def klasor_sil(baslik): del veriler[baslik]; db_set(db_key, veriler); ekrani_ciz()
        def isim_degis_dialog(eski_ad):
            txt = ft.TextField(value=eski_ad, autofocus=True, border_color=c("primary"))
            def on_save(e):
                if txt.value and txt.value != eski_ad: 
                    veriler[txt.value] = veriler[eski_ad]; del veriler[eski_ad]; db_set(db_key, veriler); eski_t = tarih_getir(eski_ad, db_key); 
                    if eski_t: tarih_guncelle(txt.value, db_key)
                    page.close(dlg); ekrani_ciz()
                else: page.close(dlg)
            dlg = ft.AlertDialog(title=ft.Text(t("degistir")), content=txt, actions=[ft.TextButton(t("kaydet"), on_click=on_save)])
            page.open(dlg)
        
        txt_yeni = ft.TextField(hint_text=t("yeni_klasor"), expand=True, border_color=c("divider"), text_style=ft.TextStyle(color=c("text_main")), hint_style=ft.TextStyle(color=c("text_sec")))
        def ekle(e):
            if txt_yeni.value and txt_yeni.value not in veriler: veriler[txt_yeni.value] = [] if tur == "siparis" else ""; db_set(db_key, veriler); tarih_guncelle(txt_yeni.value, db_key); ekrani_ciz()
            elif txt_yeni.value in veriler: page.snack_bar = ft.SnackBar(ft.Text(t("hata_isim_var"))); page.snack_bar.open=True; page.update()
        
        liste_elemanlari = []
        for baslik in veriler.keys(): 
            b = baslik; son_tarih = tarih_getir(b, db_key); sub = f"{son_tarih}" if son_tarih else ""
            liste_elemanlari.append(
                ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ikon_turu, color=c("primary"), size=28), 
                        title=ft.Text(b, color=c("text_main"), weight="bold"), 
                        subtitle=ft.Text(sub, size=12, color=c("text_sec")), 
                        on_click=lambda e, x=b: detaya_git(x), 
                        trailing=ft.PopupMenuButton(icon="more_vert", icon_color=c("text_sec"), items=[ft.PopupMenuItem(text=t("degistir"), icon="edit", on_click=lambda e, x=b: isim_degis_dialog(x)), ft.PopupMenuItem(text=t("sil"), icon="delete", on_click=lambda e, x=b: klasor_sil(x))])
                    ),
                    bgcolor=c("surface"), 
                    border_radius=10,
                    margin=ft.margin.only(bottom=5)
                )
            )
        return ft.Column([
            ft.Container(content=ft.Row([txt_yeni, ft.IconButton("add_circle", icon_color=c("primary"), icon_size=40, on_click=ekle)]), padding=10),
            ft.Column(liste_elemanlari, scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True)

    def sahne_detay_not():
        baslik = state["secili_baslik"]; veriler = db_get("notlar"); icerik = veriler.get(baslik, "")
        if isinstance(icerik, list): icerik = "\n".join(icerik)
        def kaydet(e): veriler[baslik] = e.control.value; db_set("notlar", veriler); tarih_guncelle(baslik, "notlar")
        return ft.Container(content=ft.TextField(value=icerik, multiline=True, min_lines=15, hint_text=t("not_yaz"), border="none", color=c("text_main"), cursor_color=c("primary"), on_change=kaydet), padding=15, expand=True)

    def sahne_detay_siparis():
        baslik = state["secili_baslik"]; veriler = db_get("siparisler"); liste = veriler.get(baslik, []); txt_toplam = ft.Text("", size=18, weight="bold", color=c("primary"))
        def guncelle(): veriler[baslik] = liste; db_set("siparisler", veriler); tarih_guncelle(baslik, "siparisler"); ekrani_ciz()
        def item_sil(idx): del liste[idx]; guncelle()
        def item_duzenle(idx):
            mevcut_ad = liste[idx]["ad"]; mevcut_fiyat = str(liste[idx].get("fiyat", 0))
            inp_ad = ft.TextField(label="Ürün", value=mevcut_ad, autofocus=True); inp_fiyat = ft.TextField(label="Fiyat", value=mevcut_fiyat, keyboard_type=ft.KeyboardType.NUMBER)
            def save(e):
                if inp_ad.value:
                    try: f = float(inp_fiyat.value.replace(",", "."))
                    except: f = 0.0
                    liste[idx]["ad"] = inp_ad.value; liste[idx]["fiyat"] = f; page.close(dlg); guncelle()
            dlg = ft.AlertDialog(title=ft.Text(t("degistir")), content=ft.Column([inp_ad, inp_fiyat], height=150), actions=[ft.TextButton(t("kaydet"), on_click=save)])
            page.open(dlg)
        def item_durum(idx, val): liste[idx]["ok"] = val; guncelle()
        txt_ekle_ad = ft.TextField(hint_text=t("siparis_ekle"), expand=2, border_color=c("divider"), text_style=ft.TextStyle(color=c("text_main")), hint_style=ft.TextStyle(color=c("text_sec")))
        txt_ekle_fiyat = ft.TextField(hint_text=t("fiyat_gir"), expand=1, keyboard_type=ft.KeyboardType.NUMBER, border_color=c("divider"), text_style=ft.TextStyle(color=c("text_main")), hint_style=ft.TextStyle(color=c("text_sec")))
        def ekle(e):
            if txt_ekle_ad.value:
                try: f = float(txt_ekle_fiyat.value.replace(",", ".")) if txt_ekle_fiyat.value else 0.0
                except: f = 0.0
                liste.append({"ad": txt_ekle_ad.value, "fiyat": f, "ok": False}); guncelle()

        items = []; toplam_tutar = 0.0
        for i, item in enumerate(liste):
            fiyat = item.get("fiyat", 0.0)
            if item["ok"]: toplam_tutar += fiyat 
            fiyat_metni = f"{fiyat:.2f} {t('tl')}" if fiyat > 0 else ""
            items.append(ft.Container(
                content=ft.ListTile(
                    leading=ft.Checkbox(value=item["ok"], fill_color=c("primary"), check_color=c("on_primary"), on_change=lambda e, x=i: item_durum(x, e.control.value)),
                    title=ft.Text(item["ad"], color=c("text_sec") if item["ok"] else c("text_main")),
                    subtitle=ft.Text(fiyat_metni, color=c("primary") if item["ok"] else c("text_sec")),
                    trailing=ft.PopupMenuButton(icon="more_vert", icon_color=c("text_sec"), items=[ft.PopupMenuItem(text=t("degistir"), icon="edit", on_click=lambda e, x=i: item_duzenle(x)), ft.PopupMenuItem(text=t("sil"), icon="delete", on_click=lambda e, x=i: item_sil(x))])
                ),
                bgcolor=c("surface"), border_radius=10, margin=ft.margin.only(bottom=2)
            ))
        txt_toplam.value = f"{t('toplam')}: {toplam_tutar:.2f} {t('tl')}"
        return ft.Column([ft.Container(content=txt_toplam, padding=15, bgcolor=c("surface"), border_radius=10, alignment=ft.alignment.center, border=ft.border.all(1, c("primary"))), ft.Divider(color="transparent"), ft.Column(items, scroll=ft.ScrollMode.AUTO, expand=True), ft.Divider(color=c("divider")), ft.Row([txt_ekle_ad, txt_ekle_fiyat, ft.IconButton("add_circle", icon_color=c("primary"), icon_size=40, on_click=ekle)])], expand=True)

    def sahne_ayarlar():
        def dil_set(kod): page.client_storage.set("dil", kod); state["dil"] = kod; ekrani_ciz(); page.snack_bar = ft.SnackBar(ft.Text(t("dil_degisti"))); page.snack_bar.open=True; page.update()
        def tema_set(kod): page.client_storage.set("tema", kod); state["tema"] = kod; uygula_tema(); ekrani_ciz(); page.snack_bar = ft.SnackBar(ft.Text(t("tema_degisti"))); page.snack_bar.open=True; page.update()
        
        cur_dil = state["dil"]; cur_tema = state["tema"]
        
        tema_butonlari = []
        for t_adi in THEMES.keys():
            renk = c("primary") if cur_tema == t_adi else c("surface")
            yazi = c("on_primary") if cur_tema == t_adi else c("text_sec")
            tema_butonlari.append(ft.Container(
                content=ft.Text(t_adi, color=yazi, weight="bold"),
                bgcolor=renk, padding=10, border_radius=10, on_click=lambda e, x=t_adi: tema_set(x),
                expand=True, alignment=ft.alignment.center, border=ft.border.all(1, c("divider"))
            ))

        return ft.Column([
            ft.Text(t("dil_secimi"), size=16, weight="bold", color=c("text_main")), 
            ft.Row([
                ft.ElevatedButton("Türkçe", on_click=lambda _: dil_set("TR"), bgcolor=c("primary") if cur_dil=="TR" else c("surface"), color=c("on_primary") if cur_dil=="TR" else c("text_sec"), expand=True), 
                ft.ElevatedButton("English", on_click=lambda _: dil_set("EN"), bgcolor=c("primary") if cur_dil=="EN" else c("surface"), color=c("on_primary") if cur_dil=="EN" else c("text_sec"), expand=True)
            ]), 
            ft.Divider(color=c("divider")), 
            ft.Text(t("tema_secimi"), size=16, weight="bold", color=c("text_main")),
            ft.Row(tema_butonlari),
            ft.Divider(color=c("divider")), 
            # KURUMSAL İMZA
            ft.Column([
                ft.Text(t("gelistirici"), color=c("text_sec"), weight="bold"),
                ft.Text(t("surum"), color=c("text_sec"), size=12)
            ], spacing=2)
        ])

    # --- 5. MASTER RENDER ---
    def ekrani_ciz():
        page.controls.clear(); aktif = state["ekran"]; icerik = None; show_appbar = True; baslik_control = None
        
        if aktif == "splash": 
            page.add(ft.Container(content=sahne_splash(), bgcolor="#1a1a1a", expand=True, alignment=ft.alignment.center))
            page.update()
            threading.Timer(2.0, splash_gecisi).start()
            return

        elif aktif == "ana_menu":
            # LOGO VE İSİM BURADA
            baslik_control = ft.Row([
                ft.Image(src=LOGO_FILE, width=30, height=30), 
                ft.Text(APP_NAME, weight="bold", size=20, color=BRAND_TEXT_COLOR)
            ], alignment=ft.MainAxisAlignment.CENTER)
            icerik = sahne_ana_menu()
            page.appbar = ft.AppBar(title=baslik_control, center_title=True, bgcolor=c("appbar_bg"), automatically_imply_leading=False)

        elif aktif == "liste_not": baslik_text = t("not_klasorleri"); icerik = sahne_liste("not"); page.appbar = ft.AppBar(title=ft.Text(baslik_text, color=c("text_main")), bgcolor=c("appbar_bg"), leading=ft.IconButton("arrow_back", icon_color=c("text_main"), on_click=geri_git))
        elif aktif == "liste_siparis": baslik_text = t("siparis_listeleri"); icerik = sahne_liste("siparis"); page.appbar = ft.AppBar(title=ft.Text(baslik_text, color=c("text_main")), bgcolor=c("appbar_bg"), leading=ft.IconButton("arrow_back", icon_color=c("text_main"), on_click=geri_git))
        elif aktif == "detay_not": baslik_text = f"{t('notlar')}: {state['secili_baslik']}"; icerik = sahne_detay_not(); page.appbar = ft.AppBar(title=ft.Text(baslik_text, color=c("text_main")), bgcolor=c("appbar_bg"), leading=ft.IconButton("arrow_back", icon_color=c("text_main"), on_click=geri_git))
        elif aktif == "detay_siparis": baslik_text = f"{t('siparisler')}: {state['secili_baslik']}"; icerik = sahne_detay_siparis(); page.appbar = ft.AppBar(title=ft.Text(baslik_text, color=c("text_main")), bgcolor=c("appbar_bg"), leading=ft.IconButton("arrow_back", icon_color=c("text_main"), on_click=geri_git))
        elif aktif == "ayarlar": baslik_text = t("ayarlar"); icerik = sahne_ayarlar(); page.appbar = ft.AppBar(title=ft.Text(baslik_text, color=c("text_main")), bgcolor=c("appbar_bg"), leading=ft.IconButton("arrow_back", icon_color=c("text_main"), on_click=geri_git))

        if not show_appbar: page.appbar = None
        page.add(ft.Container(content=icerik, padding=20 if show_appbar else 0, expand=True, alignment=ft.alignment.center if aktif=="splash" else ft.alignment.top_left))
        page.update()

    baslat()
    ekrani_ciz()

ft.app(target=main)