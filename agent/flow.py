import sys
import os

# Add project root and PocketFlow to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PocketFlow-main"))

from pocketflow import Flow
from agent.nodes import DecideNode, ChatNode, ExtractionNode, BookingNode

def create_hvac_agent_flow():
    """Creates and returns the HVAC booking agent flow."""
    # Instantiate nodes
    decide = DecideNode()
    chat = ChatNode()
    extract = ExtractionNode()
    book = BookingNode()

    # Define transitions
    # decide - "chat" >> chat
    # decide - "extract" >> extract
    # decide - "book" >> book
    
    # PocketFlow uses >> for default transitions and - "action" >> for named ones
    decide - "chat" >> chat
    decide - "extract" >> extract
    decide - "book" >> book
    decide - "update" >> book
    
    # Loop back to decide for extraction (data processing)
    # but STOP for chat and book (user interaction points)
    extract >> decide

    # Flow starts at decide
    return Flow(start=decide)
