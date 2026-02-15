# core/app.py

from core.pipeline.portrait import PortraitPipeline

def main():
    pipeline = PortraitPipeline(
        backend="sd_1111",
        output_dir="sd/outputs/test"
    )

    result = pipeline.generate(
        prompt="cinematic portrait of a young woman, red hair, studio light, ultra detailed",
        negative_prompt="blurry, low quality, bad anatomy",
        steps=20,
        cfg_scale=6,
        width=512,
        height=640,
        seed=42
    )

    print("✅ Generated:", result["images"])

if __name__ == "__main__":
    main()
