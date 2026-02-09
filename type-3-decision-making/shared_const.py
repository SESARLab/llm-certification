import typing
from enum import Enum

import numpy as np
import pandas as pd


class Scenario(Enum):
    CLOUD = 1

class N(Enum):
    LOW = 10
    MEDIUM = 25
    QUITE_HIGH = 50
    HIGH = 75
    VERY_HIGH = 100

class M(Enum):
    LOW = 3
    MEDIUM = 6
    HIGH = 10
    VERY_HIGH = 15

class Model(Enum):
    GEMMA_3_27B = "gemma3:27b-it-q4_K_M"
    LLAMA_3_3_70B = "llama3.3:70b-instruct-q5_K_M"
    DEEPSEEK_R1_70B = "deepseek-r1:70b"
    MISTRAL_123B = "mistral-large:123b-instruct-2411-q5_K_M"

REPETITIONS = 2
MAX_RETRIES = 20

EXAMPLE_NO_EXAMPLE = 'No example'


def finalize_df(df: pd.DataFrame, store_nan: bool, index_label: str) -> typing.Tuple[pd.DataFrame, dict]:
    export_kwargs = {'index': True, 'index_label': index_label}
    if store_nan:
        df = df.replace('', np.nan)
        export_kwargs['na_rep'] = 'nan'
    df.index = df.index.to_series().apply(lambda val: val.split('_')[-1])
    return df, export_kwargs