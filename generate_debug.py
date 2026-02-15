import torch, warnings, time, sys, traceback
from pathlib import Path
warnings.filterwarnings('ignore', message='.*NumPy.*')

print('='*60)
print(' НАЧАЛО ГЕНЕРАЦИИ')
print('='*60)
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
print()

# Загрузка модели
print(' Загрузка модели из файла (первый запуск ~45 сек)...')
model_path = 'G:/1/AI/stable-diffusion-webui-forge/models/Stable-diffusion/v1-5-pruned-emaonly.safetensors'
start = time.time()

try:
    from diffusers import StableDiffusionPipeline
    pipe = StableDiffusionPipeline.from_single_file(
        model_path,
        torch_dtype=torch.float16,
        safety_checker=None
    ).to('cuda')
    
    pipe.enable_attention_slicing()
    pipe.enable_vae_slicing()
    _ = pipe('warmup', num_inference_steps=1, generator=torch.Generator('cuda').manual_seed(42))
    
    print(f' Модель загружена | {time.time()-start:.1f} сек | VRAM: {torch.cuda.memory_allocated()/1024**3:.1f} GB')
    
    # Генерация
    print(' Генерация портрета...')
    start = time.time()
    image = pipe(
        prompt='professional portrait of a man, sharp eyes, natural skin texture',
        negative_prompt='blurry, deformed face, cartoon',
        width=512,
        height=640,
        num_inference_steps=25,
        guidance_scale=7.5,
        generator=torch.Generator('cuda').manual_seed(42)
    ).images[0]
    print(f' Генерация: {time.time()-start:.1f} сек')
    
    # Сохранение
    out_dir = Path('outputs/test_run')
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f'portrait_{int(time.time())}_42.png'
    image.save(path)
    print()
    print('='*60)
    print(' УСПЕХ!')
    print('='*60)
    print(f' {path.resolve()}')
    print('='*60)
    
except Exception as e:
    print()
    print('='*60)
    print(' ОШИБКА')
    print('='*60)
    traceback.print_exc()
    print('='*60)
    sys.exit(1)
