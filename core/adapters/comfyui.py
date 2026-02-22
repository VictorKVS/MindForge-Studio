import requests
import time
import gc
from pathlib import Path
from typing import Dict, Any, List
import os

class ComfyUIAdapter:
    """Адаптер для работы с ComfyUI API."""
    
    # Таблица оптимальных параметров под разные задачи
    OPTIMAL_PARAMS = {
        "preview": {
            "width": 256,
            "height": 256,
            "steps": 6,
            "cfg": 4.0,
            "sampler": "euler",
            "scheduler": "normal",
            "pause_sec": 1.5,
            "max_batch": 100
        },
        "standard": {
            "width": 320,
            "height": 320,
            "steps": 8,
            "cfg": 5.0,
            "sampler": "euler",
            "scheduler": "normal",
            "pause_sec": 2.0,
            "max_batch": 50
        },
        "high": {
            "width": 384,
            "height": 384,
            "steps": 10,
            "cfg": 6.0,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "pause_sec": 2.5,
            "max_batch": 20
        },
        "max": {
            "width": 448,
            "height": 448,
            "steps": 12,
            "cfg": 6.5,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "pause_sec": 3.0,
            "max_batch": 10
        },
        "experimental": {
            "width": 512,
            "height": 512,
            "steps": 15,
            "cfg": 7.0,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
            "pause_sec": 4.0,
            "max_batch": 5
        }
    }
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8188):
        """Инициализация адаптера."""
        self.url = f"http://{host}:{port}"
        self.output_dir = Path(r"G:\1\AI\ComfyUI\ComfyUI\output")
        self.batch_dir = self.output_dir / "batch"
        self.batch_dir.mkdir(exist_ok=True)
        self.first_generation = True  # Флаг первой генерации
    
    def _is_model_loaded(self) -> bool:
        """Проверка загрузки модели в ComfyUI."""
        try:
            response = requests.get(f"{self.url}/system_stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                return stats.get("gpu_memory_used", 0) > 100  # Модель загружена, если используется >100MB
            return False
        except Exception:
            return False
    
    def _cleanup(self, pause_sec: float = 2.0):
        """
        Очистка памяти и пауза для остывания.
        
        Args:
            pause_sec: Время паузы в секундах
        """
        print(" Очистка памяти...", end=" ", flush=True)
        gc.collect()
        time.sleep(pause_sec)
        print("")
    
    def _build_workflow(
        self,
        prompt: str,
        negative: str,
        width: int = 320,
        height: int = 320,
        seed: int = 42,
        steps: int = 8,
        cfg: float = 5.0,
        sampler: str = "euler",
        scheduler: str = "normal",
        filename_prefix: str = "batch/portrait"
    ) -> Dict[str, Any]:
        """
        Построение рабочего процесса ComfyUI.
        
        Args:
            prompt: Позитивный промпт
            negative: Негативный промпт
            width: Ширина изображения
            height: Высота изображения
            seed: Сид для генерации
            steps: Количество шагов
            cfg: CFG значение
            sampler: Сэмплер (euler/dpmpp_2m/...)
            scheduler: Шедулер (normal/karras/...)
            filename_prefix: Префикс для сохранения файла
            
        Returns:
            Словарь с рабочим процессом
        """
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler,
                    "scheduler": scheduler,
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["4", 1]}
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": negative, "clip": ["4", 1]}
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"images": ["8", 0], "filename_prefix": filename_prefix}
            }
        }
    
    def generate(
        self,
        prompt: str,
        negative: str = "ugly, blurry, deformed face",
        quality: str = "standard",
        seed: int = 42,
        custom_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Генерация одного изображения.
        
        Args:
            prompt: Позитивный промпт
            negative: Негативный промпт
            quality: Качество (preview/standard/high/max/experimental)
            seed: Сид для генерации
            custom_params: Кастомные параметры (переопределяют качество)
            
        Returns:
            Словарь с результатами:
            - success: bool
            - image_path: str
            - generation_time_sec: float
            - parameters: dict (использованные параметры)
        """
        # Получаем параметры качества
        params = self.OPTIMAL_PARAMS.get(quality, self.OPTIMAL_PARAMS["standard"])
        
        # Переопределяем кастомными параметрами
        if custom_params:
            params.update(custom_params)
        
        # Проверка загрузки модели
        if self.first_generation and not self._is_model_loaded():
            print(" Модель не загружена. Жду загрузки...")
            time.sleep(5.0)  # Пауза для загрузки модели
        
        # Очистка памяти с паузой из параметров
        self._cleanup(pause_sec=params["pause_sec"])
        
        # Построение рабочего процесса
        workflow = self._build_workflow(
            prompt=prompt,
            negative=negative,
            width=params["width"],
            height=params["height"],
            seed=seed,
            steps=params["steps"],
            cfg=params["cfg"],
            sampler=params["sampler"],
            scheduler=params["scheduler"]
        )
        
        # Отправка запроса
        print(" Отправка запроса в ComfyUI...", end=" ", flush=True)
        try:
            resp = requests.post(f"{self.url}/prompt", json={"prompt": workflow}, timeout=30)
            resp.raise_for_status()
            print("")
        except Exception as e:
            print(f" Ошибка: {e}")
            raise
        
        # Ожидание результата
        print(" Ожидание генерации...", end=" ", flush=True)
        existing_files = set(self.batch_dir.glob("*.png"))
        start_time = time.time()
        
        # Увеличенный таймаут для первой генерации
        timeout = 120.0 if self.first_generation else 90.0
        
        while time.time() - start_time < timeout:
            current_files = set(self.batch_dir.glob("*.png"))
            new_files = current_files - existing_files
            
            if new_files:
                latest = max(new_files, key=lambda x: x.stat().st_mtime)
                elapsed = time.time() - start_time
                
                print(f" {elapsed:.2f} сек")
                
                # Устанавливаем флаг для последующих генераций
                self.first_generation = False
                
                return {
                    "success": True,
                    "image_path": str(latest),
                    "generation_time_sec": elapsed,
                    "parameters": {
                        "quality": quality,
                        "width": params["width"],
                        "height": params["height"],
                        "steps": params["steps"],
                        "cfg": params["cfg"],
                        "sampler": params["sampler"],
                        "seed": seed
                    }
                }
            
            time.sleep(1.0)
        
        raise TimeoutError(f"Image not generated in {timeout} seconds")
    
    def generate_batch(
        self,
        prompt: str,
        negative: str = "ugly, blurry, deformed face",
        quality: str = "standard",
        count: int = 10,
        seed_base: int = 42
    ) -> Dict[str, Any]:
        """
        Генерация пакета изображений.
        
        Args:
            prompt: Позитивный промпт
            negative: Негативный промпт
            quality: Качество
            count: Количество изображений
            seed_base: Базовый сид (каждое изображение +1)
            
        Returns:
            Словарь с результатами:
            - total_requested: int
            - total_generated: int
            - success_count: int
            - failed_count: int
            - images: list (список результатов)
        """
        # Проверка ограничений
        params = self.OPTIMAL_PARAMS.get(quality, self.OPTIMAL_PARAMS["standard"])
        max_batch = params["max_batch"]
        
        if count > max_batch:
            print(f"  Запрошено {count} изображений, но максимум для качества '{quality}'  {max_batch}")
            print(f"    Будет сгенерировано только {max_batch} изображений")
            count = max_batch
        
        print(f" Генерация {count} изображений (качество: {quality})")
        print(f"   Разрешение: {params['width']}x{params['height']}")
        print(f"   Шаги: {params['steps']}, CFG: {params['cfg']}")
        print(f"   Пауза: {params['pause_sec']} сек")
        print("-" * 60)
        
        results = []
        success_count = 0
        failed_count = 0
        
        for i in range(count):
            print(f"\n[{i+1}/{count}] Генерация...", end=" ")
            
            try:
                result = self.generate(
                    prompt=prompt,
                    negative=negative,
                    quality=quality,
                    seed=seed_base + i
                )
                
                results.append(result)
                success_count += 1
                print(f" {os.path.basename(result['image_path'])}")
                
            except Exception as e:
                print(f" Ошибка: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "parameters": {"seed": seed_base + i}
                })
                failed_count += 1
        
        print("\n" + "=" * 60)
        print(f" Завершено: {success_count}/{count} успешных")
        print(f" Ошибок: {failed_count}")
        
        return {
            "total_requested": count,
            "total_generated": len(results),
            "success_count": success_count,
            "failed_count": failed_count,
            "images": results
        }
    
    def health_check(self) -> bool:
        """
        Проверка доступности сервера.
        
        Returns:
            True если сервер доступен, иначе False
        """
        try:
            resp = requests.get(f"{self.url}/", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
    
    @classmethod
    def get_available_qualities(cls) -> List[str]:
        """
        Получение списка доступных качеств.
        
        Returns:
            Список названий качеств
        """
        return list(cls.OPTIMAL_PARAMS.keys())
    
    @classmethod
    def get_quality_params(cls, quality: str) -> Dict[str, Any]:
        """
        Получение параметров для качества.
        
        Args:
            quality: Название качества
            
        Returns:
            Словарь с параметрами
        """
        return cls.OPTIMAL_PARAMS.get(quality, cls.OPTIMAL_PARAMS["standard"])
