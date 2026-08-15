from .cat import CAT
from .memory import MemoryChannel

class FTA450:
    def __init__(self, port, baud=4800, timeout=1):
        self.cat = CAT(port, baud=baud, timeout=timeout)

    def get_vfo(self):
        return self.cat.send("FA")

    def set_vfo(self, freq_mhz: float):
        freq_str = f"{freq_mhz * 1_000_000:08.0f}"
        return self.cat.send(f"FA{freq_str}")

    def read_memory(self, index: int):
        return self.cat.send(f"MR{index:03d}")

    def write_memory(self, index: int, freq_mhz: float, name: str):
        freq_str = f"{freq_mhz * 1_000_000:08.0f}"
        name = name[:8].ljust(8)
        cmd = f"MW{index:03d}{freq_str}{name}"
        return self.cat.send(cmd)

    def close(self):
        self.cat.close()

    def dump_memories(self, max_channels=200):
        memories = []
        for i in range(max_channels):
            raw = self.read_memory(i)
            if raw.startswith("MR"):
                memories.append(MemoryChannel.from_cat(i, raw))
        return memories

    def write_memory_if_changed(self, index, freq_mhz, name):
        current = self.read_memory(index)
        if not current.startswith("MR"):
            return "NO MEMORY"

        mem = MemoryChannel.from_cat(index, current)

        new_freq_hz = int(freq_mhz * 1_000_000)
        new_name = name[:8].ljust(8)
        if mem.freq_hz == new_freq_hz and mem.name == name:
            return "UNCHANGED"

        return self.write_memory(index, freq_mhz, name)
