import requests
import sys
import time

print('Проверка генерации через Forge API (512x640, 5 шагов)...')
try:
    resp = requests.post(
        'http://127.0.0.1:7860/sdapi/v1/txt2img',
        json={
            'prompt': 'test face',
            'negative_prompt': 'blurry, deformed',
            'steps': 5,
            'cfg_scale': 6.0,
            'width': 512,
            'height': 640,
            'seed': 42,
            'sampler_name': 'DPM++ 2M Karras',
            'batch_size': 1,
            'n_iter': 1
        },
        timeout=30
    )
    print(f'Статус: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        if 'images' in data and len(data['images']) > 0:
            print(' УСПЕХ! Получено изображение.')
            print(f'   Размер base64: {len(data["images"][0])} символов')
            sys.exit(0)
        else:
            print(f'  Ответ без изображений. Ключи: {list(data.keys())}')
            print(f'   Пример данных: {str(data)[:200]}')
    else:
        print(f' Ошибка {resp.status_code}')
        print(f'   Ответ: {resp.text[:300]}')
    sys.exit(1)
except requests.exceptions.Timeout:
    print(' Таймаут 30 сек  сервер ещё не готов')
    sys.exit(1)
except Exception as e:
    print(f' Исключение: {type(e).__name__}: {e}')
    sys.exit(1)
