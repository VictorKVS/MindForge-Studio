# ========================================
# Название: Upscale Batch
# Описание: Увеличение изображений до 2048x2048
# Версия: 1.0.0
# ========================================

import sys
import os
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class Upscaler:
    """Upscaling изображений для стоков"""
    
    def __init__(self, input_folder, output_folder, target_size=2048):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.target_size = target_size
        os.makedirs(output_folder, exist_ok=True)
    
    def upscale(self):
        """Upscaling всех PNG файлов"""
        images = [f for f in os.listdir(self.input_folder) if f.endswith('.png')]
        
        print("=" * 60)
        print(" UPSCALE ДО 2048x2048")
        print("=" * 60)
        print(f" Вход: {self.input_folder}")
        print(f" Выход: {self.output_folder}")
        print(f" Изображений: {len(images)}")
        print("=" * 60)
        
        success = 0
        failed = 0
        
        for img in images:
            src = os.path.join(self.input_folder, img)
            dst = os.path.join(self.output_folder, img)
            
            try:
                image = Image.open(src)
                upscaled = image.resize((self.target_size, self.target_size), Image.LANCZOS)
                upscaled.save(dst)
                print(f" {img}: {image.size}  {upscaled.size}")
                success += 1
            except Exception as e:
                print(f" {img}: Ошибка - {e}")
                failed += 1
        
        print("=" * 60)
        print(f" Успешно: {success}")
        print(f" Ошибок: {failed}")
        print(f" Результаты: {self.output_folder}")
        print("=" * 60)
        
        return {"success": success, "failed": failed}


if __name__ == "__main__":
    upscaler = Upscaler(
        input_folder="aurora/output/batch_50",
        output_folder="aurora/output/upscaled_2048",
        target_size=2048
    )
    upscaler.upscale()
