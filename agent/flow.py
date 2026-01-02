import sys
import os

# Add project root and PocketFlow to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PocketFlow-main"))

from pocketflow import Flow
from agent.nodes import DecideNode, ChatNode, ExtractionNode, BookingNode, SupervisorNode, ServiceAreaRejectNode

def create_hvac_agent_flow():
    """Creates and returns the HVAC booking agent flow."""
    # Instantiate nodes
    decide = DecideNode()
    chat = ChatNode()
    extract = ExtractionNode()
    book = BookingNode()
    supervisor = SupervisorNode()
    service_area_reject = ServiceAreaRejectNode()  # BUG-1.5 FIX

    # Define transitions
    decide - "chat" >> chat
    decide - "extract" >> extract
    decide - "book" >> book
    decide - "update" >> book
    decide - "finish" >> supervisor
    
    # Loop back to decide for extraction (data processing)
    extract >> decide
    
    # BUG-1.5 FIX: Immediate service area rejection path
    extract - "service_area_reject" >> service_area_reject
    service_area_reject >> supervisor
    
    # Supervisor is the final gatekeeper for user communication
    chat >> supervisor
    book >> chat # Book always hands over to chat for confirmation
    
    # Flow starts at decide
    return Flow(start=decide)
