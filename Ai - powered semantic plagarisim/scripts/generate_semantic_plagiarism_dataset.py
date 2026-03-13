from __future__ import annotations

import csv
import json
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "data" / "datasets" / "semantic_plagiarism_benchmark"
DOCUMENTS_DIR = DATASET_DIR / "documents"
SECTION_ORDER = ["Introduction", "Methodology", "Results", "Conclusion"]

LIGHT_REPLACEMENTS = [
    ("Universities now use", "Higher education institutions increasingly use"),
    ("Instructors combine", "Teaching teams combine"),
    ("estimate", "assess"),
    ("need timely support", "require timely support"),
    ("The approach is valuable", "This approach is useful"),
    ("The pilot system collected", "The pilot platform gathered"),
    ("grouped", "clustered"),
    ("updated", "refreshed"),
    ("reviewed", "checked"),
    ("sent targeted study recommendations", "sent focused study guidance"),
    ("Students who received early outreach", "Students who were contacted early"),
    ("completed more practice tasks", "completed more practice activities"),
    ("Faculty members reported", "Faculty reported"),
    ("paired with", "combined with"),
    ("Community energy projects", "Community energy programs"),
    ("Microgrids combine", "Microgrids bring together"),
    ("operators modeled", "operators simulated"),
    ("scheduled", "dispatched"),
    ("cut", "reduced"),
    ("Hospitals increasingly connect", "Hospitals now connect"),
    ("Security teams mapped", "Security teams documented"),
    ("created", "built"),
    ("practiced", "rehearsed"),
    ("identified", "detected"),
    ("Retailers are under pressure", "Retailers face pressure"),
    ("The program gathered", "The initiative collected"),
    ("reduced", "lowered"),
    ("Lenders increasingly use", "Financial institutions increasingly use"),
    ("explanations", "interpretability reports"),
    ("Traffic agencies now combine", "Traffic agencies increasingly combine"),
    ("ingested", "loaded"),
    ("predicted", "forecast"),
    ("Remote care programs", "Remote care initiatives"),
    ("Agronomy teams increasingly deploy", "Agronomy teams increasingly use"),
    ("Cloud disaster recovery plans", "Cloud recovery plans"),
    ("Battery recycling programs", "Battery recovery programs"),
    ("Future deployments", "Future rollouts"),
]

LIGHT_PREFIXES = [
    "In practice",
    "From an operational perspective",
    "Within the case study",
    "Across the pilot",
]

HEAVY_PREFIXES = [
    "Researchers found that",
    "The study indicates that",
    "Operational evidence shows that",
    "Project documentation suggests that",
]

README_CONTENT = """# Semantic Plagiarism Benchmark

This folder contains a synthetic but realistic evaluation dataset for the semantic plagiarism detection project.

## Dataset Size

- 60 markdown documents
- 10 topic families
- 6 documents per family
- Train split: 36 documents
- Validation split: 12 documents
- Test split: 12 documents

## Document Variants Per Family

Each family contains:

- `source`: the original source document
- `direct_copy`: a near-verbatim plagiarism case
- `paraphrase_light`: a lightly rewritten semantic plagiarism case
- `paraphrase_heavy`: a more strongly rewritten semantic plagiarism case
- `mosaic`: a mixed document that blends copied, paraphrased, and clean content
- `independent`: a related but non-plagiarized control document

## Topics

- Adaptive Learning Analytics
- Renewable Microgrids
- Healthcare Cybersecurity
- Sustainable Supply Chains
- Explainable AI in Credit Risk
- Urban Traffic Forecasting
- Telemedicine Chronic Care
- Precision Agriculture IoT
- Cloud Disaster Recovery
- Battery Recycling

## Files

- `documents/train/`, `documents/validation/`, `documents/test/`
- `metadata.csv`: one row per document
- `pair_labels.csv`: expected plagiarism pairs for derived documents
- `summary.json`: dataset totals and split counts

## Metadata Fields

`metadata.csv` includes:

- `doc_id`
- `family_id`
- `split`
- `topic`
- `title`
- `variant`
- `plagiarism_label`
- `primary_source_doc_id`
- `expected_similarity_band`
- `sections_with_overlap`
- `word_count`
- `path`

## Regeneration

To regenerate the dataset:

```bat
.venv\\Scripts\\python scripts\\generate_semantic_plagiarism_dataset.py
```

## Notes

- All documents are synthetic and intended for benchmarking, demos, and testing.
- The runtime demo corpus used by the app is still in `data/corpus/`.
- This dataset is kept separate so the main demo workflow stays lightweight.
"""


@dataclass(frozen=True)
class TopicFamily:
    family_id: str
    split: str
    topic: str
    source_title: str
    independent_title: str
    tags: list[str]
    original_sections: dict[str, list[str]]
    independent_sections: dict[str, list[str]]


