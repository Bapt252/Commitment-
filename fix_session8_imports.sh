#!/bin/bash
# Fix local import paths

echo "Fixing API import paths for Session 8..."

# Modify user_profile_api.py to handle both import scenarios for backward compatibility
cat > fix_api_imports.py << 'EOF'
#!/usr/bin/env python3

import os
import re

API_FILE = 'api/user_profile_api.py'

# Read the file
with open(API_FILE, 'r') as file:
    content = file.read()

# Check if import paths need to be fixed
if 'from analysis_session8.' in content:
    print("Found analysis_session8 imports, fixing them...")
    
    # Replace the imports
    fixed_content = re.sub(
        r'from analysis_session8\.(\w+) import (\w+)',
        r'try:\n    from analysis.\1 import \2\nexcept ImportError:\n    try:\n        from analysis_session8.\1 import \2\n    except ImportError:\n        raise ImportError("Could not import \2 from analysis.\1 or analysis_session8.\1")',
        content
    )
    
    # Write back to the file
    with open(API_FILE, 'w') as file:
        file.write(fixed_content)
    
    print("✅ Fixed imports in api/user_profile_api.py to handle both module paths")
else:
    # Add fallback code for compatibility
    lines = content.split('\n')
    import_section = False
    import_section_end = 0
    
    # Find the import section
    for i, line in enumerate(lines):
        if line.startswith('# Import our analysis modules'):
            import_section = True
            continue
        if import_section and line.strip() == '':
            import_section_end = i
            break
    
    if import_section_end > 0:
        # Add compatibility code after the import section
        compatibility_code = '''
# Add compatibility layer for different module structures
try:
    # Verify imports work
    BehavioralAnalyzer
    PatternDetector
    PreferenceScorer
except NameError:
    # If import failed, try alternative path
    try:
        from analysis_session8.behavioral_analysis import BehavioralAnalyzer
        from analysis_session8.pattern_detection import PatternDetector
        from analysis_session8.preference_scoring import PreferenceScorer
        print("Using analysis_session8 modules")
    except ImportError:
        print("ERROR: Required analysis modules not found in either 'analysis' or 'analysis_session8' packages")
'''
        lines.insert(import_section_end, compatibility_code)
        
        # Write back to the file
        with open(API_FILE, 'w') as file:
            file.write('\n'.join(lines))
        
        print("✅ Added import compatibility layer to api/user_profile_api.py")
    else:
        print("⚠️ Could not find import section in api/user_profile_api.py")
        print("The file structure may have changed. Please fix imports manually.")

print("\nAlternative option: Create symlinks between directories")
print("This would ensure either import path works:\n")
print("  ln -s analysis analysis_session8")
print("\nOr make sure your sessions modules are in the right place:")
print("  mkdir -p analysis_session8")
print("  cp analysis/behavioral_analysis.py analysis_session8/")
print("  cp analysis/pattern_detection.py analysis_session8/")
print("  cp analysis/preference_scoring.py analysis_session8/")
EOF

# Make it executable
chmod +x fix_api_imports.py

# Run it
python3 fix_api_imports.py

echo ""
echo "Fixed API import paths. Now try starting the service again:"
echo "  ./scripts/start_profile_api.sh"
echo ""
echo "If you still have problems, check if the analysis_session8 directory exists"
echo "and contains the required modules."
