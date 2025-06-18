#!/usr/bin/env python3
"""
Скрипт для очистки старых зависимостей от ChromaDB, AutoGen и других неиспользуемых пакетов
"""

import subprocess
import sys

# Список пакетов для удаления
PACKAGES_TO_REMOVE = [
    # ChromaDB и связанные
    "chromadb",
    "grpcio", 
    "grpcio-status",
    
    # AutoGen и связанные  
    "autogen-agentchat",
    
    # LangChain (если не используется)
    "langchain",
    "langchain-anthropic", 
    "langchain-aws",
    "langchain-chroma",
    "langchain-core",
    "langchain-deepseek",
    "langchain-google-genai",
    "langchain-huggingface", 
    "langchain-ollama",
    "langchain-openai",
    "langchain-text-splitters",
    "langsmith",
    
    # LlamaIndex (если не используется)
    "llama-cloud",
    "llama-cloud-services", 
    "llama-index",
    "llama-index-agent-openai",
    "llama-index-cli",
    "llama-index-core",
    "llama-index-embeddings-openai",
    "llama-index-indices-managed-llama-cloud",
    "llama-index-llms-openai",
    "llama-index-multi-modal-llms-openai",
    "llama-index-program-openai", 
    "llama-index-question-gen-openai",
    "llama-index-readers-file",
    "llama-index-readers-llama-parse",
    "llama-parse",
    
    # Mem0AI (если не используется)
    "mem0ai",
    
    # Browser automation (если не используется)
    "browser-use",
    "playwright",
    "patchright",
    
    # ML пакеты (если семантический поиск не нужен)
    "sentence-transformers",
    "transformers", 
    "torch",
    "faiss-cpu",
    "scikit-learn",
    "scipy",
    
    # Другие неиспользуемые
    "ollama",
    "qdrant-client",
    "kubernetes",
    "boto3",
    "botocore",
    "opentelemetry-api",
    "opentelemetry-exporter-otlp-proto-common",
    "opentelemetry-exporter-otlp-proto-grpc", 
    "opentelemetry-instrumentation",
    "opentelemetry-instrumentation-asgi",
    "opentelemetry-instrumentation-fastapi",
    "opentelemetry-proto",
    "opentelemetry-sdk",
    "opentelemetry-semantic-conventions",
    "opentelemetry-util-http",
    
    # Визуализация (если не используется)
    "matplotlib",
    "graphviz",
    "pyvis",
    
    # PDF обработка (если не используется)
    "pypdf",
    "pdfminer.six", 
    "pdfplumber",
    "pypdfium2",
]

def remove_packages():
    """Удаляет список пакетов"""
    print("🧹 Очистка старых зависимостей...")
    
    for package in PACKAGES_TO_REMOVE:
        try:
            print(f"Удаляем {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "uninstall", package, "-y"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} удален")
            else:
                print(f"⚠️ {package} не найден или уже удален")
                
        except Exception as e:
            print(f"❌ Ошибка удаления {package}: {e}")
    
    print("\n🔍 Проверяем оставшиеся пакеты...")
    subprocess.run([sys.executable, "-m", "pip", "list"])

def install_required():
    """Устанавливает только необходимые пакеты"""
    print("\n📦 Установка необходимых пакетов из requirements.txt...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Необходимые пакеты установлены")
    except Exception as e:
        print(f"❌ Ошибка установки: {e}")

if __name__ == "__main__":
    print("🚨 ВНИМАНИЕ: Этот скрипт удалит много пакетов!")
    print("Убедитесь, что у вас есть backup или виртуальная среда")
    
    response = input("Продолжить? (yes/no): ")
    if response.lower() in ['yes', 'y', 'да']:
        remove_packages()
        install_required()
        print("\n🎉 Очистка завершена!")
    else:
        print("Отменено пользователем")