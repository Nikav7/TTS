import json
import os
import re
import yaml

from TTS.config.shared_configs import *
from TTS.utils.generic_utils import find_module


def read_json_with_comments(json_path):
    """for backward compat."""
    # fallback to json
    with open(json_path, "r", encoding="utf-8") as f:
        input_str = f.read()
    # handle comments
    input_str = re.sub(r"\\\n", "", input_str)
    input_str = re.sub(r"//.*\n", "\n", input_str)
    data = json.loads(input_str)
    return data


def _search_configs(model_name):
    config_class = None
    paths = ["TTS.tts.configs", "TTS.vocoder.configs", "TTS.speaker_encoder"]
    for path in paths:
        try:
            config_class = find_module(path, model_name + "_config")
        except ModuleNotFoundError:
            pass
    if config_class is None:
        raise ModuleNotFoundError(f" [!] Config for {model_name} cannot be found.")
    return config_class


def _process_model_name(config_dict):
    model_name = config_dict["model"] if "model" in config_dict else config_dict["generator_model"]
    model_name = model_name.replace('_generator', '').replace('_discriminator', '')
    return model_name


def load_config(config_path: str) -> None:
    """Import `json` or `yaml` files as TTS configs. First, load the input file as a `dict` and check the model name
    to find the corresponding Config class. Then initialize the Config.

    Args:
        config_path (str): path to the config file.

    Raises:
        TypeError: given config file has an unknown type.

    Returns:
        Coqpit: TTS config object.
    """
    config_dict = {}
    ext = os.path.splitext(config_path)[1]
    if ext in (".yml", ".yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    elif ext == ".json":
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                input_str = f.read()
                data = json.loads(input_str)
        except json.decoder.JSONDecodeError:
            # backwards compat.
            data = read_json_with_comments(config_path)
    else:
        raise TypeError(f" [!] Unknown config file type {ext}")
    config_dict.update(data)
    model_name = _process_model_name(config_dict)
    config_class = _search_configs(model_name.lower())
    config = config_class()
    config.from_dict(config_dict)
    return config
