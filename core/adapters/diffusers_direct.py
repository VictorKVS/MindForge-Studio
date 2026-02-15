import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path
import time, logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

class DiffusersDirectAdapter:
    def __init__(self, model_path=None, output_dir='outputs'):
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA недоступна!')
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if model_path is None:
            model_path = 'G:/1/AI/stable-diffusion-webui-forge/models/Stable-diffusion/v1-5-pruned-emaonly.safetensors'
            if not Path(model_path).exists():
                raise FileNotFoundError(f'Модель не найдена: {model_path}')
        
        logging.info(f'Загрузка модели: {model_path}')
        start = time.time()
        
        self.pipe = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float16,
            safety_checker=None
        ).to('cuda')
        
        # Оптимизации для 12 ГБ VRAM
        self.pipe.enable_attention_slicing()
        self.pipe.enable_vae_slicing()
        
        # Warmup
        _ = self.pipe('test', num_inference_steps=1, generator=torch.Generator('cuda').manual_seed(42))
        
        vram = torch.cuda.memory_allocated() / 1024**3
        logging.info(f' Модель готова | {time.time()-start:.1f} сек | VRAM: {vram:.1f} GB')

    def generate(self, payload):
        seed = payload.get('seed', int(time.time()))
        gen = torch.Generator('cuda').manual_seed(seed)
        start = time.time()
        
        img = self.pipe(
            prompt=payload.get('prompt', 'portrait photo'),
            negative_prompt=payload.get('negative_prompt', 'blurry, deformed'),
            width=payload.get('width', 512),
            height=payload.get('height', 640),
            num_inference_steps=payload.get('steps', 25),
            guidance_scale=payload.get('cfg_scale', 7.5),
            generator=gen
        ).images[0]
        
        path = self.output_dir / f'portrait_{int(time.time())}_{seed}.png'
        img.save(path)
        elapsed = time.time() - start
        logging.info(f' Сохранено: {path.name} | {elapsed:.1f} сек')
        return {'image_path': str(path.resolve()), 'seed': seed, 'time_sec': round(elapsed, 1)}
