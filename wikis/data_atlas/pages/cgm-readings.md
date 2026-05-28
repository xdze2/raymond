---
title: Continuous Glucose Monitor (CGM) Readings
slug: cgm-readings
summary: Sub-minute interstitial glucose readings produced by wearable biosensors worn by diabetic patients, controlled by device manufacturers Dexcom and Abbott and the insurers who fund reimbursement.

# Origin taxonomy
origin: sensor
origin_subtype: biomedical, wearable

# Coordinate axes
scale: individual
time_frequency: continuous
time_depth: years
structure: structured

# Thematic
domains: [medical, behavioral, insurance]
status: active

# Impact
llm_impact: high
llm_impact_reason: LLMs can synthesize glucose time-series with diet, activity, and medication logs to generate personalized insulin dosing recommendations and detect pattern anomalies that clinicians miss in periodic chart reviews.

# Relations
related: [alpr-location-logs, nicu-physiological-waveforms, fetal-heart-rate-tracings]
gatekeepers: [Dexcom, Abbott, UnitedHealth Group, CVS Caremark, Epic Systems]
breaks_when: patient downloads their own data via Dexcom Clarity or LibreView; researcher obtains IRB-approved data-sharing agreement; insurer mandates data feed as reimbursement condition
---

## What It Is

A continuous glucose monitor is a subcutaneous filament — roughly the diameter of a human hair — inserted just below the skin, wired to a transmitter that measures interstitial glucose concentration every one to five minutes and broadcasts readings via Bluetooth to a paired phone or dedicated receiver. The two dominant systems are the Dexcom G7 and the Abbott FreeStyle Libre 3, together covering the vast majority of the ~four million CGM users in the United States. Each generates a time-series of glucose values (in mg/dL), calibration offsets, sensor confidence scores, and alert events (low glucose, rapid rise, high glucose), along with device metadata: sensor lot number, transmitter ID, session start and end timestamps.

At the individual level, a single patient's CGM archive is a dense behavioral fingerprint. A year of data at five-minute intervals produces roughly 100,000 timestamped glucose readings, from which meal timing, sleep patterns, exercise response, and medication adherence are all inferrable with high confidence — often more reliably than the patient's own recall. At population scale, Dexcom and Abbott sit on longitudinal glucose time-series for millions of users: data that has no real clinical precedent in scope or resolution.

## Who Controls It

Dexcom and Abbott are the primary gatekeepers. Both operate cloud platforms — Dexcom Clarity and Abbott LibreView — that aggregate user data and provide clinical dashboards. The terms of service grant them broad rights to use de-identified data for product development, research, and commercial purposes. Patients technically "own" their readings and can export CSVs or connect to Apple Health and similar aggregators, but the richest derived analytics (pattern reports, time-in-range calculations, population benchmarks) live on vendor servers.

Insurers occupy a parallel gatekeeper role. UnitedHealth, Anthem, and CVS Caremark control CGM reimbursement eligibility, and some are beginning to require data-feed agreements as a condition of coverage — effectively compelling patients to share data with the payer as the price of affordability. Epic Systems and other EHR vendors hold a third copy of the data where clinicians have imported patient reports into the medical record, but at lower temporal resolution than the source. A shadow market in CGM data also exists: health data brokers like Veeva and IQVIA purchase or license de-identified patient datasets from device manufacturers and specialty pharmacies.

## What It Reveals

Glucose dynamics are a metabolic proxy for almost everything. Diet, stress, sleep quality, physical activity, alcohol consumption, and infection all produce distinct glucose signatures that a sufficiently long CGM record can disentangle. This is why insurers are interested: a CGM feed is a continuous lifestyle audit that's far more granular than claims data or the occasional A1C result drawn in a clinic. For someone without diabetes wearing a CGM for metabolic monitoring — a practice gaining traction in wellness markets — the data reveals metabolic response profiles that correlate with cardiovascular risk, cognitive performance, and longevity in ways not captured by any existing clinical biomarker panel.

