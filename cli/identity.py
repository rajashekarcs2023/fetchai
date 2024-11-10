# cli/identity.py
import os
import click
from dotenv import load_dotenv, set_key, dotenv_values
from mnemonic import Mnemonic


# Generate identity command
@click.command(name="generate-identity")
@click.option(
    "-s",
    "--strength",
    type=int,
    default=256,
    show_default=True,
    help="Strength of the mnemonic (128 or 256 bits)",
)
@click.option(
    "-n",
    "--name",
    default="AGENT_KEY",
    show_default=True,
    help="Name of the environment variable",
)
@click.option(
    "-o", "--output", type=click.Path(), help="Output file for saving the generated key"
)
def identity(strength, name, output):
    """Generate an agent identity key as a mnemonic phrase and optionally save to file or .env."""

    # Generate a mnemonic phrase for the identity key
    mnemo = Mnemonic("english")
    words = mnemo.generate(strength=strength)
    env_record = f'{name}="{words}"'

    # Output the generated key to the specified file or stdout
    if output:
        with open(output, "a") as f:
            f.write(env_record + "\n")
        click.echo(f"{name} ({strength} bits) appended to {output}")
    else:
        click.echo(env_record)

    # Load existing environment variables to check if the key already exists
    load_dotenv()
    existing_env = dotenv_values(".env")

    # Check if the key already exists in .env
    if name in existing_env:
        # Ask user to confirm overwrite
        if not click.confirm(
            f"{name} already exists in .env. Do you want to overwrite it?",
            default=False,
        ):
            click.echo("Key not saved to .env.")
            return

    # Save the key to .env
    set_key(".env", name, words)
    click.echo(f"{name} saved to .env.")
