import sys
sys.path.insert(0, '.')

from core.pipeline.portrait import PortraitPipeline

print("="*60)
print(" Тест интеграции: генерация + аудит")
print("="*60)

pipeline = PortraitPipeline(user_id="test_doctor")

print("\n Запуск генерации с аудитом...")
result = pipeline.generate(
    prompt="professional portrait of radiologist in white coat",
    negative_prompt="ugly, blurry, deformed face",
    width=512,
    height=768,
    style="medical"
)

print(f"\n Генерация успешна!")
print(f"   Изображение: {result['image_path']}")
print(f"   Время: {result['generation_time_sec']} сек")
print(f"   ID генерации: {result['generation_id']}")
print(f"   Статус аудита: {result['audit_status']}")

print(f"\n Аудит-отчёт за сегодня:")
report = pipeline.get_audit_report(days=1)
for entry in report[:3]:
    print(f"    {entry['timestamp']} | {entry['user_id']} | {entry['prompt'][:50]}...")

print("\n Интеграция работает корректно!")
print("="*60)
