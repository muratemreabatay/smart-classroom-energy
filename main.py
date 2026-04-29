import customtkinter as ctk
import random
import time

# --- Yapılandırma ---
TOTAL_CHAIRS = 100
ROWS = 10
COLS = 10
UPDATE_INTERVAL_MS = 2000

POWER_RATES = {
    'LIGHTING_PER_ZONE': 3.5 / 4,
    'AC_MAX': 8.0,
    'DESK_DEVICE': 0.05
}

class AmphiTab(ctk.CTkFrame):
    def __init__(self, parent, amphi_name):
        super().__init__(parent, fg_color="transparent")
        self.amphi_name = amphi_name
        
        # State
        self.app_state = {
            "occupied": 0,
            "out_temp": 24.5,
            "out_humidity": 45,
            "zones_active": [False, False, False, False],
            "ac_power_percent": 0,
            "is_power_active": False,
            "current_power_kw": 0.0,
            "total_energy_kwh": 0.0,
            "traditional_energy_kwh": 0.0
        }
        self.chair_buttons = []
        self.zone_frames = []

        self.create_widgets()
        self.update_system()
        self.simulate_environment()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL PANEL (AMFİ PLANI) ---
        self.left_frame = ctk.CTkFrame(self, corner_radius=15)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.header_label = ctk.CTkLabel(self.left_frame, text=f"{self.amphi_name} - Bölgesel Aydınlatmalı Plan", font=("Inter", 20, "bold"))
        self.header_label.pack(pady=(15, 5))

        # --- TOPLU İŞLEMLER (KISA YOLLAR) ---
        self.bulk_frame = ctk.CTkFrame(self.left_frame, fg_color="#1e293b", corner_radius=10)
        self.bulk_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.bulk_frame, text="⚡ Hızlı Öğrenci Kontrolü", font=("Inter", 14, "bold"), text_color="#facc15").pack(side="left", padx=15)
        
        self.zone_var = ctk.StringVar(value="Tüm Amfi")
        self.zone_combo = ctk.CTkComboBox(self.bulk_frame, values=["Tüm Amfi", "Bölge 1 (Sol Ön)", "Bölge 2 (Sağ Ön)", "Bölge 3 (Sol Arka)", "Bölge 4 (Sağ Arka)"], variable=self.zone_var, width=150)
        self.zone_combo.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(self.bulk_frame, text="+5", width=40, fg_color="#10b981", hover_color="#059669", command=lambda: self.bulk_add_students(5)).pack(side="left", padx=5)
        ctk.CTkButton(self.bulk_frame, text="-5", width=40, fg_color="#ef4444", hover_color="#b91c1c", command=lambda: self.bulk_add_students(-5)).pack(side="left", padx=5)
        ctk.CTkButton(self.bulk_frame, text="Doldur", width=60, fg_color="#3b82f6", hover_color="#2563eb", command=lambda: self.bulk_fill(True)).pack(side="left", padx=5)
        ctk.CTkButton(self.bulk_frame, text="Boşalt", width=60, fg_color="#64748b", hover_color="#475569", command=lambda: self.bulk_fill(False)).pack(side="left", padx=5)

        # Tahta
        self.blackboard = ctk.CTkFrame(self.left_frame, width=350, height=40, fg_color="#2d3748", corner_radius=10)
        self.blackboard.pack(pady=5)
        ctk.CTkLabel(self.blackboard, text="AKILLI TAHTA", font=("Inter", 14, "bold"), text_color="gray").place(relx=0.5, rely=0.5, anchor="center")

        # Grid Container
        self.grid_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.grid_container.pack(expand=True, fill="both", padx=15, pady=10)
        
        self.grid_container.grid_rowconfigure((0, 1), weight=1)
        self.grid_container.grid_columnconfigure((0, 1), weight=1)

        # 4 Zone
        for i in range(4):
            zf = ctk.CTkFrame(self.grid_container, fg_color="#1e293b", corner_radius=10, border_width=1, border_color="#334155")
            row = 0 if i < 2 else 1
            col = 0 if i % 2 == 0 else 1
            zf.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.zone_frames.append(zf)

        # Chairs
        for r in range(ROWS):
            for c in range(COLS):
                idx = r * COLS + c
                zone_idx = 0
                if r < 5 and c < 5: zone_idx = 0
                elif r < 5 and c >= 5: zone_idx = 1
                elif r >= 5 and c < 5: zone_idx = 2
                else: zone_idx = 3
                
                target_frame = self.zone_frames[zone_idx]
                local_r = r % 5
                local_c = c % 5
                
                target_frame.grid_rowconfigure(local_r, weight=1)
                target_frame.grid_columnconfigure(local_c, weight=1)
                
                btn = ctk.CTkButton(
                    target_frame, 
                    text=f"{idx+1}", 
                    width=30, height=30,
                    fg_color="#334155", 
                    hover_color="#475569",
                    text_color="#94a3b8",
                    font=("Inter", 9, "bold"),
                    command=lambda i=idx, z=zone_idx: self.toggle_chair(i)
                )
                btn.grid(row=local_r, column=local_c, padx=2, pady=2)
                self.chair_buttons.append({"widget": btn, "occupied": False, "zone": zone_idx})

        # --- SAĞ PANEL (SİSTEM DURUMU) ---
        self.right_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e293b")
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.right_frame, text="Sistem ve Analiz", font=("Inter", 18, "bold")).pack(pady=(15, 10))

        # Çevre Verileri
        self.env_frame = ctk.CTkFrame(self.right_frame, fg_color="#0f172a", corner_radius=10)
        self.env_frame.pack(fill="x", padx=15, pady=5)
        self.temp_label = ctk.CTkLabel(self.env_frame, text="Dış Sıcaklık: -- °C", font=("Inter", 13))
        self.temp_label.pack(pady=5)
        self.humidity_label = ctk.CTkLabel(self.env_frame, text="Dış Nem: -- %", font=("Inter", 13))
        self.humidity_label.pack(pady=5)

        # Durum Göstergeleri
        self.sys_frame = ctk.CTkFrame(self.right_frame, fg_color="#0f172a", corner_radius=10)
        self.sys_frame.pack(fill="x", padx=15, pady=5)
        self.occupancy_label = ctk.CTkLabel(self.sys_frame, text="Doluluk: 0 / 100", font=("Inter", 15, "bold"), text_color="#3b82f6")
        self.occupancy_label.pack(pady=5)
        self.light_label = ctk.CTkLabel(self.sys_frame, text="💡 Aydınlatma: Kapalı", font=("Inter", 13))
        self.light_label.pack(pady=2)
        self.ac_label = ctk.CTkLabel(self.sys_frame, text="❄️ İklimlendirme: Kapalı", font=("Inter", 13))
        self.ac_label.pack(pady=2)
        self.power_label = ctk.CTkLabel(self.sys_frame, text="🔌 Cihaz Güçleri: Beklemede", font=("Inter", 13))
        self.power_label.pack(pady=(2, 5))

        # Tüketim Profili
        self.analytics_frame = ctk.CTkFrame(self.right_frame, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#3b82f6")
        self.analytics_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(self.analytics_frame, text="Tüketim (kWh)", font=("Inter", 13, "bold")).pack(pady=(5, 2))
        self.current_power_label = ctk.CTkLabel(self.analytics_frame, text="Anlık: 0.00 kW", font=("Inter", 13), text_color="#f59e0b")
        self.current_power_label.pack()
        self.smart_energy_label = ctk.CTkLabel(self.analytics_frame, text="Toplam: 0.000", font=("Inter", 13), text_color="#3b82f6")
        self.smart_energy_label.pack(pady=(0, 5))

        # Analiz Butonu
        ctk.CTkButton(self.right_frame, text="📊 Tasarruf Analizi", font=("Inter", 13, "bold"), fg_color="#10b981", hover_color="#059669", height=35, command=self.show_analysis_modal).pack(pady=5, padx=15, fill="x")

    def get_target_chairs(self):
        val = self.zone_var.get()
        if val == "Tüm Amfi": return self.chair_buttons
        elif "1" in val: return [c for c in self.chair_buttons if c["zone"] == 0]
        elif "2" in val: return [c for c in self.chair_buttons if c["zone"] == 1]
        elif "3" in val: return [c for c in self.chair_buttons if c["zone"] == 2]
        elif "4" in val: return [c for c in self.chair_buttons if c["zone"] == 3]
        return self.chair_buttons

    def bulk_add_students(self, count):
        targets = self.get_target_chairs()
        if count > 0:
            empties = [c for c in targets if not c["occupied"]]
            random.shuffle(empties)
            for c in empties[:count]:
                c["occupied"] = True
                self.app_state["occupied"] += 1
                c["widget"].configure(fg_color="#10b981", hover_color="#059669", text_color="white")
        else:
            count = abs(count)
            occupieds = [c for c in targets if c["occupied"]]
            random.shuffle(occupieds)
            for c in occupieds[:count]:
                c["occupied"] = False
                self.app_state["occupied"] -= 1
                c["widget"].configure(fg_color="#334155", hover_color="#475569", text_color="#94a3b8")
        self.update_system()

    def bulk_fill(self, fill_status):
        targets = self.get_target_chairs()
        for c in targets:
            if c["occupied"] != fill_status:
                c["occupied"] = fill_status
                if fill_status:
                    self.app_state["occupied"] += 1
                    c["widget"].configure(fg_color="#10b981", hover_color="#059669", text_color="white")
                else:
                    self.app_state["occupied"] -= 1
                    c["widget"].configure(fg_color="#334155", hover_color="#475569", text_color="#94a3b8")
        self.update_system()

    def toggle_chair(self, index):
        chair = self.chair_buttons[index]
        chair["occupied"] = not chair["occupied"]
        if chair["occupied"]:
            chair["widget"].configure(fg_color="#10b981", hover_color="#059669", text_color="white")
            self.app_state["occupied"] += 1
        else:
            chair["widget"].configure(fg_color="#334155", hover_color="#475569", text_color="#94a3b8")
            self.app_state["occupied"] -= 1
        self.update_system()

    def update_system(self):
        occ = self.app_state["occupied"]
        temp = self.app_state["out_temp"]
        
        zone_occ = [0, 0, 0, 0]
        for c in self.chair_buttons:
            if c["occupied"]: zone_occ[c["zone"]] += 1
                
        active_z = 0
        for i in range(4):
            is_act = zone_occ[i] > 0
            self.app_state["zones_active"][i] = is_act
            if is_act:
                active_z += 1
                self.zone_frames[i].configure(fg_color="#423b1a", border_color="#facc15")
            else:
                self.zone_frames[i].configure(fg_color="#1e293b", border_color="#334155")
        
        if occ > 0 and temp > 22.0:
            self.app_state["ac_power_percent"] = min(100, max(20, (temp - 22) * 6))
        else:
            self.app_state["ac_power_percent"] = 0

        self.app_state["is_power_active"] = occ > 0
        
        p = 0.0
        p += active_z * POWER_RATES['LIGHTING_PER_ZONE']
        p += (self.app_state["ac_power_percent"] / 100.0) * POWER_RATES['AC_MAX']
        p += (occ * POWER_RATES['DESK_DEVICE'])
        self.app_state["current_power_kw"] = p
        self.update_ui()

    def update_ui(self):
        self.temp_label.configure(text=f"Dış Sıcaklık: {self.app_state['out_temp']:.1f} °C")
        self.humidity_label.configure(text=f"Dış Nem: {int(self.app_state['out_humidity'])} %")
        self.occupancy_label.configure(text=f"Doluluk: {self.app_state['occupied']} / {TOTAL_CHAIRS}")
        
        active_z = sum(self.app_state['zones_active'])
        if active_z > 0: self.light_label.configure(text=f"💡 Aydınlatma: {active_z} Bölge AÇIK", text_color="#facc15")
        else: self.light_label.configure(text="💡 Aydınlatma: Kapalı", text_color="gray")
            
        if self.app_state["ac_power_percent"] > 0: self.ac_label.configure(text=f"❄️ İklimlendirme: %{int(self.app_state['ac_power_percent'])}", text_color="#38bdf8")
        else: self.ac_label.configure(text="❄️ İklimlendirme: Kapalı", text_color="gray")
            
        if self.app_state["is_power_active"]: self.power_label.configure(text=f"🔌 Cihazlar: {self.app_state['occupied']} Aktif", text_color="#10b981")
        else: self.power_label.configure(text="🔌 Cihazlar: Beklemede", text_color="gray")

        self.current_power_label.configure(text=f"Anlık: {self.app_state['current_power_kw']:.2f} kW")
        self.smart_energy_label.configure(text=f"Toplam: {self.app_state['total_energy_kwh']:.3f} kWh")

    def simulate_environment(self):
        temp_change = (random.random() - 0.5) * 0.4
        self.app_state["out_temp"] = max(15.0, min(40.0, self.app_state["out_temp"] + temp_change))
        hum_change = random.choice([-1, 0, 1])
        self.app_state["out_humidity"] = max(20, min(80, self.app_state["out_humidity"] + hum_change))
        self.update_system()
        self.accumulate_energy()
        self.after(UPDATE_INTERVAL_MS, self.simulate_environment)

    def accumulate_energy(self):
        SIM_SPEED = 1000
        hours_passed = (UPDATE_INTERVAL_MS * SIM_SPEED) / (1000 * 60 * 60)
        self.app_state["total_energy_kwh"] += (self.app_state["current_power_kw"] * hours_passed)
        trad_kw = (POWER_RATES['LIGHTING_PER_ZONE'] * 4) + POWER_RATES['AC_MAX']
        self.app_state["traditional_energy_kwh"] += (trad_kw * hours_passed)
        self.update_ui()
        if hasattr(self, "analysis_window") and self.analysis_window is not None and self.analysis_window.winfo_exists():
            self.update_analysis_modal()

    def show_analysis_modal(self):
        if hasattr(self, "analysis_window") and self.analysis_window is not None and self.analysis_window.winfo_exists():
            self.analysis_window.lift()
            return
        self.analysis_window = ctk.CTkToplevel(self)
        self.analysis_window.title(f"{self.amphi_name} Analizi")
        self.analysis_window.geometry("450x300")
        self.analysis_window.attributes("-topmost", True)
        ctk.CTkLabel(self.analysis_window, text=f"{self.amphi_name} Tasarruf Özeti", font=("Inter", 18, "bold")).pack(pady=15)
        
        info_f = ctk.CTkFrame(self.analysis_window, fg_color="#1e293b", corner_radius=10)
        info_f.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.mod_trad = ctk.CTkLabel(info_f, text="Eski Tip:\n0", font=("Inter", 14), text_color="#ef4444")
        self.mod_trad.pack(pady=10)
        self.mod_smart = ctk.CTkLabel(info_f, text="Akıllı:\n0", font=("Inter", 14), text_color="#3b82f6")
        self.mod_smart.pack(pady=10)
        self.mod_save = ctk.CTkLabel(info_f, text="Tasarruf:\n0", font=("Inter", 16, "bold"), text_color="#10b981")
        self.mod_save.pack(pady=10)
        self.update_analysis_modal()

    def update_analysis_modal(self):
        t = self.app_state['traditional_energy_kwh']
        s = self.app_state['total_energy_kwh']
        self.mod_trad.configure(text=f"Klasik Tüketim: {t:.3f} kWh")
        self.mod_smart.configure(text=f"Akıllı Sistem: {s:.3f} kWh")
        self.mod_save.configure(text=f"🔥 Net Tasarruf: {(t - s):.3f} kWh")


class MultiAmphiApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BMS: Akıllı Fakülte Otomasyon Sistemi")
        self.geometry("1300x850")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Tabs Container
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create 3 Tabs
        for name in ["Amfi 101", "Amfi 102", "Amfi 103"]:
            self.tabview.add(name)
            tab_frame = AmphiTab(self.tabview.tab(name), name)
            tab_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MultiAmphiApp()
    app.mainloop()
