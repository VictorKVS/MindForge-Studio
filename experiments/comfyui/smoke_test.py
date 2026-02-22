import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.adapters.comfyui import ComfyUIAdapter

print("="*60)
print(" ComfyUI Smoke Test")
print("="*60)

adapter = ComfyUIAdapter()

if not adapter.health_check():
    print(" ComfyUI server not responding at http://127.0.0.1:8188")
    print("   Start server first: cd G:\\1\\AI\\ComfyUI && .\\run_nvidia_gpu.bat")
    sys.exit(1)

print(" ComfyUI server is alive")
print("\n Generating test portrait (512x768)...")

try:
    result = adapter.generate(
        prompt="professional portrait photo of a woman, sharp eyes, natural skin texture",
        negative_prompt="ugly, blurry, deformed face",
        width=512,
        height=768
    )
    
    if result["success"]:
        print(f"\n SUCCESS! Image generated in {result['generation_time_sec']} sec")
        print(f"   Path: {result['image_path']}")
        print("="*60)
        sys.exit(0)
    else:
        print("\n Generation failed")
        sys.exit(1)
        
except Exception as e:
    print(f"\n FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
