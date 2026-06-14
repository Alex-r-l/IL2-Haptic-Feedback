# IL-2 Haptic Feedback

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
Для работы программы необходимо выключить обратную связь в настройках игры и включить передачу данных телеметрии в ИЛ-2:
1. Перейдите в папку с игрой, найдите файл `data/startup.cfg`.
2. Откройте его через блокнот и добавьте (или отредактируйте) следующие секции:
```
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
```
### 🔌 Аппаратное подключение и поддержка MMJOY2 (Новое в v1.7)
Программа поддерживает работу с самодельными контроллерами на базе прошивки **MMJOY2 (версия v20151118)**. Вывод эффектов реализован через чип-драйвер светодиодов **WS2811** и силовой ключ на составном транзисторе **КТ972А**.

#### Схема подключения компонентов:
* **Микросхема WS2811 к Arduino:**
  * Ножка №8 (VDD) ➡️ Плюс `+5V` Arduino
  * Ножка №4 (GND) ➡️ Минус `GND` Arduino
  * Ножка №6 (DIN) ➡️ Цифровой пин **B5** Arduino
  * Ножка №7 (SET) ➡️ Припаять к Ножке №4 (`GND`) микросхемы
* **Транзистор КТ972А и вибромотор (3-6V):**
  * Ножка №1 (OUTR) чипа WS2811 ➡️ Подключается к **Базе** транзистора КТ972А.
  * Между **Ножкой №1** и **Ножкой №8 (+5V)** устанавливается подтягивающий резистор номиналом **2 кОм**.
  * **Эмиттер** транзистора КТ972А ➡️ Общий минус (`GND`).
  * **Коллектор** транзистора ➡️ **Минус (-)** вибромоторчика.
  * **Плюс (+)** вибромоторчика ➡️ Напрямую к питанию `+5V` Arduino.
  * **Конденсатор 10 мкФ** установлен между **Базой** транзистора КТ972А и **Минусом (GND)**. Он работает как аппаратный фильтр, сглаживая ШИМ-сигнал от микросхемы WS2811. Благодаря этому интенсивность вибрации меняется плавно и реалистично, без резких ступенчатых рывков.
* **Защита схемы:**
  * Между контактами `+` и `-` моторчика параллельно впаивается защитный диод **1N4007** (катодом к плюсу) для гашения токов самоиндукции.
  * Между контактами `GND` и `VDD` на плате Arduino установлен электролитический конденсатор емкостью **470 мкФ** для сглаживания просадок питания.

#### Настройка конфигуратора MMJOY2:
1. Откройте конфигуратор, перейдите на вкладку **LED**.
2. Включите чекбокс **`LED-RGB WS2811(порт B5)`**.
3. В поле **«Цвет по умолчанию»** выберите **`White`**.
4. Нажмите кнопку **«Записать в контроллер»**.

*Примечание об аппаратной инверсии:* Из-за логики работы открытого коллектора чипа WS2811 схема имеет инвертированную физическую структуру. Когда программа обратной связи не запущена, подтягивающий резистор держит транзистор открытым. Сильный физический удар по ручке джойстика при выключенном скрипте может вызвать кратковременный дребезг контактов тумблеров, из-за чего MMJoy2 гасит светодиод, и мотор уходит в постоянную непрерывную вибрацию. Это конструктивная особенность схемы, а не баг программы.

### Использование
Запустите IL2_Haptic_Feedback.exe.
Выберите ваш джойстик в выпадающем списке и нажмите ПОДКЛЮЧИТЬ.
Настройте желаемые уровни вибрации ползунками (сохраняются автоматически).
Запустите игру. Статус в приложении изменится на "СОЕДИНЕНИЕ УСТАНОВЛЕНО", как только начнется вылет.

### Примечание
В свободном доступе расшифровки телеметрии ИЛ-2 нет, в данной утилите реализовано только то что мне удалось расшифровать.-----------------------------------------------------------------------------------------------------------------
README_EN.md (English Version)
# IL-2 Haptic Feedback

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
To use the program, you must disable feedback in the game settings and enable telemetry data transmission to the IL-2:
1. Navigate to the game folder and locate the `data/startup.cfg` file.
2. Open it with Notepad and add (or edit) the following sections:
```
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
```
### 🔌 Hardware Connection & MMJOY2 Support (New in v1.7)
The application supports custom DIY joysticks based on **MMJOY2 firmware (v20151118)**. Output effects are processed via the **WS2811** LED driver chip and a **KT972A** darlington transistor power switch.

#### Component Wiring:
* **WS2811 to Arduino:**
  * Pin 8 (VDD) ➡️ Arduino `+5V`
  * Pin 4 (GND) ➡️ Arduino `GND`
  * Pin 6 (DIN) ➡️ Arduino digital pin **B5**
  * Pin 7 (SET) ➡️ Connect directly to Pin 4 (`GND`) of the chip
* **KT972A Transistor & Vibration Motor (3-6V):**
  * Pin 1 (OUTR) of the WS2811 chip ➡️ Connects to the **Base** of the KT972A transistor.
  * A **2 kOhm** pull-up resistor must be installed between **Pin 1** and **Pin 8 (+5V)**.
  * **Emitter** of the KT972A ➡️ Common `GND`.
  * **Collector** of the KT972A ➡️ **Minus (-)** terminal of the vibration motor.
  * **Plus (+)** terminal of the motor ➡️ Directly to Arduino `+5V`.
  * A **10 μF capacitor** is installed between the KT972A transistor's base and ground. It acts as a hardware filter, smoothing the PWM signal from the WS2811 microcircuit. This ensures smooth and realistic vibration intensity changes, without any sudden, stepwise jerks.
* **Circuit Protection:**
  * A **1N4007** flyback diode must be soldered in parallel across the motor contacts (cathode to plus) to suppress inductive voltage spikes.
  * A **470 µF** electrolytic capacitor is placed between `GND` and `VDD` on the Arduino board to smooth out voltage drops.

#### MMJOY2 Configuration Setup:
1. Open the MMJOY2 configurator and go to the **LED** tab.
2. Check the **`LED-RGB WS2811(порт B5)`** option.
3. Set the **"Default Color"** (Цвет по умолчанию) to **`White`**.
4. Click **"Save to device"** (Записать в контроллер) in the bottom right corner.

*Hardware Inversion Note:* Due to the open-collector architecture of the WS2811 chip, this circuit uses inverted physical logic. When the haptic feedback script is not running, the pull-up resistor keeps the transistor fully open. A hard physical impact on the joystick grip while the script is off can cause momentary switch contact bounce, causing MMJoy2 to turn off the LED state and triggering a continuous, infinite motor vibration. This is a hardware design trait and not a software bug.

### Usage
Launch IL2_Haptic_Feedback.exe.
Select your joystick from the dropdown list and click CONNECT.
Adjust the desired vibration levels using the sliders (saved automatically).
Launch the game. The status in the application will change to "СОЕДИНЕНИЕ УСТАНОВЛЕНО" as soon as a mission starts.
### Note
There is no publicly available decryption of IL-2 telemetry; this utility only implements what I was able to decrypt.

<img width="303" height="452" alt="Снимок экрана 2026-03-31 160524" src="https://github.com/user-attachments/assets/5fc70b88-74ec-4915-95b0-a51fbc285c9a" />   <img width="302" height="451" alt="image" src="https://github.com/user-attachments/assets/642022f8-b886-44c1-889f-855dc9f301ba" />
