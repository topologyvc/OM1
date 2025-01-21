import asyncio
import logging
import typing as T

from llm.output_model import Command
from llm.output_model import LLM_full
from simulators.base import Simulator
from runtime.config import RuntimeConfig


class SimulatorOrchestrator:
    """
    Manages data flow to one or more simulators.

    Note: It is important that the simulators do not block the event loop.
    """

    promise_queue: list[asyncio.Task[T.Any]]
    _config: RuntimeConfig

    def __init__(self, config: RuntimeConfig):
        self._config = config
        self.promise_queue = []

    async def flush_promises(self) -> tuple[list[T.Any], list[asyncio.Task[T.Any]]]:
        """
        Flushes the promise queue and returns the completed promises 
        and the pending promises.
        """
        done_promises = []
        for promise in self.promise_queue:
            if promise.done():
                await promise
                done_promises.append(promise)
        self.promise_queue = [p for p in self.promise_queue if p not in done_promises]
        return done_promises, self.promise_queue

    async def promise(self, llm: LLM_full) -> None:
        # loop through simulators and send each one of them 
        # the current LLM_full
        for simulator in self._config.simulators:
            simulator_response = asyncio.create_task(self._promise_simulator(simulator, llm))
            self.promise_queue.append(simulator_response)

    async def _promise_simulator(self, simulator: Simulator, llm: LLM_full) -> T.Any:
    #         prompt: str = Field(..., description="The complete input to the LLM or multiagent system")
    # inputs: str = Field(..., description="The time varying inputs to the LLM or multiagent system")
    # commands: list[Command] = Field(..., description="List of commands to execute")
        logging.debug(
            f"Calling simulator {simulator.name} with input {llm.prompt}"
        )
        # input_interface = T.get_type_hints(simulator.interface)["input"](
        #     **{arg.name: arg.value for arg in in_out.arguments}
        # )
        simulator.print_raw(llm)
        # logging.debug(f"Simulator {simulator.name} returned {simulator_response}")
        # await simulator.connector.connect(simulator_response)
        return None #simulator_response
