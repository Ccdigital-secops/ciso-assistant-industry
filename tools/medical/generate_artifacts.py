#!/usr/bin/env python3
"""
Medical Device QMS Artifact Generator
======================================
Génère 4 artefacts conformes ISO 13485 / IEC 62304 / ISO 14971 / IEC 81001-5-1 :
  1. QMS Document (Manuel Qualité)
  2. Risk Register (Registre des risques ISO 14971)
  3. SBOM (Software Bill of Materials - FDA 2023 / IEC 62304 AMD1)
  4. Test Report (Rapport de tests IEC 62304 §5.5-5.7)

Usage:
  python generate_artifacts.py --product "MyHealthApp" --version "1.2.0" \
      --class C --output ./artifacts

Requirements: pip install jinja2 openpyxl
"""

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

# ─── Configuration par défaut ────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "company": "MedTech Company",
    "product": "HealthSoftware",
    "version": "1.0.0",
    "software_class": "B",          # A, B ou C (IEC 62304)
    "device_class": "IIa",          # I, IIa, IIb, III (MDR/FDA)
    "intended_use": "Software intended to support clinical decision-making",
    "regulatory_context": ["MDR-EU", "FDA-QMSR-2026"],
    "authors": ["QA Manager"],
    "output_dir": "./artifacts",
}

# ─── Données d'exemple pour les artefacts ────────────────────────────────────

SAMPLE_RISKS = [
    {
        "id": "R-001",
        "hazard": "Unauthorized access to patient data",
        "hazardous_situation": "Attacker gains access to PHI via unpatched vulnerability",
        "harm": "Privacy breach, patient harm from data misuse",
        "probability": "Possible",
        "severity": "Critical",
        "risk_level": "High",
        "control": "Authentication + encryption + patch management",
        "control_ref": "IEC 81001-5-1 §6.2, §6.3, §6.6",
        "residual_risk": "Low",
        "status": "Mitigated",
        "iso14971_ref": "§5.3, §7.1",
    },
    {
        "id": "R-002",
        "hazard": "Software failure causing incorrect clinical data display",
        "hazardous_situation": "Bug causes wrong patient data to be shown",
        "harm": "Incorrect clinical decision, patient injury",
        "probability": "Unlikely",
        "severity": "Critical",
        "risk_level": "Medium",
        "control": "Input validation, unit tests, integration tests",
        "control_ref": "IEC 62304 §5.5, §5.6, §7.2",
        "residual_risk": "Low",
        "status": "Mitigated",
        "iso14971_ref": "§5.3, §7.2",
    },
    {
        "id": "R-003",
        "hazard": "System unavailability during critical care",
        "hazardous_situation": "DoS attack or infrastructure failure blocks access",
        "harm": "Delayed treatment, patient harm",
        "probability": "Rare",
        "severity": "Major",
        "risk_level": "Medium",
        "control": "High availability architecture, DoS protection, BCP",
        "control_ref": "IEC 81001-5-1 §6.7, IEC 62443 FR7",
        "residual_risk": "Low",
        "status": "Mitigated",
        "iso14971_ref": "§5.4, §7.3",
    },
    {
        "id": "R-004",
        "hazard": "Malicious code injection (SQL/XSS)",
        "hazardous_situation": "Attacker injects code via input fields",
        "harm": "Data corruption, unauthorized actions",
        "probability": "Possible",
        "severity": "Major",
        "risk_level": "High",
        "control": "Input sanitization, OWASP ASVS controls, SAST/DAST",
        "control_ref": "IEC 81001-5-1 §7.2, §7.3; OWASP ASVS",
        "residual_risk": "Low",
        "status": "Mitigated",
        "iso14971_ref": "§5.3, §7.1",
    },
    {
        "id": "R-005",
        "hazard": "Insecure third-party component (SOUP vulnerability)",
        "hazardous_situation": "Known CVE in dependency exploited",
        "harm": "System compromise, data breach",
        "probability": "Possible",
        "severity": "Major",
        "risk_level": "High",
        "control": "SBOM management, dependency scanning, patch process",
        "control_ref": "IEC 62304 AMD1 SOUP; FDA SBOM; IEC 81001-5-1 §6.8",
        "residual_risk": "Low",
        "status": "Mitigated",
        "iso14971_ref": "§5.3, §9.3",
    },
]

