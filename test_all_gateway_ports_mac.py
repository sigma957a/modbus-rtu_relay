#!/usr/bin/env python3
"""
Скрипт для сканирования портов Gateway с Mac.
Проверяет Slave ID 1, 2, 3, 4.
"""

import sys
import time
from pymodbus.client import ModbusTcpClient
import pymodbus

def test_gateway_ports_mac():
    print('=' * 60)
    print('🔍 СКАНИРОВАНИЕ ПОРТОВ GATEWAY (MAC)')
    print(f'Pymodbus version: {pymodbus.__version__}')
    print('=' * 60)
    print()

    gateway_host = '192.168.1.254'
    gateway_port = 502
    
    try:
        client = ModbusTcpClient(host=gateway_host, port=gateway_port, timeout=2)
        
        print('Подключение к Gateway...')
        if not client.connect():
            print('❌ Не удалось подключиться к Gateway')
            return
        
        print('✅ Подключено к Gateway')
        print()
        
        ports = [1, 2, 3, 4]
        
        for slave_id in ports:
            print(f'Проверка Slave ID {slave_id}...')
            try:
                # Pymodbus v3.11+
                result = client.write_coil(address=0, value=True, device_id=slave_id)
                
                if hasattr(result, 'isError') and result.isError():
                    print(f'  ❌ Ошибка: {result}')
                else:
                    print(f'  ✅ УСПЕХ! Устройство найдено.')
            except Exception as e:
                print(f'  ❌ Ошибка: {e}')
            
            time.sleep(1)
            print()

        client.close()
        print('=' * 60)
        print('✅ СКАН ЗАВЕРШЕН')
        print('=' * 60)

    except Exception as e:
        print(f'❌ Ошибка: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gateway_ports_mac()
