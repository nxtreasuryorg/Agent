from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

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
    
    # Treasury Manager - Coordinates the team and has analysis tools
    @agent
    def treasury_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['treasury_manager'], # type: ignore[index]
            tools=[
                MockMarketDataTool(),
                MockRiskAssessmentTool(), 
                MockAuditLoggerTool()
            ],
            verbose=True
        )

    # Payment Specialist - Handles payment processing and routing
    @agent
    def payment_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['payment_specialist'], # type: ignore[index]
            tools=[
                MockPaymentProcessorTool(),
                MockAuditLoggerTool()
            ],
            verbose=True
        )

    # Market Analyst - Handles investment analysis and surplus detection
    @agent
    def market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['market_analyst'], # type: ignore[index]
            tools=[
                MockMarketDataTool(),
                MockAuditLoggerTool()
            ],
            verbose=True
        )

    # Risk Assessor - Handles compliance and balance validation
    @agent
    def risk_assessor(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_assessor'], # type: ignore[index]
            tools=[
                MockRiskAssessmentTool(),
                MockAuditLoggerTool()
            ],
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

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical, # Using hierarchical process for Treasury Manager coordination
            manager_agent=self.treasury_manager(), # Treasury Manager as the custom manager agent
            planning=True, # Enable planning for better task coordination
            verbose=True,
            # Manager will coordinate specialist agents for payment processing and investment management
        )
