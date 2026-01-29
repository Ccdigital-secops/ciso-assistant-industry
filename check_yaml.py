import yaml
import sys

try:
    with open('/code/library/libraries/iec-62443.yaml', 'r') as f:
        data = yaml.safe_load(f)
    print('✓ YAML is valid')
    print(f'URN: {data.get("urn")}')
    print(f'Name: {data.get("name")}')
    print(f'Locale: {data.get("locale")}')
    
    # Check for requirement_nodes in the correct structure
    framework = data.get("objects", {}).get("framework", {})
    req_nodes = framework.get("requirement_nodes", [])
    print(f'Framework URN: {framework.get("urn")}')
    print(f'Number of requirements: {len(req_nodes)}')
    
    if len(req_nodes) > 0:
        print(f'\nFirst 3 requirements:')
        for i, req in enumerate(req_nodes[:3]):
            print(f'  {i+1}. {req.get("ref_id")} - {req.get("name", "N/A")}')
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
