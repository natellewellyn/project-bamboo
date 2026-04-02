# EL Compliance Deep Dive: What You Need to Know to Build This Product

*Prepared for Nate Llewellyn — Flashlight Learning — March 25, 2026*

---

## Why Compliance Is the Beating Heart of This Market

Before diving into the specifics, it's worth understanding why compliance isn't just one feature among many — it's the gravitational center around which nearly every EL director's purchasing decision orbits.

EL directors live under overlapping layers of legal obligation: federal civil rights law, federal education funding law, state education codes, and OCR (Office for Civil Rights) enforcement. When they buy a product like Ellevation, they're not buying a "nice to have" — they're buying insurance against audit findings, OCR complaints, and the very real consequence of losing federal funding. This means compliance workflows aren't just a checkbox for your product. They're the reason the buyer opens her wallet.

---

## The Legal Framework: Three Layers You Need to Understand

### Layer 1: Civil Rights Law (Non-Negotiable, No Funding Tied)

**Lau v. Nichols (1974)** — The Supreme Court ruled that schools receiving federal funding must take affirmative steps to overcome language barriers. This is a civil rights obligation — it applies regardless of whether a district receives Title III money. A district cannot say "we didn't apply for Title III so we don't have to serve ELs." They do.

**Castañeda v. Pickard (1981)** — The 5th Circuit created a three-pronged test that OCR still uses today to evaluate whether a district's EL program is adequate:

1. **Theory:** Is the program based on a recognized educational theory? (Almost every program passes this test — there are many accepted approaches.)
2. **Implementation:** Are resources, staff, and practices sufficient to actually implement that theory? (This is where districts fail. Having a bilingual program on paper but no bilingual teachers = failure.)
3. **Results:** Is the program producing results over time? If students aren't gaining proficiency, the program must be modified. (This is where data becomes essential — districts must be able to demonstrate progress.)

**Why this matters for your product:** Any compliance tool must help districts answer the Castañeda test. Can they show their program design? Can they document that they have the resources to implement it? Can they demonstrate results with data? The product that makes answering these three questions easy wins.

**Equal Educational Opportunities Act (EEOA, 1974)** — Federal statute that codified the obligation: "No state shall deny equal educational opportunity... by the failure of an educational agency to take appropriate action to overcome language barriers that impede equal participation." This gives parents a private right of action — they can sue.

### Layer 2: Federal Education Law (Funding-Tied Requirements)

**ESSA / Title III** — The Every Student Succeeds Act (2015) replaced NCLB and is the current governing framework. Title III is the section specifically about English learners. Key requirements:

**Identification and placement (within 30 days of enrollment):**
- Administer a Home Language Survey (HLS) to every enrolling student
- If a language other than English is indicated, screen for English proficiency using a state-approved screener (WIDA Screener in WIDA states, ELPAC Initial in California, etc.)
- Place identified EL students in an appropriate Language Instruction Educational Program (LIEP)
- Notify parents within 30 days of the start of the school year (or within 2 weeks if the student enrolls mid-year)

**Parent notification must include (this is specific and audited):**
- The reasons for identifying their child as an EL
- The child's level of English proficiency and how it was assessed
- The method of instruction used in the child's program and methods used in other available programs
- How the program will meet the child's educational strengths and help them learn English and meet academic standards
- Exit criteria for the program
- If the child has a disability, how the language program meets the IEP objectives
- The parent's right to decline services or remove the child from the program (opt-out right)

**Annual assessment:**
- Every identified EL must be assessed for English proficiency annually using the state's approved assessment (ACCESS in WIDA states)
- Results must be reported to parents and to the state

**Reclassification and monitoring:**
- Districts must establish criteria for reclassifying students out of EL status
- Reclassified students must be monitored for at least 4 years (ESSA requirement; some states require only 2 years, but 4 is the federal floor)
- If a reclassified student is struggling, the district must provide additional support and may need to re-designate

