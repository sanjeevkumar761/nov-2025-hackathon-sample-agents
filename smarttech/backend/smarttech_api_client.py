"""
SmartTech API Client Examples

This script demonstrates how to interact with the SmartTech TSD 
Ticket Classification API using Python requests.
"""

import requests
import json
from typing import Dict, List

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"


class SmartTechAPIClient:
    """Client for SmartTech Ticket Classification API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Check API health status"""
        response = self.session.get(f"{self.base_url}/api/v1/health")
        response.raise_for_status()
        return response.json()
    
    def classify_ticket(self, ticket: Dict) -> Dict:
        """Classify a single ticket"""
        response = self.session.post(
            f"{self.base_url}/api/v1/tickets/classify",
            json=ticket
        )
        response.raise_for_status()
        return response.json()
    
    def batch_classify_tickets(self, tickets: List[Dict]) -> Dict:
        """Classify multiple tickets"""
        response = self.session.post(
            f"{self.base_url}/api/v1/tickets/batch-classify",
            json={"tickets": tickets}
        )
        response.raise_for_status()
        return response.json()
    
    def get_mock_tickets(self) -> Dict:
        """Get all mock tickets"""
        response = self.session.get(f"{self.base_url}/api/v1/tickets/mock")
        response.raise_for_status()
        return response.json()
    
    def get_mock_ticket_by_id(self, ticket_id: str) -> Dict:
        """Get specific mock ticket"""
        response = self.session.get(f"{self.base_url}/api/v1/tickets/mock/{ticket_id}")
        response.raise_for_status()
        return response.json()
    
    def get_kb_articles(self) -> Dict:
        """Get all KB articles"""
        response = self.session.get(f"{self.base_url}/api/v1/kb/articles")
        response.raise_for_status()
        return response.json()
    
    def get_kb_article(self, article_id: str) -> Dict:
        """Get specific KB article"""
        response = self.session.get(f"{self.base_url}/api/v1/kb/articles/{article_id}")
        response.raise_for_status()
        return response.json()
    
    def get_statistics(self) -> Dict:
        """Get classification statistics"""
        response = self.session.get(f"{self.base_url}/api/v1/stats")
        response.raise_for_status()
        return response.json()
    
    def reset_statistics(self) -> Dict:
        """Reset classification statistics"""
        response = self.session.delete(f"{self.base_url}/api/v1/stats")
        response.raise_for_status()
        return response.json()


# Example Usage Functions
def example_1_health_check():
    """Example 1: Check API health"""
    print("\n" + "="*60)
    print("Example 1: Health Check")
    print("="*60)
    
    client = SmartTechAPIClient()
    health = client.health_check()
    
    print(f"Status: {health['status']}")
    print(f"Agent Initialized: {health['agent_initialized']}")
    print(f"Version: {health['version']}")


def example_2_classify_single_ticket():
    """Example 2: Classify a single ticket"""
    print("\n" + "="*60)
    print("Example 2: Classify Single Ticket")
    print("="*60)
    
    client = SmartTechAPIClient()
    
    # Create a test ticket
    ticket = {
        "ticket_id": "TEST-001",
        "subject": "Cannot reset my password",
        "description": "I tried to reset my password but the link in the email expired. Need help urgently.",
        "category": "Account",
        "priority": "High",
        "user": "test.user@smarttech.com",
        "created_at": "2024-11-22 10:30:00"
    }
    
    print(f"\nTicket: {ticket['ticket_id']}")
    print(f"Subject: {ticket['subject']}")
    
    result = client.classify_ticket(ticket)
    
    print(f"\n✓ Classification Results:")
    print(f"  Intent: {result['detected_intent']}")
    print(f"  Confidence: {result['confidence']:.0%}")
    print(f"  Self-Service: {'YES' if result['self_service_eligible'] else 'NO'}")
    print(f"  Routing: {result['routing']}")
    
    if result['knowledge_base_articles']:
        print(f"\n  Recommended KB Articles:")
        for article in result['knowledge_base_articles']:
            print(f"    • {article['article_id']}: {article['title']}")
            print(f"      Success Rate: {article['success_rate']}%")


def example_3_batch_classify():
    """Example 3: Batch classify multiple tickets"""
    print("\n" + "="*60)
    print("Example 3: Batch Classification")
    print("="*60)
    
    client = SmartTechAPIClient()
    
    # Create multiple test tickets
    tickets = [
        {
            "ticket_id": "BATCH-001",
            "subject": "VPN not connecting",
            "description": "Cannot connect to VPN from home. Getting timeout error.",
            "category": "Network",
            "priority": "High",
            "user": "user1@smarttech.com"
        },
        {
            "ticket_id": "BATCH-002",
            "subject": "Need Adobe Photoshop",
            "description": "I need Adobe Photoshop for my design work. How do I request it?",
            "category": "Software",
            "priority": "Medium",
            "user": "user2@smarttech.com"
        },
        {
            "ticket_id": "BATCH-003",
            "subject": "Email setup on iPhone",
            "description": "Can't configure my work email on iPhone. Keep getting error.",
            "category": "Email",
            "priority": "Medium",
            "user": "user3@smarttech.com"
        }
    ]
    
    print(f"\nClassifying {len(tickets)} tickets...")
    
    result = client.batch_classify_tickets(tickets)
    
    print(f"\n✓ Batch Results:")
    print(f"  Total Processed: {result['summary']['total_tickets']}")
    print(f"  Self-Service Eligible: {result['summary']['self_service_eligible']} ({result['summary']['self_service_percentage']:.1f}%)")
    
    print(f"\n  Individual Results:")
    for ticket_result in result['results']:
        print(f"    • {ticket_result['ticket_id']}: {ticket_result['detected_intent']} -> {ticket_result['routing']}")


