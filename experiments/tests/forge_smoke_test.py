import sys
from pathlib import Path

# Надёжное определение корня проекта (где находится папка 'core')
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Проверка импорта перед запуском
try:
    from core.pipeline.portrait import PortraitPipeline
except ImportError as e:
    print(f" Ошибка импорта: {e}")
    print(f"Текущий PYTHONPATH: {sys.path}")
    print(f"Корень проекта: {project_root}")
    print(f"Существует 'core'? {project_root.joinpath('core').exists()}")
    sys.exit(1)

def smoke_test():
    print("=" * 70)
    print(" Smoke Test: генерация через локальный Forge")
    print("=" * 70)
    try:
        pipeline = PortraitPipeline(backend="sd_forge", output_dir="outputs/test_run")
        print(" Пайплайн инициализирован")
    except Exception as e:
        print(f" Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n Генерация тестового портрета (15-30 сек)...")
    try:
        result = pipeline.generate(
            prompt="cinematic portrait of a man, sharp eyes, natural skin texture",
            negative_prompt="blurry, deformed face, bad anatomy, plastic skin",
            steps=22,
            cfg_scale=6.0,
            seed=42
        )
        print(" Генерация успешна!")
        print(f"\n Изображение: {Path(result['images'][0]).name}")
        print(f" Seed: {result['meta']['seed']}")
        print(f"  Время: {result['meta']['generation_time_sec']} сек")
        print(f"  Backend: {result['meta']['backend']}")
        return True
    except Exception as e:
        print(f" Ошибка генерации: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n Убедись, что Forge запущен в ОТДЕЛЬНОМ окне:")
    print("   cd G:\\1\\AI\\stable-diffusion-webui-forge")
    print("   .\\webui-user.bat\n")
    
    success = smoke_test()
    
    print("\n" + "=" * 70)
    if success:
        print(" Smoke test пройден! Изображение сохранено в outputs/test_run/")
    else:
        print(" Smoke test провален.")
    print("=" * 70)
    sys.exit(0 if success else 1)
