import logging

from actions.base import ActionConnector
from actions.speak.interface import SpeakInput


class SpeakRos2Connector(ActionConnector[SpeakInput]):
    async def connect(self, output_interface: SpeakInput) -> None:

        new_msg = {"speak": output_interface.sentence}
        logging.info(f"SendThisToROS2: {new_msg}")
