"""
Test script for Financial Analyst Agent
Run this locally or in Databricks to verify everything works
"""
import sys
import os

# Add financial_agent to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'financial_agent'))


def test_tools():
    """Test individual tools"""
    print("="*70)
    print("TESTING AGENT TOOLS")
    print("="*70)

    try:
        from tools import get_financial_metrics_tool, get_ma_tool, get_swot_tool

        # Test 1: Financial Metrics Tool
        print("\n[1/3] Testing Financial Metrics Tool...")
        financial_tool = get_financial_metrics_tool()
        result = financial_tool(ticker="AAPL", metrics_type="summary")
        print("✓ Financial Metrics Tool working!")
        print(f"   Sample output (first 300 chars):\n   {result[:300]}...\n")

        # Test 2: M&A Analysis Tool
        print("[2/3] Testing M&A Analysis Tool...")
        ma_tool = get_ma_tool()
        result = ma_tool(ticker="MSFT")
        print("✓ M&A Analysis Tool working!")
        print(f"   Sample output (first 300 chars):\n   {result[:300]}...\n")

        # Test 3: SWOT Analysis Tool
        print("[3/3] Testing SWOT Analysis Tool...")
        swot_tool = get_swot_tool()
        result = swot_tool(ticker="GOOGL")
        print("✓ SWOT Analysis Tool working!")
        print(f"   Sample output (first 300 chars):\n   {result[:300]}...\n")

        print("="*70)
        print("ALL TOOLS PASSED ✓")
        print("="*70)
        return True

    except Exception as e:
        print(f"✗ Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent():
    """Test the full agent (requires Databricks environment)"""
    print("\n" + "="*70)
    print("TESTING FULL AGENT")
    print("="*70)

    try:
        from agent import create_financial_agent

        print("\nCreating agent...")
        agent = create_financial_agent(
            model_name="databricks-dbrx-instruct",
            temperature=0.1
        )
        print("✓ Agent created successfully!")

        print("\nTesting agent query...")
        response = agent.query("What are the key financial metrics for Tesla?")

        if response.get("success"):
            print("✓ Agent query successful!")
            print(f"\nAgent Response:\n{response['output'][:500]}...\n")
        else:
            print(f"✗ Agent query failed: {response.get('error')}")

        return response.get("success", False)

    except ImportError as e:
        print("⚠ Agent test skipped - Databricks environment required")
        print(f"   Error: {e}")
        print("   Note: Agent requires Databricks Foundation Model API")
        print("   Tools can still be used independently!")
        return None

    except Exception as e:
        print(f"✗ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_import():
    """Test UI can be imported"""
    print("\n" + "="*70)
    print("TESTING UI MODULE")
    print("="*70)

    try:
        from ui import FinancialAnalystUI, launch_app
        print("✓ UI module imported successfully!")
        print("✓ Ready to launch Gradio app")

        print("\nTo launch the UI, run:")
        print("  python -c 'from financial_agent.ui import launch_app; launch_app()'")

        return True

    except Exception as e:
        print(f"✗ UI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         Financial Analyst Agent - Test Suite                     ║
║         Databricks Hackathon Project                             ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    results = {
        "tools": test_tools(),
        "ui": test_ui_import(),
        "agent": test_agent()
    }

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tools:  {'✓ PASS' if results['tools'] else '✗ FAIL'}")
    print(f"UI:     {'✓ PASS' if results['ui'] else '✗ FAIL'}")
    print(f"Agent:  {'✓ PASS' if results['agent'] else '⚠ SKIP (Databricks only)' if results['agent'] is None else '✗ FAIL'}")

    if results['tools'] and results['ui']:
        print("\n✓ Core functionality working! Ready to deploy to Databricks.")
        print("\nNext steps:")
        print("  1. Push to GitHub")
        print("  2. Connect repo to Databricks")
        print("  3. Run setup_databricks.py in Databricks")
        print("  4. Deploy as Databricks App")
    else:
        print("\n⚠ Some tests failed. Check error messages above.")

    print("="*70)


if __name__ == "__main__":
    main()
