from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from typing import Annotated
import matplotlib
matplotlib.use('Agg')  # Set this before importing pyplot
import matplotlib.pyplot as plt
from langchain_experimental.utilities import PythonREPL



# Warning: This executes code locally, which can be unsafe when not sandboxed

repl = PythonREPL()

tavily_tool = TavilySearchResults(max_results=5)

@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
) -> str:
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        # Clear any existing plots
        plt.clf()
        plt.close('all')
        
        # Execute the code
        result = repl.run(code)
        
        # If a plot was created, save it
        if plt.get_fignums():
            # Save the figure
            plt.savefig('uk_gdp_chart.png', bbox_inches='tight', dpi=300)
            plt.close('all')  # Close all figures
            return f"Successfully executed code and saved plot as 'uk_gdp_chart.png'.\n{result}"
            
        return f"Successfully executed code:\n{result}"
        
    except Exception as e:
        return f"Failed to execute code. Error: {str(e)}"
    
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )