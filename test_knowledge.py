from core.knowledge.storage import KnowledgeBase

kb = KnowledgeBase()
gen_id = kb.save_generation(
    prompt="professional portrait of doctor in white coat",
    negative_prompt="ugly, blurry",
    width=512,
    height=768,
    user_id="test_user"
)

print(f" Генерация сохранена: {gen_id}")
print(f" Аудит-отчёт за сегодня:")
for entry in kb.get_audit_report():
    print(f"   {entry['timestamp']} | {entry['user_id']} | {entry['prompt']}")
