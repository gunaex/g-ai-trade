"""
Quick diagnostic script to test Advanced AI module loading
Run with: .venv311\Scripts\python.exe test_advanced_ai.py
"""
import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
print()

print("Testing imports...")
try:
    import pandas as pd
    print(f"✓ pandas {pd.__version__}")
except Exception as e:
    print(f"✗ pandas: {e}")

try:
    import numpy as np
    print(f"✓ numpy {np.__version__}")
except Exception as e:
    print(f"✗ numpy: {e}")

try:
    import ta
    print(f"✓ ta (technical analysis)")
except Exception as e:
    print(f"✗ ta: {e}")

try:
    import sklearn
    print(f"✓ sklearn {sklearn.__version__}")
except Exception as e:
    print(f"✗ sklearn: {e}")

try:
    from textblob import TextBlob
    print(f"✓ textblob")
except Exception as e:
    print(f"✗ textblob: {e}")

try:
    import ccxt
    print(f"✓ ccxt {ccxt.__version__}")
except Exception as e:
    print(f"✗ ccxt: {e}")

print()
print("Testing Advanced AI module...")
try:
    from app.ai.advanced_modules import AdvancedAITradingEngine
    print("✓ AdvancedAITradingEngine imported successfully")
    
    engine = AdvancedAITradingEngine()
    print("✓ Engine initialized successfully")
    
    # Test with dummy data
    import pandas as pd
    import numpy as np
    
    # Create dummy OHLCV data
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(40000, 41000, 200),
        'high': np.random.uniform(40500, 41500, 200),
        'low': np.random.uniform(39500, 40500, 200),
        'close': np.random.uniform(40000, 41000, 200),
        'volume': np.random.uniform(100, 1000, 200)
    })
    
    print("\n✓ Created dummy OHLCV data")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    
    # Run analysis
    print("\nRunning analysis...")
    result = engine.analyze('BTCUSDT', df, None)
    
    print("\n✓ Analysis completed successfully!")
    print(f"  Action: {result.get('action')}")
    print(f"  Confidence: {result.get('confidence')}")
    print(f"  Has modules: {'modules' in result}")
    
    if 'modules' in result:
        modules = result['modules']
        print(f"  - Regime: {modules.get('regime', {}).get('regime')}")
        print(f"  - Sentiment: {modules.get('sentiment', {}).get('interpretation')}")
        print(f"  - Risk levels: {modules.get('risk_levels', {}).get('atr')}")
        print(f"  - Reversal: {modules.get('reversal', {}).get('confidence')}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Diagnostic complete!")
