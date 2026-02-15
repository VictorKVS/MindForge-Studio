# telegram/bot/handlers/portrait.py
import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from core.pipeline.portrait import PortraitPipeline

router = Router()

SD_URL = os.getenv("SD_WEBUI_URL", "http://127.0.0.1:7860")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", r"G:\1\MindForge_Studio\sd\outputs")

pipeline = PortraitPipeline(sd_url=SD_URL, output_dir=OUTPUT_DIR)


@router.message(Command("portrait"))
async def portrait_cmd(message: Message):
    """
    /portrait
    базовый портрет для портфолио
    """
    result = pipeline.generate(
        prompt="professional cinematic portrait, studio light, sharp focus, high detail",
        negative_prompt="low quality, blurry, deformed face, bad anatomy, bad hands",
        steps=22,
        cfg_scale=6,
        width=512,
        height=640,
        seed=42,
        # пример LoRA:
        # lora="midjourney-studio-light:0.7",
    )

    image_path = result["images"][0]
    await message.answer_photo(
        photo=FSInputFile(image_path),
        caption="🎬 MindForge Studio · Portrait (draft) — одобряешь?"
    )
