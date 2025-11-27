#!/usr/bin/env python3
"""
Диагностический скрипт для проверки всех 4 портов Gateway
Отправляет команды на разные Slave ID с задержкой
Позволяет увидеть мигание LINK индикаторов и измерить напряжение на RS485
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    print("❌ pymodbus не установлен")
    print("Установите: pip install pymodbus")
    sys.exit(1)


def test_gateway_port(gateway_host, gateway_port, slave_id, port_name, delay=3):
    """Тест одного порта Gateway"""
    print("=" * 70)
    print(f"🔍 ТЕСТ {port_name} (Slave ID: {slave_id})")
    print("=" * 70)
    print()
    print(f"Gateway: {gateway_host}:{gateway_port}")
    print(f"Slave ID: {slave_id}")
    print()
    print("⚠️  ВНИМАНИЕ! Следите за:")
    print(f"   - Индикатор {port_name.replace('PORT', 'LINK')} на Gateway (должен моргнуть)")
    print(f"   - Напряжение на клеммах A и B порта {port_name}")
    print()
    
    try:
        client = ModbusTcpClient(host=gateway_host, port=gateway_port, timeout=3)
        
        if not client.connect():
            print("❌ Не удалось подключиться к Gateway")
            return False
        
        print("✅ Подключено к Gateway")
        print()
        
        # Отправляем 3 команды с задержкой
        for i in range(3):
            print(f"Попытка {i+1}/3: Отправка команды на канал 1...")
            print(f"  → Отправка Modbus TCP команды...")
            
            result = client.write_coil(address=0, value=True, unit=slave_id)
            
            print(f"  ← Получен ответ: {type(result).__name__}")
            
            if hasattr(result, 'isError'):
                if result.isError():
                    print(f"  ❌ Ошибка: {result}")
                else:
                    print(f"  ✅ Успешно!")
            
            print(f"  ⏱️  Ожидание {delay} секунд (проверьте LINK и напряжение)...")
            time.sleep(delay)
            print()
        
        client.close()
        print(f"✅ Тест {port_name} завершен")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция"""
    print()
    print("=" * 70)
    print("🧪 ДИАГНОСТИКА ВСЕХ ПОРТОВ GATEWAY")
    print("=" * 70)
    print()
    print("Этот скрипт последовательно отправляет команды на разные Slave ID,")
    print("чтобы проверить, какой порт Gateway активен.")
    print()
    print("В режиме Multi-Host все порты слушают на одном TCP порту 502,")
    print("и Gateway маршрутизирует команды по Slave ID.")
    print()
    print("Следите за индикаторами LINK1, LINK2, LINK3, LINK4 на Gateway")
    print("и измеряйте напряжение на клеммах A и B каждого порта.")
    print()
    
    # Настройки
    gateway_host = input("Gateway IP [192.168.1.254]: ").strip() or "192.168.1.254"
    gateway_port = int(input("Gateway Port [502]: ").strip() or "502")
    delay = float(input("Задержка между командами (сек) [3]: ").strip() or "3")
    
    print()
    input("Нажмите Enter, чтобы начать тест...")
    print()
    
    # Тестируем все 4 порта с разными Slave ID
    ports = [
        ("PORT 1", 1),
        ("PORT 2", 2),
        ("PORT 3", 3),
        ("PORT 4", 4),
    ]
    
    results = {}
    
    for port_name, slave_id in ports:
        success = test_gateway_port(gateway_host, gateway_port, slave_id, port_name, delay)
        results[port_name] = success
        
        # Пауза между портами
        if port_name != "PORT 4":
            print()
            print("=" * 70)
            print(f"⏸️  Пауза 5 секунд перед следующим портом...")
            print("=" * 70)
            print()
            time.sleep(5)
    
    # Итоговая сводка
    print()
    print("=" * 70)
    print("📊 ИТОГОВАЯ СВОДКА")
    print("=" * 70)
    print()
    
    for port_name, success in results.items():
        status = "✅ Работает" if success else "❌ Ошибка"
        print(f"{port_name}: {status}")
    
    print()
    print("=" * 70)
    print("💡 ИНТЕРПРЕТАЦИЯ РЕЗУЛЬТАТОВ:")
    print("=" * 70)
    print()
    print("1. Если LINK индикатор мигает:")
    print("   ✅ Gateway конвертирует TCP → RTU на этот порт")
    print()
    print("2. Если видно напряжение на клеммах A и B:")
    print("   ✅ RS485 передача работает")
    print()
    print("3. Если всё равно 0В:")
    print("   ❌ Проверьте настройки VirCOM:")
    print("      - Enable RS485 Multi-Host = Yes")
    print("      - Modbus TCP To RTU = Yes")
    print("      - Transfer Protocol = Modbus_TCP Protocol")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
