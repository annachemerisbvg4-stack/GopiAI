"""
Тест SVG рендеринга для Lucide иконок.
"""

# Настройка путей
import sys
import os

# Добавляем пути к GopiAI модулям
gopiai_paths = [
    r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Core",
    r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Widgets", 
    r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-App",
    r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Extensions",
    r"C:\Users\crazy\GOPI_AI_MODULES\rag_memory_system"
]

for path in gopiai_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Импорт Qt
try:
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QIcon, QPixmap, QPainter
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
    print("✓ PySide6 импортирован")
except ImportError as e:
    print(f"❌ PySide6 недоступен: {e}")
    exit(1)

# Создаём QApplication
app = QApplication([])

def test_svg_file(svg_path):
    """Тестирование загрузки и рендеринга SVG файла."""
    print(f"\n🔍 Тестируем: {svg_path}")
    
    if not os.path.exists(svg_path):
        print("❌ Файл не существует")
        return None
    
    # Читаем содержимое файла
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    print(f"✓ SVG содержимое: {len(svg_content)} символов")
    print(f"  Первые 100 символов: {svg_content[:100]}...")
    
    # Тестируем QSvgRenderer
    renderer = QSvgRenderer()
    if renderer.load(svg_path):
        print("✓ QSvgRenderer успешно загрузил SVG")
        print(f"  Размер по умолчанию: {renderer.defaultSize()}")
        print(f"  Валидный: {renderer.isValid()}")
        
        # Создаём QPixmap и рендерим
        pixmap = QPixmap(24, 24)
        pixmap.fill()  # Прозрачный фон
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        print(f"✓ Рендеринг завершён. Pixmap: {pixmap.size()}")
        print(f"  Пустой pixmap: {pixmap.isNull()}")
        
        # Создаём QIcon
        icon = QIcon(pixmap)
        print(f"✓ QIcon создан. Пустой: {icon.isNull()}")
        print(f"  Доступные размеры: {icon.availableSizes()}")
        
        return icon
    else:
        print("❌ QSvgRenderer не смог загрузить SVG")
        return None

# Тестируем несколько иконок
test_icons = [
    "node_modules/lucide-static/icons/house.svg",
    "node_modules/lucide-static/icons/save.svg", 
    "node_modules/lucide-static/icons/wrench.svg"
]

icons = {}
for icon_path in test_icons:
    icon_name = os.path.basename(icon_path).replace('.svg', '')
    icon = test_svg_file(icon_path)
    if icon:
        icons[icon_name] = icon

print(f"\n🎉 Успешно загружено {len(icons)} иконок: {list(icons.keys())}")

# Создаём тестовое окно для проверки
if icons:
    window = QWidget()
    layout = QVBoxLayout(window)
    
    for name, icon in icons.items():
        label = QLabel(f"Иконка: {name}")
        label.setPixmap(icon.pixmap(24, 24))
        layout.addWidget(label)
    
    window.setWindowTitle("Тест Lucide иконок")
    window.show()
    
    print("🚀 Тестовое окно показано. Закройте его для завершения.")
    app.exec()
else:
    print("❌ Ни одна иконка не загружена")

print("🚀 Тест завершён!")
