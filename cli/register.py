import click
import sys
from dotenv import set_key
from fetchai.crypto import Identity
from fetchai.registration import register_with_agentverse
from cli.env import load_environment_variables
from cli.readme import load_readme
# Register command

@click.command(name="register")
@click.option(
    "-n", "--name", prompt="Enter AI name", required=True, help="Name of the AI"
)
@click.option(
    "-r",
    "--readme",
    prompt="Enter README file path",
    required=True,
    help="Path to README file",
)
@click.option(
    "-w",
    "--webhook",
    prompt="Enter Webhook URL",
    required=True,
    help="Webhook URL for the AI",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force registration even if agent is already registered",
)
def register(name, readme, webhook, force):
    """Register an agent with AgentVerse and save to .env."""
    # Load environment variables and read README file
    agentverse_key, agent_key = load_environment_variables()
    readme_content = load_readme(readme)

    try:
        # Create AI identity
        ai_identity = Identity.from_seed(agent_key, 0)

        # Register the agent with Agentverse
        result = register_with_agentverse(
            ai_identity, webhook, agentverse_key, name, readme_content
        )
        click.echo(f"Agent successfully registered @ {ai_identity.address}")
        # Optionally save information to .env file
        set_key(".env", "AI_IDENTITY", ai_identity.address)
        set_key(".env", "AI_NAME", name)
        click.echo("Identity and name saved to .env.")
    except Exception as e:
        click.echo(f"Error registering agent: {str(e)}")
        sys.exit(1)

