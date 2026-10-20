# Privacy Caption Generation Project — Plan & Status

## Overview

This project implements the framework described in *"Creating Consistent Privacy Notices by Translating Code Segments into Privacy Captions"* (Jain, 2022). The goal is to analyze Android application source code, identify code segments that access personal information, classify their privacy behavior, and ultimately generate human-readable privacy captions that developers can use in privacy notices.

The pipeline has three major phases:

1. **APK Unpacking & PRCS Extraction** — Extract permission-requiring code segments from APK files
2. **Privacy Behavior Classification** — Label each segment with Practice and Purpose labels (PAcT taxonomy)
3. **Privacy Caption Generation** — Translate labeled segments into natural language privacy captions using NMT models

---

## Current Project Status

### What Has Been Built

The existing work lives in the `Document Analysis Module/` directory and focuses on the **API documentation analysis** sub-task — identifying what personal information each Android API accesses by reading the official Android developer documentation.

| Component | File(s) | Status |
|-----------|---------|--------|
| Raw API data parsing (SuSi sources/sinks) | `structure_input_data.py` | Complete |
| Android API documentation scraper | `utils_doc_des.py` | Complete |
| Method name cleaning for NLP | `utils_clean_method_name.py` | Complete |
| DPR / ESA semantic similarity scoring | `utils_dpr_score.py` | Complete (requires external ESA Java tool) |
| NLP dependency parsing pipeline (Stanza) | `utils_main_api_Des_to_Info_final.py` | Complete |
| Personal info extraction to CSV | `utils_main_api_Des_to_Info_Save.py` | Complete |
| Unit tests for each utility | `Sourcecode/Test/` | Complete |
| Sample decompiled Java from real APKs | `PriGenLocal/test_apk/` | Test data only — no processing scripts |

**Output produced so far:** `output/personal_info_results.csv` — a table mapping each sensitive Android API to the personal information it accesses, derived from scraping official documentation and NLP parsing.

### What Is Missing

| Phase | Component | Status |
|-------|-----------|--------|
| Phase 1 | APK unpacking and Java source extraction | **Not started** |
| Phase 1 | Filtering extracted code to only PRCS (permission-requiring call graph slices) | **Not started** |
| Phase 1 | CSV output mapping each PRCS to its API signature and category | **Not started** |
| Phase 2 | PAcT label classification model (Practice + Purpose) | **Not started** |
| Phase 2 | Annotated dataset (ADPAc) integration | **Not started** |
| Phase 3 | NMT model for caption generation | **Not started** |
| Phase 3 | Human-in-the-loop caption refinement interface | **Not started** |
| Infra | Parameterized configuration (hardcoded paths throughout existing scripts) | **Not started** |
| Infra | End-to-end pipeline that connects all phases | **Not started** |

---

## Phase 1 — APK Unpacking and PRCS Extraction (Next Step)

This is the foundational step. Every downstream task depends on having a well-structured CSV of code segments extracted from a real APK, annotated with which Android permission-requiring APIs they call.

### What This Step Must Produce

A CSV file with one row per Permission-Requiring Code Segment (PRCS), containing:

| Column | Description |
|--------|-------------|
| `app_package` | Android package name of the application |
| `apk_filename` | Source APK file name |
| `class_name` | Fully-qualified Java class containing the first hop |
| `method_name` | Method name of the first hop |
| `method_signature` | Full JVM method signature (return type + parameter types) |
| `api_called` | The permission-requiring Android API called (e.g., `getLastKnownLocation`) |
| `api_class` | Class the API belongs to (e.g., `android.location.LocationManager`) |
| `api_category` | SuSi category (e.g., `LOCATION_INFORMATION`, `UNIQUE_IDENTIFIER`) |
| `permission_required` | Android permission this API requires (e.g., `ACCESS_FINE_LOCATION`) |
| `is_user_data` | Boolean — does this access user-generated or user-identifying data |
| `hop_depth` | Number of hops from the permission-requiring API call (1, 2, or 3) |
| `code_snippet` | The raw source code of the method (the PRCS text) |

### Step-by-Step Process

#### Step 1.1 — Unpack the APK

APK files are ZIP archives. Unpacking them reveals the compiled bytecode (`classes.dex`), resources, and the `AndroidManifest.xml`. To get readable Java source code, the DEX bytecode must be decompiled.

**Tools needed:**
- **apktool** — decodes the APK structure and decompiles resource files and the manifest
- **jadx** — decompiles `.dex` bytecode directly into readable Java source code
- **dex2jar** (optional) — converts `.dex` to `.jar` for use with Java decompilers