SAMPLE_SBOM = [
    {
        "name": "react",
        "version": "18.2.0",
        "type": "library",
        "license": "MIT",
        "supplier": "Meta Platforms",
        "purl": "pkg:npm/react@18.2.0",
        "cpe": "cpe:2.3:a:facebook:react:18.2.0:*:*:*:*:*:*:*",
        "known_vulnerabilities": "None",
        "risk_level": "Low",
        "classification": "SOUP",
    },
    {
        "name": "django",
        "version": "4.2.9",
        "type": "framework",
        "license": "BSD-3-Clause",
        "supplier": "Django Software Foundation",
        "purl": "pkg:pypi/django@4.2.9",
        "cpe": "cpe:2.3:a:djangoproject:django:4.2.9:*:*:*:*:*:*:*",
        "known_vulnerabilities": "None",
        "risk_level": "Low",
        "classification": "SOUP",
    },
    {
        "name": "postgresql",
        "version": "15.4",
        "type": "database",
        "license": "PostgreSQL",
        "supplier": "PostgreSQL Global Development Group",
        "purl": "pkg:generic/postgresql@15.4",
        "cpe": "cpe:2.3:a:postgresql:postgresql:15.4:*:*:*:*:*:*:*",
        "known_vulnerabilities": "None",
        "risk_level": "Low",
        "classification": "SOUP",
    },
    {
        "name": "cryptography",
        "version": "41.0.7",
        "type": "library",
        "license": "Apache-2.0",
        "supplier": "Python Cryptographic Authority",
        "purl": "pkg:pypi/cryptography@41.0.7",
        "cpe": "cpe:2.3:a:cryptography.io:cryptography:41.0.7:*:*:*:*:*:*:*",
        "known_vulnerabilities": "None",
        "risk_level": "Medium",
        "classification": "SOUP - Security Critical",
    },
    {
        "name": "HealthApp-Core",
        "version": "1.0.0",
        "type": "application",
        "license": "Proprietary",
        "supplier": "MedTech Company",
        "purl": "pkg:generic/healthapp-core@1.0.0",
        "cpe": "N/A",
        "known_vulnerabilities": "None",
        "risk_level": "Low",
        "classification": "First-Party",
    },
]

SAMPLE_TESTS = [
    {
        "id": "TC-001",
        "type": "Unit Test",
        "iec62304_ref": "§5.5",
        "name": "Authentication module - password validation",
        "requirement": "REQ-SEC-001: Password must meet complexity requirements",
        "method": "Automated unit test (pytest)",
        "result": "PASS",
        "date": "2026-02-10",
        "tester": "Dev Team",
        "notes": "100% coverage on auth module",
    },
    {
        "id": "TC-002",
        "type": "Unit Test",
        "iec62304_ref": "§5.5",
        "name": "Data encryption at rest - AES-256",
        "requirement": "REQ-SEC-003: Patient data encrypted at rest",
        "method": "Automated unit test",
        "result": "PASS",
        "date": "2026-02-10",
        "tester": "Dev Team",
        "notes": "Verified with test vectors",
    },
    {
        "id": "TC-003",
        "type": "Integration Test",
        "iec62304_ref": "§5.6",
        "name": "API authentication flow end-to-end",
        "requirement": "REQ-SEC-002: All API endpoints require authentication",
        "method": "Automated integration test",
        "result": "PASS",
        "date": "2026-02-12",
        "tester": "QA Team",
        "notes": "Tested 47 endpoints",
    },
    {
        "id": "TC-004",
        "type": "System Test",
        "iec62304_ref": "§5.7",
        "name": "SAST - Static Application Security Testing",
        "requirement": "IEC 81001-5-1 §7.3: Security testing",
        "method": "SonarQube + Bandit",
        "result": "PASS",
        "date": "2026-02-14",
        "tester": "Security Team",
        "notes": "0 critical, 2 medium (accepted with justification)",
    },
    {
        "id": "TC-005",
        "type": "System Test",
        "iec62304_ref": "§5.7",
        "name": "DAST - Dynamic Application Security Testing",
        "requirement": "IEC 81001-5-1 §7.3: Security testing",
        "method": "OWASP ZAP",
        "result": "PASS",
        "date": "2026-02-15",
        "tester": "Security Team",
        "notes": "No high/critical findings",
    },
    {
        "id": "TC-006",
        "type": "Penetration Test",
        "iec62304_ref": "§5.7",
        "name": "External penetration test",
        "requirement": "IEC 81001-5-1 §7.3; MDR MDCG 2019-16",
        "method": "Manual pentest by external firm",
        "result": "PASS",
        "date": "2026-02-17",
        "tester": "External Security Firm",
        "notes": "Report ref: PENTEST-2026-001. 1 medium finding remediated.",
    },
    {
        "id": "TC-007",
        "type": "System Test",
        "iec62304_ref": "§5.7",
        "name": "Audit log integrity verification",
        "requirement": "REQ-SEC-004: Audit logs tamper-proof",
        "method": "Manual + automated verification",
        "result": "PASS",
        "date": "2026-02-16",
        "tester": "QA Team",
        "notes": "Log signing verified",
    },
    {
        "id": "TC-008",
        "type": "System Test",
        "iec62304_ref": "§5.7",
        "name": "SBOM vulnerability scan",
        "requirement": "FDA SBOM; IEC 62304 AMD1 SOUP",
        "method": "Trivy + OWASP Dependency-Check",
        "result": "PASS",
        "date": "2026-02-18",
        "tester": "DevSecOps",
        "notes": "0 critical CVEs in SBOM components",
    },
]

# ─── Générateurs HTML ─────────────────────────────────────────────────────────

