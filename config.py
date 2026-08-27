import os

MODEL_NAME = "bert-base-cased" # Назва базової моделі берт
DATASET_NAME = "datasets/conll2003" # назва датасету

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # авто знаходження шляху до папки проєкта
DATA_DIR = os.path.join(BASE_DIR, "data") # шлях до папки дата
MODEL_SAVE_DIR = os.path.join(BASE_DIR, "models", "fine_tuned_bert") # місце для зберігання моделі пісоя fine tuning

BATCH_SIZE = 16
LEARNING_RATE = 2e-5 # стандарт швидкості навчання для берт
EPOCHS = 3 # кількість повторного проходжеення по всьому датасету під час навчання
MAX_LENGTH = 128 # макс довжина речення в токені, все що більше обрізає