#!/usr/bin/env python3
"""
Быстрый диагностический скрипт для проверки всех 4 портов Gateway
Отправляет команды на разные Slave ID с малой задержкой (0.3 сек)
Повторяет тест 10 раз для наблюдения за LINK индикаторами
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


def main():
    """Главная функция"""
    print()
    print("=" * 70)
    print("⚡ БЫСТРАЯ ДИАГНОСТИКА ВСЕХ ПОРТОВ GATEWAY (10 ЦИКЛОВ)")
    print("=" * 70)
    print()
    print("Быстрое переключение между портами с задержкой 0.3 сек")
    print("Повторяется 10 раз для наблюдения за LINK индикаторами")
    print()
    print("⚠️  СЛЕДИТЕ ЗА:")
    print("   - Индикаторы LINK1, LINK2, LINK3, LINK4 на Gateway")
    print("   - Напряжение на клеммах A и B каждого порта (с осциллографом)")
    print()
    
    # Настройки
    gateway_host = "192.168.1.254"
    gateway_port = 502
    delay = 0.3
    cycles = 10
    
    print(f"Gateway: {gateway_host}:{gateway_port}")
    print(f"Задержка: {delay} сек")
    print(f"Циклов: {cycles}")
    print()
    
    input("Нажмите Enter, чтобы начать...")
    print()
    
    try:
        client = ModbusTcpClient(host=gateway_host, port=gateway_port, timeout=2)
        
        if not client.connect():
            print("❌ Не удалось подключиться к Gateway")
            return
        
        print("✅ Подключено к Gateway")
        print()
        print("🔄 Начинаем тест...")
        print()
        
        # Порты для тестирования
        ports = [
            ("PORT1", 1),
            ("PORT2", 2),
            ("PORT3", 3),
            ("PORT4", 4),
        ]
        
        # Выполняем циклы
        for cycle in range(cycles):
            print(f"Цикл {cycle + 1}/{cycles}:")
            
            for port_name, slave_id in ports:
                # Отправляем команду
                result = client.write_coil(address=0, value=True, unit=slave_id)
                
                # Статус
                if hasattr(result, 'isError') and not result.isError():
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"  {port_name} (ID:{slave_id}) {status}", end="", flush=True)
                
                # Задержка
                time.sleep(delay)
            
            print()  # Новая строка после каждого цикла
        
        client.close()
        
        print()
        print("=" * 70)
        print("✅ ТЕСТ ЗАВЕРШЕН")
        print("=" * 70)
        print()
        print("💡 РЕЗУЛЬТАТЫ:")
        print("   - Если LINK моргал → порт работает")
        print("   - Если на мультиметре были всплески → RS485 передаёт")
        print("   - Если везде ✅ → Gateway конвертирует TCP→RTU правильно")
        print()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
