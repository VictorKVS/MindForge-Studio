import requests
import sys

print('Проверка генерации через Forge API...')
try:
    resp = requests.post(
        'http://127.0.0.1:7860/sdapi/v1/txt2img',
        json={'prompt': 'test face', 'steps': 5, 'seed': 42, 'width': 512, 'height': 640},
        timeout=15
    )
    if resp.status_code == 200 and 'images' in resp.json():
        print(' Forge API готов к генерации!')
        print(f'   Получено {len(resp.json()["images"])} изображение(й)')
        sys.exit(0)
    else:
        print(f' Неожиданный ответ: статус {resp.status_code}')
        print(f'   Ответ: {resp.text[:200]}')
        sys.exit(1)
except Exception as e:
    print(f' Ошибка подключения: {e}')
    sys.exit(1)
