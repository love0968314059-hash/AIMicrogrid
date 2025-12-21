"""
Test script for Microgrid Digital Twin System
"""
import sys
from predictors import PredictionSystem
from digital_twin import DigitalTwin
from nlp_interface import NLPInterface

def test_predictors():
    """Test prediction system"""
    print("Testing Prediction System...")
    predictor = PredictionSystem()
    
    # Test single prediction
    pred = predictor.predict(12, day_of_year=100, day_of_week=1)
    print(f"  PV Power: {pred['pv_power']:.2f} kW")
    print(f"  Wind Power: {pred['wind_power']:.2f} kW")
    print(f"  Load: {pred['load']:.2f} kW")
    print(f"  Price: ${pred['price']:.3f}/kWh")
    print("  ✓ Prediction system working")
    
    return True

def test_digital_twin():
    """Test digital twin"""
    print("\nTesting Digital Twin...")
    dt = DigitalTwin()
    
    # Test initialization
    print("  Initializing...")
    dt.initialize()
    
    # Test step
    result = dt.step()
    print(f"  Step result: Battery SOC = {result['battery_soc']*100:.1f}%")
    print(f"  Cost: ${result['cost']:.2f}")
    print("  ✓ Digital Twin working")
    
    return True

def test_nlp():
    """Test NLP interface"""
    print("\nTesting NLP Interface...")
    dt = DigitalTwin()
    dt.initialize()
    nlp = NLPInterface(dt)
    
    # Test queries
    queries = [
        "系统状态如何？",
        "电池电量多少？",
        "当前发电情况？"
    ]
    
    for query in queries:
        response = nlp.process_query(query)
        print(f"  Q: {query}")
        print(f"  A: {response[:50]}...")
    
    print("  ✓ NLP Interface working")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Microgrid Digital Twin System - Test Suite")
    print("=" * 60)
    
    try:
        test_predictors()
        test_digital_twin()
        test_nlp()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
