Classifying data requires looking beyond just "what" the information is and focusing on "how" it behaves, how it's structured, and who owns it. This multidimensional approach helps in determining the right storage architecture, privacy requirements, and analytical methods.

Here is a proposed classification system using five distinct axes.

1. The Axis of Structure

This axis defines the format and "messiness" of the data, which dictates whether you need a rigid SQL database or a flexible data lake.

    Structured: Highly organized (e.g., Real estate title records in a ledger).

    Semi-Structured: Tags and markers separate semantic elements (e.g., Wikipedia edit histories in XML/JSON).

    Unstructured: Heavy content without a pre-defined model (e.g., The text within an Academic paper).

    Time-Series/Signal: Sequential measurements (e.g., Industrial vibration sensors).

    Graph/Network: Focused on relationships (e.g., Citation networks).

2. The Axis of Volatility & Velocity

This axis measures how quickly the data changes and the urgency with which it must be processed.

    Static/Archive: Rarely changes once recorded (e.g., Historical title transfers).

    Incremental: Grows steadily over time (e.g., New academic citations).

    Revisionary: Existing records are frequently updated (e.g., Wikipedia article edits).

    Transient/Streaming: High-speed data that may be processed and discarded (e.g., DNS query logs).

    Burst: Highly irregular frequency based on specific events.

3. The Axis of Origin (Provenance)

Understanding where the data comes from helps assess its reliability and the "noise" involved.

    Machine-Generated: Logs and automated outputs (e.g., DNS logs).

    Sensor-Derived: Physical world measurements (e.g., Vibration sensors).

    Human-Authored: Explicitly created by people (e.g., Wikipedia edits, papers).

    Transactional: Produced by a business process or exchange (e.g., Real estate transfers).

    Derived/Synthetic: Data produced by processing other datasets.

4. The Axis of Sensitivity & Governance

This axis determines the legal and ethical framework required to handle the data.

    Public/Open Source: Free for anyone to use (e.g., Wikipedia, Academic citations).

    Proprietary/Commercial: Owned by an entity for value (e.g., Industrial sensor data).

    Regulated/PII: Contains personally identifiable information (e.g., ISP-level DNS logs).

    Legal/Notarized: Requires high-integrity verification (e.g., Title transfer records).

    Classified/Confidential: High-security business or state secrets.

5. The Axis of Intent (Utility)

Why are we collecting this? The goal changes the analytical approach.

    Descriptive: To record what happened (Title transfers).

    Diagnostic: To find out why something happened (Wikipedia edit reverts).

    Predictive: To forecast future states (Using vibration sensors to predict machine failure).

    Operational: Required for a system to function (DNS logs for network routing).

    Relational: To understand influence and connectivity (Citation networks).
