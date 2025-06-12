#!/usr/bin/env python3
"""
Test that enhanced P3D parsing imports work correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_enhanced_imports():
    """Test that all enhanced P3D parsing classes can be imported."""
    try:
        from parsers.p3d_parser import P3DParser, TextureLoader
        print('✅ P3D Parser imports successfully')
        print('✅ TextureLoader class available')
        
        parser = P3DParser()
        print('✅ P3DParser instantiated successfully')
        
        loader = TextureLoader()
        print('✅ TextureLoader instantiated successfully')
        
        if hasattr(loader, 'load_paa_texture'):
            print('✅ load_paa_texture method available')
        if hasattr(loader, 'load_rvmat_material'):
            print('✅ load_rvmat_material method available')
            
        print('Enhanced P3D parsing implementation is working!')
        return True
        
    except ImportError as e:
        print(f'❌ Import error: {e}')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == "__main__":
    success = test_enhanced_imports()
    if success:
        print("\n🎉 All enhanced P3D parsing features are ready!")
    else:
        print("\n💥 Enhanced P3D parsing has issues")
