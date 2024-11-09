#!/usr/bin/env python3

import os
import click
import sys
from dotenv import load_dotenv, set_key, dotenv_values
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from mnemonic import Mnemonic

# Load environment variables from .env file
load_dotenv()

@click.group()
def cli():
    """CLI tool for AgentVerse registration and identity management."""
    pass


# Load environment variables from .env and validate keys
def load_environment_variables():
    agentverse_key = os.getenv("AGENTVERSE_KEY")
    ai_key = os.getenv("AI_KEY")

    if not agentverse_key or not ai_key:
        click.echo("Error: AGENTVERSE_KEY or AI_KEY not found in environment variables.")
        sys.exit(1)

    return agentverse_key, ai_key


# Utility function to load README content
def load_readme(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        click.echo(f"Error: README file not found at {file_path}")
        sys.exit(1)
    except IOError:
        click.echo(f"Error: Unable to read README file at {file_path}")
        sys.exit(1)


# Register command
@cli.command()
@click.option('-n', '--name', prompt="Enter AI name", required=True, help="Name of the AI")
@click.option('-r', '--readme', prompt="Enter README file path", required=True, help="Path to README file")
@click.option('-w', '--webhook', prompt="Enter Webhook URL", required=True, help="Webhook URL for the AI")
@click.option('-f', '--force', is_flag=True, help="Force registration even if agent is already registered")
def register(name, readme, webhook, force):
    """Register an agent with AgentVerse and save to .env."""
    # Load environment variables and read README file
    agentverse_key, ai_key = load_environment_variables()
    readme_content = load_readme(readme)

    try:
        # Create AI identity
        ai_identity = Identity.from_seed(ai_key, 0)

        # Register the agent with Agentverse
        result = register_with_agentverse(
            ai_identity,
            webhook,
            agentverse_key,
            name,
            readme_content
        )
        click.echo(f"Agent successfully registered: {result}")

        # Optionally save information to .env file
        set_key(".env", "AI_IDENTITY", ai_identity.to_string())
        set_key(".env", "AI_NAME", name)
        click.echo("Identity and name saved to .env.")
    except Exception as e:
        click.echo(f"Error registering agent: {str(e)}")
        sys.exit(1)


# Generate identity command
@cli.command(name="generate-identity")
@click.option('-s', '--strength', type=int, default=256, show_default=True,
              help="Strength of the mnemonic (128 or 256 bits)")
@click.option('-n', '--name', default='AGENT_KEY', show_default=True,
              help="Name of the environment variable")
@click.option('-o', '--output', type=click.Path(), help="Output file for saving the generated key")
def identity(strength, name, output):
    """Generate an agent identity key as a mnemonic phrase and optionally save to file or .env."""

    # Generate a mnemonic phrase for the identity key
    mnemo = Mnemonic("english")
    words = mnemo.generate(strength=strength)
    env_record = f'{name}="{words}"'

    # Output the generated key to the specified file or stdout
    if output:
        with open(output, 'a') as f:
            f.write(env_record + '\n')
        click.echo(f"{name} ({strength} bits) appended to {output}")
    else:
        click.echo(env_record)

    # Load existing environment variables to check if the key already exists
    load_dotenv()
    existing_env = dotenv_values(".env")

    # Check if the key already exists in .env
    if name in existing_env:
        # Ask user to confirm overwrite
        if not click.confirm(f"{name} already exists in .env. Do you want to overwrite it?", default=False):
            click.echo("Key not saved to .env.")
            return

    # Save the key to .env
    set_key(".env", name, words)
    click.echo(f"{name} saved to .env.")


if __name__ == "__main__":
    cli()
