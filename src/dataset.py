from datasets import load_dataset
from transformers import AutoTokenizer
import config


def load_and_prepare_dataset():
    """
    Завантажує датасет CoNLL-2003 і токенізатор для BERT.
    """
    print(f"Loading dataset{config.DATASET_NAME}...")

    # Блок для безпечно завантаження через try/catch
    try:
        # Спроба завантажити датасет за основною назвою
        raw_datasets = load_dataset(config.DATASET_NAME)
    except Exception as e:
        # Авто переключаємо, якщо основне джерело видасть помилку
        print(f"Не вдалося завантажити {config.DATASET_NAME}, пробуємо альт-джерело...")
        raw_datasets = load_dataset("lhoestq/conll2003")

    print(f"Завантаження токенізатора для {config.MODEL_NAME}...")
    # Завантажуємо правильний токенізатор під саме мою модель (bert-base-cased)
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)

    return raw_datasets, tokenizer


print("--- ПОЧАТОК ЗАВАНТАЖЕННЯ ---")
# Виклик фічі для отримання готового датасету та токенізватора
datasets, tokenizer = load_and_prepare_dataset()

print("\nСтруктура датасету:")
print(datasets)

# Друкую кількість речень для трьох вибірок
print("\nРозміри вибірок:")
print(f"Train size: {len(datasets['train'])}")
print(f"Validation size: {len(datasets['validation'])}")
print(f"Test size: {len(datasets['test'])}")
