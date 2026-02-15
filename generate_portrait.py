from core.adapters.diffusers_direct import DiffusersDirectAdapter

print(' Запуск генерации портрета (первый запуск ~45 сек)...')
adapter = DiffusersDirectAdapter(output_dir='outputs/test_run')
result = adapter.generate({
    'prompt': 'professional portrait of a man, sharp eyes, natural skin texture, studio lighting, 85mm lens',
    'negative_prompt': 'blurry, deformed face, bad anatomy, cartoon, plastic skin',
    'width': 512,
    'height': 640,
    'steps': 25,
    'seed': 42
})
print()
print(' Изображение: ' + result['image_path'])
print(' Время генерации: ' + str(result['time_sec']) + ' сек')
print(' Seed: ' + str(result['seed']))
