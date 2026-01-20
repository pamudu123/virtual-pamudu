import pytest
from unittest.mock import MagicMock, patch
from chat import planner_node, AgentState, AgentPlan, ToolCall, SearchParams, EmailParams

@pytest.fixture
def mock_planner_llm():
    with patch('chat.get_llm') as mock_get_llm:
        mock_model = MagicMock()
        mock_get_llm.return_value = mock_model
        
        mock_structured_llm = MagicMock()
        mock_model.with_structured_output.return_value = mock_structured_llm
        
        yield mock_structured_llm

def test_planner_brain_tool(mock_planner_llm):
    """Test Case 1: Who is Pamudu? -> Brain tool"""
    # Setup mock response
    mock_plan = AgentPlan(
        need_external_info=True,
        tool_calls=[ToolCall(tool="brain", action="search", params=SearchParams(shortcuts=["bio"]))]
    )
    mock_planner_llm.invoke.return_value = mock_plan
    
    # Run planner
    state = AgentState(query="Who is Pamudu?", conversation_history=[], plan=[], results=[], final_answer="", citations=[])
    result = planner_node(state)
    
    print(f"\nQuery: 'Who is Pamudu?'\nPlan: {result['plan']}")

    # Verify
    assert len(result["plan"]) == 1
    assert result["plan"][0]["tool"] == "brain"
    assert result["plan"][0]["action"] == "search"

def test_planner_github_tool(mock_planner_llm):
    """Test Case 2: Show me your repos -> GitHub tool"""
    mock_plan = AgentPlan(
        need_external_info=True,
        tool_calls=[ToolCall(tool="github", action="list", params=SearchParams(limit=10))]
    )
    mock_planner_llm.invoke.return_value = mock_plan
    
    state = AgentState(query="Show me your repos", conversation_history=[], plan=[], results=[], final_answer="", citations=[])
    result = planner_node(state)
    
    print(f"\nQuery: 'Show me your repos'\nPlan: {result['plan']}")

    assert len(result["plan"]) == 1
    assert result["plan"][0]["tool"] == "github"

def test_planner_greeting(mock_planner_llm):
    """Test Case 3: Hi -> No tools"""
    mock_plan = AgentPlan(
        need_external_info=False,
        response="Hi there! I'm Pamudu's AI Assistant."
    )
    mock_planner_llm.invoke.return_value = mock_plan
    
    state = AgentState(query="Hi", conversation_history=[], plan=[], results=[], final_answer="", citations=[])
    result = planner_node(state)
    
    print(f"\nQuery: 'Hi'\nAnswer: {result['final_answer']}")

    assert result["plan"] == []
    assert "Hi there" in result["final_answer"]

def test_planner_irrelevant(mock_planner_llm):
    """Test Case 4: Irrelevant query -> No tools"""
    mock_plan = AgentPlan(
        need_external_info=False,
        response="I can only help with questions about Pamudu."
    )
    mock_planner_llm.invoke.return_value = mock_plan
    
    state = AgentState(query="What is the weather in Mars?", conversation_history=[], plan=[], results=[], final_answer="", citations=[])
    result = planner_node(state)
    
    print(f"\nQuery: 'What is the weather in Mars?'\nAnswer: {result['final_answer']}")

    assert result["plan"] == []
    assert "only help with questions about Pamudu" in result["final_answer"]

def test_planner_email_workflow(mock_planner_llm):
    """Test Case 5: Email Workflow (Multi-turn)"""
    
    # Turn 1: Request to send email -> Should draft (no tool call)
    mock_plan_draft = AgentPlan(
        need_external_info=False,
        response="Here is the draft..."
    )
    mock_planner_llm.invoke.return_value = mock_plan_draft
    
    state1 = AgentState(query="Send an email to Bob saying Hi", conversation_history=[], plan=[], results=[], final_answer="", citations=[])
    result1 = planner_node(state1)
    
    print(f"\nQuery (Turn 1): 'Send an email...'\nAnswer: {result1['final_answer']}")

    assert result1["plan"] == []
    assert "draft" in result1["final_answer"]
    
    # Turn 2: Confirm send -> Should call email tool
    mock_plan_send = AgentPlan(
        need_external_info=True,
        tool_calls=[ToolCall(tool="email", action="send", params=EmailParams(email_to="bob@example.com", email_subject="Hi", email_content="Hi"))]
    )
    mock_planner_llm.invoke.return_value = mock_plan_send
    
    history = [
        {"role": "user", "content": "Send an email to Bob saying Hi"},
        {"role": "assistant", "content": "Here is the draft..."}
    ]
    state2 = AgentState(query="Yes, send it", conversation_history=history, plan=[], results=[], final_answer="", citations=[])
    result2 = planner_node(state2)
    
    print(f"\nQuery (Turn 2): 'Yes, send it'\nPlan: {result2['plan']}")

    assert len(result2["plan"]) == 1
    assert result2["plan"][0]["tool"] == "email"
    assert result2["plan"][0]["action"] == "send"
