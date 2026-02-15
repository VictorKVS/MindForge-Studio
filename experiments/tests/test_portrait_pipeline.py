import pytest
from pathlib import Path
from unittest.mock import patch


def test_init_accepts_backend_param():
    from core.pipeline.portrait import PortraitPipeline
    pipeline = PortraitPipeline(backend="sd_forge", output_dir="outputs/test")
    assert pipeline is not None


def test_init_default_backend():
    from core.pipeline.portrait import PortraitPipeline
    pipeline = PortraitPipeline(output_dir="outputs/test")
    assert hasattr(pipeline, 'backend')
    assert pipeline.backend == "sd_forge"


def test_generate_signature():
    import inspect
    from core.pipeline.portrait import PortraitPipeline
    pipeline = PortraitPipeline(backend="sd_forge", output_dir="outputs/test")
    sig = inspect.signature(pipeline.generate)
    params = list(sig.parameters.keys())
    assert "prompt" in params
    assert "negative_prompt" in params
    assert "seed" in params


@patch('core.adapters.sd_forge.SDForgeAdapter.generate')
def test_generate_returns_contract_structure(mock_generate):
    from core.pipeline.portrait import PortraitPipeline
    mock_generate.return_value = {
        "images": ["outputs/test/portrait_001.png"],
        "meta": {"seed": 42, "steps": 22, "cfg_scale": 6.0}
    }
    pipeline = PortraitPipeline(backend="sd_forge", output_dir="outputs/test")
    result = pipeline.generate(prompt="cinematic portrait", negative_prompt="blurry", seed=42)
    assert "images" in result
    assert isinstance(result["images"], list)
    assert len(result["images"]) > 0
    assert "meta" in result
    assert "seed" in result["meta"]
    assert "backend" in result["meta"]
    assert "style" in result["meta"]
    assert "pipeline" in result["meta"]


def test_output_dir_created():
    import tempfile
    import shutil
    from core.pipeline.portrait import PortraitPipeline
    tmpdir = tempfile.mkdtemp()
    try:
        output_path = Path(tmpdir) / "test_outputs"
        pipeline = PortraitPipeline(backend="sd_forge", output_dir=str(output_path))
        assert output_path.exists()
    finally:
        shutil.rmtree(tmpdir)