from abc import ABC, abstractmethod
from typing import List, Dict

class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.
    """

    @abstractmethod
    async def fetch_signals(self) -> List[Dict]:
        """
        Fetch raw signals from the data source.
        Returns a list of dictionaries containing raw article/event data.
        """
        pass
