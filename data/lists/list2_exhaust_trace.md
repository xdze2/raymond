# LIST 2: EXHAUST & TRACE DATA

Data produced as a byproduct of doing something else.
The activity as author. Nobody created this to be informative —
it accumulated as residue of action.

---

**Cell tower connection logs by carrier** — Timestamps and tower IDs when a phone registers with the network; controlled by carriers (AT&T, Vodafone), retained 1–7 years.
Tags: scale=individual domain=telecommunications,mobility status=active

**Supermarket loyalty card purchase sequences** — Itemized transaction histories linked to a named account; controlled by retailers (Kroger, Tesco), sold to data brokers.
Tags: scale=individual domain=retail,behavioral status=active

**DNS query logs at ISP level** — Domain lookups made by subscribers, timestamped and IP-linked; controlled by ISPs and resolver operators (Cloudflare, Google).
Tags: scale=individual domain=telecommunications,behavioral status=buried

**Elevator usage patterns in office buildings** — Call logs from building management systems, timestamped and floor-linked; controlled by elevator companies (Otis, KONE) and building owners.
Tags: scale=individual domain=urban,labor status=buried

**Credit card transaction location and merchant category sequences** — Purchase time, merchant, amount, MCC code; controlled by card networks (Visa, Mastercard) and issuing banks.
Tags: scale=individual domain=financial,behavioral status=active

**Google search query logs by account** — Verbatim queries, timestamps, result clicks; controlled by Google, retained per privacy policy, not externally accessible.
Tags: scale=individual domain=behavioral,digital status=buried

**Email header metadata (To, From, Subject, timestamp, IP)** — Communication graph and timing without message content; collected by email providers and accessible to intelligence agencies.
Tags: scale=individual domain=communications,behavioral status=buried

**Ride-hailing trip origin-destination pairs (Uber, Lyft)** — Pickup/dropoff coordinates, duration, fare; controlled by platform operators, occasionally subpoenaed.
Tags: scale=individual domain=mobility,behavioral status=buried

**Court e-filing system access logs** — Who queried which case records and when; controlled by PACER/state court systems, not publicly released.
Tags: scale=organizational domain=legal,behavioral status=buried

**Hospital EHR login and chart access logs** — Which staff member opened which patient record and when; controlled by hospital IT departments, audited internally.
Tags: scale=individual domain=medical,labor status=buried

**Mortgage application denial records by census tract (HMDA)** — Loan application outcomes by race, income, geography under Home Mortgage Disclosure Act; public annual release.
Tags: scale=systemic domain=financial,housing status=active

**Corporate procurement system order histories** — Vendor, quantity, price, delivery timing from ERP systems (SAP, Oracle); controlled by corporations, occasionally revealed in litigation.
Tags: scale=organizational domain=economic,logistics status=buried

**Wikipedia article edit histories** — All revisions, diffs, editor usernames/IPs, timestamps; fully public via Wikimedia dumps.
Tags: scale=systemic domain=digital,social status=active

**Airline ticketing and boarding records (PNR data)** — Passenger name, routing, seat, payment method; controlled by airlines and GDSs (Amadeus, Sabre), shared with border agencies.
Tags: scale=individual domain=mobility,security status=buried

**Smartphone app foreground/background usage logs** — Which app is active, for how long, at what time; controlled by OS makers (Apple, Google) and aggregated by analytics firms.
Tags: scale=individual domain=behavioral,digital status=active

**Workers' compensation claims by employer and industry** — Injury type, body part, employer, claim cost; controlled by state labor agencies, variably public.
Tags: scale=organizational domain=labor,health status=buried

**ATM withdrawal location and amount logs** — Cash transaction records linked to account; controlled by banks and card networks, retained for years.
Tags: scale=individual domain=financial,behavioral status=buried

**Academic literature citation networks** — Who cited whom, extracted from reference lists; aggregated by Semantic Scholar, OpenAlex, Web of Science.
Tags: scale=systemic domain=scientific,social status=active

