import asyncio
import logging
import threading

from bridges.abstract_bridge import AbstractBridge
from messangers.abstract_messanger import AbstractMessanger


logger = logging.getLogger(__name__)


def worker(left: AbstractMessanger, right: AbstractMessanger) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def process_messages():
        logger.info("process messages from %s", left.__class__.__name__)
        for message in left.transport.messages():
            await right.send_message(message)

    try:
        loop.run_until_complete(process_messages())
    finally:
        loop.close()


class SimpleBridge(AbstractBridge):
    def run(self) -> None:
        left_thread = threading.Thread(
            target=self.left.run, name=f"left_{self.left.__class__.__name__}"
        )
        right_thread = threading.Thread(
            target=self.right.run, name=f"right_{self.right.__class__.__name__}"
        )
        left_worker = threading.Thread(
            target=worker, args=(self.left, self.right), name="left_worker"
        )
        right_worker = threading.Thread(
            target=worker, args=(self.right, self.left), name="right_worker"
        )
        left_thread.start()
        right_thread.start()
        left_worker.start()
        right_worker.start()
        left_thread.join()
        right_thread.join()
        left_worker.join()
        right_worker.join()
