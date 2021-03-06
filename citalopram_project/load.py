from pathlib import Path
from typing import Tuple
import pandas as pd


def load_neurons() -> pd.DataFrame:
    """Load neurons data from the data dir to a DataFrame

    Returns:
        pd.DataFrame: DataFrame of neurons data
    """
    p = get_data_dir() / "neurons.parquet.gzip"
    return pd.read_parquet(p)


def load_distances() -> pd.DataFrame:
    """Load distance data

    Returns:
        pd.DataFrame: DataFrame with one row per combination of neurons and the distance between them
    """
    p = get_data_dir() / "distances.parquet.gzip"
    return pd.read_parquet(p)


def load_spikes(block_name: str) -> pd.DataFrame:
    """Load spiketimes data from an experimental block

    Args:
        block_name (str): Name of the block [see get_block_names]

    Returns:
        pd.DataFrame: A pandas DataFrame with one row per spiketime
    """
    p = get_data_dir() / block_name / "spiketimes.parquet.gzip"
    return pd.read_parquet(p)


def load_eeg(block_name: str) -> pd.DataFrame:
    p = get_data_dir() / block_name / "stft.parquet.gzip"
    return pd.read_parquet(p)


def load_events(block_name: str) -> pd.DataFrame:
    p = get_data_dir() / block_name / "events.parquet.gzip"
    return pd.read_parquet(p)


def get_group_names() -> Tuple[str, str, str, str, str]:
    return (
        "citalopram_continuation",
        "chronic_saline",
        "citalopram_discontinuation",
        "chronic_citalopram",
        "chronic_saline_",
    )


def concat_spikes_from_connsecutive_sessions(
    df_current: pd.DataFrame, df_next: pd.DataFrame, df_neurons: pd.DataFrame
) -> pd.DataFrame:
    """Concattenate DataFrames of spikes containing data from two consectutive sessions

    Args:
        df_current ([type]): DataFrame for current session
        df_next ([type]): DataFrame for next session
        df_neurons ([type]): Neurons DataFrame (from load_neurons())

    Returns:
        pd.DataFrame: The two DataFrames concattenated together with appropriate adjustments to spiketimes
    """
    df_neurons = df_neurons[["neuron_id", "cluster", "session_name", "group"]]
    df_current = df_current.merge(df_neurons)
    max_spikes = (
        df_current.groupby(["neuron_id", "session_name"], as_index=False)
        .spiketimes.max()
        .rename(columns={"spiketimes": "max_spike"})
    )
    df_next = (
        df_next.merge(max_spikes)
        .assign(spiketimes=lambda x: x.spiketimes.add(x.max_spike))
        .loc[lambda x: x.spiketimes >= x.max_spike]
        .drop("max_spike", axis=1)
        .merge(df_neurons)
    )
    return pd.concat([df_current, df_next])


def get_block_names() -> Tuple[str, str, str, str, str, str, str, str, str, str]:
    return (
        "pre",
        "base_shock",
        "post_base_shock",
        "chal",
        "chal_shock",
        "post_chal_shock",
        "way",
        "pre",
        "chal",
        "way",
    )


def _get_basename(project_dirname="citalopram-project") -> Path:
    return [p for p in Path(__file__).absolute().parents if p.name == project_dirname][
        0
    ]


def get_data_dir(project_dirname="citalopram-project") -> Path:
    """Get the path of the data directory

    Args:
        project_dirname (str, optional): Name of root directory in project. Defaults to "citalopram-project".

    Returns:
        Path: Path to the data directory
    """
    basepath = _get_basename(project_dirname=project_dirname)
    return basepath / "data"

