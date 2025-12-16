# lab2.py - Скачивание изображений с аннотацией

import argparse
import csv
import os
import random
import time
from pathlib import Path

from icrawler.builtin import BingImageCrawler


class ImageIterator:
    """Итератор для работы с файлом аннотации изображений."""
    
    def __init__(self, annotation_file):
        """Инициализация итератора с файлом аннотации."""
        
        self.annotation_file = annotation_file
        self.data = []
        self.load_annotation()
        self.index = 0
    
    def load_annotation(self):
        """Загрузка данных аннотации из CSV файла."""
        
        if os.path.exists(self.annotation_file):
            with open(self.annotation_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Пропускаем заголовок
                self.data = [row for row in reader]
    
    def __iter__(self):
        """Возвращает итератор."""
        return self
    
    def __next__(self):
        """Возвращает следующее изображение из аннотации."""
        
        if self.index < len(self.data):
            row = self.data[self.index]
            self.index += 1
            return {
                'absolute_path': row[0],
                'relative_path': row[1]
            }
        else:
            raise StopIteration


def cleanup_directory(directory):
    """Очистка директории от временных и ненужных файлов."""

    for file_path in Path(directory).rglob('*.*'):
        if file_path.is_file():
            if file_path.suffix.lower() in ['.txt', '.tmp', '']:
                try:
                    file_path.unlink()
                except Exception:
                    pass


def calculate_range_distribution(num_ranges, total_min, total_max):
    """Рассчитать распределение количества изображений по диапазонам."""
    
    remaining = random.randint(total_min, total_max)
    counts = []
    
    for i in range(num_ranges):
        if i == num_ranges - 1:
            count = remaining
        else:
            min_count = max(20, remaining // (num_ranges - i) // 2)
            max_count = remaining - (num_ranges - i - 1) * 20
            count = random.randint(min_count, max_count)
            remaining -= count
        counts.append(count)
    
    return counts


def collect_valid_images(directory, existing_files):
    """Собрать только валидные изображения из директории."""
    

    valid_files = []
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
    
    for file_path in Path(directory).rglob('*.*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            if file_path.stat().st_size > 10240:
                absolute_path = str(file_path.absolute())
                relative_path = str(file_path.relative_to(Path(directory).parent))
                
                if (absolute_path, relative_path) not in existing_files:
                    valid_files.append((absolute_path, relative_path))
    
    return valid_files


def download_images_for_range(range_dir, size_range, target_count, all_files):
    """Скачать изображения для одного диапазона размеров."""
    
    min_size, max_size = size_range
    print(f"\n=== Диапазон: {min_size}x{max_size} ===")
    print(f"Цель: {target_count} изображений")
    
    cleanup_directory(range_dir)
    
    downloaded_count = 0
    current_files = []
    keywords = [
        'fish',
        'fishes', 
        'aquarium fish',
        'colorful fish',
        'tropical fish',
        'marine fish',
    ]
    
    for attempt in range(2):
        try:
            crawler = BingImageCrawler(
                storage={'root_dir': range_dir},
                feeder_threads=3,
                parser_threads=3,
                downloader_threads=6,
            )
            
            keyword = random.choice(keywords)
            attempt_target = (
                target_count * 2 
                if attempt == 0 
                else target_count - downloaded_count
            )
            
            print(f"Попытка {attempt + 1}: поиск '{keyword}' ({attempt_target} изображений)")
            
            # Размеры изображений будут проверяться после скачивания
            crawler.crawl(
                keyword=keyword,
                max_num=attempt_target,
                file_idx_offset='auto',
            )
            
            time.sleep(3)
            
        except Exception as e:
            print(f"Ошибка при скачивании: {e}")
            continue
        
        cleanup_directory(range_dir)
        
        new_files = collect_valid_images(range_dir, all_files + current_files)
        current_files.extend(new_files)
        downloaded_count = len(current_files)
        
        print(f"Скачано в попытке {attempt + 1}: {len(new_files)} изображений")
        
        if downloaded_count >= target_count:
            break
    
    print(f"Итого для диапазона: {downloaded_count} изображений")
    return current_files


def download_images(output_dir, size_ranges, total_min=80, total_max=200):
    """Скачать изображения по заданным диапазонам размеров."""
    

    os.makedirs(output_dir, exist_ok=True)
    
    num_ranges = len(size_ranges)
    counts = calculate_range_distribution(num_ranges, total_min, total_max)
    
    print(f"Будет скачано изображений по диапазонам: {dict(zip(size_ranges, counts))}")
    print(f"Общее количество: {sum(counts)}")
    
    all_files = []
    
    for i, size_range in enumerate(size_ranges):
        range_dir = os.path.join(output_dir, f"range_{i + 1}")
        os.makedirs(range_dir, exist_ok=True)
        
        count = counts[i]
        range_files = download_images_for_range(
            range_dir, 
            size_range, 
            count, 
            all_files,
        )
        all_files.extend(range_files)
    
    return all_files


def create_annotation(files, annotation_file):
    """Создать файл аннотации."""
    

    with open(annotation_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['absolute_path', 'relative_path'])
        writer.writerows(files)
    
    print(f"Аннотация создана: {annotation_file}")
    print(f"Всего файлов в аннотации: {len(files)}")


def main():
    """Основная функция программы."""
    parser = argparse.ArgumentParser(
        description='Скачивание изображений fish с разными диапазонами размеров'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default='fish_images',
        help='Директория для сохранения изображений',
    )
    parser.add_argument(
        '--annotation_file',
        type=str,
        default='fish_annotation.csv',
        help='Имя файла аннотации',
    )
    parser.add_argument(
        '--size_ranges',
        type=str,
        default='300x300,500x500,700x700,900x900',
        help='Диапазоны размеров в формате minxmax,minxmax,...',
    )
    parser.add_argument(
        '--min_images',
        type=int,
        default=80,
        help='Минимальное общее количество изображений',
    )
    parser.add_argument(
        '--max_images',
        type=int,
        default=200,
        help='Максимальное общее количество изображений',
    )
    
    args = parser.parse_args()
    
    size_ranges = []
    for range_str in args.size_ranges.split(','):
        try:
            min_size, max_size = map(int, range_str.split('x'))
            size_ranges.append((min_size, max_size))
        except ValueError:
            print(f"Некорректный формат диапазона: {range_str}")
            return
    
    print(f"Диапазоны размеров: {size_ranges}")
    print(f"Целевое количество изображений: {args.min_images}-{args.max_images}")
    
    downloaded_files = download_images(
        args.output_dir,
        size_ranges,
        args.min_images,
        args.max_images,
    )
    
    if not downloaded_files:
        print("Не удалось скачать ни одного изображения!")
        return
    
    create_annotation(downloaded_files, args.annotation_file)
    
    print("\nДемонстрация работы итератора:")
    iterator = ImageIterator(args.annotation_file)
    file_count = 0
    
    for file_info in iterator:
        if file_count < 5:
            print(f"Файл {file_count + 1}: {file_info['relative_path']}")
            file_count += 1
        else:
            break


if __name__ == "__main__":
    main()