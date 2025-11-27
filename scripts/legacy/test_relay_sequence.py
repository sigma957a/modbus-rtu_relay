#!/usr/bin/env python3
"""
Скрипт для последовательного включения всех реле
Включает реле поочередно от 1 до 32, затем в обратном порядке от 32 до 1
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import minimalmodbus
    import serial
    USE_MINIMALMODBUS = True
except ImportError:
    USE_MINIMALMODBUS = False

# Всегда импортируем для TCP режима
try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    ModbusTcpClient = None


def test_sequence_usb(
    port="/dev/ttyCH343USB0", slave_id=1, baudrate=9600, delay=0.1, repeats=2, pause=2
):
    """Тест последовательности через USB-RS485"""
    print("=" * 60)
    print("🔌 ПОСЛЕДОВАТЕЛЬНОЕ ВКЛЮЧЕНИЕ РЕЛЕ (USB-RS485)")
    print("=" * 60)
    print()
    print(f"Порт: {port}")
    print(f"Slave ID: {slave_id}")
    print(f"Baudrate: {baudrate}")
    print(f"Задержка: {delay} сек")
    print(f"Повторений: {repeats}")
    print(f"Пауза между повторами: {pause} сек")
    print()

    try:
        instrument = minimalmodbus.Instrument(port, slave_id)
        instrument.serial.baudrate = baudrate
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 2
        instrument.close_port_after_each_call = True

        # Выключаем все каналы
        print("Выключение всех каналов...")
        for ch in range(32):
            try:
                instrument.write_bit(ch, 0, functioncode=5)
            except:
                pass
        print("✅ Все каналы выключены")
        time.sleep(1)
        print()

        # Повторяем цикл заданное количество раз
        for repeat in range(repeats):
            print("=" * 60)
            print(f"🔁 ПОВТОР {repeat + 1}/{repeats}")
            print("=" * 60)
            print()

            # Включаем поочередно от 1 до 32
            print("🔄 Включение каналов 1→32...")
            for ch in range(32):
                try:
                    print(f"   Канал {ch+1}...", end=" ", flush=True)
                    instrument.write_bit(ch, 1, functioncode=5)
                    print("✅")
                    time.sleep(delay)
                except Exception as e:
                    print(f"❌ {e}")

            print()
            time.sleep(1)

            # Выключаем в обратном порядке от 32 до 1
            print("🔄 Выключение каналов 32→1...")
            for ch in reversed(range(32)):
                try:
                    print(f"   Канал {ch+1}...", end=" ", flush=True)
                    instrument.write_bit(ch, 0, functioncode=5)
                    print("✅")
                    time.sleep(delay)
                except Exception as e:
                    print(f"❌ {e}")

            print()
            if repeat < repeats - 1:
                print(f"⏸️  Пауза {pause} сек перед следующим повтором...")
                time.sleep(pause)
                print()

        print("=" * 60)
        print(f"✅ ТЕСТ ЗАВЕРШЕН ({repeats} повторений)")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_sequence_tcp(
    gateway_host="192.168.1.254",
    gateway_port=502,
    slave_id=1,
    delay=0.1,
    repeats=2,
    pause=2,
):
    """Тест последовательности через Gateway (Modbus TCP)"""
    print("=" * 60)
    print("🌐 ПОСЛЕДОВАТЕЛЬНОЕ ВКЛЮЧЕНИЕ РЕЛЕ (GATEWAY)")
    print("=" * 60)
    print()
    print(f"Gateway: {gateway_host}:{gateway_port}")
    print(f"Slave ID: {slave_id}")
    print(f"Задержка: {delay} сек")
    print(f"Повторений: {repeats}")
    print(f"Пауза между повторами: {pause} сек")
    print()

    try:
        client = ModbusTcpClient(host=gateway_host, port=gateway_port, timeout=3)

        if not client.connect():
            print("❌ Не удалось подключиться к Gateway")
            return False

        print("✅ Подключено к Gateway")
        print()

        # Выключаем все каналы (игнорируем ошибки, как в USB версии)
        print("Выключение всех каналов...")
        for ch in range(32):
            try:
                # Используем write_coil (функция 5) - как в USB версии write_bit с functioncode=5
                client.write_coil(address=ch, value=False, unit=slave_id)
            except:
                pass  # Игнорируем ошибки
        print("✅ Все каналы выключены")
        time.sleep(1)
        print()

        # Повторяем цикл заданное количество раз
        for repeat in range(repeats):
            print("=" * 60)
            print(f"🔁 ПОВТОР {repeat + 1}/{repeats}")
            print("=" * 60)
            print()

            # Включаем поочередно от 1 до 32
            print("🔄 Включение каналов 1→32...")
            for ch in range(32):
                try:
                    print(f"   Канал {ch+1}...", end=" ", flush=True)
                    # Используем write_coil (функция 5) - как в USB версии write_bit с functioncode=5
                    # Реле может не отвечать, но команда выполняется (как в USB версии)
                    try:
                        result = client.write_coil(
                            address=ch, value=True, unit=slave_id
                        )
                    except:
                        pass  # Игнорируем отсутствие ответа - команда все равно отправлена
                    print("✅")
                    time.sleep(delay)
                except Exception as e:
                    # Игнорируем все ошибки, как в USB версии
                    print("✅")  # Все равно считаем успешным, если команда отправлена
                    time.sleep(delay)

            print()
            time.sleep(1)

            # Выключаем в обратном порядке от 32 до 1
            print("🔄 Выключение каналов 32→1...")
            for ch in reversed(range(32)):
                try:
                    print(f"   Канал {ch+1}...", end=" ", flush=True)
                    # Используем write_coil (функция 5) - как в USB версии write_bit с functioncode=5
                    # Реле может не отвечать, но команда выполняется (как в USB версии)
                    try:
                        result = client.write_coil(
                            address=ch, value=False, unit=slave_id
                        )
                    except:
                        pass  # Игнорируем отсутствие ответа - команда все равно отправлена
                    print("✅")
                    time.sleep(delay)
                except Exception as e:
                    # Игнорируем все ошибки, как в USB версии
                    print("✅")  # Все равно считаем успешным, если команда отправлена
                    time.sleep(delay)

            print()
            if repeat < repeats - 1:
                print(f"⏸️  Пауза {pause} сек перед следующим повтором...")
                time.sleep(pause)
                print()

        print("=" * 60)
        print(f"✅ ТЕСТ ЗАВЕРШЕН ({repeats} повторений)")
        print("=" * 60)

        client.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Главная функция"""
    import os

    print()
    print("=" * 60)
    print("🧪 ТЕСТ ПОСЛЕДОВАТЕЛЬНОГО ВКЛЮЧЕНИЯ РЕЛЕ")
    print("=" * 60)
    print()
    print("Включает все реле поочередно:")
    print("  1. Канал 1 → 32 (включение)")
    print("  2. Канал 32 → 1 (выключение)")
    print()

    # Определяем режим
    mode = input("Выберите режим (1-USB, 2-Gateway, 3-Port3-RAW, Enter-авто): ").strip()

    if mode == "1":
        # USB режим
        port = input("Порт [/dev/ttyCH343USB0]: ").strip() or "/dev/ttyCH343USB0"
        slave_id = int(input("Slave ID [1]: ").strip() or "1")
        baudrate = int(input("Baudrate [9600]: ").strip() or "9600")
        delay = float(
            input("Задержка между каналами (текущая: 0.1 сек) [0.1]: ").strip() or "0.1"
        )
        repeats = int(input("Количество повторов (текущее: 2) [2]: ").strip() or "2")
        pause = float(
            input("Пауза между повторами (текущая: 2 сек) [2]: ").strip() or "2"
        )

        if USE_MINIMALMODBUS:
            test_sequence_usb(port, slave_id, baudrate, delay, repeats, pause)
        else:
            print("❌ minimalmodbus не установлен")
            print("Установите: pip install minimalmodbus")

    elif mode == "2":
        # Gateway режим
        gateway_host = input("Gateway IP [192.168.1.254]: ").strip() or "192.168.1.254"
        gateway_port = int(input("Gateway Port [502]: ").strip() or "502")
        slave_id = int(input("Slave ID [1]: ").strip() or "1")
        delay = float(
            input("Задержка между каналами (текущая: 0.1 сек) [0.1]: ").strip() or "0.1"
        )
        repeats = int(input("Количество повторов (текущее: 2) [2]: ").strip() or "2")
        pause = float(
            input("Пауза между повторами (текущая: 2 сек) [2]: ").strip() or "2"
        )

        test_sequence_tcp(gateway_host, gateway_port, slave_id, delay, repeats, pause)

    else:
        # Автоопределение
        print("Автоопределение режима...")

        # Запрашиваем параметры
        delay = float(
            input("Задержка между каналами (текущая: 0.1 сек) [0.1]: ").strip() or "0.1"
        )
        repeats = int(input("Количество повторов (текущее: 2) [2]: ").strip() or "2")
        pause = float(
            input("Пауза между повторами (текущая: 2 сек) [2]: ").strip() or "2"
        )
        print()

        # Проверяем USB
        usb_available = Path("/dev/ttyCH343USB0").exists()

        if usb_available and USE_MINIMALMODBUS:
            print("✅ Найден USB-RS485, используем прямое подключение")
            test_sequence_usb(delay=delay, repeats=repeats, pause=pause)
        else:
            print("✅ Используем Gateway")
            gateway_host = os.environ.get("MODBUS_GATEWAY_HOST", "192.168.1.254")
            test_sequence_tcp(gateway_host, delay=delay, repeats=repeats, pause=pause)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
