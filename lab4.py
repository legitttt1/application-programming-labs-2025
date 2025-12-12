# lab4_commit1.py
import pandas as pd
import matplotlib.pyplot as plt
import os
from PIL import Image
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--annotation', type=str, default='fish_annotation.csv')
    parser.add_argument('--output', type=str, default='result')
    args = parser.parse_args()

    # Загрузка данных из CSV файла
    try:
        df = pd.read_csv(args.annotation, header=None, names=['abs_path', 'rel_path'])
    except Exception as e:
        print(f"Ошибка чтения CSV: {e}")
        return

    print(f"Загружено {len(df)} записей из {args.annotation}")

    # Вычисление площади для каждого изображения
    areas = []
    for i, path in enumerate(df['abs_path']):
        try:
            if os.path.exists(path):
                with Image.open(path) as img:
                    width, height = img.size
                    area = width * height
                    areas.append(area)
            else:
                areas.append(None)
        except Exception as e:
            areas.append(None)
    
    df['area'] = areas
    
    # Удаление строк без вычисленной площади
    df_clean = df.dropna(subset=['area']).copy()
    print(f"Успешно обработано {len(df_clean)} изображений")

    # Сортировка по площади
    df_sorted = df_clean.sort_values('area').reset_index(drop=True)

    # Сохранение результатов в CSV
    output_csv = f'{args.output}_data.csv'
    df_sorted.to_csv(output_csv, index=False)
    print(f"Данные сохранены в {output_csv}")

    # Построение графика
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, len(df_sorted)+1), df_sorted['area'], 'b-', linewidth=2)
    plt.title('Площадь изображений (отсортировано по возрастанию)')
    plt.xlabel('Номер изображения в отсортированном списке')
    plt.ylabel('Площадь (пиксели)')
    plt.grid(True, alpha=0.3)
    
    # Сохранение графика
    output_plot = f'{args.output}_plot.png'
    plt.tight_layout()
    plt.savefig(output_plot, dpi=150)
    plt.close()
    print(f"График сохранен в {output_plot}")

    # Вывод статистики
    print("\nСтатистика площади изображений:")
    print(f"Минимальная: {df_sorted['area'].min():,.0f} пикселей")
    print(f"Максимальная: {df_sorted['area'].max():,.0f} пикселей")
    print(f"Средняя: {df_sorted['area'].mean():,.0f} пикселей")

if __name__ == "__main__":
    main()