FAMILIES = [
    TopicFamily(
        family_id="F01",
        split="train",
        topic="Adaptive Learning Analytics",
        source_title="Learning Analytics for Early Academic Intervention",
        independent_title="Peer Coaching Strategies in Data-Informed Classrooms",
        tags=["education", "analytics", "student-support"],
        original_sections={
            "Introduction": [
                "Universities now use learning analytics dashboards to identify students who are falling behind before final exams.",
                "Instructors combine quiz history, attendance patterns, and discussion activity to estimate which learners need timely support.",
                "The approach is valuable in large classes where individual mentoring time is limited.",
            ],
            "Methodology": [
                "The pilot system collected weekly assessment scores, login frequency, and assignment submission gaps from the course platform.",
                "A risk model grouped students into low, medium, and high-support categories and updated the label after each new activity.",
                "Advisors reviewed the model output every Friday and sent targeted study recommendations to students with rising risk scores.",
            ],
            "Results": [
                "Students who received early outreach completed more practice tasks and were less likely to miss the next assignment deadline.",
                "Faculty members reported that the dashboard helped them prioritize intervention without reading every raw activity log.",
                "The strongest gains appeared when automated alerts were paired with short human feedback sessions.",
            ],
            "Conclusion": [
                "Learning analytics is most effective when institutions treat prediction as a support tool rather than a punishment mechanism.",
                "Transparent communication about data use increases student trust and improves participation in advising programs.",
                "Future deployments should monitor bias and ensure that high-risk labels trigger constructive help.",
            ],
        },
        independent_sections={
            "Introduction": [
                "Some universities focus less on prediction and more on building peer coaching routines inside gateway courses.",
                "In those settings, students learn how to review one another's draft solutions before an instructor steps in.",
                "The main objective is to strengthen belonging and self-regulation rather than to rank learners by risk.",
            ],
            "Methodology": [
                "Program coordinators trained volunteer mentors, scheduled small weekly study circles, and issued reflection prompts after each session.",
                "Course teams tracked attendance at the circles, follow-up office hour visits, and the number of revision plans students completed.",
                "They also interviewed participants about which types of feedback felt practical during busy assessment periods.",
            ],
            "Results": [
                "Students said that peer explanations made complex topics feel less intimidating before major tests.",
                "Attendance remained highest when mentors shared concrete revision tactics instead of general encouragement alone.",
                "The strongest benefit was a more consistent pattern of help-seeking across the semester.",
            ],
            "Conclusion": [
                "Peer coaching does not replace analytics, but it offers a human-centered complement for institutions that want earlier academic conversations.",
                "Programs work best when mentors receive training on inclusion, confidentiality, and referral pathways.",
                "Future studies can compare how predictive alerts and peer support interact in the same course.",
            ],
        },
    ),
    TopicFamily(
        family_id="F02",
        split="train",
        topic="Renewable Microgrids",
        source_title="Renewable Microgrids for Community Energy Resilience",
        independent_title="Community Tariff Design for Local Energy Sharing",
        tags=["energy", "microgrids", "sustainability"],
        original_sections={
            "Introduction": [
                "Community energy projects increasingly rely on renewable microgrids to keep critical services running during grid disruptions.",
                "Microgrids combine rooftop solar, battery storage, and controllable demand so neighborhoods can manage energy locally.",
                "The model is especially important for campuses, clinics, and municipal shelters that cannot tolerate long outages.",
            ],
            "Methodology": [
                "During the pilot, operators modeled hourly demand, battery state of charge, and local weather forecasts for the district network.",
                "An optimization routine scheduled charging, discharging, and backup generator use to minimize both cost and outage risk.",
                "The engineering team also ran emergency simulations to test how the system behaved during sudden transmission failures.",
            ],
            "Results": [
                "The microgrid cut peak imports from the main grid and supplied priority loads for longer than the previous diesel-only setup.",
                "Operators reported smoother voltage management once battery dispatch rules were aligned with forecast uncertainty.",
                "Residents responded positively when the project dashboard showed how local generation supported neighborhood resilience.",
            ],
            "Conclusion": [
                "Renewable microgrids deliver the most value when technical design is matched with transparent governance and maintenance planning.",
                "Community trust improves when operators explain curtailment decisions and publish service priorities in advance.",
                "Future projects should connect resilience metrics with equity goals so vulnerable users receive dependable protection.",
            ],
        },
        independent_sections={
            "Introduction": [
                "Another challenge in local energy systems is deciding how households should be billed when they share electricity resources.",
                "Tariff design influences whether residents view a neighborhood program as fair and understandable.",
                "Without clear pricing rules, even a technically sound project can face resistance from participants.",
            ],
            "Methodology": [
                "Policy analysts compared flat participation fees, time-based pricing, and credit schemes for exported solar energy.",
                "They interviewed residents about bill predictability and tested which pricing formats were easiest to explain at public meetings.",
                "The review also considered how concession programs could protect low-income households from sudden price swings.",
            ],
            "Results": [
                "Residents preferred tariffs that used a small fixed fee and a visible credit for locally generated power.",
                "More complex pricing formulas confused participants even when they promised slightly lower average bills.",
                "Clear billing examples improved enrollment more than aggressive short-term discounts.",
            ],
            "Conclusion": [
                "Successful energy sharing requires both engineering reliability and billing arrangements that people can trust.",
                "Tariff rules should therefore be tested with users before a new program is launched at scale.",
                "Future work could link tariff design with resilience incentives during emergencies.",
            ],
        },
    ),
    TopicFamily(
        family_id="F03",
        split="train",
        topic="Healthcare Cybersecurity",
        source_title="Cybersecurity Operations for Connected Hospitals",
        independent_title="Identity Verification Practices in Telehealth Services",
        tags=["healthcare", "cybersecurity", "risk-management"],
        original_sections={
            "Introduction": [
                "Hospitals increasingly connect infusion pumps, imaging systems, and clinical workstations to the same digital environment.",
                "That connectivity improves coordination, but it also expands the number of entry points available to ransomware groups.",
                "Cybersecurity programs in healthcare therefore have to protect patient care as well as information assets.",
            ],
            "Methodology": [
                "Security teams mapped medical devices, segmented sensitive networks, and created an asset inventory for unsupported systems.",
                "They added endpoint monitoring on administrative machines and practiced incident response drills with clinical supervisors.",
                "The hospital also reviewed vendor access privileges to identify accounts that no longer matched operational needs.",
            ],
            "Results": [
                "The updated controls shortened detection time for suspicious behavior on shared workstations and remote access gateways.",
                "Phishing simulations showed that staff responded faster once brief scenario-based training replaced annual slide decks.",
                "Clinical leaders were more willing to participate when the security team linked each safeguard to patient safety outcomes.",
            ],
            "Conclusion": [
                "Healthcare cybersecurity is strongest when technical controls, procurement policies, and clinical workflows are reviewed together.",
                "Executives should measure downtime risk, not just compliance checklists, when they prioritize security investments.",
                "Future planning must include older devices that cannot be patched easily but still support essential care.",
            ],
        },
        independent_sections={
            "Introduction": [
                "Telehealth expansion has made identity verification a daily operational concern for clinics offering remote appointments.",
                "Providers need to confirm that the correct patient is present without creating a confusing sign-in process.",
                "The issue is especially sensitive when services involve minors, interpreters, or shared family devices.",
            ],
            "Methodology": [
                "Clinic managers compared one-time passcodes, portal-based logins, and front-desk identity checks completed before each session.",
                "They reviewed drop-off points in the appointment journey and noted where patients asked for help.",
                "Special attention was given to accessibility barriers for older adults and patients with limited digital literacy.",
            ],
            "Results": [
                "Verification worked best when patients received a simple preparation checklist before the consultation day.",
                "Portal-only methods caused more confusion among first-time users than assisted verification through reception staff.",
                "Clear identity processes reduced appointment delays and improved clinician confidence at the start of calls.",
            ],
            "Conclusion": [
                "Secure telehealth requires authentication steps that are understandable as well as technically reliable.",
                "Designing those steps with patient support teams prevents avoidable friction during care delivery.",
                "Future service design should balance privacy expectations with practical access needs.",
            ],
        },
    ),
    TopicFamily(
        family_id="F04",
        split="train",
        topic="Sustainable Supply Chains",
        source_title="Emission Reduction Strategies in Retail Supply Chains",
        independent_title="Supplier Well-Being Audits in Global Procurement",
        tags=["supply-chain", "sustainability", "operations"],
        original_sections={
            "Introduction": [
                "Retailers are under pressure to reduce supply chain emissions without creating new delivery delays for customers.",
                "Most of the operational footprint sits upstream in production, packaging, and freight movement across multiple partners.",
                "As a result, sustainability teams now need data systems that connect environmental goals with daily logistics decisions.",
            ],
            "Methodology": [
                "The program gathered purchase order histories, shipment routes, and supplier energy disclosures for a twelve-month period.",
                "Analysts compared consolidation policies, packaging redesign options, and mode shifts from air freight to rail where feasible.",
                "Procurement managers also introduced quarterly scorecards so suppliers could see how energy use affected contract reviews.",
            ],
            "Results": [
                "Shipment consolidation lowered transport emissions on stable product lines without materially affecting service levels.",
                "Packaging redesign delivered fast gains because smaller cartons improved vehicle utilization across several regions.",
                "Suppliers engaged more seriously after the retailer paired reporting requests with practical improvement guidance.",
            ],
            "Conclusion": [
                "Sustainable supply chains improve when environmental metrics are embedded in routine procurement and planning meetings.",
                "Data transparency matters, but firms must also share transition support if they expect suppliers to change behavior.",
                "Future work should connect carbon reporting with resilience planning so disruptions do not erase climate gains.",
            ],
        },
        independent_sections={
            "Introduction": [
                "Global procurement teams are also being asked to review labor conditions and worker well-being across supplier networks.",
                "These social audits involve different evidence than emissions programs, yet they face similar coordination challenges.",
                "Buyers need processes that move beyond one-off compliance paperwork toward continuous improvement.",
            ],
            "Methodology": [
                "Audit managers combined worker interviews, overtime records, and grievance logs from factories in three regions.",
                "They compared remote monitoring tools with in-person site visits and tracked which method revealed more actionable issues.",
                "Suppliers were encouraged to submit corrective action plans that specified ownership and completion dates.",
            ],
            "Results": [
                "Factories responded better when audit findings were discussed with line supervisors rather than only senior executives.",
                "Worker hotlines generated more credible evidence after employees received information about confidentiality protections.",
                "Progress was strongest where buyers linked social expectations to long-term sourcing commitments.",
            ],
            "Conclusion": [
                "Social sustainability in procurement requires trust, follow-through, and clear escalation pathways for unresolved issues.",
                "Audits alone rarely improve conditions unless commercial teams support corrective action over time.",
                "Future studies can examine how environmental and labor programs interact in shared supplier scorecards.",
            ],
        },
    ),
    TopicFamily(
        family_id="F05",
        split="train",
        topic="Explainable AI in Credit Risk",
        source_title="Explainable AI for Responsible Credit Risk Decisions",
        independent_title="Fairness Monitoring in Consumer Lending Models",
        tags=["finance", "ai", "governance"],
        original_sections={
            "Introduction": [
                "Lenders increasingly use machine learning to estimate credit risk, but opaque models can make decisions difficult to justify.",
                "Regulators and customers both expect institutions to explain why an application was approved, declined, or referred for review.",
                "Explainable AI helps risk teams connect predictive performance with accountability requirements.",
            ],
            "Methodology": [
                "The evaluation compared gradient boosted models with simpler baselines on repayment history, income stability, and utilization data.",
                "Analysts generated local explanations for individual cases and global importance summaries for policy committees.",
                "They also tested whether explanation outputs stayed consistent when small changes were introduced to borderline applications.",
            ],
            "Results": [
                "Model performance improved over the baseline, but the clearest benefit came from faster review of contested decisions.",
                "Credit officers trusted the system more when explanations highlighted both positive and negative contributing factors.",
                "Consistency checks exposed a few unstable cases that were routed back to human review before deployment.",
            ],
            "Conclusion": [
                "Explainable AI supports responsible lending when institutions treat interpretability as part of governance rather than a final report.",
                "Documentation should show how explanations are used in appeals, overrides, and model monitoring routines.",
                "Future releases must examine whether explanation quality remains stable as borrower behavior changes over time.",
            ],
        },
        independent_sections={
            "Introduction": [
                "A related challenge in lending is determining whether a model behaves fairly across demographic and socioeconomic groups.",
                "Even transparent systems can produce unequal outcomes if monitoring focuses only on average accuracy.",
                "Fairness reviews therefore need operational thresholds that product teams understand and revisit regularly.",
            ],
            "Methodology": [
                "Risk managers tracked approval rates, manual review rates, and default performance across multiple customer segments.",
                "They combined quantitative metrics with policy reviews to see whether product rules amplified disparities.",
                "The monitoring process also documented when human overrides corrected or worsened unequal patterns.",
            ],
            "Results": [
                "Segment-level dashboards revealed gaps that were hidden when analysts looked only at portfolio-wide averages.",
                "Governance meetings improved once fairness findings were discussed alongside profit and loss metrics.",
                "Teams found it easier to act when monitoring reports linked disparities to concrete product settings.",
            ],
            "Conclusion": [
                "Fair lending requires repeated monitoring, not a single pre-launch validation exercise.",
                "Organizations need escalation procedures for cases where commercial goals conflict with fairness commitments.",
                "Future work can combine interpretability and fairness evidence in a unified governance review.",
            ],
        },
    ),
    TopicFamily(
        family_id="F06",
        split="train",
        topic="Urban Traffic Forecasting",
        source_title="Urban Traffic Forecasting with Multimodal Data",
        independent_title="Pedestrian Safety Planning Around Shared Streets",
        tags=["transport", "forecasting", "smart-city"],
        original_sections={
            "Introduction": [
                "Traffic agencies now combine road sensors, public transport feeds, and event calendars to forecast congestion more accurately.",
                "Urban mobility patterns change quickly when weather, school schedules, or venue traffic alter normal demand.",
                "Forecasting tools help city teams adjust signals and communicate travel advice before queues become severe.",
            ],
            "Methodology": [
                "The project ingested loop detector counts, bus arrival data, rainfall information, and venue schedules for the central corridor.",
                "Forecast models predicted traffic speed fifteen, thirty, and sixty minutes ahead so operators could compare intervention windows.",
                "Engineers also tested whether adding real-time transit crowding data improved estimates around rail stations.",
            ],
            "Results": [
                "Short-horizon forecasts were accurate enough to support signal timing adjustments during evening peaks and stadium events.",
                "Transit inputs improved predictions near interchanges where car and bus demand shifted together.",
                "Control room staff said the dashboard was most useful when forecasts were paired with recommended actions instead of raw charts alone.",
            ],
            "Conclusion": [
                "Traffic forecasting systems are most effective when they support operational choices rather than passive monitoring.",
                "Agencies should review forecast error after major events so model updates reflect unusual mobility patterns.",
                "Future deployments can integrate curb usage and freight deliveries to capture a wider share of urban demand.",
            ],
        },
        independent_sections={
            "Introduction": [
                "Cities are also redesigning shared streets to improve pedestrian comfort and reduce conflict with fast-moving vehicles.",
                "These programs require planners to understand where people pause, cross, and gather during different times of day.",
                "Safety planning therefore depends on observation methods that go beyond vehicle throughput alone.",
            ],
            "Methodology": [
                "Urban design teams conducted walking audits, conflict mapping, and video review at school zones and market streets.",
                "They compared permanent infrastructure changes with low-cost temporary measures such as bollards, paint, and curb extensions.",
                "Community workshops were used to identify locations where existing traffic rules felt confusing or unsafe.",
            ],
            "Results": [
                "Pedestrian comfort improved most where slower turning movements were paired with clearer crossing priorities.",
                "Temporary measures provided useful evidence, but residents preferred projects that included lasting design commitments.",
                "School communities placed high value on visible crossing support during arrival and departure periods.",
            ],
            "Conclusion": [
                "Shared street planning should combine safety data, local observation, and community feedback before permanent designs are finalized.",
                "Vehicle efficiency metrics alone are not enough to judge whether a corridor serves people well.",
                "Future studies can compare pedestrian outcomes before and after signal policy changes in the same district.",
            ],
        },
    ),
    TopicFamily(
        family_id="F07",
        split="validation",
        topic="Telemedicine Chronic Care",
        source_title="Telemedicine Support for Chronic Disease Management",
        independent_title="Appointment Navigation Services for Virtual Clinics",
        tags=["telemedicine", "chronic-care", "digital-health"],
        original_sections={
            "Introduction": [
                "Remote care programs are increasingly used to support patients managing chronic conditions between in-person appointments.",
                "Telemedicine can reduce travel burden, but long-term benefit depends on whether patients stay engaged with the service.",
                "Successful programs therefore combine clinical review with practical follow-up that fits daily routines.",
            ],
            "Methodology": [
                "The clinic combined video consultations, medication reminders, and home monitoring data for patients with diabetes and hypertension.",
                "Nurses reviewed blood pressure trends, missed reading alerts, and symptom notes before each scheduled virtual check-in.",
                "Escalation rules directed high-risk cases to same-day phone calls or in-person assessment when measurements drifted outside safe ranges.",
            ],
            "Results": [
                "Patients who uploaded readings consistently were more likely to adjust treatment plans early rather than waiting for the next clinic visit.",
                "Nurses reported that structured dashboards reduced time spent searching through scattered patient messages.",
                "Engagement improved when the program offered short coaching calls after each major medication change.",
            ],
            "Conclusion": [
                "Telemedicine supports chronic care best when digital monitoring is linked to clear response pathways and relationship-based follow-up.",
                "Programs should track drop-off points carefully because technical access alone does not guarantee sustained participation.",
                "Future service design must account for language support, caregiver involvement, and device usability at home.",
            ],
        },
        independent_sections={
            "Introduction": [
                "Virtual clinics also need practical appointment navigation so patients can move through registration and follow-up without confusion.",
                "Many missed virtual visits happen because patients are unsure about links, timing, or required preparation steps.",
                "Navigation services can therefore be as important as the clinical platform itself.",
            ],
            "Methodology": [
                "Service coordinators tested reminder messages, call-center scripts, and translated appointment instructions for different patient groups.",
                "They tracked how often patients requested help before a visit and which preparation errors caused delays.",
                "The evaluation also reviewed how staff handed off unresolved access problems to technical support teams.",
            ],
            "Results": [
                "Simple reminder sequences reduced no-show rates more effectively than long instructional emails sent only once.",
                "Patients appreciated having a named contact person when appointments involved multiple specialists.",
                "Translated instructions were especially valuable when households shared one device across several family members.",
            ],
            "Conclusion": [
                "Navigation support is a core part of virtual care delivery, not just an administrative extra.",
                "Programs that reduce confusion at the access stage create better conditions for clinical engagement later on.",
                "Future work can combine navigation data with quality-of-care outcomes for virtual services.",
            ],
        },
    ),
    TopicFamily(
        family_id="F08",
        split="validation",
        topic="Precision Agriculture IoT",
        source_title="Precision Agriculture with Field Sensors and Drone Imagery",
        independent_title="Cooperative Training Models for Digital Farming Adoption",
        tags=["agriculture", "iot", "precision-farming"],
        original_sections={
            "Introduction": [
                "Agronomy teams increasingly deploy field sensors and drone imagery to manage irrigation, fertilizer use, and crop stress.",
                "Precision agriculture tools are attractive because they can reveal small field variations that are hidden in manual inspection.",
                "However, the value of the technology depends on whether growers can turn data into timely operational decisions.",
            ],
            "Methodology": [
                "The farm trial combined soil moisture probes, weather stations, and multispectral drone flights across several irrigation zones.",
                "Agronomists compared sensor alerts with scouting notes and adjusted watering schedules according to crop growth stage.",
                "They also reviewed fertilizer application maps to see whether low-performing patches required different treatment plans.",
            ],
            "Results": [
                "Sensor-guided irrigation reduced unnecessary watering on plots that retained moisture longer after rainfall.",
                "Drone imagery helped staff find stressed areas earlier than routine field walks on large blocks.",
                "The biggest gains came when field managers discussed the data together instead of treating each dashboard separately.",
            ],
            "Conclusion": [
                "Precision agriculture performs best when digital measurements are integrated with agronomic judgment and local knowledge.",
                "Growers need tools that summarize action priorities rather than overwhelming them with raw observations.",
                "Future deployments should study how seasonal labor, connectivity limits, and equipment maintenance affect adoption.",
            ],
        },
        independent_sections={
            "Introduction": [
                "Digital farming programs also depend on whether growers feel confident enough to adopt unfamiliar tools in everyday operations.",
                "Cooperative training models can reduce that barrier by letting farmers learn from peers in similar production systems.",
                "Adoption therefore involves social support as much as technical capability.",
            ],
            "Methodology": [
                "Extension officers organized demonstration days, peer-led workshops, and follow-up visits across a regional cooperative.",
                "They recorded which training formats helped growers move from curiosity to regular tool use within one season.",
                "The review also noted how financing options and service support influenced adoption decisions.",
            ],
            "Results": [
                "Growers were more willing to test new tools when they saw examples from farms with comparable water and labor constraints.",
                "Hands-on workshops produced better retention than vendor presentations that focused mostly on features.",
                "Adoption increased when cooperatives linked training with shared maintenance support and group purchasing.",
            ],
            "Conclusion": [
                "Digital agriculture spreads faster when training is local, practical, and tied to trusted peer networks.",
                "Programs should therefore invest in demonstration capacity as well as device procurement.",
                "Future studies can compare training-led adoption with subsidy-led adoption across regions.",
            ],
        },
    ),
    TopicFamily(
        family_id="F09",
        split="test",
        topic="Cloud Disaster Recovery",
        source_title="Cloud Disaster Recovery for Business Continuity",
        independent_title="Cloud Cost Governance in Multi-Team Platforms",
        tags=["cloud", "resilience", "devops"],
        original_sections={
            "Introduction": [
                "Cloud disaster recovery plans are now central to business continuity for organizations running critical digital services.",
                "Outages can originate from application failures, regional incidents, or operational mistakes during routine deployments.",
                "Recovery design must therefore address both infrastructure redundancy and the speed of coordinated response.",
            ],
            "Methodology": [
                "The engineering team configured multi-region backups, infrastructure templates, and automated failover checks for key services.",
                "They practiced recovery drills every month and measured how long databases, queues, and identity services took to return.",
                "Runbooks were updated after each exercise to capture communication gaps between platform, security, and product teams.",
            ],
            "Results": [
                "Frequent rehearsal reduced uncertainty during incidents because teams knew which systems could be restored in parallel.",
                "Backup integrity improved once restore tests became part of the release cycle rather than a separate audit activity.",
                "Leadership gained confidence when recovery reports showed realistic timelines instead of theoretical capacity statements.",
            ],
            "Conclusion": [
                "Cloud resilience depends on disciplined testing, shared ownership, and clear recovery objectives for every major service.",
                "Organizations should document not only technical failover steps but also decision rights during stressful incidents.",
                "Future work can examine how platform standardization affects recovery performance across multiple business units.",
            ],
        },
        independent_sections={
            "Introduction": [
                "As cloud usage grows, many organizations struggle to understand which teams are driving cost increases across shared platforms.",
                "Cost governance is difficult because spending is distributed across storage, compute, data transfer, and third-party services.",
                "A reliable governance model must therefore help teams see trade-offs without slowing experimentation completely.",
            ],
            "Methodology": [
                "FinOps analysts grouped spend by product line, environment type, and architectural pattern for a six-month review.",
                "They examined idle resources, oversized workloads, and inconsistent tagging that made accountability difficult.",
                "Engineering leads also tested budget alerts and approval workflows for unusually expensive configuration changes.",
            ],
            "Results": [
                "The biggest savings came from removing forgotten development environments and resizing over-provisioned databases.",
                "Teams acted faster when cost reports were linked to named owners and visible technical recommendations.",
                "Budget alerts worked best when they prompted review conversations rather than automatic blame.",
            ],
            "Conclusion": [
                "Cloud cost governance succeeds when financial visibility is embedded in engineering routines and platform design standards.",
                "Purely finance-driven controls rarely work if engineers cannot see how to change usage patterns safely.",
                "Future studies can compare cost optimization programs across centralized and decentralized platform teams.",
            ],
        },
    ),
    TopicFamily(
        family_id="F10",
        split="test",
        topic="Battery Recycling",
        source_title="Battery Recycling Pathways for the Circular Economy",
        independent_title="Charging Infrastructure Standards for Electric Mobility",
        tags=["battery", "circular-economy", "materials"],
        original_sections={
            "Introduction": [
                "Battery recycling programs are becoming essential as electric vehicle adoption increases around the world.",
                "Used battery packs contain valuable materials, but recovery is complicated by safety risks, design variation, and transport rules.",
                "A circular economy approach therefore depends on systems that can identify, sort, and process batteries efficiently.",
            ],
            "Methodology": [
                "The recycling study tracked pack collection, diagnostic screening, disassembly workflows, and material recovery rates at a pilot facility.",
                "Engineers compared modules suitable for second-life storage with units that required immediate material extraction.",
                "The project also reviewed how labeling quality affected worker safety and throughput during dismantling.",
            ],
            "Results": [
                "Screening batteries before disassembly reduced avoidable handling time and improved routing to reuse or recycling streams.",
                "Recovery rates were highest when product information was available in a consistent digital format for the facility.",
                "Operators noted that process bottlenecks often came from packaging and transport requirements rather than chemistry alone.",
            ],
            "Conclusion": [
                "Battery recycling works best when product design, logistics, and recovery operations are planned as one system.",
                "Manufacturers can support circularity by improving traceability and making pack architecture easier to interpret safely.",
                "Future regulation should align producer responsibility with practical data-sharing requirements across the value chain.",
            ],
        },
        independent_sections={
            "Introduction": [
                "Electric mobility growth also depends on charging infrastructure that is dependable, interoperable, and easy to locate.",
                "Drivers experience frustration when charging sites differ in connector standards, payment systems, or reliability.",
                "Infrastructure planning therefore requires coordination between technical standards and user experience design.",
            ],
            "Methodology": [
                "Transport planners reviewed charging uptime records, connector compatibility data, and site accessibility across urban corridors.",
                "They interviewed drivers about common failure points and compared maintenance models used by different operators.",
                "The assessment also considered how signage and pricing clarity influenced station choice during longer trips.",
            ],
            "Results": [
                "Drivers valued charger reliability more than headline power ratings when choosing repeat charging locations.",
                "Clear payment instructions reduced abandoned sessions and support calls at mixed-operator sites.",
                "Site operators improved trust when they published uptime metrics and repair timelines openly.",
            ],
            "Conclusion": [
                "Charging infrastructure standards should support both hardware compatibility and a predictable user journey.",
                "Planning decisions must therefore include maintenance capacity, accessibility, and transparent information for drivers.",
                "Future research can compare how regional standardization affects charger utilization over time.",
            ],
        },
    ),
]


