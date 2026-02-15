# experiments/forge_test.py
"""Тест генерации через локальный Forge — без Telegram, только ядро"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pipeline.portrait import PortraitPipeline


def test_forge_generation():
    print("=" * 70)
    print("🔥 Тест генерации через локальный Forge")
    print("=" * 70)
    
    # 1. Инициализация пайплайна с поддержкой 'backend'
    try:
        pipeline = PortraitPipeline(backend="sd_forge", output_dir="outputs/test_forge")
        print("✅ Пайплайн инициализирован с параметром 'backend'")
    except TypeError as e:
        print(f"❌ Ошибка: {e}")
        print("   Убедись, что в __init__ есть параметр 'backend'")
        return False
    
    # 2. Генерация тестового портрета
    print("\n🎨 Генерация портрета (ожидание 15-30 сек)...")
    try:
        result = pipeline.generate(
            prompt="cinematic portrait of a man, sharp eyes, natural skin texture, studio lighting, film grain",
            negative_prompt="blurry, deformed face, bad anatomy, plastic skin, doll, cartoon, anime",
            steps=22,
            cfg_scale=6.0,
            seed=42
        )
        print("✅ Генерация успешна!")
        print(f"\n📸 Изображение: {result['images'][0]}")
        print(f"🎲 Seed: {result['meta']['seed']}")
        print(f"⏱️  Время: {result['meta']['generation_time_sec']} сек")
        
        # Открыть изображение
        try:
            img = Image.open(result["images"][0])
            img.show()
            print("\n🖼️  Изображение открыто в просмотрщике")
        except Exception as e:
            print(f"⚠️  Не удалось открыть: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n❗ Убедись, что Forge запущен:")
    print("   cd G:\\1\\AI\\stable-diffusion-webui-forge")
    print("   webui-user.bat")
    print("   (дождись 'Running on local URL: http://127.0.0.1:7860')\n")
    
    success = test_forge_generation()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 Тест пройден! Пайплайн работает с твоим локальным Forge.")
    else:
        print("💥 Тест провален. См. ошибки выше.")
    print("=" * 70)
    sys.exit(0 if success else 1)