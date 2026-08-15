class MemoryChannel:
    def __init__(self, index, freq_hz, name):
        self.index = index
        self.freq_hz = freq_hz
        self.name = name

    @classmethod
    def from_cat(cls, index, raw):
        # Example response: "MR001118000000TOWER   ;"
        raw = raw.strip(";")

        freq_hz = int(raw[5:13])
        name = raw[13:].strip()

        return cls(index, freq_hz, name)

    def __repr__(self):
        try:
            mhz = float(self.freq_hz) / 1_000_000
            mhz_str = f"{mhz:.3f}"
        except (TypeError, ValueError):
            mhz_str = "INVALID"
        return f"<Mem {int(self.index):03d}: {mhz_str} MHz '{self.name}'>"

