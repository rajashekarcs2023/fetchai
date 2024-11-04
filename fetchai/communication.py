import base64
import hashlib
import json
import struct
from typing import Any
from uuid import uuid4
from dataclasses import dataclass

import requests
from pydantic import BaseModel, UUID4

from fetchai.crypto import Identity
from fetchai.registration import DEFAULT_ALMANAC_API_URL

JsonStr = str


class Envelope(BaseModel):
    version: int
    sender: str
    target: str
    session: UUID4
    schema_digest: str
    protocol_digest: str | None = None
    payload: str | None = None
    expires: int | None = None
    nonce: int | None = None
    signature: str | None = None

    def encode_payload(self, value: JsonStr):
        self.payload = base64.b64encode(value.encode()).decode()

    def decode_payload(self) -> str:
        if self.payload is None:
            return ""

        return base64.b64decode(self.payload).decode()

    def sign(self, identity: Identity):
        try:
            self.signature = identity.sign_digest(self._digest())
        except Exception as err:
            raise ValueError(f"Failed to sign envelope: {err}") from err

    def verify(self) -> bool:
        if self.signature is None:
            raise ValueError("Envelope signature is missing")
        return Identity.verify_digest(self.sender, self._digest(), self.signature)

    def _digest(self) -> bytes:
        hasher = hashlib.sha256()
        hasher.update(self.sender.encode())
        hasher.update(self.target.encode())
        hasher.update(str(self.session).encode())
        hasher.update(self.schema_digest.encode())
        if self.payload is not None:
            hasher.update(self.payload.encode())
        if self.expires is not None:
            hasher.update(struct.pack(">Q", self.expires))
        if self.nonce is not None:
            hasher.update(struct.pack(">Q", self.nonce))
        return hasher.digest()


def lookup_endpoint_for_agent(agent_address: str) -> str:
    r = requests.get(f"{DEFAULT_ALMANAC_API_URL}/agents/{agent_address}")
    r.raise_for_status()

    return r.json()["endpoints"][0]["url"]


def send_message_to_agent(
    sender: Identity,
    target: str,
    protocol_digest: str | None,
    model_digest: str,
    payload: Any,
):
    """
    Send a message to an agent.
    :param sender: The identity of the sender.
    :param target: The address of the target agent.
    :param protocol_digest: The digest of the protocol that is being used
    :param model_digest: The digest of the model that is being used
    :param payload: The payload of the message.
    :return:
    """
    json_payload = json.dumps(payload, separators=(",", ":"))

    env = Envelope(
        version=1,
        sender=sender.address,
        target=target,
        session=uuid4(),
        schema_digest=model_digest,
        protocol_digest=protocol_digest,
    )

    env.encode_payload(json_payload)
    env.sign(sender)

    print(env.model_dump_json())

    # query the almanac to lookup the target agent
    endpoint = lookup_endpoint_for_agent(target)
    print(endpoint)

    # send the envelope to the target agent
    r = requests.post(
        endpoint,
        headers={"content-type": "application/json"},
        data=env.model_dump_json(),
    )
    r.raise_for_status()


@dataclass
class AgentMessage:
    # The address of the sender of the message.
    sender: str
    # The address of the target of the message.
    target: str
    # The payload of the message.
    payload: Any


def parse_message_from_agent(content: JsonStr) -> AgentMessage:
    """
    Parse a message from an agent.
    :param content: A string containing the JSON envelope.
    :return: An AgentMessage object.
    """

    env = Envelope.model_validate_json(content)

    if not env.verify():
        raise ValueError("Invalid envelope signature")

    json_payload = env.decode_payload()
    payload = json.loads(json_payload)

    return AgentMessage(sender=env.sender, target=env.target, payload=payload)
