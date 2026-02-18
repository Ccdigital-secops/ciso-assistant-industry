# ✅ Intégration Référentiels Santé/Médical dans CISO Assistant - TERMINÉE

**Date**: 18 février 2026  
**Statut**: ✅ **SUCCÈS COMPLET**

---

## 📋 Résumé de l'intégration

Intégration de 3 nouveaux référentiels sectoriels santé/médical dans CISO Assistant Industry, avec alignement réglementaire MDR UE et FDA, et 4 fichiers de mapping inter-standards.

---

## 🎯 Référentiels créés

### 1. **IEC 81001-5-1** - Cybersécurité des logiciels de santé
- **Fichier**: `backend/library/libraries/iec-81001-5-1.yaml`
- **URN**: `urn:intuitem:risk:framework:iec-81001-5-1`
- **Scope**: Activités de sécurité dans le cycle de vie des logiciels de santé
- **Sections couvertes**:
  - §4 : Exigences générales (système de management, rôles)
  - §5 : Gestion des risques de sécurité (processus, évaluation, maîtrise, résiduel, revue)
  - §6 : Exigences de sécurité (auth, crypto, audit, intégrité, patches, config, SBOM)
  - §7 : Conception et développement sécurisés (architecture, codage, tests, V&V)
  - §8 : Production et post-production (vulnérabilités, incidents, surveillance, fin de vie)
  - **MDR** : Alignement Annexe I GSPR 17 + MDCG 2019-16 (dossier technique)
  - **FDA** : Alignement Cybersecurity Guidance 2023 + QMSR 2026 + SBOM
- **Groupes d'implémentation**: BASIC / ENHANCED
- **Langues**: EN + FR

