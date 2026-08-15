from .memory import MemoryChannel
from .radio import FTA450
from typing import Optional, Dict

class MemoryDiff:
    def __init__(self, radio: FTA450, config: dict):
        self.radio = radio
        self.config = config

    def diff(self, max_channels=200):
        radio_mem: Dict[int, MemoryChannel] = {
            m.index: m for m in self.radio.dump_memories(max_channels)
        }
        cfg_mem: Dict[int, dict] = {
            m["index"]: m for m in self.config["memories"]
        }

        diffs = []

        all_indices = sorted(set(radio_mem.keys()) | set(cfg_mem.keys()))

        for idx in all_indices:
            r: Optional[MemoryChannel] = radio_mem.get(idx)
            c: Optional[dict] = cfg_mem.get(idx)

            if r is None:
                diffs.append((idx, "config_only", None, c))
                continue

            if c is None:
                diffs.append((idx, "radio_only", r, None))
                continue

            freq_changed = (r.freq_hz != int(c["freq"] * 1_000_000))
            name_changed = (r.name != c["name"])

            if freq_changed or name_changed:
                diffs.append((idx, "changed", r, c))

        return diffs