def example_4_get_mock_data():
    """Example 4: Retrieve mock data"""
    print("\n" + "="*60)
    print("Example 4: Get Mock Data")
    print("="*60)
    
    client = SmartTechAPIClient()
    
    # Get all mock tickets
    mock_tickets = client.get_mock_tickets()
    print(f"\nTotal Mock Tickets: {mock_tickets['count']}")
    
    # Get specific ticket
    ticket = client.get_mock_ticket_by_id("TSD-2024-002")
    print(f"\nSample Ticket: {ticket['ticket_id']}")
    print(f"Subject: {ticket['subject']}")
    print(f"Description: {ticket['description'][:60]}...")


def example_5_kb_articles():
    """Example 5: Access KB articles"""
    print("\n" + "="*60)
    print("Example 5: Knowledge Base Articles")
    print("="*60)
    
    client = SmartTechAPIClient()
    
    # Get all KB articles
    kb_articles = client.get_kb_articles()
    print(f"\nTotal KB Articles: {kb_articles['count']}")
    
    # Get specific article
    article = client.get_kb_article("KB-001")
    print(f"\nSample Article: {article['article_id']}")
    print(f"Title: {article['title']}")
    print(f"Success Rate: {article['success_rate']}%")
    print(f"Avg Resolution Time: {article['avg_resolution_time']}")
    print(f"Steps:")
    for i, step in enumerate(article['steps'], 1):
        print(f"  {i}. {step}")


def example_6_statistics():
    """Example 6: Get classification statistics"""
    print("\n" + "="*60)
    print("Example 6: Classification Statistics")
    print("="*60)
    
    client = SmartTechAPIClient()
    
    stats = client.get_statistics()
    
    print(f"\nTotal Classifications: {stats['total_classifications']}")
    print(f"Self-Service Count: {stats['self_service_count']}")
    print(f"Self-Service %: {stats['self_service_percentage']:.1f}%")
    
    if stats['intent_distribution']:
        print(f"\nIntent Distribution:")
        for intent, count in sorted(stats['intent_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {intent}: {count}")
    
    if stats['routing_distribution']:
        print(f"\nRouting Distribution:")
        for routing, count in stats['routing_distribution'].items():
            print(f"  • {routing}: {count}")


def example_7_curl_commands():
    """Example 7: Show curl command examples"""
    print("\n" + "="*60)
    print("Example 7: Curl Command Examples")
    print("="*60)
    
    curl_examples = """
# Health Check
curl http://localhost:8000/api/v1/health

# Classify Single Ticket
curl -X POST http://localhost:8000/api/v1/tickets/classify \\
  -H "Content-Type: application/json" \\
  -d '{
    "ticket_id": "TEST-001",
    "subject": "Password reset needed",
    "description": "Cannot reset my password",
    "category": "Account",
    "priority": "High",
    "user": "test@smarttech.com"
  }'

# Get Mock Tickets
curl http://localhost:8000/api/v1/tickets/mock

# Get KB Articles
curl http://localhost:8000/api/v1/kb/articles

# Get Statistics
curl http://localhost:8000/api/v1/stats

# Batch Classify
curl -X POST http://localhost:8000/api/v1/tickets/batch-classify \\
  -H "Content-Type: application/json" \\
  -d '{
    "tickets": [
      {
        "ticket_id": "B1",
        "subject": "VPN issue",
        "description": "Cannot connect",
        "category": "Network",
        "priority": "High",
        "user": "user@smarttech.com"
      }
    ]
  }'
"""
    
    print(curl_examples)


def run_all_examples():
    """Run all examples"""
    try:
        example_1_health_check()
        example_2_classify_single_ticket()
        example_3_batch_classify()
        example_4_get_mock_data()
        example_5_kb_articles()
        example_6_statistics()
        example_7_curl_commands()
        
        print("\n" + "="*60)
        print("✓ All Examples Completed Successfully!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to API server")
        print("Make sure the server is running: python smarttech_api.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SmartTech API Client Examples")
    print("="*60)
    print("\nMake sure the API server is running:")
    print("  python smarttech_api.py")
    print("\nThen run these examples to test the API")
    print("="*60)
    
    # Run all examples
    run_all_examples()