The output of this step is a directory tree of `.java` files mirroring the application's package structure.

#### Step 1.2 — Parse `AndroidManifest.xml` for Declared Permissions

Before analyzing code, extract which permissions the application declares in its manifest. This provides the ground truth for which categories of personal information the app can access. Each `<uses-permission>` entry maps directly to a class of sensitive data.

**Examples of permission-to-data mappings:**
- `ACCESS_FINE_LOCATION` → GPS coordinates, location data
- `READ_CONTACTS` → contact names, phone numbers, emails
- `READ_CALL_LOG` → call history, phone numbers
- `CAMERA` → photos, video
- `READ_SMS` → message content
- `GET_ACCOUNTS` → Google account, email addresses

This manifest scan produces an initial filter — only APIs related to declared permissions are relevant PRCS candidates.

#### Step 1.3 — Identify Permission-Requiring API Calls in Source Code

Scan the decompiled Java source for calls to Android APIs that require runtime permissions. The existing project already has a catalog of these APIs in:

- `Document Analysis Module/input/CatSources_v0_9.txt` — source APIs (data collection)
- `Document Analysis Module/input/CatSinks_v0_9.txt` — sink APIs (data transmission)
- `Document Analysis Module/output/formatted_sources.csv` — parsed version
- `Document Analysis Module/output/formatted_sinks.csv` — parsed version

Each entry in these files follows the format:

```
<ClassName: ReturnType methodName(ParameterTypes)>  CATEGORY
```

A scan of the decompiled source must match method calls against these signatures. A match indicates that the method is a **first hop** — the direct caller of a permission-requiring API.

**Filtering criteria for user-permission-related data:**
The SuSi categories that indicate direct access to user personal information include:
- `LOCATION_INFORMATION` — `getLastKnownLocation`, `requestLocationUpdates`
- `UNIQUE_IDENTIFIER` — `getDeviceId`, `getImei`, `getAndroidId`, `getMacAddress`
- `ACCOUNT_INFORMATION` — `getAccounts`, `getPassword`
- `CONTACT_INFORMATION` — `query` on `ContactsContract`
- `CALL_LOG` — `query` on `CallLog.Calls`
- `SMS_MMS` — `query` on `Telephony.Sms`
- `CALENDAR_INFORMATION` — `query` on `CalendarContract`
- `BROWSER_INFORMATION` — `query` on `Browser.BookmarkColumns`
- `NETWORK_INFORMATION` — `getNetworkInfo`, `getActiveNetworkInfo`
- `BLUETOOTH_INFORMATION` — `startDiscovery`, `getBondedDevices`
- `PHONE_INFORMATION` — `getLine1Number`, `getSubscriberId`
- `AUDIO_INPUT_OUTPUT` — `startRecording`, `setAudioSource`
- `FILE_IO` — file reads on sensitive directories (camera roll, documents)
- `SYNCHRONIZATION_DATA` — `addPeriodicSync`, `requestSync`

Non-user-data categories (to exclude or flag separately):
- `SYSTEM_SERVICES` — accessing system-level services without personal data implications
- `IPC` — inter-process communication not involving user data
- `NETWORK` — generic network calls not tied to identifiable data

#### Step 1.4 — Build the Call Graph (Hops)

A PRCS is not just the single method that calls the permission API — it includes the chain of methods that pass that personal information forward. This is the call graph hop structure described in the research:

- **Hop 1**: The method that directly calls the permission-requiring API
- **Hop 2**: Any method that calls Hop 1 (and therefore receives or uses the result)
- **Hop 3**: Any method that calls Hop 2

Per the research, approximately 80% of personal information usage occurs within the first three hops, so the extraction is capped at depth 3.

Building this requires a call graph over the decompiled source. This can be done statically by:
1. Parsing method signatures and their call sites
2. Following return values and parameter passing from the first-hop API call upward through the call chain

Each PRCS is recorded as a set of method code snippets (one per hop), linked together.

#### Step 1.5 — Enrich with Android Official Documentation via NLP

Once the PRCS CSV is built, each row's `api_called` and `api_class` columns are matched against the existing NLP pipeline in `Document Analysis Module/`:

