#!/usr/bin/env python3
"""
Test script for NEXUS Alexa Skill
Tests all voice commands locally without Alexa hardware
"""

import requests
import json
import sys

ALEXA_ENDPOINT = "http://localhost:5001/alexa"

def test_launch():
    """Test 'Alexa, open NEXUS'"""
    event = {
        "version": "1.0",
        "session": {"new": True, "sessionId": "test-session-1"},
        "request": {
            "type": "LaunchRequest",
            "requestId": "test-req-1",
            "timestamp": "2026-03-05T12:00:00Z"
        }
    }
    
    response = requests.post(ALEXA_ENDPOINT, json=event)
    print("\n🎙️  'Alexa, open NEXUS'")
    print("=" * 50)
    if response.status_code == 200:
        data = response.json()
        ssml = data.get("response", {}).get("outputSpeech", {}).get("ssml", "")
        # Extract text from SSML
        text = ssml.replace("<speak>", "").replace("</speak>", "").replace("<break time=\"0.5s\"/>", "... ")
        print(f"Alexa says: {text}")
        print("✅ Launch working")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def test_priority_today():
    """Test 'What's my priority today?'"""
    event = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "test-session-1"},
        "request": {
            "type": "IntentRequest",
            "requestId": "test-req-2",
            "timestamp": "2026-03-05T12:01:00Z",
            "intent": {
                "name": "PriorityTodayIntent"
            }
        }
    }
    
    response = requests.post(ALEXA_ENDPOINT, json=event)
    print("\n🎙️  'Alexa, ask NEXUS what's my priority today'")
    print("=" * 50)
    if response.status_code == 200:
        data = response.json()
        ssml = data.get("response", {}).get("outputSpeech", {}).get("ssml", "")
        text = ssml.replace("<speak>", "").replace("</speak>", "")
        print(f"Alexa says: {text[:200]}...")
        print("✅ Priority intent working")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

def test_find_opportunities():
    """Test 'Find federal opportunities'"""
    event = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "test-session-1"},
        "request": {
            "type": "IntentRequest",
            "requestId": "test-req-3",
            "timestamp": "2026-03-05T12:02:00Z",
            "intent": {
                "name": "FindOpportunitiesIntent"
            }
        }
    }
    
    response = requests.post(ALEXA_ENDPOINT, json=event)
    print("\n🎙️  'Alexa, tell NEXUS to find federal opportunities'")
    print("=" * 50)
    if response.status_code == 200:
        data = response.json()
        ssml = data.get("response", {}).get("outputSpeech", {}).get("ssml", "")
        text = ssml.replace("<speak>", "").replace("</speak>", "")
        print(f"Alexa says: {text[:200]}...")
        print("✅ Find opportunities intent working")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

def test_daily_target():
    """Test 'What's my daily target?'"""
    event = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "test-session-1"},
        "request": {
            "type": "IntentRequest",
            "requestId": "test-req-4",
            "timestamp": "2026-03-05T12:03:00Z",
            "intent": {
                "name": "DailyTargetIntent"
            }
        }
    }
    
    response = requests.post(ALEXA_ENDPOINT, json=event)
    print("\n🎙️  'Alexa, ask NEXUS what's my daily target'")
    print("=" * 50)
    if response.status_code == 200:
        data = response.json()
        ssml = data.get("response", {}).get("outputSpeech", {}).get("ssml", "")
        text = ssml.replace("<speak>", "").replace("</speak>", "")
        print(f"Alexa says: {text[:200]}...")
        print("✅ Daily target intent working")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

def test_add_to_pipeline():
    """Test 'Add to pipeline'"""
    event = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "test-session-1"},
        "request": {
            "type": "IntentRequest",
            "requestId": "test-req-5",
            "timestamp": "2026-03-05T12:04:00Z",
            "intent": {
                "name": "AddToPipelineIntent"
            }
        }
    }
    
    response = requests.post(ALEXA_ENDPOINT, json=event)
    print("\n🎙️  'Alexa, ask NEXUS to add to pipeline'")
    print("=" * 50)
    if response.status_code == 200:
        data = response.json()
        ssml = data.get("response", {}).get("outputSpeech", {}).get("ssml", "")
        text = ssml.replace("<speak>", "").replace("</speak>", "")
        print(f"Alexa says: {text[:200]}...")
        print("✅ Add to pipeline intent working")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

def test_help():
    """Test Help intent"""
    event = {
        "version": "1.0",
        "session": {"new": False, "sessionId": "test-session-1"},
        "request": {
            "type": "IntentRequest",
            "requestId": "test-req-6",
            "timestamp": "2026-03-05T12:05:00Z",
            "intent": {
                "name": "AMAZON.HelpIntent"
            }
        }
    }
    
    response = requests.post(ALEXA_ENDPOINT, json=event)
    print("\n🎙️  'Alexa, help'")
    print("=" * 50)
    if response.status_code == 200:
        data = response.json()
        ssml = data.get("response", {}).get("outputSpeech", {}).get("ssml", "")
        text = ssml.replace("<speak>", "").replace("</speak>", "")
        print(f"Alexa says: {text[:200]}...")
        print("✅ Help intent working")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

def main():
    print("🎙️ NEXUS Alexa Skill - Local Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        health = requests.get("http://localhost:5001/alexa/health", timeout=5)
        if health.status_code == 200:
            print("✅ Alexa skill server is running on port 5001")
            print(f"   Connected to: {health.json().get('connected_to_nexus', 'unknown')}")
        else:
            print("❌ Alexa skill server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Alexa skill server: {e}")
        print("   Make sure to run: python3 nexus_alexa_skill.py")
        return
    
    print("\n" + "=" * 60)
    
    # Run all tests
    tests = [
        ("Launch", test_launch),
        ("Priority Today", test_priority_today),
        ("Find Opportunities", test_find_opportunities),
        ("Daily Target", test_daily_target),
        ("Add to Pipeline", test_add_to_pipeline),
        ("Help", test_help)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("=" * 60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Alexa skill is working correctly.")
        print("\nNext steps:")
        print("1. Start ngrok: ngrok http 5001")
        print("2. Configure in Alexa Developer Console")
        print("3. Start talking to NEXUS!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\nMake sure:")
        print("- NEXUS API is running on port 8000")
        print("- Alexa skill server is running on port 5001")
        print("- All API endpoints are accessible")

if __name__ == "__main__":
    main()