**Prescription drug dispensing records by pharmacy** — Drug, dose, prescriber, patient, date; controlled by pharmacies and PBMs (CVS Caremark, Express Scripts), partially accessible via state PDMPs.
Tags: scale=individual domain=medical,behavioral status=buried

**Container ship AIS position and port call logs** — Vessel identity, position, speed from mandatory transponders; aggregated by MarineTraffic, UN Comtrade correlates cargo.
Tags: scale=systemic domain=maritime,economic status=active

**Public transit fare gate tap records** — Card ID, station entry/exit, time; controlled by transit agencies (TfL, MTA), retained for dispute resolution.
Tags: scale=individual domain=mobility,behavioral status=buried

**Corporate email server send/receive logs (SMTP metadata)** — Internal communication graph and timing; controlled by IT departments and email security vendors (Proofpoint, Mimecast).
Tags: scale=organizational domain=labor,communications status=buried

**Payday loan and high-interest credit application records** — Application volume, approval rates, loan terms by zip code; controlled by lenders, partially reported to CFPB.
Tags: scale=organizational domain=financial,social status=buried

**Real estate title transfer records** — Buyer, seller, price, date, deed type; controlled by county recorder offices, partially aggregated by PropStream, ATTOM.
Tags: scale=systemic domain=housing,financial status=active

**Hotel key-card door entry logs** — Room access timestamps for each guest key; controlled by hotel property management systems (Oracle OPERA), retained briefly.
Tags: scale=individual domain=mobility,behavioral status=buried

**Government employee time-and-attendance records** — Clock-in/out, leave type, supervisor, agency; controlled by OPM and agency HR systems in the US.
Tags: scale=individual domain=labor,government status=buried

**E-commerce return reason codes** — Product return category, stated reason, processing outcome; controlled by platforms (Amazon, Shopify merchants), proprietary.
Tags: scale=systemic domain=retail,behavioral status=buried

**Court appearance and warrant records in municipal systems** — Failure-to-appear rates, warrant issuance by judge and zip code; controlled by municipal courts, rarely aggregated.
Tags: scale=systemic domain=legal,social status=buried

**Social media posting timestamps and device metadata** — When and from what device a post was created; controlled by platforms (Meta, X), partially available via API.
Tags: scale=individual domain=digital,behavioral status=active

**Eviction filing records by landlord and courthouse** — Filing frequency, outcomes, property address; controlled by courts, aggregated by Princeton Eviction Lab and local journalists.
Tags: scale=systemic domain=housing,legal status=buried

**VPN provider connection logs** — Session start/end, IP assignment, data volume; controlled by VPN operators, retention varies (many claim no-log).
Tags: scale=individual domain=telecommunications,behavioral status=buried

**Student LMS interaction logs (Canvas, Blackboard)** — Page views, assignment submissions, video watch times; controlled by universities and LMS vendors.
Tags: scale=individual domain=education,behavioral status=buried

**Health insurance claim denial patterns by insurer and ICD code** — Denial rates by diagnosis and procedure; controlled by insurers, partially reported under ACA to CMS.
Tags: scale=systemic domain=medical,financial status=buried

**Prison phone call records (Securus, ICSolutions)** — Duration, parties, timestamps of inmate calls; controlled by prison telecom vendors, sold to law enforcement.
Tags: scale=individual domain=legal,communications status=buried

**Trucking ELD (electronic logging device) records** — Hours of service, location, speed from mandated FMCSA devices; controlled by carriers and ELD vendors.
Tags: scale=individual domain=labor,mobility status=buried

**Dark pattern interaction logs on e-commerce checkout pages** — Click paths, exit rates, time-on-page near forced subscription opt-ins; controlled by platforms, proprietary.
Tags: scale=systemic domain=digital,behavioral status=buried

**Restaurant point-of-sale item and table turn data** — Menu item sales, table occupancy, server ID; controlled by POS vendors (Toast, Square) and restaurant owners.
Tags: scale=organizational domain=retail,economic status=buried

**Immigration court hearing continuance logs** — Reasons for delay, requesting party, judge, outcome; controlled by EOIR, partially accessible via FOIA.
Tags: scale=systemic domain=legal,government status=buried

