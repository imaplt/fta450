import click
from .radio import FTA450
from .validator import ProtocolValidator
from .config import load_defaults
from .diff import MemoryDiff
from .radio import FTA450Clone  # or .clone if you put it there

@click.group()
@click.option("--port", help="Serial port for the radio")
@click.option("--baud", type=int, help="Baud rate")
@click.option("--timeout", type=int, help="Timeout")
@click.pass_context
def cli(ctx, port, baud, timeout):
    defaults = load_defaults()
    port = port or defaults.get("port")
    baud = baud or defaults.get("baud", 4800)
    timeout = timeout or defaults.get("timeout", 1)

    if not port:
        raise click.UsageError("No port specified and no default in config file.")

    ctx.obj = FTA450(port=port, baud=baud, timeout=timeout)


@cli.command()
@click.pass_context
def read_vfo(ctx):
    radio: FTA450 = ctx.obj
    print(radio.get_vfo())


@cli.command()
@click.argument("freq", type=float)
@click.pass_context
def set_vfo(ctx, freq):
    radio = ctx.obj
    print(radio.set_vfo(freq))

@cli.command()
@click.argument("index", type=int)
@click.pass_context
def read_mem(ctx, index):
    radio = ctx.obj
    print(radio.read_memory(index))

@cli.command()
@click.argument("index", type=int)
@click.argument("freq", type=float)
@click.argument("name", type=str)
@click.pass_context
def write_mem(ctx, index, freq, name):
    radio = ctx.obj
    print(radio.write_memory(index, freq, name))

@cli.command()
@click.argument("config_file")
@click.pass_context
def load_memories(ctx, config_file):
    radio = ctx.obj
    cfg = load_defaults().load_config(config_file)
    for mem in cfg["memories"]:
        radio.write_memory(mem["index"], mem["freq"], mem["name"])
        print(f"Wrote {mem['index']}")

@cli.command()
@click.option("--max", default=200, help="Max memory channels to scan")
@click.pass_context
def dump(ctx, max):
    radio = ctx.obj
    for mem in radio.dump_memories(max):
        print(mem)

@cli.command()
@click.pass_context
def validate(ctx):
    radio = ctx.obj
    v = ProtocolValidator(radio)
    results = v.validate()
    for cmd, resp in results.items():
        print(f"{cmd}: {resp}")

@cli.command()
@click.argument("config_file")
@click.option("--max", default=200, help="Max memory channels to scan")
@click.pass_context
def diff(ctx, config_file, max):

    radio = ctx.obj
    cfg = load_defaults().load_config(config_file)
    d = MemoryDiff(radio, cfg)

    for idx, status, r, c in d.diff(max):
        print(f"Index {idx:03d}: {status}")
        if r:
            print(f"  Radio:  {r}")
        if c:
            print(f"  Config: freq={c['freq']} name='{c['name']}'")
        print()

@cli.command()
@click.argument("config_file")
@click.pass_context
def import_yaml(ctx, config_file):
    radio = ctx.obj
    cfg = load_defaults().load_config(config_file)

    for mem in cfg["memories"]:
        idx = mem["index"]
        freq = mem["freq"]
        name = mem["name"]

        result = radio.write_memory_if_changed(idx, freq, name)
        print(f"{idx:03d}: {result}")

# @click.group()
# def cli():
#     pass

@cli.command()
def clone_download():
    defaults = load_defaults()
    port = defaults.get("port")
    baud = defaults.get("baud", 4800)
    timeout = defaults.get("timeout", 1)

    if not port:
        raise click.UsageError("No port specified and no default in config file.")

    clone = FTA450Clone(port, baud=baud, timeout=timeout)
    try:
        blocks = clone.clone_download()
        click.echo(f"Received {len(blocks)} blocks")
        for bid, data in blocks:
            click.echo(f"Block {bid}: {len(data)} bytes")
    finally:
        clone.close()
