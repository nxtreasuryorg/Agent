from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os

# Import the mock tools for treasury agents
from treasury_agent.tools.mock_market_data import MockMarketDataTool
from treasury_agent.tools.mock_risk_assessment import MockRiskAssessmentTool
from treasury_agent.tools.mock_payment_processor import MockPaymentProcessorTool
from treasury_agent.tools.mock_audit_logger import MockAuditLoggerTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class TreasuryAgent():
    """Hierarchical Treasury Team - Treasury Manager coordinates specialist agents for payment processing and investment management"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # Treasury Manager - Coordinates the team (no tools for manager in hierarchical process)
    @agent
    def treasury_manager(self) -> Agent:
        # Create LLM instance for the manager using CrewAI's LLM class
        manager_llm = LLM(
            model="bedrock/amazon.nova-micro-v1:0",
            temperature=0.3,
            max_tokens=2000
        )
        
        return Agent(
            config=self.agents_config['treasury_manager'], # type: ignore[index]
            tools=[], # No tools for manager in hierarchical process - tools assigned to specialists
            llm=manager_llm,
            verbose=True
        )

    # Payment Specialist - Handles payment processing and routing
    @agent
    def payment_specialist(self) -> Agent:
        # Create LLM instance for the payment specialist using CrewAI's LLM class
        specialist_llm = LLM(
            model="bedrock/amazon.nova-micro-v1:0",
            temperature=0.3,
            max_tokens=2000
        )
        
        return Agent(
            config=self.agents_config['payment_specialist'], # type: ignore[index]
            tools=[
                MockPaymentProcessorTool(),
                MockMarketDataTool(), # Payment specialist needs market data for routing optimization
                MockAuditLoggerTool()
            ],
            llm=specialist_llm,
            verbose=True
        )

    # Market Analyst - Handles investment analysis and surplus detection
    @agent
    def market_analyst(self) -> Agent:
        # Create LLM instance for the market analyst using CrewAI's LLM class
        analyst_llm = LLM(
            model="bedrock/amazon.nova-micro-v1:0",
            temperature=0.3,
            max_tokens=2000
        )
        
        return Agent(
            config=self.agents_config['market_analyst'], # type: ignore[index]
            tools=[
                MockMarketDataTool(),
                MockAuditLoggerTool()
            ],
            llm=analyst_llm,
            verbose=True
        )

    # Risk Assessor - Handles compliance and balance validation
    @agent
    def risk_assessor(self) -> Agent:
        # Create LLM instance for the risk assessor using CrewAI's LLM class
        assessor_llm = LLM(
            model="bedrock/amazon.nova-micro-v1:0",
            temperature=0.3,
            max_tokens=2000
        )
        
        return Agent(
            config=self.agents_config['risk_assessor'], # type: ignore[index]
            tools=[
                MockRiskAssessmentTool(),
                MockMarketDataTool(), # Risk assessor needs market data for risk evaluation
                MockAuditLoggerTool()
            ],
            llm=assessor_llm,
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
    # Treasury Coordination Task - Manager coordinates the team
    @task
    def treasury_coordination_task(self) -> Task:
        return Task(
            config=self.tasks_config['treasury_coordination_task'], # type: ignore[index]
            output_file='output/treasury_report.md'
        )

    # Payment Processing Task - Specialist analyzes payment options
    @task
    def payment_processing_task(self) -> Task:
        return Task(
            config=self.tasks_config['payment_processing_task'], # type: ignore[index]
            output_file='output/payment_analysis.md'
        )

    # Market Analysis Task - Specialist analyzes investment opportunities
    @task
    def market_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_analysis_task'], # type: ignore[index]
            output_file='output/market_analysis.md'
        )

    # Risk Assessment Task - Specialist validates compliance and balance
    @task
    def risk_assessment_task(self) -> Task:
        return Task(
            config=self.tasks_config['risk_assessment_task'], # type: ignore[index]
            output_file='output/risk_assessment.md'
        )

    # Final Treasury Report Task - Manager synthesizes all specialist work
    @task
    def final_treasury_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_treasury_report_task'], # type: ignore[index]
            output_file='output/final_treasury_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Hierarchical Treasury Team crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        # Create the LLM instance for the manager using CrewAI's LLM class
        manager_llm = LLM(
            model="bedrock/amazon.nova-micro-v1:0",
            temperature=0.3,  # Slightly higher for better reasoning
            max_tokens=2000   # More tokens for complex coordination tasks
        )

        return Crew(
            agents=[
                self.payment_specialist(),
                self.market_analyst(), 
                self.risk_assessor()
            ], # Only specialist agents - manager agent is specified separately
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical, # Using hierarchical process for Treasury Manager coordination
            manager_agent=self.treasury_manager(), # Treasury Manager as the custom manager agent
            manager_llm=manager_llm, # Specify LLM instance for the manager in hierarchical process
            planning=False, # Disable planning to avoid LLM issues with Task Execution Planner
            verbose=True,
            # Manager will coordinate specialist agents for payment processing and investment management
        )
