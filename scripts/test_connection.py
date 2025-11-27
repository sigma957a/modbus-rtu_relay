#!/usr/bin/env python3
"""
Скрипт для тестирования реле с локального Mac.
Автоматически определяет версию pymodbus и использует правильные аргументы.
"""

import sys
import time
from pymodbus.client import ModbusTcpClient
import pymodbus

def test_relay_mac():
    print('=' * 60)
    print('🧪 ТЕСТ РЕЛЕ С ЛОКАЛЬНОЙ МАШИНЫ (MAC)')
    print(f'Pymodbus version: {pymodbus.__version__}')
    print('=' * 60)
    print()

    gateway_host = '192.168.1.254'
    gateway_port = 502
    slave_id = 1

    print(f'Gateway: {gateway_host}:{gateway_port}')
    print(f'Slave ID: {slave_id}')
    print()

    try:
        client = ModbusTcpClient(host=gateway_host, port=gateway_port, timeout=3)
        
        print('Подключение к Gateway...')
        if not client.connect():
            print('❌ Не удалось подключиться к Gateway')
            return
        
        print('✅ Подключено к Gateway')
        print()
        
        # Тест канала 1
        print('Тест канала 1...')
        print('Включение...', end=' ', flush=True)
        
        # Попытка определить правильный аргумент для slave id
        try:
            # Pymodbus v3.11+
            result = client.write_coil(address=0, value=True, device_id=slave_id)
        except TypeError:
            try:
                # Pymodbus v3.x (ранние)
                result = client.write_coil(address=0, value=True, slave=slave_id)
            except TypeError:
                # Pymodbus v2.x
                result = client.write_coil(address=0, value=True, unit=slave_id)
        
        if hasattr(result, 'isError') and result.isError():
            print(f'❌ Ошибка: {result}')
        else:
            print('✅ Успешно')
        
        time.sleep(2)
        
        print('Выключение...', end=' ', flush=True)
        
        try:
            result = client.write_coil(address=0, value=False, device_id=slave_id)
        except TypeError:
            try:
                result = client.write_coil(address=0, value=False, slave=slave_id)
            except TypeError:
                result = client.write_coil(address=0, value=False, unit=slave_id)
        
        if hasattr(result, 'isError') and result.isError():
            print(f'❌ Ошибка: {result}')
        else:
            print('✅ Успешно')
        
        client.close()
        print()
        print('=' * 60)
        print('✅ ТЕСТ ЗАВЕРШЕН')
        print('=' * 60)

    except Exception as e:
        print(f'❌ Ошибка: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_relay_mac()
