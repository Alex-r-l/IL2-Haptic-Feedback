# -*- coding: utf-8 -*-
import socket
import sdl2
import ctypes
import time
import threading
import json
import os
import tkinter as tk
from tkinter import ttk

# --- КОНСТАНТЫ ---
CONFIG_FILE = "config.json"
UDP_IP = "127.0.0.1"
UDP_PORT = 29373
APP_VERSION = "IL-2 Haptic Feedback v1.6" # Повысил версию для поддержки разных пакетов

DEFAULT_DATA = {
    "selected_joy": "",
    "lang": "RU",
    "engine_work": 0, "fire": 50, "damage": 100,
    "g_load": 100, "g_neg": 50, "flaps": 50, "gear": 50, "touchdown": 50
}

RU_NAMES = {
    "engine_work": "Двигатель", "fire": "Стрельба",
    "damage": "Дамаг", "g_load": "Перегрузка", "g_neg": "Отриц.перегруз",
    "flaps": "Закрылки", "gear": "Шасси", "touchdown": "Касание земли"
}

# --- ДАННЫЕ ЯЗЫКОВ ---
LANG_DATA = {
    "RU": {
        "joy_label": "Джойстик (Force Feedback):",
        "btn_conn": "ПОДКЛЮЧИТЬ",
        "btn_refr": "ОБНОВИТЬ",
        "btn_test": "ТЕСТ ВИБРАЦИИ (50%)",
        "status_wait": "ИЛ-2: ОЖИДАНИЕ ТЕЛЕМЕТРИИ...",
        "status_ok": "ИЛ-2: СОЕДИНЕНИЕ УСТАНОВЛЕНО",
        "listen": "Слушаю телеметрию:",
        "credits": "Сделано в России, г. Вологда  •  Автор: Baloo",
        "names": RU_NAMES
    },
    "EN": {
        "joy_label": "Joystick (Force Feedback):",
        "btn_conn": "CONNECT",
        "btn_refr": "REFRESH",
        "btn_test": "VIBRATION TEST (50%)",
        "status_wait": "IL-2: WAITING FOR TELEMETRY...",
        "status_ok": "IL-2: CONNECTION ESTABLISHED",
        "listen": "Listening telemetry:",
        "credits": "Made in Russia, Vologda  •  Author: Baloo",
        "names": {
            "engine_work": "Engine", "fire": "Firing",
            "damage": "Damage", "g_load": "G-Load", "g_neg": "Negative G",
            "flaps": "Flaps", "gear": "Gear", "touchdown": "Touchdown"
        }
    }
}