**Streaming service viewing duration and dropout points** — Exact timestamps when users paused, rewound, or stopped; controlled by platforms (Netflix, Spotify), proprietary.
Tags: scale=individual domain=behavioral,digital status=buried

**Police dispatch CAD logs** — Call type, address, unit assigned, response time, disposition; controlled by police departments, partially obtainable via public records requests.
Tags: scale=systemic domain=law enforcement,urban status=buried

**Supply chain sub-tier purchase orders** — Contracts between tier-2 and tier-3 suppliers below brand visibility; controlled by suppliers, rarely visible to auditors or brands.
Tags: scale=organizational domain=economic,labor status=buried

**Political campaign donor geographic clustering** — Donation sequences by address over time, cross-referenced with FEC filings; partially public via FEC bulk data.
Tags: scale=systemic domain=political,financial status=active

**Gambling transaction sequences at casino floors** — Bet size, game type, time, loyalty card ID; controlled by casinos and gaming commissions, rarely public.
Tags: scale=individual domain=behavioral,financial status=buried

**Search and rescue mission logs by coast guard district** — Incident type, position, vessel, outcome; controlled by USCG, partially public.
Tags: scale=systemic domain=maritime,government status=buried

**Internal corporate Slack/Teams message metadata** — Sender, recipient, channel, timestamp, reaction count without message content; controlled by employers and Microsoft/Salesforce.
Tags: scale=individual domain=labor,communications status=buried

**Parking meter payment records by block face** — Payment time, duration, location; controlled by municipalities and parking management vendors (ParkMobile, Conduent).
Tags: scale=individual domain=mobility,urban status=buried

**Emergency room triage queue wait times by chief complaint** — Time-stamped acuity assignments; controlled by hospital ED systems, rarely aggregated regionally.
Tags: scale=organizational domain=medical,infrastructure status=missing

**[MISSING] Gig economy algorithmic task assignment logs** — Which worker was offered which task, at what price, after which factors; controlled by platforms (DoorDash, Amazon Flex), never disclosed.
Tags: scale=systemic domain=labor,digital status=missing

**[MISSING] Landlord blacklist database entries** — Names submitted to tenant screening databases (SafeRent, CoreLogic) and dispute outcomes; controlled by screening companies, no public audit.
Tags: scale=individual domain=housing,legal status=missing

**[MISSING] Social credit or behavior scoring in private platforms** — Internal risk or trustworthiness scores applied to users by platforms (Airbnb, Uber) affecting access; not disclosed to subjects.
Tags: scale=individual domain=behavioral,digital status=missing

---

## PATTERN NOTE

Exhaust data is structurally different from sensor data in one key respect: a human action is always the proximate cause, yet the data subject is almost never the data controller. The gap between who generates the data and who owns it is the central power dynamic of the digital economy. Most of this data was not designed to be informative about individuals — it was designed to run a system (a billing platform, a transit network, a court docket) — and its secondary value as behavioral intelligence was discovered afterward, often by parties far removed from the original transaction.

The most politically significant pattern here is suppression by operational opacity: organizations routinely claim data is "not collected" or "not retained in that form" when it is, in fact, an automatic byproduct of any modern IT system. Exhaust data also accumulates differently at different scales: individual behavioral traces are suppressed for privacy reasons (or competitive ones), while systemic aggregates that would reveal institutional patterns — insurer denial rates, eviction filing frequencies by landlord, algorithmic assignment logic — are suppressed for liability and competitive reasons. The [MISSING] items in this list are not technically missing; they exist in live databases. They are missing from public accountability.

LLMs are most likely to change access here by enabling inference attacks: combining individually innocuous exhaust streams (transit taps, loyalty card purchases, app usage timestamps) to reconstruct information that no single source reveals. This has already driven GDPR enforcement and is the frontier of both privacy risk and investigative journalism. The second LLM effect is lowering the cost of FOIA processing and court records analysis — making buried-but-technically-public exhaust data tractable to process at scale for the first time.
