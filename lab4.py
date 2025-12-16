# lab4_commit2.py

import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image


def load_csv_with_error_handling(file_path):
    """Загрузка CSV файла с обработкой ошибок форматирования"""
    try:
        return pd.read_csv(file_path, header=None, names=['abs_path', 'rel_path'])
    except Exception:
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    data.append([parts[0], parts[-1]])
                else:
                    print(f"Пропущена строка {line_num}: недостаточно полей")
        return pd.DataFrame(data, columns=['abs_path', 'rel_path'])


def calculate_image_areas(df):
    """Вычисление площади для всех изображений в DataFrame"""
    areas = []
    for i, path in enumerate(df['abs_path']):
        if i % 20 == 0:
            print(f"Обработка изображения {i+1}/{len(df)}...")

        try:
            # Проверяем оба пути: абсолютный и относительный
            img_path = None
            if os.path.exists(path):
                img_path = path
            elif 'rel_path' in df.columns and os.path.exists(df.iloc[i]['rel_path']):
                img_path = df.iloc[i]['rel_path']

            if img_path:
                with Image.open(img_path) as img:
                    area = img.width * img.height
                    areas.append(area)
            else:
                areas.append(None)

        except Exception:
            areas.append(None)

    return areas


def main():
    parser = argparse.ArgumentParser(description='Анализ площади изображений')
    parser.add_argument('--annotation', type=str, required=True, 
                       help='Файл аннотации CSV')
    parser.add_argument('--output', type=str, default='result', 
                       help='Префикс выходных файлов')
    parser.add_argument('--min_area', type=float, 
                       help='Минимальная площадь для фильтрации')
    parser.add_argument('--max_area', type=float, 
                       help='Максимальная площадь для фильтрации')
    args = parser.parse_args()

    # 1. Загрузка данных
    print("=" * 50)
    print("Загрузка данных...")
    df = load_csv_with_error_handling(args.annotation)
    print(f"Загружено {len(df)} записей")

    # 2. Вычисление площади
    print("\nВычисление площади изображений...")
    df['area'] = calculate_image_areas(df)

    # 3. Фильтрация (если указаны параметры)
    df_clean = df.dropna(subset=['area']).copy()

    if args.min_area is not None:
        df_clean = df_clean[df_clean['area'] >= args.min_area]

    if args.max_area is not None:
        df_clean = df_clean[df_clean['area'] <= args.max_area]

    print(f"После фильтрации осталось {len(df_clean)} изображений")

    # 4. Сортировка и сохранение
    df_sorted = df_clean.sort_values('area').reset_index(drop=True)
    df_sorted.to_csv(f'{args.output}_data.csv', index=False)

    # 5. Построение графика
    plt.figure(figsize=(12, 6))
    plt.plot(
        range(1, len(df_sorted) + 1),
        df_sorted['area'],
        'b-',
        linewidth=2,
        marker='o',
        markersize=3
    )
    plt.title(f'Площадь изображений (n={len(df_sorted)})')
    plt.xlabel('Номер изображения')
    plt.ylabel('Площадь (пиксели)')
    plt.grid(True, alpha=0.3)

    # Добавляем линию среднего значения
    mean_area = df_sorted['area'].mean()
    plt.axhline(
        y=mean_area,
        color='r',
        linestyle='--',
        label=f'Среднее: {mean_area:,.0f}'
    )
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'{args.output}_plot.png', dpi=150)
    plt.close()

    # 6. Вывод результатов
    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ:")
    print(f"Файл данных: {args.output}_data.csv")
    print(f"Файл графика: {args.output}_plot.png")

    if not df_sorted.empty:
        stats = df_sorted['area'].describe()
        print(f"\nСтатистика площади:")
        print(f"  Минимум: {stats['min']:,.0f}")
        print(f"  Максимум: {stats['max']:,.0f}")
        print(f"  Среднее: {stats['mean']:,.0f}")
        print(f"  Медиана: {stats['50%']:,.0f}")


if __name__ == "__main__":
    main()