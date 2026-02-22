# КОНТРАКТ ЗАКАЗА MINDFORGE STUDIO

## Что такое "заказ"

Заказ  это структурированный запрос на генерацию изображений с чёткими параметрами, который можно:
- Сохранить в репозиторий как `automation/orders/<id>/project.yaml`
- Запустить одной командой: `python scripts/run_order.py --file automation/orders/<id>/project.yaml`
- Воспроизвести на любой машине с настроенным окружением
- Отследить через систему одобрения (approved/rejected)

## Типы заказов

### 1. Портрет (portrait)
Генерация одного или серии профессиональных портретов.

**Параметры:**
```yaml
type: portrait
count: 10                # количество изображений
quality: standard        # preview/standard/high/max
subject:
  gender: woman          # woman/man/neutral
  age_range: "25-35"     # возрастная группа
  ethnicity: caucasian   # optional: caucasian/african/asian/latino
style:
  preset: business       # business/medical/creative/cinematic
  clothing: suit         # suit/white_coat/casual/artistic
  background: studio     # studio/office/neutral/creative
output:
  size: 320x320          # целевой размер
  format: png            # png/jpg
Пример использования:
Генерация 10 бизнес-портретов женщин 25-35 лет для загрузки на Adobe Stock
2. Серия (series)
Генерация серии изображений с единым стилем для одного клиента/проекта.
Параметры:
type: series
series_name: "Tech_Executives_2026"
count_per_subject: 5     # 5 вариаций на субъект
subjects:
  - gender: woman, age: "30-40", role: "CTO"
  - gender: man, age: "40-50", role: "CEO"
  - gender: woman, age: "25-35", role: "VP Engineering"
style:
  preset: corporate
  color_palette: "blue_gray"  # ограничение палитры для единства стиля
  lighting: "studio_key"      # единое освещение для всей серии
output:
  naming_convention: "{role}_{index}"  # CEO_01, CTO_01, etc.
Пример использования:
Серия из 15 изображений (3 субъекта  5 вариаций) для сайта технологической компании
3. Комикс/раскадровка (comic)
Генерация последовательности кадров по сценарию.
Параметры:
type: comic
story_id: "SF_001"
panels:
  - sequence: 1
    prompt: "astronaut floating in space, helmet visor reflecting Earth"
    negative: "deformed face, blurry"
    style: cinematic
  - sequence: 2
    prompt: "astronaut looking at damaged spaceship hull, worried expression"
    negative: "ugly, distorted features"
    style: cinematic
  - sequence: 3
    prompt: "close-up of astronaut's face inside helmet, determination"
    negative: "bad anatomy, asymmetrical face"
    style: cinematic
output:
  size: 512x768          # вертикальный формат для комикса
  format: png
  sequence_naming: true  # panel_01.png, panel_02.png...
Пример использования:
Раскадровка из 10 кадров для научно-фантастического короткометражного фильма
4. Озвучка/аудио (audio)  будущее
Генерация аудио-контента (пока не реализовано).
Параметры (планируемые):
type: audio
source: text            # text/file/video
content: "Hello world"  # или путь к файлу
voice: female_neutral   # выбор голоса
output_format: mp3
Формат файла заказа
Каждый заказ хранится как:
automation/orders/<order_id>/
 project.yaml        # основной файл заказа
 prompts/            # дополнительные промпты (опционально)
    custom.txt
 references/         # референсы для стиля (опционально)
    moodboard.jpg
 README.md           # описание заказа для человека
Пример минимального заказа (automation/orders/portrait_001/project.yaml)
# Заказ: 10 бизнес-портретов женщин
order_id: portrait_001
created_at: "2026-02-19"
type: portrait
status: pending          # pending/running/completed/failed

parameters:
  count: 10
  quality: standard      # см. таблицу в Canon.md
  seed_base: 42          # базовое значение для вариаций

subject:
  gender: woman
  age_range: "25-35"
  ethnicity: caucasian

style:
  preset: business
  clothing: suit
  background: studio_neutral

output:
  target_folder: "sd/outputs/portrait_001"
  size: "320x320"
  format: "png"

meta
  intended_use: "Adobe Stock upload"
  keywords: "business, professional, woman, executive, corporate"
  price_tier: "standard"  # standard/premium
Валидация заказа
Заказ проходит валидацию через core/schemas/order.py (pydantic):
Проверка обязательных полей
Проверка допустимых значений (например, quality только из списка)
Проверка ограничений (например, count  50 для quality: standard)
Автоматический расчёт безопасных параметров генерации
Жизненный цикл заказа
Создан (pending)
    
Запущен (running)  генерация изображений
    
Завершён (completed)  все изображения сгенерированы
    
Ревью (review)  человек одобряет/отклоняет
    
Опубликован (published)  approved изображения в архиве для загрузки
Отчёт о выполнении
После завершения заказа создаётся generation_report.json:
{
  "order_id": "portrait_001",
  "status": "completed",
  "total_requested": 10,
  "total_generated": 10,
  "success_count": 10,
  "failed_count": 0,
  "images": [
    {
      "filename": "portrait_001_001.png",
      "path": "sd/outputs/portrait_001/images/portrait_001_001.png",
      "generation_time_sec": 3.2,
      "temperature_c": 74,
      "vram_used_mb": 5842,
      "parameters": {
        "width": 320,
        "height": 320,
        "steps": 8,
        "cfg": 5.0
      }
    }
  ],
  "approved": ["portrait_001_001.png", "portrait_001_003.png", ...],
  "rejected": ["portrait_001_007.png", ...]
}
Безопасность и ограничения
Автоматические ограничения
Максимум 50 изображений за один заказ (для quality: standard)
При превышении  заказ разбивается на части с паузами между ними
При температуре >80C  автоматическая пауза до остывания
Ручное одобрение
Все изображения проходят ручное ревью перед публикацией
Отклонённые изображения перемещаются в rejected/
Одобренные  в approved/ и готовы к загрузке на маркетплейсы
Интеграция с системой
Заказ является "единицей работы" для всей системы:
pipeline.generate(order)  генерация
review.approve(order, image_id)  одобрение
publish.prepare(order)  подготовка к публикации
telegram.bot  управление заказами через бота
Примеры готовых заказов
См. папку automation/orders/examples/ для готовых шаблонов:
business_portrait_woman.yaml
medical_doctor_series.yaml
cinematic_headshot.yaml
