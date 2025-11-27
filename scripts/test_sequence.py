#!/usr/bin/env python3
"""
Скрипт для ПОСЛЕДОВАТЕЛЬНОГО тестирования реле с локального Mac.
Включает/выключает все 32 канала по очереди.
"""

import sys
import time
import subprocess
import platform
from pymodbus.client import ModbusTcpClient
import pymodbus

def print_failure_report(host, failure_type="PING"):
    print('\n' + '!' * 60)
    print('❌ ОТЧЕТ ОБ ОШИБКЕ ПОДКЛЮЧЕНИЯ')
    print('!' * 60)
    print(f'Целевой хост: {host}')
    
    if failure_type == "PING":
        print('Тип ошибки: Нет ответа на PING (ICMP)')
        print('\n🔍 ВОЗМОЖНЫЕ ПРИЧИНЫ И РЕШЕНИЯ:')
        print('1. 🔌 Питание Gateway:')
        print('   - Проверьте, горит ли индикатор PWR на устройстве.')
        print('2. 🔗 Физическое подключение:')
        print('   - Проверьте Ethernet кабель.')
        print('   - Горят ли индикаторы LINK/ACT на порту?')
        print('3. 🌐 Настройки сети:')
        print('   - Проверьте IP адрес вашего компьютера.')
        print('   - Убедитесь, что вы в одной подсети с Gateway (192.168.1.x).')
        print('4. 🔢 Настройки IP Gateway:')
        print('   - Убедитесь, что IP адрес Gateway действительно 192.168.1.254.')
        
    elif failure_type == "MODBUS_CONNECT":
        print('Тип ошибки: Порт 502 недоступен (TCP Connection Refused/Timeout)')
        print('\n🔍 ВОЗМОЖНЫЕ ПРИЧИНЫ И РЕШЕНИЯ:')
        print('1. ⚙️ Настройки Gateway:')
        print('   - Проверьте, что порт устройства установлен на 502.')
        print('   - Проверьте, что протокол установлен как "Modbus TCP to RTU".')
        print('2. 🔄 Зависшее соединение:')
        print('   - Попробуйте перезагрузить Gateway (выкл/вкл питание).')
        print('3. 🧱 Блокировка:')
        print('   - Проверьте настройки Firewall.')

    print('=' * 60)

def ping_gateway(host):
    """
    Проверяет доступность хоста через ping с таймером.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    
    print(f'📡 Проверка связи с {host}... ⏳ 0s', end='', flush=True)
    
    start_time = time.time()
    try:
        # Запускаем ping
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        while process.poll() is None:
            elapsed = int(time.time() - start_time)
            print(f'\r📡 Проверка связи с {host}... ⏳ {elapsed}s', end='', flush=True)
            time.sleep(0.5)
            
            # Таймаут 5 секунд
            if elapsed > 5:
                process.kill()
                print(f'\r📡 Проверка связи с {host}... ❌ Timeout')
                return False

        print() # Перенос строки
        if process.returncode == 0:
            print(f'✅ Связь с {host} есть')
            return True
        else:
            print(f'❌ Нет связи с {host}')
            return False
    except Exception as e:
        print(f'\n❌ Ошибка при выполнении ping: {e}')
        return False

def test_sequence_mac():
    print('=' * 60)
    print('🧪 ПОСЛЕДОВАТЕЛЬНЫЙ ТЕСТ РЕЛЕ (MAC)')
    print(f'Pymodbus version: {pymodbus.__version__}')
    print('=' * 60)
    print()

    # Настройки
    gateway_host = '192.168.1.254'
    gateway_port = 502
    slave_id = 1
    delay = 0.02
    repeats = 4

    print(f'Gateway: {gateway_host}:{gateway_port}')
    print(f'Slave ID: {slave_id}')
    print(f'Задержка: {delay} сек')
    print(f'Повторов: {repeats}')
    print()

    # Проверка ping
    if not ping_gateway(gateway_host):
        print_failure_report(gateway_host, "PING")
        print('❌ Тест остановлен из-за отсутствия связи')
        return

    try:
        client = ModbusTcpClient(host=gateway_host, port=gateway_port, timeout=3)
        
        print('Подключение к Gateway...')
        if not client.connect():
            print('❌ Не удалось подключиться к Gateway')
            print_failure_report(gateway_host, "MODBUS_CONNECT")
            return
        
        print('✅ Подключено к Gateway')
        print()

        # Функция для отправки команды с учетом версии pymodbus
        def write_coil_safe(addr, val):
            try:
                return client.write_coil(address=addr, value=val, device_id=slave_id)
            except TypeError:
                try:
                    return client.write_coil(address=addr, value=val, slave=slave_id)
                except TypeError:
                    return client.write_coil(address=addr, value=val, unit=slave_id)

        # Сначала выключаем все
        print('Выключение всех каналов...')
        for i in range(32):
            write_coil_safe(i, False)
        print('✅ Все выключены')
        print()

        for cycle in range(repeats):
            print(f'=' * 40)
            print(f'🔁 ЦИКЛ {cycle + 1}/{repeats}')
            print(f'=' * 40)
            
            print('🔄 Включение 1 -> 32...')
            for i in range(32):
                result = write_coil_safe(i, True)
                status = "✅" if not (hasattr(result, 'isError') and result.isError()) else "❌"
                print(f'Канал {i+1}: {status}', end='\r')
                time.sleep(delay)
            print(f'Канал 32: ✅ (Готово)   ')
            
            time.sleep(1)
            
            print('🔄 Выключение 32 -> 1...')
            for i in range(31, -1, -1):
                result = write_coil_safe(i, False)
                status = "✅" if not (hasattr(result, 'isError') and result.isError()) else "❌"
                print(f'Канал {i+1}: {status}', end='\r')
                time.sleep(delay)
            print(f'Канал 1: ✅ (Готово)    ')
            
            if cycle < repeats - 1:
                print('⏸️  Пауза 1 сек...')
                time.sleep(1)
            print()

        client.close()
        print('=' * 60)
        print('✅ ТЕСТ ЗАВЕРШЕН')
        print('=' * 60)

    except Exception as e:
        print(f'❌ Ошибка: {e}')
        
        # Дополнительная подсказка для ошибки No response
        if "No response received" in str(e) or "Connection reset" in str(e):
             print('\n' + '!' * 60)
             print('⚠️  СОВЕТ ПО УСТРАНЕНИЮ:')
             print('Если вы видите ошибку "No response" или "Connection reset", но связь есть:')
             print('1. Откройте веб-интерфейс Gateway.')
             print('2. Перейдите в настройки порта (Serial Settings).')
             print('3. Нажмите кнопку "Restart DEV" (или Submit, затем Restart).')
             print('   ❗ Простого сохранения настроек часто недостаточно!')
             print('!' * 60)

        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sequence_mac()