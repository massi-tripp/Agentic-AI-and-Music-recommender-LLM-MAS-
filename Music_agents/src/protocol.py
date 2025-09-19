from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class Performative(str, Enum):
    REQUEST="REQUEST"; INFORM="INFORM"; PROPOSE="PROPOSE"
    ACCEPT="ACCEPT"; REJECT="REJECT"

class ACLMessage(BaseModel):
    sender: str
    receiver: str
    performative: Performative
    conv_id: str
    content: Dict[str, Any] = Field(default_factory=dict)
    nonce: str
    sig: str
