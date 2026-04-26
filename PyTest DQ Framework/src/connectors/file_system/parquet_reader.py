from pathlib import Path
from typing import Optional

import pandas as pd


class ParquetReader:
	"""Reader for parquet datasets written to a folder (including partitioned datasets)."""

	@staticmethod
	def validate_path(dataset_path: Path) -> None:
		if not dataset_path.exists():
			raise FileNotFoundError(f"Parquet dataset path not found: {dataset_path}")

	def read_dataset(self, dataset_path: Path, columns: Optional[list[str]] = None) -> pd.DataFrame:
		self.validate_path(dataset_path)
		data_df = pd.read_parquet(path=dataset_path, columns=columns)
		return data_df.reset_index(drop=True)
