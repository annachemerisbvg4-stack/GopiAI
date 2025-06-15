"""
Методы для интеграции файлового проводника с текстовым редактором
"""

def _connect_file_explorer_signals(self):
    """Подключение сигналов файлового проводника"""
    try:
        # Подключаем двойной клик для открытия файлов
        if hasattr(self.file_explorer, 'file_double_clicked'):
            self.file_explorer.file_double_clicked.connect(self._open_file_in_editor)
            print("[OK] Сигнал file_double_clicked подключен")
        
        # Подключаем одинарный клик для выбора файлов
        if hasattr(self.file_explorer, 'file_selected'):
            self.file_explorer.file_selected.connect(self._on_file_selected)
            print("[OK] Сигнал file_selected подключен")
            
        print("[OK] Сигналы файлового проводника подключены")
        
    except Exception as e:
        print(f"[WARNING] Ошибка подключения сигналов файлового проводника: {e}")

def _open_file_in_editor(self, file_path):
    """Открытие файла в редакторе по двойному клику"""
    try:
        print(f"📂 Открываем файл: {file_path}")
        
        # Проверяем, что это действительно файл
        import os
        if not os.path.isfile(file_path):
            print(f"⚠️ Это не файл: {file_path}")
            return
            
        # Открываем файл в новой вкладке
        if hasattr(self.tab_document, 'open_file_in_tab'):
            self.tab_document.open_file_in_tab(file_path)
        else:
            # Fallback - используем add_new_tab
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                filename = os.path.basename(file_path)
                self.tab_document.add_new_tab(filename, content)
                print(f"✅ Файл открыт (fallback): {filename}")
            except Exception as e:
                print(f"❌ Ошибка открытия файла: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка при открытии файла в редакторе: {e}")

def _on_file_selected(self, file_path):
    """Обработка выбора файла в проводнике"""
    try:
        print(f"📄 Выбран файл: {file_path}")
        # Здесь можно добавить дополнительную логику при выборе файла
        # например, показать информацию о файле в статусной строке
    except Exception as e:
        print(f"[WARNING] Ошибка обработки выбора файла: {e}")