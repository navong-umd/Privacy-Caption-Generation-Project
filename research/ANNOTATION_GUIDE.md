# How to Label a Flow: A Walkthrough for First-Time Annotators

This is the practical companion to [ANNOTATION_CODEBOOK.md](ANNOTATION_CODEBOOK.md). The codebook says *what* each label means; this guide shows *how* to read a row and decide, step by step, with real examples.

Expect the first 20 rows to take 3–5 minutes each. After calibration most rows take 1–2 minutes.

---

## 1. What you are doing

The analysis tool found places in an app where some value is read by one API call (the **source**) and later reaches another API call (the **sink**). Each row in your sheet is one such path, called a **flow**.

For every flow you answer three questions:

1. **Is this actually personal data?** The tool is often wrong. If not, mark `not_personal` and stop.
2. **What does the app do with it?** (Practice: Processing, Collecting, Sharing, Other)
3. **Why?** (Purpose: Functionality, Advertisement, Analytics, Other)

You never need to understand every line of code. You need to find the source, the sink, and who owns the code in between.

---

## 2. Set up your spreadsheet

1. Open your sheet (for example `solo_ali.csv`) in Excel or Google Sheets.
2. Freeze the header row.
3. Hide or narrow these columns so the important ones fit on screen: `class_name`, `method_name`.
4. Make the `snippet` column wide and turn on **Wrap text**. The ` | ` marks separate lines of code.
5. Keep these columns visible side by side: `source_api`, `pi_type`, `sink_api`, `sink_type`, `snippet`, then the label columns.

**Rules for the file:**
- Mark a label by typing `1`. Leave everything else blank.
- Do not delete, reorder or rename columns. Do not edit `prcs_id` or `annotator`.
- When saving from Excel, choose **CSV UTF-8**. In Google Sheets, use File → Download → CSV.
- Work in sessions of 60–90 minutes. Fatigue is the biggest source of errors.

---

## 3. How to read one row: five steps

### Step 1: Read the source. Is it personal data?

Look at `source_api` and `pi_type`. The format is `package.Class->method`.

The tool tags a lot of ordinary plumbing as personal data. Use this cheat sheet:

| Source looks like | Usually | Why |
|---|---|---|
| `Location->getLatitude/getLongitude`, `LocationManager->getLastKnownLocation` | **Personal** (location) | The device's position. |
| `Settings$Secure->getString` | **Usually personal** (device ID) | Usually reads `android_id`, a per-device identifier. If the snippet shows a different setting name, judge from that. |
| `TelephonyManager->getDeviceId/getImei/getLine1Number/getSubscriberId` | **Personal** | Phone identifiers or number. |
| `AccountManager->getAccounts` | **Personal** | The user's accounts / emails. |
| `ContentResolver->query` | **Often personal** | Depends on what is queried (contacts, media, calendar). Look in the snippet for `ContactsContract`, `MediaStore`, `CalendarContract`. |
| `TelephonyManager->getNetworkOperatorName`, `NetworkInfo->getType/getSubtype` | **Borderline** | Carrier name or wifi-vs-mobile. Decide together during calibration and write the rule down. |
| `Calendar->get/getInstance/getTime` | **Not personal** | Just today's date and time, not the user's calendar. |
| `Uri->getQueryParameter` | **Not personal** unless the snippet shows it reads an email, token or ID | A URL parameter. |
| `ClassLoader->loadClass/getResourceAsStream`, `System->getSecurityManager` | **Not personal** | Loading code. |
| `SSLContext`, `TrustManagerFactory`, `SSLEngineResult` | **Not personal** | Setting up encryption. |
| `MatrixCursor->getCount` | **Not personal** | A row count. |

**If it is not personal:** put `1` in `not_personal`, leave every `P_` and `U_` column blank, set `confidence`, and move on. That is a complete answer, and an important one: it measures how often the tool is wrong.

### Step 2: Read the sink. Where does the data go?

Look at `sink_type` first, then check `sink_api` to make sure it is real.