def lowercase_first(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def normalize_sentence(text: str) -> str:
    sentence = " ".join(text.split()).strip()
    if not sentence.endswith("."):
        sentence += "."
    return sentence


def replace_phrases(text: str) -> str:
    updated = text
    for source, target in LIGHT_REPLACEMENTS:
        updated = updated.replace(source, target)
    return updated


def lightly_paraphrase(sentence: str, index: int) -> str:
    updated = replace_phrases(sentence)
    if index % 2 == 0:
        updated = f"{LIGHT_PREFIXES[index % len(LIGHT_PREFIXES)]}, {lowercase_first(updated)}"
    elif " because " in updated:
        left, right = updated[:-1].split(" because ", maxsplit=1)
        updated = f"Because {lowercase_first(right)}, {lowercase_first(left)}."
    return normalize_sentence(updated)


def heavily_paraphrase(sentence: str, index: int) -> str:
    updated = replace_phrases(sentence).rstrip(".")
    if " to " in updated and len(updated.split(" to ", maxsplit=1)[0].split()) > 4:
        left, right = updated.split(" to ", maxsplit=1)
        transformed = f"To {lowercase_first(right)}, {lowercase_first(left)}"
    elif " when " in updated:
        left, right = updated.split(" when ", maxsplit=1)
        transformed = f"When {lowercase_first(right)}, {lowercase_first(left)}"
    elif " and " in updated and index % 2 == 1:
        left, right = updated.split(" and ", maxsplit=1)
        transformed = f"{right.capitalize()}, while {lowercase_first(left)}"
    else:
        transformed = f"{HEAVY_PREFIXES[index % len(HEAVY_PREFIXES)]} {lowercase_first(updated)}"
    return normalize_sentence(transformed)


def paraphrase_sections(sections: dict[str, list[str]], strength: str) -> dict[str, list[str]]:
    paraphrased: dict[str, list[str]] = {}
    for section_index, section in enumerate(SECTION_ORDER):
        transformed_sentences: list[str] = []
        for sentence_index, sentence in enumerate(sections[section]):
            position = section_index * 3 + sentence_index
            if strength == "light":
                transformed_sentences.append(lightly_paraphrase(sentence, position))
            else:
                transformed_sentences.append(heavily_paraphrase(sentence, position))
        paraphrased[section] = transformed_sentences
    return paraphrased


def direct_copy_sections(sections: dict[str, list[str]]) -> dict[str, list[str]]:
    copied = {section: list(sentences) for section, sentences in sections.items()}
    copied["Conclusion"] = list(copied["Conclusion"]) + [
        "The document reproduces the original study wording with only a minimal framing sentence."
    ]
    return copied


def mosaic_sections(source_sections: dict[str, list[str]], independent_sections: dict[str, list[str]]) -> dict[str, list[str]]:
    return {
        "Introduction": [
            independent_sections["Introduction"][0],
            source_sections["Introduction"][1],
            lightly_paraphrase(source_sections["Introduction"][2], 2),
        ],
        "Methodology": [
            source_sections["Methodology"][0],
            lightly_paraphrase(source_sections["Methodology"][1], 4),
            source_sections["Methodology"][2],
        ],
        "Results": [
            lightly_paraphrase(source_sections["Results"][0], 6),
            source_sections["Results"][1],
            independent_sections["Results"][2],
        ],
        "Conclusion": [
            independent_sections["Conclusion"][0],
            heavily_paraphrase(source_sections["Conclusion"][1], 10),
            source_sections["Conclusion"][2],
        ],
    }


def build_markdown(
    doc_id: str,
    family: TopicFamily,
    title: str,
    variant: str,
    label: str,
    sections: dict[str, list[str]],
    source_doc_id: str | None,
) -> str:
    tags = ", ".join(family.tags)
    lines = [
        "---",
        f"doc_id: {doc_id}",
        f"family_id: {family.family_id}",
        f"topic: {family.topic}",
        f"split: {family.split}",
        f"variant: {variant}",
        f"plagiarism_label: {label}",
        f"primary_source_doc_id: {source_doc_id or ''}",
        f"tags: [{tags}]",
        "---",
        "",
        f"# {title}",
        "",
    ]
    for section in SECTION_ORDER:
        lines.append(f"## {section}")
        lines.append(" ".join(sections[section]))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def create_documents(family: TopicFamily) -> list[dict[str, str]]:
    source_doc_id = f"{family.family_id.lower()}_source"
    variants = [
        {
            "doc_id": source_doc_id,
            "title": family.source_title,
            "variant": "source",
            "plagiarism_label": "none",
            "sections": family.original_sections,
            "primary_source_doc_id": "",
            "expected_similarity_band": "self-reference only",
            "sections_with_overlap": "none",
        },
        {
            "doc_id": f"{family.family_id.lower()}_direct_copy",
            "title": f"Replicated Draft on {family.topic}",
            "variant": "direct_copy",
            "plagiarism_label": "direct",
            "sections": direct_copy_sections(family.original_sections),
            "primary_source_doc_id": source_doc_id,
            "expected_similarity_band": "0.85-1.00",
            "sections_with_overlap": "Introduction|Methodology|Results|Conclusion",
        },
        {
            "doc_id": f"{family.family_id.lower()}_paraphrase_light",
            "title": f"Reworded Review of {family.topic}",
            "variant": "paraphrase_light",
            "plagiarism_label": "semantic",
            "sections": paraphrase_sections(family.original_sections, "light"),
            "primary_source_doc_id": source_doc_id,
            "expected_similarity_band": "0.70-0.88",
            "sections_with_overlap": "Introduction|Methodology|Results|Conclusion",
        },
        {
            "doc_id": f"{family.family_id.lower()}_paraphrase_heavy",
            "title": f"Reframed Discussion of {family.topic}",
            "variant": "paraphrase_heavy",
            "plagiarism_label": "semantic",
            "sections": paraphrase_sections(family.original_sections, "heavy"),
            "primary_source_doc_id": source_doc_id,
            "expected_similarity_band": "0.55-0.78",
            "sections_with_overlap": "Introduction|Methodology|Results|Conclusion",
        },
        {
            "doc_id": f"{family.family_id.lower()}_mosaic",
            "title": f"Composite Notes on {family.topic}",
            "variant": "mosaic",
            "plagiarism_label": "mixed",
            "sections": mosaic_sections(family.original_sections, family.independent_sections),
            "primary_source_doc_id": source_doc_id,
            "expected_similarity_band": "0.60-0.84",
            "sections_with_overlap": "Introduction|Methodology|Results|Conclusion",
        },
        {
            "doc_id": f"{family.family_id.lower()}_independent",
            "title": family.independent_title,
            "variant": "independent",
            "plagiarism_label": "none",
            "sections": family.independent_sections,
            "primary_source_doc_id": "",
            "expected_similarity_band": "0.00-0.20",
            "sections_with_overlap": "none",
        },
    ]

    rows: list[dict[str, str]] = []
    for variant in variants:
        doc_path = DOCUMENTS_DIR / family.split / f"{variant['doc_id']}.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        content = build_markdown(
            doc_id=variant["doc_id"],
            family=family,
            title=variant["title"],
            variant=variant["variant"],
            label=variant["plagiarism_label"],
            sections=variant["sections"],
            source_doc_id=variant["primary_source_doc_id"] or None,
        )
        doc_path.write_text(content, encoding="utf-8")
        rows.append(
            {
                "doc_id": variant["doc_id"],
                "family_id": family.family_id,
                "split": family.split,
                "topic": family.topic,
                "title": variant["title"],
                "variant": variant["variant"],
                "plagiarism_label": variant["plagiarism_label"],
                "primary_source_doc_id": variant["primary_source_doc_id"],
                "expected_similarity_band": variant["expected_similarity_band"],
                "sections_with_overlap": variant["sections_with_overlap"],
                "word_count": str(len(content.split())),
                "path": str(doc_path.relative_to(DATASET_DIR)).replace("\\", "/"),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if DATASET_DIR.exists():
        shutil.rmtree(DATASET_DIR)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    document_rows: list[dict[str, str]] = []
    pair_rows: list[dict[str, str]] = []

    for family in FAMILIES:
        rows = create_documents(family)
        document_rows.extend(rows)
        source_doc_id = f"{family.family_id.lower()}_source"
        for row in rows:
            if row["doc_id"] == source_doc_id or not row["primary_source_doc_id"]:
                continue
            pair_rows.append(
                {
                    "document_id": row["doc_id"],
                    "source_document_id": row["primary_source_doc_id"],
                    "family_id": family.family_id,
                    "split": family.split,
                    "topic": family.topic,
                    "variant": row["variant"],
                    "expected_match_type": row["plagiarism_label"],
                    "expected_similarity_band": row["expected_similarity_band"],
                    "sections_with_overlap": row["sections_with_overlap"],
                }
            )

    write_csv(
        DATASET_DIR / "metadata.csv",
        document_rows,
        [
            "doc_id",
            "family_id",
            "split",
            "topic",
            "title",
            "variant",
            "plagiarism_label",
            "primary_source_doc_id",
            "expected_similarity_band",
            "sections_with_overlap",
            "word_count",
            "path",
        ],
    )
    write_csv(
        DATASET_DIR / "pair_labels.csv",
        pair_rows,
        [
            "document_id",
            "source_document_id",
            "family_id",
            "split",
            "topic",
            "variant",
            "expected_match_type",
            "expected_similarity_band",
            "sections_with_overlap",
        ],
    )

    summary = {
        "dataset_name": "semantic_plagiarism_benchmark",
        "total_documents": len(document_rows),
        "total_families": len(FAMILIES),
        "documents_per_family": 6,
        "split_counts": {
            split: sum(1 for row in document_rows if row["split"] == split)
            for split in ("train", "validation", "test")
        },
        "variant_counts": {
            variant: sum(1 for row in document_rows if row["variant"] == variant)
            for variant in ("source", "direct_copy", "paraphrase_light", "paraphrase_heavy", "mosaic", "independent")
        },
        "topics": [family.topic for family in FAMILIES],
    }
    (DATASET_DIR / "README.md").write_text(README_CONTENT, encoding="utf-8")
    (DATASET_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
