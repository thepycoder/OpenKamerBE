from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
import os
from typing import List, Optional, Union


@dataclass
class Member:
    name: str
    image_url: str
    party: str
    birthyear: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, dictionary: dict):
        return cls(**dictionary)


@dataclass
class Document:
    nr: str
    zitting: str
    bron: str
    indieningsdatum: datetime
    auteurs: List[Member]
    type: str
    stemming: str


@dataclass
class Vote:
    session_id: str
    date: Optional[datetime] = None
    nr_within_session: int = -1
    subject: str = ""
    summarized_vote: dict = field(default_factory=lambda: {})
    yay: List[str] = field(default_factory=lambda: [])
    nay: List[str] = field(default_factory=lambda: [])
    dunno: List[str] = field(default_factory=lambda: [])
    srcfile: Union[str, os.PathLike[str]] = ""

    def to_dict(self) -> dict:
        """Serializes the object to a dictionary."""
        return {
            field.name: self._serialize(getattr(self, field.name))
            for field in fields(self)
        }

    @staticmethod
    def _serialize(value):
        """Helper function to serialize datetime and PathLike objects into JSON serializable formats."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, os.PathLike):
            return os.fspath(value)
        return value

    @classmethod
    def from_dict(cls, dictionary: dict):
        """Deserializes a dictionary to a Vote object."""
        return cls(
            **{key: cls._deserialize(key, value) for key, value in dictionary.items()}
        )

    @staticmethod
    def _deserialize(key, value):
        """Helper function to deserialize specific fields from dictionary to their correct types."""
        if key == "date" and value is not None:
            return datetime.fromisoformat(value)
        if key == "srcfile" and value:
            return os.path.normpath(value)
        return value


@dataclass
class KamerStuk:
    nr: str
    sleutel: str
    titel: str
    zittingsperiode: int
    hoofddocument: Document
    eurovoc_descriptor: str
    stemming_kamer: Vote
