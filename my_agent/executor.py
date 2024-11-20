from typing import Dict, List, Generator
from my_agent.agent import graph
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphExecutor:
    def __init__(self, graph=None):
        from my_agent.agent import graph as default_graph
        logger.info("Initializing GraphExecutor")
        self.graph = graph if graph is not None else default_graph
    
    def execute_single(self, user_input: str, recursion_limit: int = 150):
        """Execute the graph for a single user input"""
        logger.info(f"Executing graph with input: {user_input}")
        try:
            events = self.graph.stream(
                {
                    "messages": [
                        (
                            "user",
                            user_input
                        )
                    ],
                },
                {"recursion_limit": recursion_limit},
            )
            logger.info("Graph execution started")
            
            for event in events:
                # Debug: Log the raw event structure
                logger.debug(f"Raw event data: {event}")
                
                # If there are messages, log the first one's content
                if 'researcher' in event and event['researcher'].get('messages'):
                    msg = event['researcher']['messages'][0]
                    logger.debug(f"First researcher message content type: {type(msg.content)}")
                    if isinstance(msg.content, list):
                        logger.debug(f"Content list items: {[type(item) for item in msg.content]}")
                
                yield event
                
        except Exception as e:
            logger.error(f"Error in execute_single: {str(e)}", exc_info=True)
            raise
    
    def execute_chat(self, messages: List[Dict], recursion_limit: int = 150) -> Generator:
        """Execute the graph for a chat history"""
        events = self.graph.stream(
            {
                "messages": messages
            },
            {"recursion_limit": recursion_limit},
        )
        return events

# Example usage in test_multi_agent.py or streamlit app
if __name__ == "__main__":
    executor = GraphExecutor()
    events = executor.execute_single(
        "First, get the UK's GDP over the past 5 years, then make a line chart of it. "
        "Once you make the chart, finish."
    )
    for s in events:
        print(s)
        print("----")