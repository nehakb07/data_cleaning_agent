import pandas as pd
import numpy as np


class DataProfiler:

    def profile(self, df):

        profile = {}

        total_rows = len(df)

        for col in df.columns:

            dtype = str(df[col].dtype)
            missing_count = df[col].isna().sum()
            missing_percent = (missing_count / total_rows) * 100

            unique_count = df[col].nunique(dropna=True)
            unique_ratio = unique_count / total_rows

            sample_values = df[col].dropna().astype(str).head(5).tolist()

            numeric_flag = pd.api.types.is_numeric_dtype(df[col])

            profile[col] = {
                "dtype": dtype,
                "missing_percent": round(missing_percent, 2),
                "unique_count": int(unique_count),
                "unique_ratio": round(unique_ratio, 3),
                "sample_values": sample_values,
                "is_numeric": numeric_flag
            }

        return profile
