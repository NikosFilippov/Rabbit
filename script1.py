
import kagglehub
from kagglehub import KaggleDatasetAdapter
file_path = ""
df = kagglehub.dataset_load(
  KaggleDatasetAdapter.PANDAS,
  "uciml/mushroom-classification",
  file_path,pandas_kwargs={"sheet_name": None},
)
print("First 5 records:", df.head())