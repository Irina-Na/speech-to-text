"""
Скрипт для диагностики поддержки CUDA/GPU в PyTorch.
Запустите этот скрипт, чтобы проверить, почему GPU не используется.
"""
import sys
import os

try:
    import torch
except OSError as e:
    if "DLL" in str(e) or "dll" in str(e).lower() or "WinError" in str(e):
        print("=" * 60)
        print("ОШИБКА: Не удается загрузить библиотеки PyTorch (DLL)")
        print("=" * 60)
        print(f"\nДетали ошибки: {e}")
        print("\n" + "=" * 60)
        print("РЕШЕНИЕ ПРОБЛЕМЫ С DLL")
        print("=" * 60)
        print("\n1. Установите Visual C++ Redistributables:")
        print("   Скачайте и установите с официального сайта Microsoft:")
        print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("   (или более новую версию)")
        print("\n2. Переустановите PyTorch:")
        print("   pip uninstall torch torchvision torchaudio")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        print("\n3. Если проблема сохраняется, попробуйте:")
        print("   - Перезагрузить компьютер")
        print("   - Установить все обновления Windows")
        print("   - Проверить антивирус (может блокировать DLL)")
        print("\n4. Альтернатива - установить CPU-only версию:")
        print("   pip uninstall torch torchvision torchaudio")
        print("   pip install torch torchvision torchaudio")
        sys.exit(1)
    else:
        raise
except ImportError:
    print("ОШИБКА: PyTorch не установлен!")
    print("Установите PyTorch: pip install torch")
    sys.exit(1)

try:
    print("=" * 60)
    print("ДИАГНОСТИКА ПОДДЕРЖКИ CUDA/GPU")
    print("=" * 60)
    print(f"\n✓ PyTorch установлен: версия {torch.__version__}")
    
    # Проверка доступности CUDA
    cuda_available = torch.cuda.is_available()
    print(f"\nCUDA доступна: {'ДА ✓' if cuda_available else 'НЕТ ✗'}")
    
    if cuda_available:
        print(f"\nКоличество GPU: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"    Память: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
        print(f"\nТекущий GPU: {torch.cuda.current_device()}")
        print(f"Версия CUDA (PyTorch): {torch.version.cuda}")
    else:
        print("\n" + "=" * 60)
        print("ПРОБЛЕМА: CUDA недоступна")
        print("=" * 60)
        print("\nВозможные причины и решения:")
        print("\n1. PyTorch установлен БЕЗ поддержки CUDA (CPU-only)")
        print("   Решение: Переустановите PyTorch с поддержкой CUDA")
        print("   Команда для Windows (CUDA 12.1):")
        print("   pip uninstall torch torchvision torchaudio")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        print("\n2. Драйверы NVIDIA не установлены")
        print("   Решение: Установите драйверы с https://www.nvidia.com/drivers")
        print("\n3. Версия CUDA несовместима")
        print("   Решение: Проверьте совместимость версий на https://pytorch.org/get-started/locally/")
        print("\n4. GPU не поддерживает CUDA")
        print("   Решение: Убедитесь, что у вас GPU от NVIDIA с поддержкой CUDA")
    
    # Дополнительная информация
    print("\n" + "=" * 60)
    print("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ")
    print("=" * 60)
    print(f"Версия Python: {sys.version}")
    print(f"Платформа: {sys.platform}")
    
    if hasattr(torch.backends, 'cudnn'):
        print(f"cuDNN доступен: {torch.backends.cudnn.enabled}")
        if torch.backends.cudnn.enabled:
            print(f"Версия cuDNN: {torch.backends.cudnn.version()}")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n⚠ Неожиданная ошибка: {e}")
    print("Попробуйте переустановить PyTorch")
    sys.exit(1)
