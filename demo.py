#!/usr/bin/env python3
"""
Demo script for the EPV Research Platform
Shows key features and usage examples
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def demo_quick_analysis():
    """Demo quick EPV analysis"""
    print("=" * 50)
    print("DEMO: Quick EPV Analysis")
    print("=" * 50)

    try:
        from main import EPVResearchPlatform

        platform = EPVResearchPlatform()

        # Demo with a well-known stock
        symbol = "AAPL"
        print(f"Analyzing {symbol}...")

        # This will use yfinance to get real data
        results = platform.quick_epv(symbol)

        print(f"\n📊 Results for {results['company_name']} ({symbol}):")
        print(f"  • EPV per share: ${results['epv_per_share']:.2f}")

        if results["current_price"]:
            print(f"  • Current price: ${results['current_price']:.2f}")

        if results["margin_of_safety"] is not None:
            status = "UNDERVALUED" if results["margin_of_safety"] > 0 else "OVERVALUED"
            print(
                f"  • Margin of safety: {results['margin_of_safety']:.1f}% ({status})"
            )

        print(f"  • Quality score: {results['quality_score']:.2f}/1.0")
        print(f"  • Cost of capital: {results['cost_of_capital']:.1%}")

        return True

    except Exception as e:
        print(f"❌ Error in quick analysis: {e}")
        print("Note: This requires internet connection and yfinance package")
        return False


def demo_cache_functionality():
    """Demo cache functionality"""
    print("\n" + "=" * 50)
    print("DEMO: Cache System")
    print("=" * 50)

    try:
        from utils.cache_manager import CacheManager

        cache = CacheManager()

        # Store some demo data
        cache.set("demo_key", {"analysis": "demo", "score": 0.85}, expiry_hours=1)

        # Retrieve it
        data = cache.get("demo_key")
        print(f"✅ Cache storage/retrieval working: {data}")

        # Get cache stats
        stats = cache.get_cache_stats()
        print(
            f"📈 Cache stats: {stats['total_entries']} entries, {stats['total_size_bytes']} bytes"
        )

        return True

    except Exception as e:
        print(f"❌ Error in cache demo: {e}")
        return False


def demo_data_models():
    """Demo data models"""
    print("\n" + "=" * 50)
    print("DEMO: Financial Data Models")
    print("=" * 50)

    try:
        from models.financial_models import CompanyProfile, EPVCalculation
        from datetime import date

        # Create a sample company profile
        profile = CompanyProfile(
            symbol="DEMO",
            company_name="Demo Corporation",
            sector="Technology",
            industry="Software",
            description="A demonstration company for the EPV platform",
        )

        print(f"✅ Company Profile: {profile.company_name} ({profile.symbol})")
        print(f"   Sector: {profile.sector}, Industry: {profile.industry}")

        # Create a sample EPV calculation
        epv = EPVCalculation(
            symbol="DEMO",
            calculation_date=date.today(),
            normalized_earnings=1000000,
            shares_outstanding=100000,
            cost_of_capital=0.10,
            earnings_per_share=10.0,
            epv_per_share=100.0,
            epv_total=10000000,
        )

        print(f"✅ EPV Calculation: ${epv.epv_per_share:.2f} per share")
        print(f"   Total EPV: ${epv.epv_total:,.0f}")

        return True

    except Exception as e:
        print(f"❌ Error in data models demo: {e}")
        return False


def demo_quality_assessment():
    """Demo quality assessment features"""
    print("\n" + "=" * 50)
    print("DEMO: Quality Assessment System")
    print("=" * 50)

    try:
        from analysis.epv_calculator import EPVCalculator
        from models.financial_models import (
            IncomeStatement,
            BalanceSheet,
            FinancialRatios,
        )
        from datetime import date

        calculator = EPVCalculator()

        # Create sample financial data
        income_statements = [
            IncomeStatement(
                "DEMO", "annual", 2023, net_income=1000000, revenue=10000000
            ),
            IncomeStatement("DEMO", "annual", 2022, net_income=900000, revenue=9500000),
            IncomeStatement("DEMO", "annual", 2021, net_income=800000, revenue=9000000),
        ]

        balance_sheets = [
            BalanceSheet(
                "DEMO",
                "annual",
                2023,
                total_assets=5000000,
                total_equity=3000000,
                current_assets=2000000,
                current_liabilities=1000000,
            ),
            BalanceSheet(
                "DEMO",
                "annual",
                2022,
                total_assets=4500000,
                total_equity=2700000,
                current_assets=1800000,
                current_liabilities=900000,
            ),
            BalanceSheet(
                "DEMO",
                "annual",
                2021,
                total_assets=4000000,
                total_equity=2400000,
                current_assets=1600000,
                current_liabilities=800000,
            ),
        ]

        financial_ratios = [
            FinancialRatios("DEMO", date.today(), roe=15.0, current_ratio=2.0),
            FinancialRatios("DEMO", date.today(), roe=14.0, current_ratio=2.1),
            FinancialRatios("DEMO", date.today(), roe=13.0, current_ratio=2.0),
        ]

        # Calculate quality score
        quality_score, analysis = calculator.calculate_quality_score(
            income_statements, balance_sheets, financial_ratios
        )

        print(f"✅ Quality Score: {quality_score:.2f}/1.0")
        print(f"📝 Interpretation: {analysis['interpretation']}")
        print("🔍 Components:")
        for component, score in analysis["components"].items():
            print(f"   • {component}: {score:.2f}")

        print("💡 Recommendations:")
        for rec in analysis["recommendations"]:
            print(f"   • {rec}")

        return True

    except Exception as e:
        print(f"❌ Error in quality assessment demo: {e}")
        return False


def main():
    """Run all demos"""
    print("🚀 EPV Research Platform Demo")
    print("Demonstrating key features and capabilities\n")

    demos = [
        ("Data Models", demo_data_models),
        ("Cache System", demo_cache_functionality),
        ("Quality Assessment", demo_quality_assessment),
        ("Quick EPV Analysis", demo_quick_analysis),  # This one requires internet
    ]

    results = []

    for name, demo_func in demos:
        try:
            success = demo_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} demo failed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("DEMO SUMMARY")
    print("=" * 50)

    successful = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")

    print(f"\nDemo Results: {successful}/{total} passed")

    if successful == total:
        print("\n🎉 All demos passed! The EPV Research Platform is working correctly.")
    else:
        print(
            f"\n⚠️  {total - successful} demo(s) failed. Some features may not work correctly."
        )

    print("\n📚 Next Steps:")
    print("1. Install all dependencies: pip install -r requirements.txt")
    print("2. Try the command line: python3 src/main.py quick --symbol AAPL")
    print("3. Start the web interface: python3 src/main.py web")
    print("4. Read the documentation in README.md")

    return 0 if successful == total else 1


if __name__ == "__main__":
    exit(main())