| `sink_type` | Means | Practice it suggests |
|---|---|---|
| `network` | Sent over the internet (`okhttp3`, `java.net.URL`, `HttpURLConnection`, `Socket`) | **Sharing** |
| `ipc` | Handed to another component (`Intent`, `Binder`, `ContentProvider`) | **Sharing** only if it leaves the app; otherwise Processing |
| `storage` | Written to the device (`SharedPreferences`, files, databases) | **Processing** |
| `logging` | Written to the system log (`android.util.Log`) | **Processing** |
| `serialization` | Converted to JSON or bytes (`Gson->toJson`, `JSONObject->put`) | **Processing**, and often a step before sending |
| `heuristic_unknown` | The tool guessed | **Read `sink_api` yourself**: `LinkedHashMap->put` or `View->postOnAnimation` is just in-app work (Processing); anything HTTP-like is Sharing |

Two traps:
- A "storage" sink that *reads* (`SharedPreferences->getString`) is not a write. Treat it as Processing.
- `Socket->close` or `Connection->close` does not send anything by itself. Only mark Sharing if the snippet shows the value being added to a request, header or body.

### Step 3: Read the snippet. Who owns the code?

Each block in the snippet starts with a line like:

```
// com.google.android.gms.measurement.internal.a5->q
```

That is `package.Class->method`: the method where the next lines run. Lines under it like

```
v0, Lkg0;->g()Z
```

are calls. `Lkg0;` is the class being called, `g` is the method, and the letters after `)` are the return type (`Z` true/false, `I` number, `V` nothing, `L...;` an object). You can ignore the `v0, v1` registers.

Read the **package names** along the chain. They tell you whose code handles the data:

| Package contains | Owner | Purpose it suggests |
|---|---|---|
| `com.google.android.gms.ads`, `gms.internal.ads`, `com.facebook.ads`, `applovin`, `unity3d.ads`, `ironsource`, `mopub`, `vungle`, `chartboost` | Ad SDK | **Advertisement** |
| `firebase.analytics`, `gms.measurement`, `crashlytics`, `amplitude`, `mixpanel`, `segment`, `appsflyer`, `adjust`, `branch` | Analytics / attribution SDK | **Analytics** |
| The app's own package (`com.duolingo`, `com.snapchat`, `com.zhiliaoapp.musically`, `tv.periscope`) | The app | Usually **Functionality** |
| Short meaningless names (`p.fxa`, `uj`, `kg0`) | Obfuscated, unknown | Look for any readable package elsewhere in the chain; if there is none, use Functionality with `confidence` 1 |

If ad or analytics code appears anywhere between the source and the sink, that usually decides the purpose, even inside a feature screen.

### Step 4: Mark the Practice columns

For a personal flow:
- `P_Collecting`: almost always `1`, because the source reads the data.
- `P_Processing`: `1` if the data is used on the device (compared, formatted, stored, logged, shown).
- `P_Sharing`: `1` only if the data leaves the app (step 2).
- `P_Other`: rarely. Explain it in `notes`.

Several can be `1` at once.

### Step 5: Mark Purpose, confidence and notes

- Purpose from step 3. Mark more than one if two owners clearly use it.
- `confidence`: `3` sure, `2` probably, `1` guessing.
- `notes`: one short phrase on anything unusual, for example `carrier name; borderline`, `sink is a read, not a write`, `ads SDK in chain`.

---

## 4. Three worked examples

These are real flows from apps that are **not** in your sheets.

### Example A: looks like data, isn't (Instagram)

| Field | Value |
|---|---|
| source_api | `java.util.Calendar->get` |
| pi_type | `CALENDAR_INFORMATION` |
| sink_api | `android.content.SharedPreferences->getString` |
| sink_type | `storage` |
| snippet (start) | `// com.instagram.util.c.c->a  v0, v1, Ljava/util/Calendar;->get(I)I  // com.instagram.reels.ui.dw->b ...` |

- **Step 1:** `Calendar->get` reads a field of the current date. It is not the user's calendar, even though the tool says `CALENDAR_INFORMATION`.
- **Answer:** `not_personal` = 1, all `P_`/`U_` blank, confidence 3. Note: `current date, not user calendar`.

### Example B: real personal data sent to a server (Twitter)