1. **Fetch documentation** (`utils_doc_des.py`) — retrieve the official description for the API from developer.android.com
2. **Clean method and class names** (`utils_clean_method_name.py`) — tokenize CamelCase identifiers, strip prefixes, remove stopwords
3. **Semantic scoring** (`utils_dpr_score.py`) — use ESA/DPR to compute how closely the documentation language aligns with known personal-information categories
4. **NLP extraction** (`utils_main_api_Des_to_Info_final.py`) — parse the documentation sentence with Stanza, extract the direct object and noun phrase that names the personal data accessed

This enrichment step adds two columns to the PRCS CSV:
- `doc_description` — the official Android documentation text for the API
- `personal_information_type` — the extracted natural language name of the data (e.g., "last known location", "device serial number", "account password")

#### Step 1.6 — Output the PRCS CSV

The final output is a validated CSV file with one row per PRCS, ready to feed into Phase 2 (PAcT classification). Rows where documentation could not be found or personal information could not be extracted are flagged with a `needs_review` column set to `True` for manual inspection.

### Known Challenges and How to Handle Them

**Obfuscated code**: Many production APKs use ProGuard or R8 obfuscation, which renames classes and methods to single letters. The strategy from the research paper is to focus on the *type* of the variable rather than its name. Additionally, checking if the API signature still matches the SuSi catalog works regardless of identifier names, since the underlying Android framework calls are not renamed.

**Third-party libraries**: Apps bundle many third-party SDKs (advertising, analytics). PRCS from these libraries should be included because the research paper specifically calls out that developers often miss privacy implications of bundled libraries.

**APIs not in the SuSi catalog**: The SuSi catalog covers approximately 100+ APIs but is not exhaustive. Any permission-requiring API call found in the manifest but not matched in the catalog should be logged separately for manual review and potential catalog extension.

**Documentation not found**: The existing pipeline already handles this — entries where `utils_doc_des.py` returns no result are flagged. The `androidx.compose` namespace is a known gap since it is not documented on developer.android.com in the same structure.

---

## Project Phases Summary

```
Phase 1: APK Unpacking & PRCS Extraction   ← CURRENT FOCUS
    │
    ├── 1.1  Unpack APK → Java source files
    ├── 1.2  Parse AndroidManifest.xml → declared permissions
    ├── 1.3  Scan source for permission-requiring API calls (SuSi catalog)
    ├── 1.4  Build call graph → extract 3-hop PRCS chains
    ├── 1.5  Enrich with Android docs + NLP personal info extraction
    └── 1.6  Output: prcs_dataset.csv
         │
Phase 2: Privacy Behavior Classification
    │
    ├── 2.1  Train/apply PAcT classifier (Practice labels: Processing, Sharing, Collecting)
    ├── 2.2  Train/apply PAcT classifier (Purpose labels: Functionality, Analytics, Advertisement)
    └── 2.3  Output: prcs_labeled.csv
         │
Phase 3: Privacy Caption Generation
    │
    ├── 3.1  Fine-tune NMT model (Code2Seq or similar) on labeled PRCS
    ├── 3.2  Generate candidate captions
    ├── 3.3  Human-in-the-loop refinement
    └── 3.4  Output: privacy captions per PRCS, ready for use in privacy notices
```

---

## Technical Dependencies for Phase 1

### APK Processing Tools
- **apktool** — APK decoding and manifest extraction
- **jadx** — DEX to Java decompilation (preferred over dex2jar for readability)

### Existing Project Dependencies
- Python 3.x
- `pandas` — CSV handling
- `requests` + `beautifulsoup4` — Android documentation scraping
- `nltk` — stopword removal, tokenization
- `stanza` — dependency parsing for NLP extraction
- **ESA tool** (Java) — semantic relatedness scoring; requires setup via `Lib/setup_esa.ps1`

### Existing Data Assets
- `input/CatSources_v0_9.txt` + `input/CatSinks_v0_9.txt` — SuSi API catalog (79 source APIs, 79 sink APIs)
- `output/formatted_sources.csv` + `output/formatted_sinks.csv` — Parsed API catalog ready for matching
- `PriGenLocal/test_apk/` — Sample decompiled Java files for testing the extraction pipeline

---

## Reference Papers

1. Jain, V. (2022). *Creating Consistent Privacy Notices by Translating Code Segments into Privacy Captions.* IEEE RE 2022.
2. Kunz, I. et al. (2023). *Privacy Property Graph: Towards Automated Privacy Threat Modeling via Static Graph-based Analysis.* PoPETs 2023.
3. Jain, V. et al. (2021). *PriGen: Towards Automated Translation of Android Applications' Code to Privacy Captions.*
4. Jain, V. et al. (2022). *PAcT: Detecting and Classifying Privacy Behavior of Android Applications.*
