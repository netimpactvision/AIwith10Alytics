#!/usr/bin/env python3
"""
Example client for the Financial Analysis API.
Demonstrates how to use the API endpoints programmatically.
"""

import json
import time
from typing import Optional

import requests


class FinancialAnalysisClient:
    """Client for interacting with the Financial Analysis API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health_check(self) -> bool:
        """Check if the API server is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except requests.RequestException:
            return False

    def start_analysis(
        self, stock: str, execution_mode: str = "parallel"
    ) -> Optional[str]:
        """Start an asynchronous financial analysis."""
        try:
            response = self.session.post(
                f"{self.base_url}/analyze",
                json={"stock": stock, "execution_mode": execution_mode},
            )
            response.raise_for_status()
            return response.json().get("task_id")
        except requests.RequestException as e:
            print(f"Error starting analysis: {e}")
            return None

    def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get the status of a task."""
        try:
            response = self.session.get(f"{self.base_url}/status/{task_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting task status: {e}")
            return None

    def run_sync_analysis(
        self, stock: str, execution_mode: str = "parallel"
    ) -> Optional[dict]:
        """Run a synchronous financial analysis."""
        try:
            response = self.session.post(
                f"{self.base_url}/analyze/sync",
                json={"stock": stock, "execution_mode": execution_mode},
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error running sync analysis: {e}")
            return None

    def list_tasks(self) -> Optional[dict]:
        """List all tasks."""
        try:
            response = self.session.get(f"{self.base_url}/tasks")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error listing tasks: {e}")
            return None

    def wait_for_completion(
        self, task_id: str, poll_interval: int = 5, timeout: int = 600
    ) -> Optional[dict]:
        """Wait for a task to complete with polling."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            if not status:
                return None

            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                print(f"Task failed: {status.get('error')}")
                return status

            print(f"Task {task_id} is {status['status']}... waiting {poll_interval}s")
            time.sleep(poll_interval)

        print(f"Task {task_id} timed out after {timeout} seconds")
        return None


def main():
    """Example usage of the Financial Analysis API client."""
    client = FinancialAnalysisClient()

    # Check if server is running
    print("🔍 Checking API server health...")
    if not client.health_check():
        print(
            "❌ API server is not running. Please start it first with: python start_server.py"
        )
        return

    print("✅ API server is healthy")

    # Example 1: Async analysis with polling
    print("\n📊 Example 1: Asynchronous Analysis")
    stock_symbol = "RELIANCE"

    print(f"Starting analysis for {stock_symbol}...")
    task_id = client.start_analysis(stock_symbol, "parallel")

    if task_id:
        print(f"✅ Analysis started with task ID: {task_id}")

        # Wait for completion
        result = client.wait_for_completion(task_id, poll_interval=10)
        if result and result["status"] == "completed":
            print(
                f"✅ Analysis completed in {result.get('execution_time', 0):.2f} seconds"
            )
            print("📄 Results saved to task_outputs/ directory")
        else:
            print("❌ Analysis failed or timed out")

    # Example 2: List all tasks
    print("\n📋 Example 2: List All Tasks")
    tasks = client.list_tasks()
    if tasks:
        print(f"Found {len(tasks.get('tasks', []))} tasks:")
        for task in tasks.get("tasks", []):
            print(
                f"  - {task['task_id']}: {task['status']} ({task.get('stock', 'N/A')})"
            )

    # Example 3: Synchronous analysis (commented out as it takes time)
    print("\n⚡ Example 3: Synchronous Analysis (Quick Demo)")
    print("Note: This would run a full analysis synchronously. Skipping for demo.")

    # Uncomment the following lines to run a sync analysis:
    # print(f"Running synchronous analysis for {stock_symbol}...")
    # sync_result = client.run_sync_analysis(stock_symbol, "sequential")
    # if sync_result:
    #     print(f"✅ Sync analysis completed: {sync_result['status']}")
    #     print(f"⏱️ Execution time: {sync_result.get('execution_time', 0):.2f} seconds")

    print("\n🎉 Examples completed!")
    print("💡 Check the API documentation at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
