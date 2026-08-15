class ProtocolValidator:
    REQUIRED_COMMANDS = [
        "FA",  # VFO A read
        "FB",  # VFO B read
        "MR000",  # Memory read
    ]

    def __init__(self, radio):
        self.radio = radio

    def validate(self):
        results = {}
        for cmd in self.REQUIRED_COMMANDS:
            resp = self.radio.cat.send(cmd)
            results[cmd] = resp if resp else "NO RESPONSE"
        return results
