# GENERATION_PIPELINE.md

## Контракт генерации портрета

### Входные данные (заказ)
```yaml
order:
  type: portrait
  style: [cinematic | linkedin | avatar | tech]
  identity_lock: true|false
  seed: integer|null
  denoising: 0.0-1.0 (только для img2img)
  loras: list[str]|null