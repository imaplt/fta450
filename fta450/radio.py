from .cat import CAT
from .memory import MemoryChannel
import serial

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

class FTA450Clone:
    def __init__(self, port, baud=4800, timeout=1.0):
        self.ser = serial.Serial(port, baudrate=baud, timeout=timeout)

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _read_exact(self, n):
        data = self.ser.read(n)
        if len(data) != n:
            raise RuntimeError(f"Expected {n} bytes, got {len(data)}")
        return data

    def clone_handshake(self):
        # Basic Yaesu-style clone handshake (FTA-550/750 family)
        # This may need tweaking once we see real traffic.
        frame = b"\x02\x00\x00\x00\x00\x03"
        self.ser.write(frame)
        ack = self._read_exact(1)
        if ack != b"\x06":
            raise RuntimeError(f"Handshake failed, got {ack!r}")

    def read_block(self):
        start = self._read_exact(1)

        # End of transmission
        if start == b"\x04":
            return None

        if start != b"\x02":
            raise RuntimeError(f"Invalid block start: {start!r}")

        block_id = self._read_exact(1)
        len_hi = self._read_exact(1)
        len_lo = self._read_exact(1)

        length = (len_hi[0] << 8) | len_lo[0]

        data = self._read_exact(length)
        checksum = self._read_exact(1)
        end = self._read_exact(1)

        if end != b"\x03":
            raise RuntimeError(f"Invalid block end: {end!r}")

        # TODO: verify checksum once we know the algorithm
        return block_id[0], data

    def clone_download(self):
        self.clone_handshake()

        blocks = []
        while True:
            block = self.read_block()
            if block is None:
                break

            blocks.append(block)
            # ACK block
            self.ser.write(b"\x06")

        return blocks
