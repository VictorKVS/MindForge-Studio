"""
Схема заказа для генерации изображений.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal, Any
from datetime import datetime
from enum import Enum

class QualityEnum(str, Enum):
    """Доступные уровни качества."""
    preview = "preview"
    standard = "standard"
    high = "high"
    max = "max"
    experimental = "experimental"

class Subject(BaseModel):
    """Субъект изображения."""
    gender: Literal["woman", "man", "neutral"] = Field(..., description="Пол")
    age_range: str = Field(..., description="Возрастная группа, например: '25-35'")
    ethnicity: Optional[Literal["caucasian", "african", "asian", "latino"]] = Field(None, description="Этническая принадлежность")

class Style(BaseModel):
    """Стиль изображения."""
    preset: Literal["business", "medical", "creative", "cinematic"] = Field(..., description="Пресет стиля")
    clothing: Optional[str] = Field(None, description="Одежда, например: 'suit', 'white_coat'")
    background: Optional[str] = Field(None, description="Фон, например: 'studio', 'office'")

class OutputConfig(BaseModel):
    """Конфигурация вывода."""
    size: str = Field("320x320", description="Размер изображения")
    format: Literal["png", "jpg"] = Field("png", description="Формат файла")
    target_folder: Optional[str] = Field(None, description="Целевая папка")

class OrderStatus(str, Enum):
    """Статус заказа."""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class Order(BaseModel):
    """Основная схема заказа."""
    order_id: str = Field(..., description="Уникальный идентификатор заказа")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания")
    type: Literal["portrait", "series", "comic"] = Field("portrait", description="Тип заказа")
    status: OrderStatus = Field(OrderStatus.pending, description="Статус заказа")
    
    # Параметры генерации
    count: int = Field(10, ge=1, le=100, description="Количество изображений")
    quality: QualityEnum = Field(QualityEnum.standard, description="Уровень качества")
    seed_base: int = Field(42, description="Базовый сид")
    
    # Субъект
    subject: Subject = Field(..., description="Субъект изображения")
    
    # Стиль
    style: Style = Field(..., description="Стиль изображения")
    
    # Вывод
    output: OutputConfig = Field(default_factory=OutputConfig, description="Конфигурация вывода")
    
    # Метаданные
    meta: Optional[Dict[str, str]] = Field(None, description="Дополнительные метаданные")
    
    # Пользовательские параметры (переопределяют качество)
    custom_params: Optional[Dict[str, Any]] = Field(None, description="Кастомные параметры генерации")