**Title III funding specifics:**
- Formula grants to states, which sub-grant to districts
- Supplemental — must supplement, not supplant, state and local funding
- Requires a "plan of service" describing how funds will be used
- Districts must report on specific accountability indicators
- If a district fails to meet Title III progress targets for 2+ consecutive years, the state must take corrective action

### Layer 3: State Education Law (The Wildcard)

Every state adds its own requirements on top of federal law. This is where compliance gets truly complex and where a flexible product has an advantage over a rigid one. Key areas of variation:

**Reclassification criteria** vary significantly:
- Some states use only the ACCESS/ELPAC score (e.g., a composite score of 4.5 or 5.0)
- Others require multiple measures: ACCESS score + academic achievement + teacher recommendation + parent consultation
- Some states have specific criteria for different grade bands
- A few states have an additional local assessment requirement

**Program model mandates:**
- Texas requires Bilingual Education programs in any district with 20+ EL students of the same language in the same grade
- Some states mandate specific instructional minute requirements based on proficiency level (e.g., New York's "Units of Study" requirements)
- California's Proposition 58 (2016) expanded bilingual program options after decades of English-only policy

**Monitoring periods:**
- Federal floor: 4 years post-reclassification
- Some states use 2 years (they were grandfathered from NCLB provisions)
- During monitoring, districts must track academic performance and intervene if students are struggling

**Staffing requirements:**
- States differ on what certification/endorsement EL teachers need (ESL endorsement, bilingual certification, TESOL degree, etc.)
- Some states have alternative pathways or waiver provisions
- Paraprofessional requirements vary

---

## WIDA: The Assessment Ecosystem You're Building Around

### What WIDA Is

WIDA (originally "World-Class Instructional Design and Assessment") is a consortium housed at the University of Wisconsin-Madison. It's not a government agency — it's a membership organization of states that have collectively adopted its standards and assessments. As of 2026, WIDA member states and territories include 41 states, Washington DC, and several US territories. The major non-WIDA states are California (uses ELPAC), Texas (uses TELPAS), and New York (uses NYSESLAT, though they also use WIDA standards).

### The WIDA Standards Framework

WIDA provides English Language Development (ELD) standards that describe what EL students should be able to do at each proficiency level across academic content areas. The five standards are:

1. **Social and Instructional Language** — Language for social interaction and classroom routines
2. **Language of Language Arts** — Language needed for ELA content
3. **Language of Mathematics** — Language needed for math content
4. **Language of Science** — Language needed for science content
5. **Language of Social Studies** — Language needed for social studies content

Each standard is articulated across six proficiency levels and multiple grade-level clusters (K, 1, 2-3, 4-5, 6-8, 9-12).

### ACCESS for ELLs — The High-Stakes Annual Test

ACCESS (Assessing Comprehension and Communication in English State-to-State) is the annual summative English language proficiency assessment that virtually all EL students in WIDA states must take. It is THE compliance assessment — the one that determines whether students can be reclassified, whether districts are making adequate progress, and what gets reported to the state and feds.

**Four domains tested:** Listening, Speaking, Reading, Writing

**Score reporting:**
- Domain scores: 1.0–6.0 for each of the four domains
- Composite score: Weighted combination (Reading 35%, Writing 35%, Listening 15%, Speaking 15%)
- Proficiency levels:
  - 1 — Entering
  - 2 — Emerging (previously "Beginning")
  - 3 — Developing
  - 4 — Expanding (previously "Intermediate")
  - 5 — Bridging
  - 6 — Reaching

**Testing window:** Typically January through March (states set specific windows)

**Results availability:** Usually May through June — this is a critical data moment for EL departments because results drive reclassification decisions that must happen before the next school year

**Score delivery:** Through WIDA AMS (Assessment Management System) — districts download score files and need to get them into their SIS and/or EL management platform

**Alternate ACCESS:** For EL students with the most significant cognitive disabilities (those who take the state's alternate academic assessment). Scored on a different scale.

### WIDA Screener — The Identification Tool

When a Home Language Survey indicates a student might be an EL, the district administers the WIDA Screener (grades 1-12) or WIDA Screener for Kindergarten to determine initial English proficiency. This is what happens within that 30-day identification window.

**Product implication:** Your system needs to capture both screener results (initial identification) and annual ACCESS results (ongoing proficiency tracking). The screener result establishes the student's initial proficiency level and triggers their entry into EL services.

### WIDA AMS (Assessment Management System)

This is WIDA's online portal where districts manage testing — registering students, assigning test sessions, and retrieving results. Score data can be exported as CSV files. Many districts then need to manually import this data into their SIS or EL platform.

**Product opportunity:** If you can streamline the WIDA AMS → your platform data flow (either through direct import of WIDA score files or, ideally, an API integration), you eliminate a major pain point. Districts currently do a lot of manual data entry or CSV juggling to get ACCESS scores where they need them.

---

## The Data: What Districts Must Track and Where It Lives

### The Student Record for an EL Student

For each identified EL student, a district needs to maintain (and potentially report) data across several categories. Here's what a complete student compliance record looks like:

**Identification data:**
- Home Language Survey results (date administered, language(s) indicated)
- Initial screener administered (WIDA Screener, ELPAC Initial, etc.)
- Initial screener results (domain scores and composite)
- Date of initial identification as EL
- Parent notification date and method (letter sent, language of notification)
- Program placement (which LIEP model, when placed)

**Annual assessment data (every year the student is an EL):**
- ACCESS/ELPAC scores — all domains plus composite
- Year-over-year growth trajectory
- Testing accommodations used (if any)
- Whether the student participated (non-participation must be explained)

**Service delivery data:**
- Type of EL services received (pull-out, push-in, sheltered, bilingual, etc.)
- Minutes of service per week
- Teacher providing services (and their certification status)
- Accommodations and modifications in general education classes

**Academic performance data:**
- Grades in core content areas
- State academic assessment results (the regular state test, not ACCESS)
- Benchmark/interim assessment results (this is where Flashlight data comes in)
- Attendance and discipline data (for equity monitoring)

**Reclassification data (when a student exits):**
- Date of reclassification
- Criteria met (ACCESS score, grades, teacher input, parent consultation — whatever the state requires)
- Evidence documentation (the actual scores and records that justified the decision)

**Post-reclassification monitoring data (4 years after exit):**
- Academic grades each semester/year
- State test results
- Any intervention provided if the student struggled
- Final monitoring exit date

### Where This Data Currently Lives (The Fragmentation Problem)

This is the core problem your product needs to solve. Today, in a typical district:

| Data | Where It Lives | Format |
|------|---------------|--------|
| Student demographics, enrollment | SIS (PowerSchool, Infinite Campus) | Database, accessible via API or Clever/ClassLink |
| Home Language Survey results | Often paper forms or scanned PDFs | Varies wildly |
| WIDA Screener results | WIDA AMS or manually entered in SIS | CSV export from WIDA AMS |
| ACCESS scores | WIDA AMS → imported to SIS (hopefully) | CSV export, sometimes PDF score reports |
| Flashlight benchmark scores | Flashlight platform | Flashlight's system (you own this) |
| State academic test scores | State assessment portal | CSV or API |
| Service delivery logs | Spreadsheets, Ellevation, or paper | Excel, or platform-specific |
| Parent notifications | Word docs, filing cabinets, sometimes Ellevation | Paper or PDF |
| Reclassification decisions | Spreadsheets, Ellevation, or paper forms | Varies |
| Monitoring records | Spreadsheets or Ellevation | Varies |
| Teacher certification records | HR/SIS | Often a separate HR system |

The EL specialist's daily reality is stitching all of this together. They toggle between 4-6 systems to answer a simple question like "Is this student eligible for reclassification?" That question requires: current ACCESS score (WIDA AMS or SIS), academic grades (SIS), teacher recommendation (email or form), and state assessment results (state portal). If the district doesn't have Ellevation or a similar platform, the specialist is doing this in Excel.

---

## The Reports: What Has to Be Produced and When

### Federal Reports

**Title III Annual Performance Report** — Districts receiving Title III funds must report to the state (which then reports to ED) on:
- Number and percentage of EL students making progress toward English proficiency (as measured by ACCESS/ELPAC)
- Number and percentage of EL students attaining English proficiency (reclassified)
- Number and percentage of EL students meeting challenging state academic content standards
- These are broken down by subgroups when numbers are large enough

**ESSA State Plan Accountability** — States must include an English Learner Progress indicator in their accountability system. This typically measures year-over-year growth on ACCESS/ELPAC. Districts need to be able to produce the underlying data.

**CRDC (Civil Rights Data Collection)** — The Office for Civil Rights collects data from every public school district every other year. EL-related data points include:
- EL student enrollment by school
- EL students in gifted/talented programs
- EL students in AP/IB courses
- EL students receiving special education services
- EL students experiencing discipline (suspensions, expulsions)
- This data is public and used by OCR to identify potential civil rights issues

### State Reports (Highly Variable)

States typically require districts to report on some combination of:
- Total EL enrollment by school, grade, language, proficiency level
- New identifications during the year
- Students receiving services by program model type
- ACCESS/ELPAC participation rates and results
- Reclassification rates
- Long-term EL (LTEL) counts — students who have been EL for 5+ years
- Post-reclassification monitoring status and outcomes
- Title III expenditure reports
- Staffing reports (ESL-certified teachers, caseloads)

**Reporting cycles:** Most state reporting happens annually, typically in the fall (for prior year data) or in conjunction with the state's annual data collection window. Some states have mid-year reporting requirements.

### Local/Board Reports

EL directors typically produce for their school board:
- Annual program overview: enrollment trends, demographics, languages served
- Assessment results: ACCESS growth and proficiency rates, comparison to state averages
- Reclassification rates and trends
- LTEL analysis: how many students have been EL for 5+ years, what's being done
- Achievement gap data: EL students vs. non-EL students on state tests
- Budget and resource allocation
- Compliance status: any audit findings or corrective actions

### Compliance Monitoring/Audit Reports

States periodically audit districts for compliance (sometimes called "monitoring visits" or "program reviews"). When this happens, the district must produce documentation showing:
- Proper and timely identification procedures
- Evidence of parent notification (copies of letters, records of delivery)
- Service delivery documentation
- Qualified staffing evidence
- Assessment participation and results
- Reclassification records with evidence of criteria being met
- Post-reclassification monitoring records
- Title III expenditure documentation
- EL participation in general education programs (equity data)

**This is where districts panic.** If they don't have a centralized system, gathering audit evidence means pulling from a dozen sources and hoping nothing was lost. A product that makes audit readiness the default state (rather than a crisis-mode exercise) is enormously valuable.

---

## OCR: The Enforcement Mechanism You Need to Understand

The Office for Civil Rights (within the U.S. Department of Education) enforces civil rights requirements including Lau/EEOA obligations for EL students. OCR matters for two reasons: it's the "teeth" behind EL compliance, and fear of OCR findings drives purchasing decisions.

### How OCR Investigations Start

- **Parent/community complaints** — Anyone can file a complaint with OCR. Common triggers: a parent whose child was identified late, wasn't screened, didn't receive services, or was improperly reclassified.
- **CRDC data analysis** — OCR uses data from the Civil Rights Data Collection to identify red flags (e.g., a district where 0% of EL students are in gifted programs, or where EL discipline rates are far above non-EL rates).
- **Compliance reviews** — OCR proactively selects districts for review.

### What OCR Looks For

OCR evaluates districts against the Castañeda test and Lau requirements. Common findings include:
- Failure to identify EL students in a timely manner
- Failure to notify parents in a language they understand
- Inadequate EL services (not enough minutes, no qualified staff, no appropriate program)
- Failure to monitor reclassified students
- Segregation of EL students from academic and extracurricular programs
- Failure to provide EL students with disabilities appropriate services
- Lack of translated materials for parents

### Consequences

- **Resolution agreement/corrective action plan** — The district must agree to specific actions with timelines. OCR monitors compliance.
- **Referral to DOJ** — In severe cases, OCR refers to the Department of Justice for enforcement action.
- **Funding implications** — In theory, OCR can recommend termination of federal funding. In practice, this almost never happens, but the threat drives behavior.

**Product implication:** If your platform can help a district demonstrate to OCR that they identified students on time, notified parents, provided services, and monitored reclassified students — with timestamps and documentation — that's a powerful sales argument. "OCR-ready" is a meaningful positioning claim.

---

## Dual-Identified Students: Where EL and Special Education Collide

Students who are both English Learners and have a disability (sometimes called "dual-identified" or "EL + IEP" students) represent one of the most challenging compliance areas — and one of the most common OCR complaint triggers.

### The Core Tension

When a student is struggling academically, is it because of a language barrier, a disability, or both? Getting this wrong in either direction causes harm:
- **Under-identification of disability:** Attributing a student's struggles entirely to language difference delays necessary special education services.
- **Over-identification of disability:** Students are misclassified as having a disability when they're actually experiencing normal second-language acquisition. This disproportionately affects EL students and is a civil rights concern.

### Compliance Requirements for Dual-Identified Students

- Evaluation for special education must be conducted in the student's native language or other mode of communication (IDEA requirement)
- The evaluation team must include someone knowledgeable about second language acquisition
- The IEP must address both the disability and English language development — you can't just pick one
- EL services cannot be reduced or eliminated because a student has an IEP
- The student must participate in ACCESS testing (with appropriate accommodations) unless they qualify for Alternate ACCESS

### Data Implication

Your product needs to be able to flag and track dual-identified students separately, because they have additional documentation requirements and are a compliance focal point during audits and OCR reviews.

---

## Long-Term English Learners (LTELs): The Growing Accountability Pressure

LTELs — students who have been classified as EL for 5 or more years (some states use 6+) without reaching proficiency — are an increasingly scrutinized population.

### Why LTELs Matter for Compliance

- ESSA requires states to report LTEL data
- Several states (notably California) have specific LTEL-focused legislation requiring districts to identify and intervene
- High LTEL rates signal program ineffectiveness (Castañeda prong 3)
- OCR may investigate if LTEL rates are disproportionately high

### Data Needs

- Ability to identify LTELs (students with 5+ years in EL status)
- Year-over-year ACCESS growth trajectories (are they progressing slowly or plateaued?)
- Program history (what services have they received over the years?)
- Academic performance trends
- Intervention documentation

---

## Questions You Should Be Asking (That You Didn't Know to Ask)

Based on everything above, here are the questions that will accelerate your understanding and inform product decisions:

### About the Compliance Workflow

1. **What does the reclassification workflow actually look like, step by step, in the districts you'll serve?** This varies by state and is often the most complex workflow an EL specialist manages. Shadowing this process would be invaluable.

2. **How do districts handle the "monitoring" years after reclassification?** In many districts, monitoring is the compliance area most likely to have gaps. Students get reclassified and then nobody checks on them for 4 years. This is an OCR risk and a product opportunity.

3. **What happens when a new student enrolls mid-year?** The 30-day identification clock starts ticking immediately. In high-mobility districts (military, migrant, refugee), mid-year enrollment is constant. The intake workflow is one of the most time-sensitive compliance processes.

4. **How do districts document parent notification in a language the parent understands?** This is a surprisingly hard problem. Districts need translated letters in dozens of languages. Do they use translation services? Pre-built templates? How do they track that the letter was actually sent and received?

### About Data and Systems

5. **What does the WIDA AMS → district data pipeline actually look like?** Who downloads the score files? What format are they in? How do they get into the SIS? How much manual work is involved? Is there an API or is it all CSV?

6. **What role does Clever/ClassLink play in the EL data ecosystem?** You already know they pass rostering data. But do they pass EL-specific data (proficiency level, program placement, LIEP type)? If not, that's a gap your product needs to fill.

7. **How do districts currently generate their state compliance reports?** Are they manually pulling data into Excel? Does the SIS have built-in reports? Does Ellevation generate them? Understanding the report generation pain is critical.

8. **What data does Flashlight currently have about EL students that you could leverage?** Flashlight's benchmark assessment data shows academic English proficiency in a way that's different from ACCESS. Could this data serve as a leading indicator for reclassification readiness? If so, that's a unique product angle.

### About the Market

9. **What percentage of Flashlight's 200+ districts are in WIDA states vs. non-WIDA?** This determines whether you can build a WIDA-first product or need to support multiple assessment systems from day one.

10. **What do districts that can't afford Ellevation do instead?** The answer is almost certainly "spreadsheets and paper." Understanding their specific pain points and workarounds tells you what the MVP needs to solve.

11. **Who in the district actually runs the ACCESS testing logistics?** Is it the EL director? An assessment coordinator? Understanding this person's workflow might reveal product opportunities around test administration, not just data management.

12. **How do districts handle state-specific compliance requirements?** Do they maintain their own checklists? Do they rely on their state education agency's guidance documents? Is there an opportunity for your product to encode state-specific compliance rules?

### About the Regulatory Environment

13. **Are there any pending federal or state policy changes that could shift compliance requirements?** The political climate around immigration and bilingual education affects EL programs. Policy shifts (like changes to reclassification criteria or Title III funding levels) could create product opportunities or risks.

14. **What role do state education agencies (SEAs) play in EL compliance?** SEAs issue guidance, conduct monitoring visits, and sometimes provide technical assistance tools. Understanding what the SEA provides for free helps you position your product correctly.

15. **How does the English Learner accountability indicator work in your target states' ESSA plans?** Each state designed its own EL progress indicator. Some use growth on ACCESS, some use proficiency attainment rates, some use a combination. Your product needs to surface the metrics that map to how the state actually evaluates districts.

### About Product Positioning

16. **Is the buyer (EL director) buying a compliance tool or a data platform?** These sound the same but the framing matters. A "compliance tool" sells on fear (avoid audit findings). A "data platform" sells on empowerment (make better decisions for students). The most successful products do both, but the lead message matters.

17. **What would make an EL director switch from Ellevation?** Price? Better Flashlight assessment integration? Easier compliance reporting? Friendlier UX for teachers? Or is there a feature gap Ellevation doesn't address? You need to hear this from directors directly.

18. **Could you build a "compliance score" or "audit readiness" dashboard that gives EL directors a real-time view of where they have gaps?** Think of it as a health check: "You have 12 students overdue for monitoring. You have 3 students without parent notification on file. Your ACCESS participation rate is 94%." This would be genuinely new and valuable.

---

## A Note on Research Standards

Per your project context, I want to be transparent about the confidence level of the information above:

**High confidence:** The legal framework (Lau, Castañeda, ESSA/Title III, IDEA), WIDA structure and ACCESS test design, federal reporting requirements, and general compliance workflows. These are well-established and well-documented.

**Medium confidence:** Specific state variations, WIDA membership numbers (states occasionally join or leave), exact CRDC reporting frequency, and specific Ellevation feature details. These change and should be verified against current sources.

**Flagged as hypotheses (not verified facts):** The percentage breakdowns of how districts manage compliance today (spreadsheets vs. platforms), the specific data fields in WIDA score exports, and the availability of WIDA APIs. These should be validated in customer discovery interviews.

I'd strongly recommend supplementing this with the actual regulatory documents — particularly your target states' ESSA plans, their EL-specific guidance documents, and the OCR's "Dear Colleague Letter" on EL students (the most recent comprehensive one is from January 2015). Those are primary sources that will fill gaps this overview can't.
