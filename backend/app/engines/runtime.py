"""Bound CPU parallelism to avoid thread contention during short-text inference."""
import os


def configure_torch_threads():
    import torch
    try:
        count = max(1, min(32, int(os.getenv("TORCH_NUM_THREADS", "2"))))
    except ValueError:
        count = 2
    if torch.get_num_threads() != count:
        torch.set_num_threads(count)
