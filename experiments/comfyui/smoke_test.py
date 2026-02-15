import sys
from pathlib import Path
sys.path.insert(0, str(Path(file).parent.parent.parent))
from core.adapters.comfyui import ComfyUIAdapter
print("="*60)
print(" ComfyUI Smoke Test")
print("="*60)
adapter = ComfyUIAdapter()
try:
result = adapter.generate(
prompt="professional portrait photo of a woman, sharp eyes, natural skin texture",
negative_prompt="ugly, blurry, deformed face",
width=512,
height=768
)
print(f"\n SUCCESS! Image: {result['image_path']}")
print(f" Time: {result['generation_time_sec']} sec")
print("="*60)
sys.exit(0)
except Exception as e:
print(f"\n FAILED: {e}")
import traceback
traceback.print_exc()
sys.exit(1)
