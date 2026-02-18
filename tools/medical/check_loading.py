"""Script de vérification du chargement des référentiels santé dans CISO Assistant"""
from core.models import Framework, StoredLibrary, RequirementNode

print("=" * 60)
print("VERIFICATION DES REFERENTIELS SANTE")
print("=" * 60)

health_urns = [
    'urn:intuitem:risk:framework:iec-81001-5-1',
    'urn:intuitem:risk:framework:iso-14971-2019',
    'urn:intuitem:risk:framework:iec-62304-2006-amd1-2015',
    'urn:intuitem:risk:framework:iso-13485-2016',
]

print("\n[FRAMEWORKS]")
for urn in health_urns:
    try:
        f = Framework.objects.get(urn=urn)
        req_count = f.requirement_nodes.count()
        assessable = f.requirement_nodes.filter(assessable=True).count()
        print(f"  OK  {f.ref_id:20} | {req_count:3} noeuds | {assessable:3} evaluables")
    except Framework.DoesNotExist:
        print(f"  ERR {urn} -> NON TROUVE")

print("\n[LIBRAIRIES STOCKEES]")
for lib in StoredLibrary.objects.all().order_by('ref_id'):
    if any(k in lib.urn for k in ['81001', '14971', '62304', '13485']):
        print(f"  {'AUTO' if lib.autoload else '    '} {lib.ref_id:45} | autoload={lib.autoload}")

print("\n[TOUS LES FRAMEWORKS DISPONIBLES]")
for f in Framework.objects.all().order_by('ref_id'):
    print(f"  - {f.ref_id}")

print("\n" + "=" * 60)
print("VERIFICATION TERMINEE")
print("=" * 60)
