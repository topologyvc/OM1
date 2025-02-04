import logging
import time
import typing as T

from actions import describe_action
from inputs.base import SensorOutput
from providers.io_provider import IOProvider
from runtime.config import RuntimeConfig


class Fuser:
    """
    Combines multiple agent inputs into a single formatted prompt.

    Responsible for integrating system prompts, input streams, action descriptions,
    and command prompts into a coherent format for LLM processing.

    Parameters
    ----------
    config : RuntimeConfig
        Runtime configuration containing system prompts and agent actions.

    Attributes
    ----------
    config : RuntimeConfig
        Runtime configuration settings.
    io_provider : IOProvider
        Provider for handling I/O data and timing.
    """

    def __init__(self, config: RuntimeConfig):
        """
        Initialize the Fuser with runtime configuration.

        Parameters
        ----------
        config : RuntimeConfig
            Runtime configuration object.
        """
        self.config = config
        self.io_provider = IOProvider()

    def fuse(self, inputs: list[SensorOutput], finished_promises: list[T.Any]) -> str:
        """
        Combine all inputs into a single formatted prompt string.

        Integrates system prompts, input buffers, action descriptions, and
        command prompts into a structured format for LLM processing.

        Parameters
        ----------
        inputs : list[SensorOutput]
            List of agent input objects containing latest input buffers.
        finished_promises : list[Any]
            List of completed promises from previous actions.

        Returns
        -------
        str
            Fused prompt string combining all inputs and context.
        """
        # Record the timestamp of the input
        self.io_provider.fuser_start_time = time.time()

        # Combine all inputs, memories, and configurations into a single prompt
        system_prompt = (
            self.config.system_prompt_base
            + "\n"
            + self.config.system_governance
            + "\n"
            + self.config.system_prompt_examples
        )

        input_strings = [input.formatted_latest_buffer() for input in inputs]
        logging.debug(f"InputMessageArray: {input_strings}")
        inputs_fused = " ".join([s for s in input_strings if s is not None])

        # descriptions of various possible actions
        actions_fused = "\n\n\n".join(
            [describe_action(action.name) for action in self.config.agent_actions]
        )

        question_prompt = "What will you do? Command: "

        # this is the final prompt:
        # (1) a (typically) fixed overall system prompt with the agents, name, rules, and examples
        # (2) all the inputs (vision, sound, etc.)
        # (3) a (typically) fixed list of available actions
        # (4) a (typically) fixed system prompt requesting commands to be generated
        fused_prompt = f"{system_prompt}\n\n{inputs_fused}\n\nAVAILABLE MODULES:\n{actions_fused}\n\n{question_prompt}"

        # Record the timestamp of the output
        self.io_provider.fuser_end_time = time.time()

        return fused_prompt
