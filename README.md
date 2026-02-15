# MindForge Studio

AI-powered portrait generation studio with secure compliance pipeline.

## Features

- Stable Diffusion 1.5 / SDXL image generation via ComfyUI
- Zero Trust AI Architecture - isolated generation pipeline
- Compliance-first - audit trails, data encryption, access controls
- Healthcare-ready - DICOM/PACS integration, 152-FZ compliant

## Quick Start

```powershell
# 1. Clone repository
git clone https://github.com/VictorKVS/MindForge-Studio.git
cd MindForge-Studio

# 2. Install dependencies
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Configure ComfyUI adapter
copy config.example.yaml config.yaml
# Edit config.yaml -> set comfyui.host/port

# 4. Start ComfyUI server (separate window)
cd G:\1\AI\ComfyUI
.\run_nvidia_gpu.bat

# 5. Run generation test
python experiments\comfyui\smoke_test.py
Documentation
Adapters: ComfyUI Integration (docs/adapters/comfyui.md)
Security Architecture (docs/security/zero-trust-ai.md)
Compliance Checklist (docs/compliance/healthcare.md)
Security & Compliance
All generations logged with immutable audit trail
VRAM isolation between requests (Zero Trust principle)
Automatic PII detection in prompts (OWASP Top-10 for LLMs)
152-FZ / 187-FZ compliant data handling
Contributing
See CONTRIBUTING.md
License
Proprietary - All rights reserved (c) Viktor Kulichenko 2026
