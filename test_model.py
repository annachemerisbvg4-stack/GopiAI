import sys
# Сразу печатаем, какой Python используется, для 100% уверенности
print(f"--- Используется Python из: {sys.executable}\n")

try:
    # Пытаемся импортировать главную библиотеку
    from sentence_transformers import SentenceTransformer
    print("[OK] Библиотека 'sentence_transformers' успешно импортирована.")

    model_name = 'sentence-transformers/nli-mpnet-base-v2'
    print(f"[INFO] Попытка загрузить модель: '{model_name}'...")

    # ЭТО ТА САМАЯ СТРОКА, КОТОРАЯ ВЫЗЫВАЕТ ОШИБКУ ВНУТРИ GOPIAI
    model = SentenceTransformer(model_name)

    print("\n✅✅✅ [УСПЕХ!] Модель успешно загружена!")
    print("Объект модели:", model)

    # Проверим, что она может работать
    test_embedding = model.encode("Это тестовое предложение.")
    print("\n✅✅✅ [УСПЕХ!] Кодирование предложения работает. Размер вектора:", test_embedding.shape)

except Exception as e:
    print("\n❌❌❌ [ОШИБКА!] Произошла ошибка при загрузке или использовании модели.")
    # Печатаем полное сообщение об ошибке, чтобы увидеть все детали
    import traceback
    traceback.print_exc()