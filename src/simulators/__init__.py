import os
import importlib
import inspect
import typing as T
import logging

from simulators.base import Simulator


def load_simulator(sim_name: str) -> T.Type[Simulator]:
    """
    Load a simulator from the simulators directory.

    Args:
        name: The name of the simulator class to load.

    Returns:
        An instance of the simulator.
    """
    # Get all files in plugins directory
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    plugin_files = [f[:-3] for f in os.listdir(plugins_dir) if f.endswith(".py")]

    # Import all simulators and find Simulator subclasses
    simulator_classes = {}
    for plugin in plugin_files:
        simulator = importlib.import_module(f"simulators.plugins.{plugin}")
        for name, obj in inspect.getmembers(simulator):
            if (
                inspect.isclass(obj)
                and obj != Simulator
            ):
                simulator_classes[name] = obj

    logging.info(f"Simulator classes: {simulator_classes}")

    # Find requested simulator class
    if sim_name not in simulator_classes:
        raise ValueError(f"Simulator {name} not found")

    return simulator_classes[sim_name]