### 2. **ISO 14971:2019** - Gestion des risques pour dispositifs médicaux
- **Fichier**: `backend/library/libraries/iso-14971-2019.yaml`
- **URN**: `urn:intuitem:risk:framework:iso-14971-2019`
- **Scope**: Application de la gestion des risques aux dispositifs médicaux (dont SaMD)
- **Clauses couvertes**:
  - §4 : Système de gestion des risques (plan, dossier, responsabilités)
  - §5 : Analyse des risques (utilisation prévue, identification dangers, estimation)
  - §6 : Évaluation des risques (critères d'acceptabilité, décision)
  - §7 : Maîtrise des risques (options, mise en œuvre, résiduel, risque/bénéfice)
  - §8 : Évaluation du risque résiduel global + rapport
  - §9 : Activités post-production (collecte info, actions, cybersécurité post-prod)
- **Groupes d'implémentation**: CLASS-I / CLASS-IIa / CLASS-IIb / CLASS-III
- **Langues**: EN + FR

### 3. **IEC 62304:2006+AMD1:2015** - Cycle de vie logiciel médical
- **Fichier**: `backend/library/libraries/iec-62304-2006-amd1-2015.yaml`
- **URN**: `urn:intuitem:risk:framework:iec-62304-2006-amd1-2015`
- **Scope**: Processus du cycle de vie des logiciels de dispositifs médicaux
- **Clauses couvertes**:
  - §4 : Exigences générales (QMS, gestion risques, classification A/B/C)
  - §5 : Processus de développement (planification, exigences, architecture, codage, tests, release)
  - §6 : Maintenance (plan, analyse problèmes, modifications)
  - §7 : Gestion des risques logiciels (analyse, mesures, vérification)
  - §8 : Gestion de configuration (plan, SBOM, contrôle modifications)
  - §9 : Résolution des problèmes (signalement, évaluation, avis de sécurité)
  - **AMD1** : Logiciels existants + SOUP (Software of Unknown Provenance)
- **Groupes d'implémentation**: CLASS-A / CLASS-B / CLASS-C
- **Langues**: EN + FR

---

## 🔗 Mappings créés

| Mapping | Fichier | Description |
|---------|---------|-------------|
| IEC 81001-5-1 ↔ ISO 27001:2022 | `mapping-iec-81001-5-1-to-iso27001-2022.yaml` | Réutilisation preuves ISO 27001 pour cybersécurité santé |
| IEC 81001-5-1 ↔ ISO 14971:2019 | `mapping-iec-81001-5-1-to-iso-14971-2019.yaml` | Intégration cybersécurité + gestion risques médicaux |
| IEC 62304 ↔ IEC 81001-5-1 | `mapping-iec-62304-to-iec-81001-5-1.yaml` | Cycle de vie logiciel + cybersécurité santé |
| IEC 81001-5-1 ↔ NIST SP 800-66 | `mapping-iec-81001-5-1-to-nist-sp-800-66-rev2.yaml` | Alignement HIPAA pour organisations US |

---

## 🔍 Référentiels existants liés dans la bibliothèque

Les référentiels suivants, déjà présents, sont directement liés aux nouveaux frameworks :

| Référentiel existant | Lien avec les nouveaux | Type de lien |
|---|---|---|
| `hds-v2.yaml` | IEC 81001-5-1 | Hébergement données santé FR - complémentaire |
| `clausier-sante-v2.yaml` | ISO 14971 + MDR | Clauses contractuelles santé FR |
| `pgssi-s-1.0.yaml` | IEC 81001-5-1 | Politique générale SI santé (ANS) |
| `gdpr.yaml` | MDR Annexe I + ISO 14971 | Protection données personnelles de santé |
| `iso27001-2022.yaml` | IEC 81001-5-1 (référencé) | SMSI - base de IEC 81001-5-1 |
| `nist-sp-800-66-rev2.yaml` | IEC 81001-5-1 | HIPAA Security Rule (US) |
| `cra-regulation-annexes.yaml` | MDR + IEC 81001-5-1 | Cyber Resilience Act UE |
| `owasp-asvs-5.0.0.yaml` | IEC 62304 §5.5 + IEC 81001-5-1 §7.2 | Sécurité applicative / codage sécurisé |
| `nist-ssdf-1.1.yaml` | IEC 62304 + IEC 81001-5-1 §7 | Secure Software Development Framework |
| `iec-62443.yaml` | IEC 81001-5-1 (systèmes médicaux connectés) | Cybersécurité systèmes industriels/médicaux |

---

## 🏗️ Architecture réglementaire couverte

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISPOSITIF MÉDICAL LOGICIEL                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │  ISO 14971:2019  │    │  IEC 62304:2006  │                    │
│  │  Gestion risques │◄──►│  Cycle de vie   │                     │
│  │  médicaux        │    │  logiciel       │                     │
│  └────────┬────────┘    └────────┬────────┘                     │
│           │                      │                               │
│           └──────────┬───────────┘                              │
│                      ▼                                           │
│           ┌─────────────────────┐                               │
│           │   IEC 81001-5-1     │                               │
│           │   Cybersécurité     │                               │
│           │   logiciels santé   │                               │
│           └──────────┬──────────┘                              │
│                      │                                           │
│         ┌────────────┼────────────┐                            │
│         ▼            ▼            ▼                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ MDR UE   │ │ FDA 2023 │ │ISO 27001 │                       │
│  │ GSPR 17  │ │ QMSR2026 │ │  HIPAA   │                       │
│  │MDCG 2019 │ │  SBOM    │ │ 800-66   │                       │
│  └──────────┘ └──────────┘ └──────────┘                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Déploiement

### Commandes pour charger les nouvelles bibliothèques

```bash
# 1. Stocker les nouvelles bibliothèques
docker exec backend poetry run python manage.py storelibraries

# 2. Activer l'autoload pour les nouveaux frameworks
docker exec backend poetry run python manage.py shell -c \
  "from core.models import StoredLibrary; \
   StoredLibrary.objects.filter(urn__in=[ \
     'urn:intuitem:risk:library:iec-81001-5-1', \
     'urn:intuitem:risk:library:iso-14971-2019', \
     'urn:intuitem:risk:library:iec-62304-2006-amd1-2015' \
   ], autoload=False).update(autoload=True)"

# 3. Charger automatiquement les bibliothèques
docker exec backend poetry run python manage.py autoloadlibraries

# 4. Vérifier le chargement
docker exec backend poetry run python manage.py shell -c \
  "from core.models import Framework; \
   frameworks = Framework.objects.filter(urn__in=[ \
     'urn:intuitem:risk:framework:iec-81001-5-1', \
     'urn:intuitem:risk:framework:iso-14971-2019', \
     'urn:intuitem:risk:framework:iec-62304-2006-amd1-2015' \
   ]); \
   print(f'Frameworks chargés: {frameworks.count()}'); \
   [print(f'  - {f.name}') for f in frameworks]"
```

---

## 🎯 Cas d'usage

### 1. Fabricant de dispositif médical logiciel (SaMD)
- Évaluer la conformité **IEC 62304** pour le cycle de vie logiciel
- Intégrer la gestion des risques **ISO 14971** avec la cybersécurité **IEC 81001-5-1**
- Préparer le dossier technique **MDR UE** (Annexe I GSPR 17)
- Préparer la soumission **FDA** (Cybersecurity Guidance 2023 + QMSR 2026)

### 2. Responsable cybersécurité santé
- Évaluer la posture cybersécurité selon **IEC 81001-5-1**
- Réutiliser les preuves **ISO 27001** via le mapping
- Aligner avec **HIPAA** (NIST SP 800-66) pour les opérations US

### 3. Auditeur / Organisme notifié
- Vérifier la conformité MDR avec les exigences GSPR 17
- Évaluer l'intégration cybersécurité dans le QMS (QMSR 2026)
- Contrôler la cohérence entre ISO 14971 et IEC 81001-5-1

---

## 📝 Notes importantes

### Relation entre les normes
- **IEC 81001-5-1** référence **ISO 14971** pour la gestion des risques de sécurité
- **IEC 62304** est la norme de cycle de vie, **IEC 81001-5-1** ajoute les activités cybersécurité
- **MDR Annexe I GSPR 17** exige l'application de l'état de l'art → IEC 81001-5-1 est la référence
- **FDA QMSR 2026** aligne 21 CFR Part 820 avec **ISO 13485** → compatible avec IEC 62304

### Classification des logiciels
- **IEC 62304** : Classes A, B, C (basées sur le risque de sécurité patient)
- **ISO 14971** : Classes I, IIa, IIb, III (basées sur la classification MDR/FDA)
- **IEC 81001-5-1** : BASIC / ENHANCED (basées sur le niveau de risque cybersécurité)

---

**Auteur**: Assistant IA Antigravity  
**Date de complétion**: 18 février 2026, 22:10 CET
