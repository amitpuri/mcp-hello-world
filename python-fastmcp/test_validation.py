#!/usr/bin/env python3
"""Test Pydantic validation in FastMCP implementation"""

from shared.types import ChatRequest, ListModelsRequest, ModelProvider
from pydantic import ValidationError

def test_valid_requests():
    """Test valid request creation"""
    print("🧪 Testing valid requests...")
    
    # Valid chat request
    chat_req = ChatRequest(prompt="Hello world", temperature=0.7, max_tokens=100)
    print(f"✅ Valid ChatRequest: {chat_req.prompt}, temp={chat_req.temperature}")
    
    # Valid list models request
    list_req = ListModelsRequest(provider=ModelProvider.OPENAI)
    print(f"✅ Valid ListModelsRequest: {list_req.provider}")

def test_invalid_requests():
    """Test invalid request validation"""
    print("\n🧪 Testing invalid requests...")
    
    # Invalid temperature
    try:
        ChatRequest(prompt="Hello", temperature=2.0)
        print("❌ Should have failed for temperature > 1.0")
    except ValidationError as e:
        print("✅ Caught invalid temperature:", str(e).split('\n')[0])
    
    # Invalid max_tokens
    try:
        ChatRequest(prompt="Hello", max_tokens=-1)
        print("❌ Should have failed for negative max_tokens")
    except ValidationError as e:
        print("✅ Caught invalid max_tokens:", str(e).split('\n')[0])
    
    # Missing prompt
    try:
        ChatRequest()
        print("❌ Should have failed for missing prompt")
    except ValidationError as e:
        print("✅ Caught missing prompt:", str(e).split('\n')[0])
    
    # Invalid provider
    try:
        ListModelsRequest(provider="invalid_provider")
        print("❌ Should have failed for invalid provider")
    except ValidationError as e:
        print("✅ Caught invalid provider:", str(e).split('\n')[0])

def test_task_detection():
    """Test task type detection"""
    print("\n🧪 Testing task type detection...")
    
    from shared.types import determine_task_type, TaskType
    
    test_cases = [
        ("Write a creative story", TaskType.CREATIVE),
        ("Debug this code", TaskType.CODING),
        ("Analyze the data", TaskType.ANALYTICAL),
        ("Hello there", TaskType.GENERAL)
    ]
    
    for prompt, expected in test_cases:
        result = determine_task_type(prompt)
        if result == expected:
            print(f"✅ '{prompt}' → {result.value}")
        else:
            print(f"❌ '{prompt}' → {result.value} (expected {expected.value})")

def test_model_selection():
    """Test model selection logic"""
    print("\n🧪 Testing model selection...")
    
    from shared.types import select_model_for_task, TaskType, ModelProvider
    
    test_cases = [
        (TaskType.CREATIVE, None, ModelProvider.CLAUDE),
        (TaskType.CODING, None, ModelProvider.OLLAMA),
        (TaskType.ANALYTICAL, None, ModelProvider.OPENAI),
        (TaskType.GENERAL, "claude", ModelProvider.CLAUDE)
    ]
    
    for task_type, preferred, expected in test_cases:
        result = select_model_for_task(task_type, preferred)
        if result == expected:
            print(f"✅ {task_type.value} + {preferred} → {result.value}")
        else:
            print(f"❌ {task_type.value} + {preferred} → {result.value} (expected {expected.value})")

if __name__ == "__main__":
    print("🚀 FastMCP Validation Tests")
    print("=" * 40)
    
    test_valid_requests()
    test_invalid_requests()
    test_task_detection()
    test_model_selection()
    
    print("\n🎉 FastMCP validation tests completed!")