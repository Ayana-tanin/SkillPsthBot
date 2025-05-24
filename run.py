import os
import sys
import subprocess
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Запуск команды и вывод её вывода в реальном времени."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=True
    )
    
    # Вывод вывода команды в реальном времени
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    return process.returncode

def main():
    try:
        # Проверяем, установлен ли uvicorn
        logger.info("Проверка установки uvicorn...")
        if run_command("pip show uvicorn") != 0:
            logger.info("Установка uvicorn...")
            if run_command("pip install uvicorn") != 0:
                logger.error("Не удалось установить uvicorn")
                return 1

        # Запускаем start.py
        logger.info("Запуск приложения...")
        return run_command("python start.py")
        
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 