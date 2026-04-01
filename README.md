# IL-2 Haptic Feedback v1.5

[RU] Программа для добавления эффектов тактильной отдачи (Force Feedback) на джойстики (FFB) в симуляторе **ИЛ-2 Штурмовик** через UDP-телеметрию.
*Специально разработана и протестирована для классических джойстиков с одним вибромотором.*

---

## Описание (RU)
Утилита считывает данные телеметрии из игры и передает их на ваше устройство с поддержкой вибрации в реальном времени.

**Основные возможности:**
* **Двигатель:** Эффекты работы, форсажа и вибрация при перекруте (оверспид).
* **Бой:** Вибрация при стрельбе и получении повреждений самолета.
* **Пилотаж:** Тряска при положительных и отрицательных перегрузках.
* **Механизация:** Тактильные эффекты при работе шасси, закрылок и импульс при касании земли.
* **Интерфейс:** Гибкая настройка интенсивности каждого эффекта через удобный GUI.

### Настройка игры
Для работы программы необходимо включить передачу данных в ИЛ-2:
1. Перейдите в папку с игрой, найдите файл `data/startup.cfg`.
2. Откройте его через блокнот и добавьте (или отредактируйте) следующие секции:

[KEY = motiondevice]
    addr = "127.0.0.1"
    decimation = 2
    enable = true
    port = 29373

[KEY = telemetrydevice]
    addr = "127.0.0.1"
    decimation = 2
    enable = true
    port = 29373

### Использование
Запустите IL2_Haptic_Feedback.exe.
Выберите ваш джойстик в выпадающем списке и нажмите ПОДКЛЮЧИТЬ.
Настройте желаемые уровни вибрации ползунками (сохраняются автоматически).
Запустите игру. Статус в приложении изменится на "СОЕДИНЕНИЕ УСТАНОВЛЕНО", как только начнется вылет.

-----------------------------------------------------------------------------------------------------------------
README_EN.md (English Version)
# IL-2 Haptic Feedback v1.5

A utility for adding tactile Force Feedback (FFB) effects to joysticks in IL-2 Sturmovik via UDP telemetry.
*Specifically designed and tested for legacy joysticks equipped with a single vibration motor.*

---

## Description (EN)
The utility reads telemetry data from the game and transmits it to your vibration-enabled device in real time.

**Key features:**
* **Engine:** Effects of operation, afterburner, and vibration during overspeed.
* **Combat:** Vibration when firing and when the aircraft takes damage.
* **Flight:** Shaking during positive and negative G-forces.
* **Mechanization:** Tactile effects during landing gear and flap operation, plus an impulse upon ground contact.
* **Interface:** Flexible adjustment of each effect's intensity via a convenient GUI.

### Game Setup
For the program to work, you need to enable data transmission in IL-2:
1. Navigate to the game folder and locate the `data/startup.cfg` file.
2. Open it with Notepad and add (or edit) the following sections:

[KEY = motiondevice]
    addr = "127.0.0.1"
    decimation = 2
    enable = true
    port = 29373

[KEY = telemetrydevice]
    addr = "127.0.0.1"
    decimation = 2
    enable = true
    port = 29373

### Usage
Launch IL2_Haptic_Feedback.exe.
Select your joystick from the dropdown list and click CONNECT.
Adjust the desired vibration levels using the sliders (saved automatically).
Launch the game. The status in the application will change to "СОЕДИНЕНИЕ УСТАНОВЛЕНО" as soon as a mission starts.

<img width="303" height="452" alt="Снимок экрана 2026-03-31 160524" src="https://github.com/user-attachments/assets/5fc70b88-74ec-4915-95b0-a51fbc285c9a" />