class Il2VibroApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_VERSION)
        self.root.geometry("400x570")
        self.root.resizable(False, False)
        
        self.running = True
        self.haptic = None
        self.joy = None
        self.eff_id = -1
        self.last_packet_time = 0
        
        self.settings = self.load_config()
        self.cur_lang = self.settings.get("lang", "RU")
        self.init_net()
        self.create_widgets()
        self.refresh_joysticks()
        
        if self.settings["selected_joy"]:
            self.connect_haptic(self.settings["selected_joy"])

        threading.Thread(target=self.telemetry_loop, daemon=True).start()
        self.update_status_ui()

    def load_config(self):
        import sys
        if getattr(sys, 'frozen', False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_path, CONFIG_FILE)
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return {**DEFAULT_DATA, **json.load(f)}
            except: return DEFAULT_DATA
        return DEFAULT_DATA

    def save_config(self):
        try:
            self.settings["selected_joy"] = self.joy_combo.get()
            self.settings["lang"] = self.lang_combo.get()
            for key in RU_NAMES.keys():
                self.settings[key] = self.cfg_vars[key].get()
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except: pass

    def init_net(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: self.sock.bind((UDP_IP, UDP_PORT))
        except: pass
        self.sock.setblocking(False)

    def refresh_joysticks(self):
        # При обновлении также применяем язык из комбобокса
        self.cur_lang = self.lang_combo.get()
        self.update_ui_texts()
        
        sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_JOYSTICK | sdl2.SDL_INIT_HAPTIC)
        sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK | sdl2.SDL_INIT_HAPTIC)
        vibration_joys = []
        for i in range(sdl2.SDL_NumJoysticks()):
            j = sdl2.SDL_JoystickOpen(i)
            if j and sdl2.SDL_JoystickIsHaptic(j):
                vibration_joys.append(sdl2.SDL_JoystickNameForIndex(i).decode('utf-8', errors='ignore'))
            if j: sdl2.SDL_JoystickClose(j)
        self.joy_combo['values'] = vibration_joys

    def connect_haptic(self, name):
        if self.haptic: sdl2.SDL_HapticClose(self.haptic)
        if self.joy: sdl2.SDL_JoystickClose(self.joy)
        for i in range(sdl2.SDL_NumJoysticks()):
            if sdl2.SDL_JoystickNameForIndex(i).decode('utf-8', errors='ignore') == name:
                self.joy = sdl2.SDL_JoystickOpen(i)
                self.haptic = sdl2.SDL_HapticOpenFromJoystick(self.joy)
                if self.haptic:
                    eff = sdl2.SDL_HapticEffect()
                    eff.type = sdl2.SDL_HAPTIC_CONSTANT
                    self.eff_id = sdl2.SDL_HapticNewEffect(self.haptic, ctypes.byref(eff))
                    return True
        return False

    def create_widgets(self):
        L = LANG_DATA[self.cur_lang]
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель (Название и Язык)
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill=tk.X)
        self.lbl_joy_title = ttk.Label(top_bar, text=L["joy_label"], font=("Arial", 10, "bold"))
        self.lbl_joy_title.pack(side=tk.LEFT)
        
        self.lang_combo = ttk.Combobox(top_bar, values=["RU", "EN"], width=5, state="readonly")
        self.lang_combo.set(self.cur_lang)
        self.lang_combo.pack(side=tk.RIGHT)

        self.joy_combo = ttk.Combobox(main_frame, state="readonly")
        self.joy_combo.pack(fill=tk.X, pady=5)
        if self.settings["selected_joy"]: self.joy_combo.set(self.settings["selected_joy"])
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        self.btn_conn = ttk.Button(btn_frame, text=L["btn_conn"], command=lambda: self.connect_haptic(self.joy_combo.get()))
        self.btn_conn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.btn_refr = ttk.Button(btn_frame, text=L["btn_refr"], command=self.refresh_joysticks)
        self.btn_refr.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        self.cfg_vars = {}
        self.slider_labels = {}
        for key, ru_name in RU_NAMES.items():
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=2)
            lbl = ttk.Label(frame, text=L["names"][key], width=15)
            lbl.pack(side=tk.LEFT)
            self.slider_labels[key] = lbl
            
            var = tk.IntVar(value=self.settings.get(key, DEFAULT_DATA[key]))
            self.cfg_vars[key] = var
            scale = ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=var, 
                              command=lambda v, val_var=var: val_var.set(int(float(v))))
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Label(frame, textvariable=var, width=4).pack(side=tk.RIGHT)

        self.btn_test = ttk.Button(main_frame, text=L["btn_test"], command=self.test_vibe)
        self.btn_test.pack(pady=25)
        self.status_label = ttk.Label(main_frame, text=L["status_wait"], font=("Arial", 10, "bold"))
        self.status_label.pack()

        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Separator(footer_frame, orient=tk.HORIZONTAL).pack(fill=tk.X)
        self.lbl_udp = ttk.Label(main_frame, text=f"{L['listen']} {UDP_IP}:{UDP_PORT}", font=("Arial", 9))
        self.lbl_udp.pack(pady=2)
        self.credits_label = ttk.Label(footer_frame, 
                                  text=L["credits"], 
                                  font=("Verdana", 8, "italic"), 
                                  foreground="#888888")
        self.credits_label.pack(pady=5)

    def update_ui_texts(self):
        L = LANG_DATA[self.cur_lang]
        self.lbl_joy_title.config(text=L["joy_label"])
        self.btn_conn.config(text=L["btn_conn"])
        self.btn_refr.config(text=L["btn_refr"])
        self.btn_test.config(text=L["btn_test"])
        self.lbl_udp.config(text=f"{L['listen']} {UDP_IP}:{UDP_PORT}")
        self.credits_label.config(text=L["credits"])
        for key in RU_NAMES.keys():
            if key in self.slider_labels:
                self.slider_labels[key].config(text=L["names"][key])

    def get_mult(self, name): return self.cfg_vars[name].get() / 100.0

    def update_status_ui(self):
        L = LANG_DATA[self.cur_lang]
        if time.time() - self.last_packet_time < 2:
            self.status_label.config(text=L["status_ok"], foreground="#228B22")
        else:
            self.status_label.config(text=L["status_wait"], foreground="#0000FF")
        self.root.after(1000, self.update_status_ui)

    def test_vibe(self):
        if self.haptic: self.run_vibe(16383, 1000)

    def run_vibe(self, level, length_ms):
        if not self.haptic or self.eff_id < 0: return
        new_eff = sdl2.SDL_HapticEffect()
        new_eff.type = sdl2.SDL_HAPTIC_CONSTANT
        new_eff.constant.length = length_ms
        new_eff.constant.level = int(max(0, min(32767, level)))
        sdl2.SDL_HapticUpdateEffect(self.haptic, self.eff_id, ctypes.byref(new_eff))
        sdl2.SDL_HapticRunEffect(self.haptic, self.eff_id, 1)

    def telemetry_loop(self):
        FIRE_RANGES = [(135, 140), (150, 160)] 
        DMG_MIN = 1000
        DMG_MAX = 1600
        MAX_FFB = 32767
        last_vibe_time = 0
        last_f_l, last_f_r = 0, 0
        last_touch_sum = 0  
        g_val = 0

        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                self.last_packet_time = time.time()
                p_len = len(data)
                curr_pwr, curr_len = 0, 50

                # --- ОБРАБОТКА ПАКЕТА 131 ---
                if p_len == 131:
                    # Двигатель
                    if self.get_mult("engine_work") > 0:
                        eng_val = data[37]
                        if 1 < eng_val < 120:
                            base_eng = (min(eng_val, 100) / 100.0) * MAX_FFB
                            curr_pwr = max(curr_pwr, (base_eng / 5) * self.get_mult("engine_work"))
                            if data[24] == 72: # Форсаж
                                curr_pwr = max(curr_pwr, (MAX_FFB / 1.5) * self.get_mult("engine_work"))
                            if eng_val > 101: # Оверспид
                                curr_pwr = max(curr_pwr, (MAX_FFB / 1.0) * self.get_mult("engine_work"))
                    # Перегрузки
                    if self.get_mult("g_load") > 0:
                        val_raw = data[115]
                        if 1 <= val_raw <= 60:  
                            g_val = 0 if data[56] > 0 else 0.1 
                        elif val_raw > 60:
                            g_val = (val_raw - 60) / 2 # 2. Если значение выше 60 (интенсивная перегрузка)
                        else:
                            g_val = 0 # 3. Во всех остальных случаях (ниже 57) — вибрации нет
                        if g_val > 0:
                            g_pwr = min(g_val, 1.0) # Ограничиваем сверху 1.0, чтобы не было перегруза по формуле
                            curr_pwr = max(curr_pwr, MAX_FFB * g_pwr * self.get_mult("g_load"))
                    if self.get_mult("g_neg") > 0 and data[100] > 180:
                        curr_pwr = max(curr_pwr, (MAX_FFB * 0.3) * self.get_mult("g_neg"))
                    # Закрылки
                    if self.get_mult("flaps") > 0:
                        f_l, f_r = data[119], data[120]
                        if f_l != last_f_l or f_r != last_f_r:
                            curr_pwr = max(curr_pwr, (MAX_FFB / 2.0) * self.get_mult("flaps"))
                        last_f_l, last_f_r = f_l, f_r
                    # Шасси
                    if self.get_mult("gear") > 0 and any(data[i] > 0 for i in range(53, 55)):
                        curr_pwr = max(curr_pwr, (MAX_FFB / 2.0) * self.get_mult("gear"))
                    # Касание
                    if self.get_mult("touchdown") > 0:
                        current_touch_sum = sum(data[64:68])
                        if current_touch_sum != last_touch_sum:
                            max_touch_val = current_touch_sum / 5
                            curr_pwr = max(curr_pwr, MAX_FFB * (max_touch_val / 255.0) * self.get_mult("touchdown"))
                            curr_len = 100
                        last_touch_sum = current_touch_sum

                # --- ОБРАБОТКА ПАКЕТА 147 ---
                elif p_len == 147:
                    # Двигатель
                    if self.get_mult("engine_work") > 0:
                        eng_val = max(data[45], data[49])
                        if 1 < eng_val < 120:
                            base_eng = (min(eng_val, 100) / 100.0) * MAX_FFB
                            curr_pwr = max(curr_pwr, (base_eng / 5) * self.get_mult("engine_work"))
                            if data[32] == 72: # Форсаж
                                curr_pwr = max(curr_pwr, (MAX_FFB / 1.5) * self.get_mult("engine_work"))
                            if eng_val > 101: # Оверспид
                                curr_pwr = max(curr_pwr, MAX_FFB * self.get_mult("engine_work"))
                    # Перегрузки
                    if self.get_mult("g_load") > 0:
                        val_raw = data[131]
                        if 1 <= val_raw <= 60:
                            g_val = 0 if data[67] > 0 else 0.1 
                        elif val_raw > 60:
                            g_val = (val_raw - 60) / 2 # 2. Если значение выше 60 (интенсивная перегрузка)
                        else:
                            g_val = 0 # 3. Во всех остальных случаях (ниже 57) — вибрации нет
                        if g_val > 0:
                            g_pwr = min(g_val, 1.0) # Ограничиваем сверху 1.0, чтобы не было перегруза по формуле
                            curr_pwr = max(curr_pwr, MAX_FFB * g_pwr * self.get_mult("g_load"))
                    # Закрылки
                    if self.get_mult("flaps") > 0:
                        f_l, f_r = data[135], data[136]
                        if f_l != last_f_l or f_r != last_f_r:
                            curr_pwr = max(curr_pwr, (MAX_FFB / 2.0) * self.get_mult("flaps"))
                        last_f_l, last_f_r = f_l, f_r
                    # Шасси
                    if self.get_mult("gear") > 0 and any(data[i] > 0 for i in [69, 70, 73, 74]):
                        curr_pwr = max(curr_pwr, (MAX_FFB / 2.0) * self.get_mult("gear"))
                    # Касание
                    if self.get_mult("touchdown") > 0:
                        current_touch_sum = sum(data[81:92])
                        if current_touch_sum != last_touch_sum:
                            max_touch_val = current_touch_sum / 11
                            curr_pwr = max(curr_pwr, MAX_FFB * (max_touch_val / 255.0) * self.get_mult("touchdown"))
                            curr_len = 100
                        last_touch_sum = current_touch_sum

                # --- УНИВЕРСАЛЬНЫЕ ЭФФЕКТЫ (ПО ДЛИНЕ ПАКЕТА) ---
                # Стрельба
                if any(low <= p_len <= high for low, high in FIRE_RANGES):
                    if self.get_mult("fire") > 0:
                        curr_pwr, curr_len = MAX_FFB * self.get_mult("fire"), 40 
                # Дамаг
                elif p_len >= DMG_MIN:
                    if self.get_mult("damage") > 0:
                        ratio = (min(p_len, DMG_MAX) - DMG_MIN) / (DMG_MAX - DMG_MIN)
                        curr_pwr, curr_len = (MAX_FFB * ratio) * self.get_mult("damage"), 300

                # --- ОТПРАВКА НА ДЖОЙСТИК ---
                if curr_pwr > 0:
                    if time.time() - last_vibe_time > 0.02:
                        self.run_vibe(curr_pwr, max(curr_len, 60))
                        last_vibe_time = time.time()

            except BlockingIOError: time.sleep(0.005)
            except: continue

    def on_close(self):
        self.save_config()
        self.running = False
        if self.haptic: sdl2.SDL_HapticClose(self.haptic)
        if self.joy: sdl2.SDL_JoystickClose(self.joy)
        self.sock.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Il2VibroApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()