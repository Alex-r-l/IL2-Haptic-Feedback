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
APP_VERSION = "IL-2 Haptic Feedback v1.5" # Обновил версию, так как добавили правки

DEFAULT_DATA = {
    "selected_joy": "",
    "engine_work": 0, "fire": 50, "damage": 100,
    "g_load": 100, "g_neg": 50, "flaps": 50, "gear": 50, "touchdown": 50
}

RU_NAMES = {
    "engine_work": "Двигатель", "fire": "Стрельба",
    "damage": "Дамаг", "g_load": "Перегрузка", "g_neg": "Отриц.перегруз",
    "flaps": "Закрылки", "gear": "Шасси", "touchdown": "Касание земли"
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
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Джойстик (Force Feedback):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.joy_combo = ttk.Combobox(main_frame, state="readonly")
        self.joy_combo.pack(fill=tk.X, pady=5)
        if self.settings["selected_joy"]: self.joy_combo.set(self.settings["selected_joy"])
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="ПОДКЛЮЧИТЬ", command=lambda: self.connect_haptic(self.joy_combo.get())).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_frame, text="ОБНОВИТЬ", command=self.refresh_joysticks).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)

        self.cfg_vars = {}
        for key, ru_name in RU_NAMES.items():
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=f"{ru_name}", width=15).pack(side=tk.LEFT)
            var = tk.IntVar(value=self.settings.get(key, DEFAULT_DATA[key]))
            self.cfg_vars[key] = var
            scale = ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=var, 
                              command=lambda v, val_var=var: val_var.set(int(float(v))))
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Label(frame, textvariable=var, width=4).pack(side=tk.RIGHT)

        ttk.Button(main_frame, text="ТЕСТ ВИБРАЦИИ (50%)", command=self.test_vibe).pack(pady=25)
        
        self.status_label = ttk.Label(main_frame, text="Ожидание ИЛ-2...", font=("Arial", 10, "bold"))
        self.status_label.pack()

        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Separator(footer_frame, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(main_frame, text=f"Слушаю телеметрию: {UDP_IP}:{UDP_PORT}", font=("Arial", 9)).pack(pady=2)
        credits_label = ttk.Label(footer_frame, 
                                  text="Сделано в России, г. Вологда  •  Автор: Baloo", 
                                  font=("Verdana", 8, "italic"), 
                                  foreground="#888888")
        credits_label.pack(pady=5)

    def get_mult(self, name): return self.cfg_vars[name].get() / 100.0

    def update_status_ui(self):
        if time.time() - self.last_packet_time < 2:
            self.status_label.config(text="ИЛ-2: СОЕДИНЕНИЕ УСТАНОВЛЕНО", foreground="#228B22")
        else:
            self.status_label.config(text="ИЛ-2: ОЖИДАНИЕ ТЕЛЕМЕТРИИ...", foreground="#0000FF")
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

        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                self.last_packet_time = time.time()
                p_len = len(data)
                curr_pwr, curr_len = 0, 50

                if p_len == 131:
                    # --- ДВИГАТЕЛЬ ---
                    if self.get_mult("engine_work") > 0:    
                        eng_val = data[37]
                        if (1 < eng_val < 120): 
                            base_eng = (min(eng_val, 100) / 100.0) * MAX_FFB
                            curr_pwr = max(curr_pwr, (base_eng / 3) * self.get_mult("engine_work"))
                    
                            if data[24] == 72:
                                curr_pwr = max(curr_pwr, (MAX_FFB / 1.5) * self.get_mult("engine_work"))
                        
                            if eng_val > 101:
                                curr_pwr = max(curr_pwr, (MAX_FFB / 1.0) * self.get_mult("engine_work"))
                     
                    # --- ПЕРЕГРУЗКА ---
                    if self.get_mult("g_load") > 0:
                        g_val = (data[114] * 0.1) if data[56] > 0 else data[114]
                        if g_val > 0:
                            g_intensity = g_val / 250.0
                            vibe_pwr = MAX_FFB * g_intensity * self.get_mult("g_load")
                            curr_pwr = max(curr_pwr, vibe_pwr)
                        
                    if self.get_mult("g_neg") > 0:
                        if data[100] > 180: 
                            curr_pwr = max(curr_pwr, (MAX_FFB * 0.3) * self.get_mult("g_neg"))

                    # --- МЕХАНИЗАЦИЯ ---
                    # закрылки
                    if self.get_mult("flaps") > 0:                    
                        f_l, f_r = data[119], data[120]            
                        if f_l != last_f_l or f_r != last_f_r:
                            curr_pwr = max(curr_pwr, (MAX_FFB / 2.0) * self.get_mult("flaps"))
                        last_f_l, last_f_r = f_l, f_r
                    # шасси
                    if self.get_mult("gear") > 0:                    
                        if any(data[i] > 0 for i in range(53, 55)):
                            curr_pwr = max(curr_pwr, (MAX_FFB / 2.0) * self.get_mult("gear"))

                    # --- КАСАНИЕ ---
                    if self.get_mult("touchdown") > 0:
                        current_touch_sum = sum(data[64:68])
                        if current_touch_sum != last_touch_sum:
                            curr_pwr = max(curr_pwr, MAX_FFB * self.get_mult("touchdown") * 0.8)
                            curr_len = 100 
                        last_touch_sum = current_touch_sum 

                # --- ФИНАЛЬНЫЙ ВЫБОР ЭФФЕКТА (Приоритеты) ---
                # Стрельба и Дамаг проверяются по длине пакета (p_len)
                
                # 1. СТРЕЛЬБА (Проверяем оба диапазона)
                if any(low <= p_len <= high for low, high in FIRE_RANGES):
                    if self.get_mult("fire") > 0:
                        curr_pwr = MAX_FFB * self.get_mult("fire")
                        curr_len = 40 

                # 2. ДАМАГ (Используем обычный if, чтобы он работал независимо)
                elif p_len >= DMG_MIN:
                    if self.get_mult("damage") > 0:
                        p_len_capped = min(p_len, DMG_MAX) 
                        ratio = (p_len_capped - DMG_MIN) / (DMG_MAX - DMG_MIN)
                        curr_pwr = (MAX_FFB * ratio) * self.get_mult("damage")
                        curr_len = 300

                # --- ОТПРАВКА НА ДЖОЙСТИК ---
                if curr_pwr > 0:
                    if time.time() - last_vibe_time > 0.02:
                        effective_len = max(curr_len, 60)
                        self.run_vibe(curr_pwr, effective_len)
                        last_vibe_time = time.time()

            except BlockingIOError: 
                time.sleep(0.005) # Оптимально для частого опроса
            except: 
                continue

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