| Field | Value |
|---|---|
| source_api | `android.provider.Settings$Secure->getString` |
| pi_type | `UNIQUE_IDENTIFIER` |
| sink_api | `okhttp3.Interceptor$Chain->request` |
| sink_type | `network` |
| snippet (start) | `// qdg->h  Settings$Secure;->getString(...)  // qdg->e  Lqdg;->h(Context)  // tv.periscope.android.api.RestClient->lambda$new$0  Lqdg;->e(Context)  // tv.periscope.android.api.a->intercept ... Interceptor$Chain;->request()` |

- **Step 1:** `Settings$Secure->getString` reads the device ID, so this is personal.
- **Step 2:** the sink is an HTTP request interceptor, so the data goes over the network: Sharing.
- **Step 3:** the chain goes through `tv.periscope.android.api.RestClient`, Twitter's own Periscope API client. No ad or analytics package: Functionality.
- **Answer:** `P_Collecting`, `P_Sharing` = 1 (`P_Processing` 1 as well: it is passed through and attached to the request), `U_Functionality` = 1, confidence 2. Note: `device id added to own API requests`.

### Example C: uncertain, and that is fine (Spotify)

| Field | Value |
|---|---|
| source_api | `android.telephony.TelephonyManager->getNetworkOperatorName` |
| pi_type | `NETWORK_INFORMATION` |
| sink_api | `java.net.Socket->close` |
| sink_type | `network` |
| snippet (start) | `// p.wgu->P  TelephonyManager;->getNetworkOperatorName()  // p.fo1->a  Lp/wgu;->P(Context, JSONObject)  ...  Socket;->close()V` |

- **Step 1:** carrier name. Borderline: use whatever rule you agreed in calibration. Here, treat it as personal device information.
- **Step 2:** it is put into a `JSONObject` (`p.fo1->a` takes a JSONObject), which is Processing. The sink is `Socket->close`, which sends nothing by itself, so there is no clear evidence of Sharing.
- **Step 3:** every class is obfuscated (`p.wgu`, `p.fo1`). Owner unknown.
- **Answer:** `P_Collecting`, `P_Processing` = 1, `U_Functionality` = 1, confidence 1. Note: `carrier name into JSON; send not visible; obfuscated`.

Low confidence is a correct answer when the evidence is thin. Do not guess Sharing because the sink type says `network`.

---

## 5. How to know you are doing it right

### Before you start: calibration (about 1 hour, both annotators)

1. Each of you labels your own `calibration_<you>.csv` (20 flows from WhatsApp) **alone**, without talking.
2. Send both files to Ali, who runs the agreement report (commands in the codebook, section 6).
3. Sit together and go through **every** row where you disagree. For each, decide the right answer and **write the rule** into the codebook's worked examples. For example: "NetworkInfo->getType counts as not personal".
4. Look at the report. If not-personal kappa or the PAcT macro kappa is below **0.6**, do a second calibration round with a fresh set.

| Cohen's kappa | Means |
|---|---|
| below 0.40 | Poor: the definitions are unclear; talk again before going on |
| 0.40–0.60 | Moderate: fix the labels with the lowest kappa |
| 0.60–0.80 | Substantial: good enough to proceed |
| above 0.80 | Almost perfect |

### While you label

- **Overlap sheet: do not discuss it** until both of you are finished. It is what measures agreement.
- When you are unsure, mark your best answer with `confidence` 1 and a note. Do not spend more than 5 minutes on one row.
- Keep a short list of new rules you decide on, and add them to the codebook after your session.

### Self-check after about 50 rows

Pick 10 rows you labeled at least two days earlier. Cover your old answers and label them again. If you disagree with yourself on more than 2, reread the codebook before continuing.

### Warning signs

- Almost every row is `U_Functionality`. Check step 3 again: are you reading the package names?
- You mark `P_Sharing` for `storage` or `logging` sinks. Those stay on the device.
- You almost never use `not_personal`. In this dataset, roughly half of the flows start from date, URL, class-loading or encryption calls.
- Rows take under 20 seconds each. You are probably not reading the sink and snippet.

### After the overlap round

Ali runs the agreement report. A low kappa on one label (for example `purpose_Analytics`) means that label's definition needs a clearer rule, not that someone is "wrong". Fix the rule, then adjudicate the disagreements as described in the codebook.
