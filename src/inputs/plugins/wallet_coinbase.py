import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import List, Optional

from cdp import Cdp, Wallet

from inputs.base import AgentInputConfig
from inputs.base.loop import LoopInput
from providers.io_provider import IOProvider


@dataclass
class Message:
    timestamp: float
    message: str


class WalletCoinbase(LoopInput[float]):
    """
    Queries current ETH balance and reports a balance increase
    """

    def __init__(self, config: AgentInputConfig = AgentInputConfig()):
        super().__init__(config)

        # Track IO
        self.io_provider = IOProvider()
        self.messages: list[str] = []

        self.POLL_INTERVAL = 0.5  # seconds between blockchain data updates
        self.COINBASE_WALLET_ID = os.environ.get("COINBASE_WALLET_ID")
        logging.debug(f"Using {self.COINBASE_WALLET_ID} as the coinbase wallet id")

        # Initialize Wallet
        API_KEY = os.environ.get("COINBASE_API_KEY")
        API_SECRET = os.environ.get("COINBASE_API_SECRET")
        Cdp.configure(API_KEY, API_SECRET)

        try:
            # fetch wallet data
            self.wallet = Wallet.fetch(self.COINBASE_WALLET_ID)
            logging.debug(f"Wallet: {self.wallet}")
        except Exception as e:
            logging.error(f"Error fetching Coinbase Wallet data: {e}")

        self.ETH_balance = float(self.wallet.balance("eth"))
        self.ETH_balance_previous = self.ETH_balance

        logging.info("Testing: WalletCoinbase: Initialized")

    async def _poll(self) -> List[float]:
        """
        Poll for Coinbase Wallet balance updates.

        Returns
        -------
        List[float]
            [current_balance, balance_change]
        """
        await asyncio.sleep(self.POLL_INTERVAL)

        # randomly simulate ETH inbound transfers for debugging purposes
        # if random.randint(0, 10) > 7:
        #     faucet_transaction = self.wallet.faucet(asset_id='eth')
        #     faucet_transaction.wait()
        #     logging.info(f"WalletCoinbase: Faucet transaction: {faucet_transaction}")

        self.wallet = Wallet.fetch(self.COINBASE_WALLET_ID)
        logging.debug(
            f"WalletCoinbase: Wallet refreshed: {self.wallet.balance('eth')}, the current balance is {self.ETH_balance}"
        )
        self.ETH_balance = float(self.wallet.balance("eth"))
        balance_change = self.ETH_balance - self.ETH_balance_previous
        self.ETH_balance_previous = self.ETH_balance

        return [self.ETH_balance, balance_change]

    async def _raw_to_text(self, raw_input: List[float]) -> Optional[Message]:
        """
        Convert balance data to human-readable message.

        Parameters
        ----------
        raw_input : List[float]
            [current_balance, balance_change]

        Returns
        -------
        Message
            Timestamped status or transaction notification
        """
        balance_change = raw_input[1]

        message = ""

        if balance_change > 0:
            message = f"{balance_change:.5f}"
        else:
            return None

        logging.debug(f"WalletCoinbase: {message}")
        return Message(timestamp=time.time(), message=message)

    async def raw_to_text(self, raw_input: float):
        """
        Process balance update and manage message buffer.

        Parameters
        ----------
        raw_input : float
            Raw balance data
        """
        pending_message = await self._raw_to_text(raw_input)

        if pending_message is not None:
            self.messages.append(pending_message)

    def formatted_latest_buffer(self) -> Optional[str]:
        """
        Format and clear the buffer contents. If there are multiple ETH transactions,
        combine them into a single message.

        Returns
        -------
        Optional[str]
            Formatted string of buffer contents or None if buffer is empty
        """
        if len(self.messages) == 0:
            return None

        transaction_sum = 0

        # all the messages, by definition, are non-zero
        for message in self.messages:
            transaction_sum += float(message.message)

        last_message = self.messages[-1]
        result_message = Message(
            timestamp=last_message.timestamp,
            message=f"You just received {transaction_sum:.5f} ETH.",
        )

        result = f"""
        {self.__class__.__name__} INPUT
        // START
        {result_message.message}
        // END
        """

        self.io_provider.add_input(
            self.__class__.__name__, result_message.message, result_message.timestamp
        )
        self.messages = []
        return result