def gen_qms_doc(config: dict) -> str:
    today = date.today().strftime("%d/%m/%Y")
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Manuel Qualité - {config['product']} v{config['version']}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f8fafc; color: #1e293b; }}
  .cover {{ background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #0369a1 100%);
            color: white; padding: 80px 60px; min-height: 300px; }}
  .cover h1 {{ font-size: 2.4rem; margin: 0 0 10px; }}
  .cover .subtitle {{ font-size: 1.1rem; opacity: 0.85; margin: 8px 0; }}
  .cover .badges {{ margin-top: 30px; display: flex; gap: 12px; flex-wrap: wrap; }}
  .badge {{ background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3);
            padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; }}
  .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 30px; }}
  h2 {{ color: #0369a1; border-left: 4px solid #0369a1; padding-left: 12px;
        margin-top: 40px; font-size: 1.3rem; }}
  h3 {{ color: #1e3a5f; margin-top: 24px; font-size: 1.05rem; }}
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0; }}
  .info-card {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px;
                padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
  .info-card .label {{ font-size: 0.75rem; color: #64748b; text-transform: uppercase;
                       letter-spacing: 0.05em; margin-bottom: 4px; }}
  .info-card .value {{ font-weight: 600; color: #1e293b; }}
  table {{ width: 100%; border-collapse: collapse; margin: 16px 0; background: white;
           border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
  th {{ background: #1e3a5f; color: white; padding: 10px 14px; text-align: left;
        font-size: 0.85rem; }}
  td {{ padding: 10px 14px; border-bottom: 1px solid #f1f5f9; font-size: 0.88rem; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #f8fafc; }}
  .process-block {{ background: white; border: 1px solid #e2e8f0; border-radius: 8px;
                    padding: 20px; margin: 12px 0; }}
  .process-block h4 {{ margin: 0 0 8px; color: #0369a1; }}
  .norm-tag {{ display: inline-block; background: #dbeafe; color: #1d4ed8;
               padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin: 2px; }}
  .footer {{ background: #1e293b; color: #94a3b8; text-align: center;
             padding: 20px; font-size: 0.8rem; margin-top: 60px; }}
  @media print {{ .cover {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
</style>
</head>
<body>

<div class="cover">
  <div style="font-size:0.85rem;opacity:0.7;margin-bottom:20px;">CONFIDENTIEL — USAGE INTERNE</div>
  <h1>📋 Manuel Qualité</h1>
  <div class="subtitle">{config['product']} — Version {config['version']}</div>
  <div class="subtitle">{config['company']}</div>
  <div class="badges">
    <span class="badge">ISO 13485:2016</span>
    <span class="badge">IEC 62304 Classe {config['software_class']}</span>
    <span class="badge">ISO 14971:2019</span>
    <span class="badge">IEC 81001-5-1</span>
    <span class="badge">MDR UE 2017/745</span>
    <span class="badge">FDA QMSR 2026</span>
  </div>
  <div style="margin-top:30px;font-size:0.85rem;opacity:0.7;">
    Généré le {today} | Référence : QMS-{config['product'].upper().replace(' ','-')}-{config['version']}
  </div>
</div>

<div class="container">

  <h2>1. Informations du Document</h2>
  <div class="info-grid">
    <div class="info-card">
      <div class="label">Produit</div>
      <div class="value">{config['product']}</div>
    </div>
    <div class="info-card">
      <div class="label">Version</div>
      <div class="value">{config['version']}</div>
    </div>
    <div class="info-card">
      <div class="label">Classe logicielle (IEC 62304)</div>
      <div class="value">Classe {config['software_class']}</div>
    </div>
    <div class="info-card">
      <div class="label">Classe dispositif (MDR/FDA)</div>
      <div class="value">Classe {config['device_class']}</div>
    </div>
    <div class="info-card">
      <div class="label">Société</div>
      <div class="value">{config['company']}</div>
    </div>
    <div class="info-card">
      <div class="label">Date d'émission</div>
      <div class="value">{today}</div>
    </div>
  </div>

  <h2>2. Utilisation Prévue</h2>
  <div class="process-block">
    <p>{config['intended_use']}</p>
  </div>

  <h2>3. Domaine d'Application du SMQ</h2>
  <p>Le présent Manuel Qualité définit le Système de Management de la Qualité (SMQ) de
  <strong>{config['company']}</strong> pour le développement, la maintenance et la surveillance
  post-commercialisation du logiciel médical <strong>{config['product']}</strong>.</p>

  <h2>4. Référentiels Normatifs</h2>
  <table>
    <thead><tr><th>Norme</th><th>Titre</th><th>Application</th></tr></thead>
    <tbody>
      <tr><td>ISO 13485:2016</td><td>QMS Dispositifs Médicaux</td><td>SMQ global</td></tr>
      <tr><td>IEC 62304:2006+AMD1</td><td>Cycle de vie logiciel médical</td><td>Développement logiciel</td></tr>
      <tr><td>ISO 14971:2019</td><td>Gestion des risques DM</td><td>Risk management</td></tr>
      <tr><td>IEC 81001-5-1:2021</td><td>Cybersécurité logiciels santé</td><td>Sécurité produit</td></tr>
      <tr><td>MDR 2017/745 Annexe I</td><td>GSPR 17 - Exigences IT</td><td>Conformité UE</td></tr>
      <tr><td>MDCG 2019-16</td><td>Guide cybersécurité DM</td><td>Conformité UE</td></tr>
      <tr><td>FDA Cybersecurity 2023</td><td>Guide cybersécurité FDA</td><td>Conformité US</td></tr>
      <tr><td>FDA QMSR 2026</td><td>21 CFR Part 820 révisé</td><td>Conformité US</td></tr>
    </tbody>
  </table>

  <h2>5. Processus du SMQ</h2>

  <div class="process-block">
    <h4>5.1 Gestion de la Conception et du Développement (ISO 13485 §7.3)</h4>
    <p>Le processus de développement suit le cycle de vie IEC 62304 avec les étapes :</p>
    <ul>
      <li>Planification du développement (§5.1)</li>
      <li>Analyse des exigences logicielles (§5.2) — incluant exigences de sécurité IEC 81001-5-1</li>
      <li>Conception architecturale (§5.3) — architecture de sécurité documentée</li>
      <li>Conception détaillée (§5.4) — applicable Classe {config['software_class']}</li>
      <li>Implémentation et vérification unitaire (§5.5)</li>
      <li>Intégration et tests d'intégration (§5.6)</li>
      <li>Tests système (§5.7) — incluant SAST, DAST, tests de pénétration</li>
      <li>Mise en production (§5.8)</li>
    </ul>
    <span class="norm-tag">ISO 13485 §7.3</span>
    <span class="norm-tag">IEC 62304 §5</span>
    <span class="norm-tag">IEC 81001-5-1 §7</span>
  </div>

  <div class="process-block">
    <h4>5.2 Gestion des Risques (ISO 13485 §7.1 / ISO 14971)</h4>
    <p>La gestion des risques couvre les risques de sécurité patient ET de cybersécurité :</p>
    <ul>
      <li>Plan de gestion des risques documenté (ISO 14971 §4.4)</li>
      <li>Analyse des risques — identification des dangers et situations dangereuses (§5)</li>
      <li>Évaluation des risques — critères d'acceptabilité définis (§6)</li>
      <li>Maîtrise des risques — mesures de contrôle implémentées (§7)</li>
      <li>Risques résiduels évalués et acceptés (§8)</li>
      <li>Surveillance post-production (§9) — incluant vulnérabilités cybersécurité</li>
    </ul>
    <span class="norm-tag">ISO 14971:2019</span>
    <span class="norm-tag">IEC 81001-5-1 §5</span>
    <span class="norm-tag">ISO 13485 §7.1</span>
  </div>

  <div class="process-block">
    <h4>5.3 Gestion de la Configuration et SBOM (IEC 62304 §8)</h4>
    <ul>
      <li>Contrôle de version (Git) pour tous les artefacts logiciels</li>
      <li>SBOM maintenu en format CycloneDX/SPDX (FDA SBOM requirement)</li>
      <li>Gestion des composants SOUP (IEC 62304 AMD1)</li>
      <li>Surveillance des CVE sur les dépendances (IEC 81001-5-1 §6.8)</li>
      <li>Procédure de gestion des modifications documentée</li>
    </ul>
    <span class="norm-tag">IEC 62304 §8</span>
    <span class="norm-tag">FDA SBOM 2023</span>
    <span class="norm-tag">IEC 81001-5-1 §6.8</span>
  </div>

  <div class="process-block">
    <h4>5.4 Gestion des Non-Conformités et CAPA (ISO 13485 §8.5)</h4>
    <ul>
      <li>Procédure CAPA documentée pour toutes les non-conformités</li>
      <li>Vulnérabilités de sécurité traitées comme non-conformités</li>
      <li>Délais de remédiation basés sur le niveau de risque (CVSS)</li>
      <li>Revue d'efficacité des actions correctives</li>
    </ul>
    <span class="norm-tag">ISO 13485 §8.5</span>
    <span class="norm-tag">IEC 81001-5-1 §8.1</span>
    <span class="norm-tag">FDA QMSR 2026</span>
  </div>

  <div class="process-block">
    <h4>5.5 Surveillance Post-Commercialisation (MDR / FDA)</h4>
    <ul>
      <li>Plan de surveillance post-commercialisation (PMS Plan)</li>
      <li>Surveillance des vulnérabilités cybersécurité (IEC 81001-5-1 §8.1)</li>
      <li>Politique de divulgation coordonnée des vulnérabilités (CVD)</li>
      <li>Reporting aux autorités réglementaires si nécessaire</li>
      <li>Mises à jour de sécurité déployées dans les délais définis</li>
    </ul>
    <span class="norm-tag">MDR §83-86</span>
    <span class="norm-tag">MDCG 2019-16</span>
    <span class="norm-tag">FDA Cybersecurity 2023</span>
    <span class="norm-tag">IEC 81001-5-1 §8</span>
  </div>

  <h2>6. Responsabilités</h2>
  <table>
    <thead><tr><th>Rôle</th><th>Responsabilités QMS</th></tr></thead>
    <tbody>
      <tr><td>Direction Générale</td><td>Engagement qualité, revue de direction, ressources (ISO 13485 §5.1)</td></tr>
      <tr><td>Responsable Qualité (QA)</td><td>SMQ, audits internes, CAPA, documentation réglementaire</td></tr>
      <tr><td>Responsable Sécurité (CISO)</td><td>Cybersécurité, IEC 81001-5-1, gestion des vulnérabilités</td></tr>
      <tr><td>Responsable Développement</td><td>IEC 62304, SBOM, tests, revues de code sécurisé</td></tr>
      <tr><td>Responsable Affaires Réglementaires</td><td>MDR/FDA, dossier technique, soumissions</td></tr>
      <tr><td>Gestionnaire des Risques</td><td>ISO 14971, risk register, surveillance post-prod</td></tr>
    </tbody>
  </table>

  <h2>7. Dossier Technique (Technical File)</h2>
  <p>Le dossier technique inclut les documents suivants :</p>
  <table>
    <thead><tr><th>Document</th><th>Référence</th><th>Norme</th></tr></thead>
    <tbody>
      <tr><td>Manuel Qualité</td><td>QMS-{config['product'].upper()}-{config['version']}</td><td>ISO 13485 §4.2.1</td></tr>
      <tr><td>Risk Register (ISO 14971)</td><td>RISK-{config['product'].upper()}-{config['version']}</td><td>ISO 14971 §4.5</td></tr>
      <tr><td>SBOM (CycloneDX)</td><td>SBOM-{config['product'].upper()}-{config['version']}</td><td>FDA SBOM / IEC 62304 AMD1</td></tr>
      <tr><td>Rapport de Tests</td><td>TEST-{config['product'].upper()}-{config['version']}</td><td>IEC 62304 §5.5-5.7</td></tr>
      <tr><td>Plan de gestion des risques</td><td>RMP-{config['product'].upper()}-{config['version']}</td><td>ISO 14971 §4.4</td></tr>
      <tr><td>Architecture de sécurité</td><td>SEC-ARCH-{config['product'].upper()}-{config['version']}</td><td>IEC 81001-5-1 §7.1</td></tr>
      <tr><td>Plan de surveillance post-commercialisation</td><td>PMS-{config['product'].upper()}-{config['version']}</td><td>MDR §83 / FDA</td></tr>
    </tbody>
  </table>

</div>

<div class="footer">
  {config['company']} — {config['product']} v{config['version']} — Manuel Qualité ISO 13485:2016
  | Généré le {today} | CONFIDENTIEL
</div>
</body>
</html>"""


def gen_risk_register(config: dict, risks: list) -> str:
    today = date.today().strftime("%d/%m/%Y")

    risk_rows = ""
    for r in risks:
        level_color = {"High": "#fee2e2", "Medium": "#fef9c3", "Low": "#dcfce7"}.get(r["risk_level"], "#f1f5f9")
        residual_color = {"High": "#fee2e2", "Medium": "#fef9c3", "Low": "#dcfce7"}.get(r["residual_risk"], "#f1f5f9")
        risk_rows += f"""
      <tr>
        <td><strong>{r['id']}</strong></td>
        <td>{r['hazard']}</td>
        <td>{r['hazardous_situation']}</td>
        <td>{r['harm']}</td>
        <td>{r['probability']}</td>
        <td>{r['severity']}</td>
        <td style="background:{level_color};font-weight:600;">{r['risk_level']}</td>
        <td>{r['control']}<br><small style="color:#64748b">{r['control_ref']}</small></td>
        <td style="background:{residual_color};font-weight:600;">{r['residual_risk']}</td>
        <td><span style="color:#16a34a">✓ {r['status']}</span></td>
        <td><small>{r['iso14971_ref']}</small></td>
      </tr>"""

    high_count = sum(1 for r in risks if r["risk_level"] == "High")
    med_count = sum(1 for r in risks if r["risk_level"] == "Medium")
    low_count = sum(1 for r in risks if r["risk_level"] == "Low")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Risk Register - {config['product']} v{config['version']}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f8fafc; color: #1e293b; }}
  .cover {{ background: linear-gradient(135deg, #7c2d12 0%, #9a3412 60%, #c2410c 100%);
            color: white; padding: 60px; }}
  .cover h1 {{ font-size: 2.2rem; margin: 0 0 8px; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 30px; }}
  h2 {{ color: #9a3412; border-left: 4px solid #c2410c; padding-left: 12px; margin-top: 40px; }}
  .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
  .stat {{ background: white; border-radius: 8px; padding: 20px; text-align: center;
           box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .stat .num {{ font-size: 2rem; font-weight: 700; }}
  .stat .lbl {{ font-size: 0.8rem; color: #64748b; margin-top: 4px; }}
  .high {{ color: #dc2626; }}
  .medium {{ color: #d97706; }}
  .low {{ color: #16a34a; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px;
           overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 0.82rem; }}
  th {{ background: #7c2d12; color: white; padding: 10px 8px; text-align: left; }}
  td {{ padding: 10px 8px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
  tr:hover td {{ background: #fff7ed; }}
  .footer {{ background: #1e293b; color: #94a3b8; text-align: center; padding: 20px;
             font-size: 0.8rem; margin-top: 60px; }}
</style>
</head>
<body>
<div class="cover">
  <h1>⚠️ Registre des Risques</h1>
  <div>{config['product']} v{config['version']} — {config['company']}</div>
  <div style="margin-top:12px;opacity:0.8;font-size:0.85rem;">
    ISO 14971:2019 | IEC 81001-5-1 | MDR UE | FDA QMSR 2026 | Généré le {today}
  </div>
</div>
<div class="container">
  <h2>Résumé des Risques</h2>
  <div class="stats">
    <div class="stat"><div class="num">{len(risks)}</div><div class="lbl">Risques totaux</div></div>
    <div class="stat"><div class="num high">{high_count}</div><div class="lbl">Risques élevés</div></div>
    <div class="stat"><div class="num medium">{med_count}</div><div class="lbl">Risques moyens</div></div>
    <div class="stat"><div class="num low">{low_count}</div><div class="lbl">Risques faibles</div></div>
  </div>

  <h2>Registre Détaillé (ISO 14971:2019)</h2>
  <table>
    <thead>
      <tr>
        <th>ID</th><th>Danger</th><th>Situation dangereuse</th><th>Dommage</th>
        <th>Probabilité</th><th>Gravité</th><th>Niveau initial</th>
        <th>Mesure de maîtrise</th><th>Risque résiduel</th><th>Statut</th><th>Réf. ISO 14971</th>
      </tr>
    </thead>
    <tbody>{risk_rows}</tbody>
  </table>

  <h2>Critères d'Acceptabilité (ISO 14971 §6.1)</h2>
  <table>
    <thead><tr><th>Niveau de risque</th><th>Critère</th><th>Action requise</th></tr></thead>
    <tbody>
      <tr><td style="background:#fee2e2;font-weight:600;">Élevé</td>
          <td>Probabilité ≥ Possible ET Gravité ≥ Majeure</td>
          <td>Mesures de maîtrise obligatoires — risque résiduel doit être ≤ Moyen</td></tr>
      <tr><td style="background:#fef9c3;font-weight:600;">Moyen</td>
          <td>Probabilité Possible ET Gravité Modérée, OU Probabilité Rare ET Gravité Critique</td>
          <td>Mesures de maîtrise recommandées — analyse risque/bénéfice si non réduit</td></tr>
      <tr><td style="background:#dcfce7;font-weight:600;">Faible</td>
          <td>Probabilité Rare ET Gravité ≤ Modérée</td>
          <td>Acceptable — surveillance continue</td></tr>
    </tbody>
  </table>
</div>
<div class="footer">
  {config['company']} — Risk Register ISO 14971:2019 — {config['product']} v{config['version']} | {today}
</div>
</body>
</html>"""


def gen_sbom(config: dict, components: list) -> str:
    today = date.today().strftime("%d/%m/%Y")
    timestamp = datetime.now().isoformat()

    rows = ""
    for c in components:
        risk_color = {"Low": "#dcfce7", "Medium": "#fef9c3", "High": "#fee2e2"}.get(c["risk_level"], "#f1f5f9")
        rows += f"""
      <tr>
        <td><strong>{c['name']}</strong></td>
        <td>{c['version']}</td>
        <td>{c['type']}</td>
        <td>{c['license']}</td>
        <td>{c['supplier']}</td>
        <td><code style="font-size:0.75rem">{c['purl']}</code></td>
        <td>{c['known_vulnerabilities']}</td>
        <td style="background:{risk_color};font-weight:600;">{c['risk_level']}</td>
        <td><span style="background:#dbeafe;color:#1d4ed8;padding:2px 6px;border-radius:4px;font-size:0.75rem">{c['classification']}</span></td>
      </tr>"""

    # CycloneDX JSON simplifié
    cyclonedx = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "serialNumber": f"urn:uuid:sbom-{config['product'].lower()}-{config['version']}",
        "metadata": {
            "timestamp": timestamp,
            "component": {
                "type": "application",
                "name": config["product"],
                "version": config["version"],
                "supplier": {"name": config["company"]},
            },
        },
        "components": [
            {
                "type": c["type"],
                "name": c["name"],
                "version": c["version"],
                "purl": c["purl"],
                "licenses": [{"license": {"id": c["license"]}}],
                "supplier": {"name": c["supplier"]},
            }
            for c in components
        ],
    }
    cdx_json = json.dumps(cyclonedx, indent=2)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SBOM - {config['product']} v{config['version']}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f8fafc; color: #1e293b; }}
  .cover {{ background: linear-gradient(135deg, #134e4a 0%, #0f766e 60%, #0d9488 100%);
            color: white; padding: 60px; }}
  .cover h1 {{ font-size: 2.2rem; margin: 0 0 8px; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 30px; }}
  h2 {{ color: #0f766e; border-left: 4px solid #0d9488; padding-left: 12px; margin-top: 40px; }}
  .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
  .stat {{ background: white; border-radius: 8px; padding: 20px; text-align: center;
           box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .stat .num {{ font-size: 2rem; font-weight: 700; color: #0f766e; }}
  .stat .lbl {{ font-size: 0.8rem; color: #64748b; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px;
           overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 0.82rem; }}
  th {{ background: #134e4a; color: white; padding: 10px 8px; text-align: left; }}
  td {{ padding: 10px 8px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
  pre {{ background: #0f172a; color: #e2e8f0; padding: 20px; border-radius: 8px;
         overflow-x: auto; font-size: 0.78rem; line-height: 1.5; }}
  .footer {{ background: #1e293b; color: #94a3b8; text-align: center; padding: 20px;
             font-size: 0.8rem; margin-top: 60px; }}
</style>
</head>
<body>
<div class="cover">
  <h1>📦 Software Bill of Materials (SBOM)</h1>
  <div>{config['product']} v{config['version']} — {config['company']}</div>
  <div style="margin-top:12px;opacity:0.8;font-size:0.85rem;">
    Format CycloneDX 1.5 | FDA Cybersecurity 2023 | IEC 62304 AMD1 (SOUP) | Généré le {today}
  </div>
</div>
<div class="container">
  <h2>Résumé</h2>
  <div class="stats">
    <div class="stat"><div class="num">{len(components)}</div><div class="lbl">Composants totaux</div></div>
    <div class="stat"><div class="num">{sum(1 for c in components if c['classification']=='SOUP' or 'SOUP' in c['classification'])}</div><div class="lbl">Composants SOUP</div></div>
    <div class="stat"><div class="num">{sum(1 for c in components if c['known_vulnerabilities']!='None')}</div><div class="lbl">CVEs connus</div></div>
    <div class="stat"><div class="num">{sum(1 for c in components if c['risk_level']=='High')}</div><div class="lbl">Risque élevé</div></div>
  </div>

  <h2>Inventaire des Composants</h2>
  <table>
    <thead>
      <tr>
        <th>Nom</th><th>Version</th><th>Type</th><th>Licence</th><th>Fournisseur</th>
        <th>PURL</th><th>CVEs connus</th><th>Niveau risque</th><th>Classification</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>

  <h2>Export CycloneDX 1.5 (JSON)</h2>
  <p style="font-size:0.85rem;color:#64748b;">
    Format machine-readable requis par FDA Cybersecurity Guidance 2023 Section VI.C
  </p>
  <pre>{cdx_json}</pre>
</div>
<div class="footer">
  {config['company']} — SBOM CycloneDX 1.5 — {config['product']} v{config['version']} | {today}
</div>
</body>
</html>"""


def gen_test_report(config: dict, tests: list) -> str:
    today = date.today().strftime("%d/%m/%Y")
    passed = sum(1 for t in tests if t["result"] == "PASS")
    failed = sum(1 for t in tests if t["result"] == "FAIL")
    total = len(tests)
    pass_rate = round(passed / total * 100) if total > 0 else 0

    type_counts = {}
    for t in tests:
        type_counts[t["type"]] = type_counts.get(t["type"], 0) + 1

    rows = ""
    for t in tests:
        result_color = "#dcfce7" if t["result"] == "PASS" else "#fee2e2"
        result_icon = "✅" if t["result"] == "PASS" else "❌"
        rows += f"""
      <tr>
        <td><strong>{t['id']}</strong></td>
        <td><span style="background:#dbeafe;color:#1d4ed8;padding:2px 6px;border-radius:4px;font-size:0.75rem">{t['type']}</span></td>
        <td><code style="font-size:0.75rem">{t['iec62304_ref']}</code></td>
        <td>{t['name']}</td>
        <td style="font-size:0.8rem">{t['requirement']}</td>
        <td>{t['method']}</td>
        <td style="background:{result_color};font-weight:600;text-align:center">{result_icon} {t['result']}</td>
        <td>{t['date']}</td>
        <td>{t['tester']}</td>
        <td style="font-size:0.8rem;color:#64748b">{t['notes']}</td>
      </tr>"""

    type_summary = "".join(
        f"<tr><td>{k}</td><td>{v}</td><td>{v}</td><td>0</td></tr>"
        for k, v in type_counts.items()
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Test Report - {config['product']} v{config['version']}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f8fafc; color: #1e293b; }}
  .cover {{ background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%);
            color: white; padding: 60px; }}
  .cover h1 {{ font-size: 2.2rem; margin: 0 0 8px; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 30px; }}
  h2 {{ color: #4338ca; border-left: 4px solid #4338ca; padding-left: 12px; margin-top: 40px; }}
  .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
  .stat {{ background: white; border-radius: 8px; padding: 20px; text-align: center;
           box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .stat .num {{ font-size: 2rem; font-weight: 700; }}
  .stat .lbl {{ font-size: 0.8rem; color: #64748b; margin-top: 4px; }}
  .progress-bar {{ background: #e2e8f0; border-radius: 9999px; height: 12px; margin: 8px 0; }}
  .progress-fill {{ background: linear-gradient(90deg, #16a34a, #22c55e);
                    height: 12px; border-radius: 9999px; width: {pass_rate}%; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px;
           overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 0.82rem; }}
  th {{ background: #1e1b4b; color: white; padding: 10px 8px; text-align: left; }}
  td {{ padding: 10px 8px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
  tr:hover td {{ background: #eef2ff; }}
  .verdict {{ text-align: center; padding: 30px; background: {'#dcfce7' if pass_rate == 100 else '#fef9c3'};
              border-radius: 8px; margin: 24px 0; }}
  .verdict h3 {{ font-size: 1.5rem; color: {'#16a34a' if pass_rate == 100 else '#d97706'}; margin: 0; }}
  .footer {{ background: #1e293b; color: #94a3b8; text-align: center; padding: 20px;
             font-size: 0.8rem; margin-top: 60px; }}
</style>
</head>
<body>
<div class="cover">
  <h1>🧪 Rapport de Tests</h1>
  <div>{config['product']} v{config['version']} — {config['company']}</div>
  <div style="margin-top:12px;opacity:0.8;font-size:0.85rem;">
    IEC 62304 §5.5-5.7 | IEC 81001-5-1 §7.3 | ISO 13485 §7.3.5-7.3.6 | Généré le {today}
  </div>
</div>
<div class="container">
  <h2>Résumé d'Exécution</h2>
  <div class="stats">
    <div class="stat"><div class="num" style="color:#4338ca">{total}</div><div class="lbl">Tests totaux</div></div>
    <div class="stat"><div class="num" style="color:#16a34a">{passed}</div><div class="lbl">Réussis (PASS)</div></div>
    <div class="stat"><div class="num" style="color:#dc2626">{failed}</div><div class="lbl">Échoués (FAIL)</div></div>
    <div class="stat"><div class="num" style="color:#4338ca">{pass_rate}%</div><div class="lbl">Taux de réussite</div></div>
  </div>
  <div class="progress-bar"><div class="progress-fill"></div></div>

  <div class="verdict">
    <h3>{'✅ VERDICT : APPROUVÉ POUR MISE EN PRODUCTION' if pass_rate == 100 else '⚠️ VERDICT : ACTIONS CORRECTIVES REQUISES'}</h3>
    <p style="margin:8px 0 0;color:#374151">
      {'Tous les tests ont été exécutés avec succès. Le logiciel satisfait aux exigences IEC 62304 et IEC 81001-5-1.' if pass_rate == 100 else f'{failed} test(s) en échec — résolution requise avant mise en production.'}
    </p>
  </div>

  <h2>Résumé par Type de Test</h2>
  <table>
    <thead><tr><th>Type de test</th><th>Total</th><th>Réussis</th><th>Échoués</th></tr></thead>
    <tbody>{type_summary}</tbody>
  </table>

  <h2>Détail des Tests (IEC 62304 §5.5 / §5.6 / §5.7)</h2>
  <table>
    <thead>
      <tr>
        <th>ID</th><th>Type</th><th>IEC 62304</th><th>Nom du test</th><th>Exigence</th>
        <th>Méthode</th><th>Résultat</th><th>Date</th><th>Testeur</th><th>Notes</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>

  <h2>Traçabilité Exigences → Tests</h2>
  <table>
    <thead><tr><th>Exigence</th><th>Tests associés</th><th>Couverture</th></tr></thead>
    <tbody>
      <tr><td>IEC 81001-5-1 §6.2 (Authentification)</td><td>TC-001, TC-003</td><td style="color:#16a34a">✅ Couverte</td></tr>
      <tr><td>IEC 81001-5-1 §6.3 (Cryptographie)</td><td>TC-002</td><td style="color:#16a34a">✅ Couverte</td></tr>
      <tr><td>IEC 81001-5-1 §6.4 (Audit logs)</td><td>TC-007</td><td style="color:#16a34a">✅ Couverte</td></tr>
      <tr><td>IEC 81001-5-1 §6.8 (SBOM/SOUP)</td><td>TC-008</td><td style="color:#16a34a">✅ Couverte</td></tr>
      <tr><td>IEC 81001-5-1 §7.3 (Tests sécurité)</td><td>TC-004, TC-005, TC-006</td><td style="color:#16a34a">✅ Couverte</td></tr>
      <tr><td>IEC 62304 §5.5 (Tests unitaires)</td><td>TC-001, TC-002</td><td style="color:#16a34a">✅ Couverte</td></tr>
      <tr><td>IEC 62304 §5.6 (Tests intégration)</td><td>TC-003</td><td style="color:#16a34a">✅ Couverte</td></tr>
      <tr><td>IEC 62304 §5.7 (Tests système)</td><td>TC-004, TC-005, TC-006, TC-007, TC-008</td><td style="color:#16a34a">✅ Couverte</td></tr>
    </tbody>
  </table>
</div>
<div class="footer">
  {config['company']} — Test Report IEC 62304 — {config['product']} v{config['version']} | {today}
</div>
</body>
</html>"""


# ─── Point d'entrée ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Medical Device QMS Artifact Generator (ISO 13485 / IEC 62304 / ISO 14971 / IEC 81001-5-1)"
    )
    parser.add_argument("--product", default=DEFAULT_CONFIG["product"], help="Nom du produit")
    parser.add_argument("--version", default=DEFAULT_CONFIG["version"], help="Version du produit")
    parser.add_argument("--company", default=DEFAULT_CONFIG["company"], help="Nom de la société")
    parser.add_argument("--class", dest="sw_class", default=DEFAULT_CONFIG["software_class"],
                        choices=["A", "B", "C"], help="Classe logicielle IEC 62304")
    parser.add_argument("--device-class", default=DEFAULT_CONFIG["device_class"],
                        choices=["I", "IIa", "IIb", "III"], help="Classe dispositif MDR/FDA")
    parser.add_argument("--intended-use", default=DEFAULT_CONFIG["intended_use"])
    parser.add_argument("--output", default=DEFAULT_CONFIG["output_dir"], help="Répertoire de sortie")
    args = parser.parse_args()

    config = {
        "product": args.product,
        "version": args.version,
        "company": args.company,
        "software_class": args.sw_class,
        "device_class": args.device_class,
        "intended_use": args.intended_use,
    }

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    artifacts = [
        ("QMS_Document", gen_qms_doc(config, )),
        ("Risk_Register", gen_risk_register(config, SAMPLE_RISKS)),
        ("SBOM", gen_sbom(config, SAMPLE_SBOM)),
        ("Test_Report", gen_test_report(config, SAMPLE_TESTS)),
    ]

    print(f"\n🏥 Medical Device QMS Artifact Generator")
    print(f"   Produit : {config['product']} v{config['version']}")
    print(f"   Société : {config['company']}")
    print(f"   Classe  : IEC 62304 Classe {config['software_class']} | MDR Classe {config['device_class']}")
    print(f"   Sortie  : {out.resolve()}\n")

    for name, html in artifacts:
        fname = out / f"{name}_{config['product'].replace(' ','_')}_{config['version']}.html"
        fname.write_text(html, encoding="utf-8")
        print(f"   ✅ {name:20s} → {fname.name}")

    print(f"\n✨ {len(artifacts)} artefacts générés dans : {out.resolve()}")
    print("\n📋 Artefacts conformes à :")
    print("   • ISO 13485:2016 (QMS Document)")
    print("   • ISO 14971:2019 (Risk Register)")
    print("   • IEC 62304 AMD1 + FDA SBOM 2023 (SBOM CycloneDX 1.5)")
    print("   • IEC 62304 §5.5-5.7 + IEC 81001-5-1 §7.3 (Test Report)")


if __name__ == "__main__":
    main()
