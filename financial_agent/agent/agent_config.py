"""
Financial Analyst Agent Configuration
Uses Databricks Mosaic AI Agent Framework with MLflow
"""
import os
from typing import Any, Dict, List
import mlflow
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.chat_models import ChatDatabricks
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool

# Import our custom tools
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.financial_metrics import get_financial_metrics_tool
from tools.ma_analyzer import get_ma_tool
from tools.swot_analyzer import get_swot_tool


class FinancialAnalystAgent:
    """Financial Analyst Agent using Databricks Foundation Models"""

    def __init__(
        self,
        model_name: str = "databricks-dbrx-instruct",
        temperature: float = 0.1,
        max_tokens: int = 2000
    ):
        """
        Initialize the Financial Analyst Agent

        Args:
            model_name: Databricks Foundation Model to use
            temperature: LLM temperature for response generation
            max_tokens: Maximum tokens for LLM responses
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize LLM
        self.llm = ChatDatabricks(
            endpoint=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Initialize tools
        self.tools = self._create_tools()

        # Create agent
        self.agent = self._create_agent()

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

    def _create_tools(self) -> List[StructuredTool]:
        """Create LangChain tools from our custom tool classes"""

        # Initialize tool instances
        financial_metrics_tool = get_financial_metrics_tool()
        ma_tool = get_ma_tool(llm_client=self.llm)
        swot_tool = get_swot_tool(llm_client=self.llm)

        # Wrap as LangChain StructuredTools
        tools = [
            StructuredTool.from_function(
                func=financial_metrics_tool,
                name=financial_metrics_tool.name,
                description=financial_metrics_tool.description,
            ),
            StructuredTool.from_function(
                func=ma_tool,
                name=ma_tool.name,
                description=ma_tool.description,
            ),
            StructuredTool.from_function(
                func=swot_tool,
                name=swot_tool.name,
                description=swot_tool.description,
            ),
        ]

        return tools

    def _create_agent(self):
        """Create the agent with system prompt"""

        system_prompt = """You are an expert financial analyst assistant with access to real-time financial data and analysis tools.

Your capabilities include:
1. Fetching comprehensive financial metrics for any publicly traded company
2. Analyzing merger and acquisition (M&A) activity in industries
3. Generating detailed SWOT analyses for companies

When a user asks about a company:
- Use the company's stock ticker symbol (e.g., AAPL for Apple, MSFT for Microsoft)
- Fetch relevant financial metrics first
- Provide clear, actionable insights based on the data
- Use multiple tools when appropriate to give comprehensive analysis

Guidelines:
- Always cite specific numbers and metrics in your analysis
- Explain financial ratios and metrics in plain language
- Highlight both positive and negative aspects objectively
- When comparing companies, ensure fair comparisons (same industry/sector)
- If you don't have enough information, ask the user for clarification

You should be:
- Professional and objective
- Data-driven in your analysis
- Clear and concise in explanations
- Proactive in identifying relevant insights

Format your responses clearly with sections and bullet points where appropriate.
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return agent

    def query(self, user_input: str) -> Dict[str, Any]:
        """
        Process user query and return analysis

        Args:
            user_input: User's question or request

        Returns:
            Dictionary with agent output and metadata
        """
        try:
            result = self.agent_executor.invoke({"input": user_input})

            return {
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            }

        except Exception as e:
            return {
                "output": f"Error processing query: {str(e)}",
                "success": False,
                "error": str(e)
            }

    def log_to_mlflow(self, experiment_name: str = "/Users/financial-analyst-agent"):
        """
        Log the agent to MLflow for tracking and deployment

        Args:
            experiment_name: MLflow experiment name
        """
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run(run_name="financial_analyst_agent"):
            # Log parameters
            mlflow.log_param("model_name", self.model_name)
            mlflow.log_param("temperature", self.temperature)
            mlflow.log_param("max_tokens", self.max_tokens)
            mlflow.log_param("num_tools", len(self.tools))

            # Log agent as a model
            mlflow.langchain.log_model(
                self.agent_executor,
                "financial_analyst_agent",
                input_example={"input": "What are the financial metrics for Apple?"}
            )

            print(f"Agent logged to MLflow experiment: {experiment_name}")


def create_financial_agent(
    model_name: str = "databricks-dbrx-instruct",
    temperature: float = 0.1,
    max_tokens: int = 2000
) -> FinancialAnalystAgent:
    """
    Factory function to create a Financial Analyst Agent

    Args:
        model_name: Databricks Foundation Model to use
        temperature: LLM temperature
        max_tokens: Maximum tokens for responses

    Returns:
        Configured FinancialAnalystAgent instance
    """
    return FinancialAnalystAgent(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )


if __name__ == "__main__":
    # Example usage
    agent = create_financial_agent()

    # Test query
    response = agent.query("What are the key financial metrics for Apple (AAPL)?")
    print("\n" + "="*70)
    print("AGENT RESPONSE:")
    print("="*70)
    print(response["output"])
