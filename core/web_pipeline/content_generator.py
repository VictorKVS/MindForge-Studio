# ========================================
# Название: Web Content Generator
# Описание: Генерация контента для сайтов
# Версия: 1.1.0 (Premium Black & White)
# ========================================

import sys
import os
import json
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class WebContentGenerator:
    """Генерация контента для сайтов"""
    
    def __init__(self, knowledge_path="knowledge"):
        self.knowledge_path = knowledge_path
        self.layouts = self._load_yaml("web/layouts.yaml")
        self.colors = self._load_yaml("web/color_schemes.yaml")
    
    def _load_yaml(self, filename):
        filepath = os.path.join(self.knowledge_path, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf8') as f:
                return yaml.safe_load(f)
        return {}
    
    def generate_layout(self, order):
        """Генерация JSON макета сайта"""
        website = order.get("website", {})
        visual = order.get("visual", {})
        content = website.get("content", {})
        
        color_scheme = self.colors.get(visual.get("color_scheme", "premium_black_white"), {})
        
        layout = {
            "meta": {
                "title": content.get("hero", {}).get("headline", "Website"),
                "description": content.get("hero", {}).get("subheadline", ""),
                "color_scheme": visual.get("color_scheme", "premium_black_white"),
                "colors": color_scheme,
                "style": "premium"
            },
            "pages": [],
            "sections": []
        }
        
        # Hero секция
        hero = content.get("hero", {})
        layout["sections"].append({
            "type": "hero",
            "headline": hero.get("headline", ""),
            "subheadline": hero.get("subheadline", ""),
            "cta": hero.get("cta", ""),
            "background_image": hero.get("image", ""),
            "layout": "full_width",
            "min_height": "800px"
        })
        
        # Остальные секции
        for section in content.get("sections", []):
            layout["sections"].append({
                "type": section.get("type", "about"),
                "title": section.get("title", ""),
                "content": section.get("content", ""),
                "items": section.get("items", []),
                "layout": "minimal_grid"
            })
        
        return layout
    
    def export_figma_json(self, layout, output_path):
        """Экспорт в формат Figma JSON"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        colors = layout["meta"]["colors"]
        
        figma_data = {
            "document": {
                "name": layout["meta"]["title"],
                "pages": [
                    {
                        "name": "Home",
                        "frames": []
                    }
                ]
            },
            "components": [],
            "styles": {
                "colors": colors,
                "typography": {
                    "heading": {"font": "Playfair Display", "size": 64, "weight": 700},
                    "body": {"font": "Inter", "size": 16, "weight": 400}
                }
            }
        }
        
        for i, section in enumerate(layout["sections"]):
            frame = {
                "name": f"{section['type']}_{i}",
                "type": section["type"],
                "x": 0,
                "y": i * 800,
                "width": 1440,
                "height": 800,
                "content": section
            }
            figma_data["document"]["pages"][0]["frames"].append(frame)
        
        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(figma_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def export_html(self, layout, output_path):
        """Экспорт в HTML + Tailwind (Premium Black & White)"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        colors = layout["meta"]["colors"]
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{layout["meta"]["title"]}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '{colors.get("primary", "#000000")}',
                        secondary: '{colors.get("secondary", "#1A1A1A")}',
                        accent: '{colors.get("accent", "#FFFFFF")}',
                        background: '{colors.get("background", "#FFFFFF")}',
                        text: '{colors.get("text", "#000000")}'
                    }},
                    fontFamily: {{
                        heading: ['Playfair Display', 'serif'],
                        body: ['Inter', 'sans-serif']
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        h1, h2, h3 {{ font-family: 'Playfair Display', serif; }}
    </style>
</head>
<body class="bg-background text-text">
'''
        
        # Hero секция (премиум стиль)
        hero = layout["sections"][0] if layout["sections"] else {}
        html += f'''
    <!-- Hero Section - Premium -->
    <section class="min-h-[800px] flex items-center justify-center bg-primary text-accent">
        <div class="text-center px-8">
            <h1 class="text-7xl font-bold mb-6 tracking-wider">{hero.get("headline", "")}</h1>
            <p class="text-xl mb-12 font-light tracking-wide">{hero.get("subheadline", "")}</p>
            <button class="border-2 border-accent text-accent hover:bg-accent hover:text-primary px-12 py-4 text-lg font-semibold tracking-wider transition-all duration-300">
                {hero.get("cta", "Explore")}
            </button>
        </div>
    </section>
'''
        
        # Остальные секции (премиум стиль)
        for section in layout["sections"][1:]:
            html += f'''
    <!-- {section["type"].title()} Section -->
    <section class="py-24 px-8 bg-background">
        <div class="max-w-6xl mx-auto">
            <h2 class="text-5xl font-bold mb-12 text-center tracking-wider">{section.get("title", "")}</h2>
            <p class="text-xl text-center font-light mb-16">{section.get("content", "")}</p>
'''
            # Items (services)
            if section.get("items"):
                html += '''
            <div class="grid grid-cols-1 md:grid-cols-3 gap-12">
'''
                for item in section["items"]:
                    html += f'''
                <div class="text-center p-8 border border-primary">
                    <h3 class="text-2xl font-semibold mb-4">{item}</h3>
                </div>
'''
                html += '''
            </div>
'''
            
            html += '''
        </div>
    </section>
'''
        
        # Footer (премиум)
        html += '''
    <!-- Footer -->
    <footer class="bg-primary text-accent py-12 px-8">
        <div class="max-w-6xl mx-auto text-center">
            <p class="text-lg font-light"> 2026 Premium Design Studio. All rights reserved.</p>
        </div>
    </footer>
'''
        
        html += '''
</body>
</html>
'''
        
        with open(output_path, 'w', encoding='utf8') as f:
            f.write(html)
        
        return output_path


if __name__ == "__main__":
    generator = WebContentGenerator()
    
    # Премиум тестовый заказ
    test_order = {
        "website": {
            "niche": "premium_portfolio",
            "content": {
                "hero": {
                    "headline": "TIMELESS ELEGANCE",
                    "subheadline": "Premium design studio crafting digital experiences",
                    "cta": "Explore Our Work",
                    "image": "hero_premium.png"
                },
                "sections": [
                    {"type": "about", "title": "ABOUT US", "content": "We create sophisticated digital solutions"},
                    {"type": "services", "title": "OUR SERVICES", "items": ["Brand Identity", "Web Design", "Art Direction"]}
                ]
            }
        },
        "visual": {
            "color_scheme": "premium_black_white"
        }
    }
    
    print("=" * 60)
    print(" WEB CONTENT GENERATOR  PREMIUM BLACK & WHITE")
    print("=" * 60)
    
    layout = generator.generate_layout(test_order)
    print(f" Макет сгенерирован: {len(layout['sections'])} секций")
    
    figma_path = generator.export_figma_json(layout, "exports/figma/premium_layout.json")
    print(f" Figma JSON: {figma_path}")
    
    html_path = generator.export_html(layout, "exports/html/premium_site.html")
    print(f" HTML: {html_path}")
    
    print("=" * 60)
    print(" ПРЕМИУМ ЧЕРНО-БЕЛЫЙ САЙТ ГОТОВ!")
    print("=" * 60)
