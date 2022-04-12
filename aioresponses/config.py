"""
Project Configurations
Load environment from dotenv file
Grab config values from environment

.env file expected in project root
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv((Path(__file__).parent.parent / ".env").resolve())
