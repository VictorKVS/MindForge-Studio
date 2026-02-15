from core.adapters.diffusers_direct import DiffusersDirectAdapter

# Инициализация
adapter = DiffusersDirectAdapter(output_dir='outputs/test_run')

# Генерация портрета
result = adapter.generate({
    'prompt': 'cinematic portrait of a man, sharp eyes, natural skin texture, professional photography, 85mm lens',
    'negative_prompt': 'blurry, deformed face, bad anatomy, cartoon, ugly, plastic skin',
    'width': 512,
    'height': 640,
    'steps': 25,
    'cfg_scale': 7.5,
    'seed': 42
})

print(f' Изображение: {result["image_path"]}')
print(f' Время: {result["time_sec"]} сек')
print(f' Seed: {result["seed"]}')
