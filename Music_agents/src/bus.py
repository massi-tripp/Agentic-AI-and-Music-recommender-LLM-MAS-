import asyncio
from typing import Dict
from .protocol import ACLMessage

class MessageBus:
    def __init__(self): self.queues: Dict[str, asyncio.Queue] = {}
    def mailbox(self, agent_id: str) -> asyncio.Queue:
        self.queues.setdefault(agent_id, asyncio.Queue(maxsize=1000))
        return self.queues[agent_id]
    async def send(self, msg: ACLMessage):
        await self.mailbox(msg.receiver).put(msg)

bus = MessageBus()