At population scale, aggregated CGM data reveals which food products, activity patterns, and medications produce the best glycemic outcomes across different demographic groups — information worth billions to pharmaceutical companies, food manufacturers, and insurers optimizing risk pools. Novo Nordisk, Eli Lilly, and others have active research partnerships with CGM manufacturers precisely because real-world glucose response data at this scale didn't exist before CGMs. The asymmetry is stark: the patient generates the data with their own body; the value accrues to the platform.

## Current Access Landscape

**Who has it:** Dexcom and Abbott (full time-series), insurers (claims-linked aggregate), EHR systems (clinic-imported summaries), approved research partners under data-sharing agreements.

**Who doesn't:** Public health agencies lack systematic access to real-time population glucose data. Independent researchers must apply through manufacturer-specific programs with restrictive terms. Patients themselves often can't export more than 90 days of history without a clinical account.

**Partial access points:** The Tidepool open-source diabetes data platform aggregates CGM data donated voluntarily by patients (roughly 100,000 users); the JAEB Center for Health Research has run NIH-funded studies using manufacturer-provided datasets. Direct-to-patient APIs exist (Dexcom Developer Portal) and are used by third-party apps like Nightscout and xDrip+, which in turn have enabled a patient-led open-source ecosystem for real-time monitoring.

**Historical leaks or ruptures:** No major data breach specific to CGM records has become public, though Dexcom disclosed a separate data incident in 2023 affecting non-CGM account information. The more consequential rupture has been political: the FDA's 2023 guidance enabling interoperability requirements for CGM devices forced manufacturers to open data flows to third-party apps, meaningfully expanding patient-controlled access.

## Cracks & Pressure Points

- **Regulatory pressure:** The FDA's Digital Health Center of Excellence is developing interoperability standards that would require CGM manufacturers to support open APIs; the 21st Century Cures Act's information-blocking rules already apply to EHR-held CGM data.
- **Investigative journalism:** STAT News and The Markup have covered the commercial use of patient health data by device manufacturers, increasing regulatory attention on CGM data specifically.
- **Litigation:** Class action suits against health data brokers (e.g., the litigation against data aggregator Ciox Health) are establishing precedents about permissible use of de-identified patient data that will affect CGM data licensing.
- **Technical circumvention:** The Nightscout Project and xDrip+ enable patients to extract CGM data in real time and store it on personal servers, outside manufacturer platforms entirely. The open-source community has reverse-engineered Bluetooth protocols for several devices.
- **Market alternatives:** Consumer CGM programs from Levels Health and Supersapiens aggregate user data voluntarily and have begun publishing aggregate findings — a partial substitute for manufacturer-held population data.

## LLM & AI Impact

LLMs don't change who holds the raw data, but they dramatically lower the threshold for acting on it. A clinician reviewing a patient's 90-day CGM report sees a chart; an LLM processing the same time-series can identify meal timing patterns, quantify glycemic variability, flag anomalous sensor sessions, and draft plain-language summaries for patients who can't interpret the numbers themselves. The more significant AI impact is at population scale: once a manufacturer or insurer grants a research team access to millions of CGM time-series, LLMs and foundation models trained on those archives can generate predictive models of glycemic response that individual clinicians cannot replicate from their patient panels. The access barrier is unchanged — the analysis barrier has collapsed. What remains out of reach is the inference that could be made if CGM data were linked to food purchase records, genomics, and pharmacy claims — linkages that technically exist in insurance databases but are rarely assembled and almost never shared. Impact: **high**.

## See Also

→ [[nicu-physiological-waveforms]] — same structural problem: continuous high-resolution physiological data controlled by hospital vendors, rarely archived at source resolution
→ [[vehicle-obd-telemetry]] — comparable individual behavioral telemetry generated by a device, controlled by a commercial intermediary
→ [[utility-smart-meter-data]] — parallel 15-minute behavioral fingerprinting at household level, analogous gatekeeper dynamics with utilities
