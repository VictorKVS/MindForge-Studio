import torch, warnings, time
from pathlib import Path
warnings.filterwarnings('ignore', message='.*NumPy.*')

print(' Загрузка модели из локального файла...')
print('   Путь: G:/1/AI/stable-diffusion-webui-forge/models/Stable-diffusion/v1-5-pruned-emaonly.safetensors')
print('   (первый запуск ~45 сек  загрузка в VRAM)')
print()

start = time.time()

from diffusers import StableDiffusionPipeline
pipe = StableDiffusionPipeline.from_single_file(
    'G:/1/AI/stable-diffusion-webui-forge/models/Stable-diffusion/v1-5-pruned-emaonly.safetensors',
    torch_dtype=torch.float16,
    safety_checker=None
).to('cuda')

pipe.enable_attention_slicing()
pipe.enable_vae_slicing()
_ = pipe('warmup', num_inference_steps=1, generator=torch.Generator('cuda').manual_seed(42))

load_sec = time.time() - start
print(f' Модель загружена | {load_sec:.1f} сек | VRAM: {torch.cuda.memory_allocated()/1024**3:.1f} GB')
print()

# Генерация портрета
print(' Генерация портрета...')
start = time.time()
image = pipe(
    prompt='professional portrait of a man, sharp eyes, natural skin texture, studio lighting',
    negative_prompt='blurry, deformed face, bad anatomy, cartoon, plastic skin',
    width=512,
    height=640,
    num_inference_steps=25,
    guidance_scale=7.5,
    generator=torch.Generator('cuda').manual_seed(42)
).images[0]
gen_sec = time.time() - start

# Сохранение
out_dir = Path('outputs/test_run')
out_dir.mkdir(parents=True, exist_ok=True)
path = out_dir / f'portrait_{int(time.time())}_42.png'
image.save(path)

print()
print('='*60)
print(' ПОРТРЕТ СГЕНЕРИРОВАН НА RTX 3060')
print('='*60)
print(f' Файл: {path.resolve()}')
print(f'  Загрузка модели: {load_sec:.1f} сек')
print(f'  Генерация: {gen_sec:.1f} сек')
print(f'  Итого: {load_sec + gen_sec:.1f} сек')
print('='*60)
