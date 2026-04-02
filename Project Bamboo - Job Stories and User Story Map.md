# Project Bamboo — Job Stories & User Story Map Inputs

*Synthesized from interviews with Kristi (18-year ESL leadership) and Linsey (product & compliance expertise)*

---

## Part 1: Job Stories

> **Format:** When I… (context) / But… (barrier) / Help me… (goal) / So I… (outcome)

---

### Compliance & Documentation

**JS-01 — Staying ahead of compliance deadlines**
When I'm managing compliance obligations for all of my multilingual students across dozens of schools and hundreds of students,
But deadlines are spread across multiple task types and I'm tracking them in spreadsheets or from memory,
Help me see a single compliance calendar that shows exactly what's due, for which students, and when,
So I can stay ahead of requirements without things slipping through the cracks.

---

**JS-02 — Generating parent notification letters**
When WIDA screener results come in and I'm required by law to notify parents,
But I have to manually pull results, write individualized letters, and track who has and hasn't been notified,
Help me auto-generate compliant parent communication letters from screener data and track delivery status,
So I can meet notification deadlines without spending hours on paperwork for every student.

---

**JS-03 — Creating IELPs at scale**
When ACCESS scores are available and it's time to build Individualized English Language Plans,
But creating each IELP requires pulling data from multiple places and the process is repetitive and time-consuming,
Help me generate pre-populated IELPs based on each student's data with AI-suggested instructional goals,
So I can produce compliant, high-quality plans in a fraction of the time.

---

**JS-04 — Managing home language surveys**
When a new student enrolls in the district,
But I'm not confident whether a home language survey was completed or whether the student was correctly identified as an EL,
Help me track survey completion status and flag students who may need to be screened or re-evaluated,
So I can ensure every eligible student receives the services they're entitled to.

---

### Progress Monitoring & Instruction

**JS-05 — Monitoring student growth across assessments**
When I want to understand whether my EL students are making adequate progress toward English proficiency,
But data lives in separate systems — WIDA, Flashlight, state assessments — and there's no unified view,
Help me see each student's proficiency trajectory across all relevant assessments in one place,
So I can identify students at risk of stalling and intervene before the window closes.

---

**JS-06 — Turning data into instructional action**
When a teacher asks me what they should actually *do* with a student based on their ACCESS scores,
But current tools give data without actionable recommendations and don't connect to instruction,
Help me generate differentiated instructional recommendations tied to each student's proficiency level,
So I can equip teachers with a clear next step instead of leaving them to interpret the data alone.

---

**JS-07 — Drilling into performance gaps**
When I notice that a subgroup of my EL students isn't meeting growth targets and I need to understand why,
But my current system only shows top-level aggregates and I can't trace the issue back to a classroom or teacher,
Help me drill down from district-level data to building, classroom, and individual student in a few clicks,
So I can make targeted decisions about resources and interventions rather than guessing.

---

### Student Management

**JS-08 — Receiving a transferring student**
When a student transfers into my district from another school or district,
But their EL history, prior IELP plans, and assessment records are stuck in the sending district's system,
Help me quickly access or import the student's complete EL record so I can review their history immediately,
So I can place them appropriately and continue their services without any gap in support.

---

**JS-09 — Sending a student's record to another district**
When one of my EL students is transferring out to another district,
But there's no clean way to export and share their EL file in a format the receiving district can actually use,
Help me package and transmit the student's full EL record — assessments, IELPs, communications — electronically,
So I can ensure continuity of services and protect the district from compliance liability.

---

### Reporting & Analytics

**JS-10 — Answering ad hoc questions from leadership**
When a superintendent or school board asks me a question about EL program performance during a meeting,
But I don't have the right report ready and pulling the data manually takes days,
Help me query my data in natural language and get a clear, accurate answer almost instantly,
So I can show up to leadership conversations confident and data-ready, not scrambling.

---

**JS-11 — Evaluating program effectiveness over time**
When I need to assess whether our EL program is actually moving the needle on student outcomes year over year,
But longitudinal data is hard to compile and my tools don't surface trends or comparisons automatically,
Help me see multi-year trend reports on EL population growth, proficiency levels, and growth rates,
So I can make evidence-based decisions about program design and present credible results to stakeholders.

---

---

## Part 2: User Story Map

> Activities represent the high-level user journey backbone. Tasks are the steps within each activity. User stories are the specific "as a [user], I want to [do X] so that [Y]" items to build.

---

### Backbone Activity 1 — Identify & Enroll EL Students

**Tasks:**
- Administer home language survey to new enrollees
- Determine which students require WIDA screening
- Conduct WIDA screener and record results
- Make formal EL identification decision
- Process parental waivers

**User Stories:**
- As an EL coordinator, I want to track which newly enrolled students have completed a home language survey so that no student is inadvertently missed.
- As an EL coordinator, I want to flag students who completed a home language survey indicating a non-English home language so that they are automatically queued for WIDA screening.
- As a district admin, I want to see a real-time dashboard of students pending identification decisions so that I can ensure we're within the required identification window.
- As an EL coordinator, I want to record and store parental waiver decisions alongside the student record so that I have a complete audit trail.

---

### Backbone Activity 2 — Manage Compliance Documentation

**Tasks:**
- Create and maintain IELP plans
- Track compliance deadlines by state and student
- Generate and send required parent communications
- Maintain compliance audit trail
- Run compliance status reports

**User Stories:**
- As an EL director, I want to generate an IELP pre-populated with a student's current ACCESS scores and demographic data so that I spend less time on data entry and more time on quality review.
- As an EL coordinator, I want a compliance calendar view showing upcoming parent notification deadlines so that I never miss a federally required communication.
- As a district admin, I want to see which students are missing required compliance documents (IELP, parent letters, etc.) at a glance so that I can address gaps before an audit.
- As an EL coordinator, I want to log parent communications and store delivery confirmations so that I can prove compliance if questioned.

---

### Backbone Activity 3 — Administer & Track Assessments

**Tasks:**
- Schedule WIDA screeners for new students
- Import WIDA ACCESS scores after annual testing
- Import state standardized test scores
- View assessment history per student

**User Stories:**
- As an EL coordinator, I want to import WIDA ACCESS scores from a file upload or direct integration so that results are in the system without manual entry.
- As an EL coordinator, I want to view a student's full assessment history — screeners, ACCESS, and state tests — on a single profile page so that I have complete context when making placement decisions.
- As an EL teacher, I want to see my students' most recent proficiency level scores by domain (reading, writing, listening, speaking) so that I can target instruction appropriately.
- As a district admin, I want to see a report of students whose ACCESS scores have not yet been imported so that I can follow up before compliance deadlines hit.

---

### Backbone Activity 4 — Monitor Student Progress

**Tasks:**
- View individual student proficiency trajectory
- Compare student growth to expected benchmarks
- Identify students at risk of insufficient growth
- Surface trends at classroom, building, and district level

**User Stories:**
- As an EL director, I want to drill down from district-level performance data to individual student data so that I can investigate gaps and take action at the right level.
- As an EL teacher, I want to see which of my students are on track to meet annual growth targets and which are falling behind so that I can prioritize where to focus my intervention time.
- As a building-level coordinator, I want to compare EL student growth rates across teachers in my building so that I can identify coaching opportunities or share best practices.
- As an EL director, I want to see year-over-year program-level growth trends so that I can evaluate program effectiveness and report results to leadership.

---

### Backbone Activity 5 — Generate Instructional Plans

**Tasks:**
- Review student proficiency data and goals
- Generate AI-recommended instructional strategies
- Align interventions to proficiency domain gaps
- Share instructional plans with teachers

**User Stories:**
- As an EL coordinator, I want the system to suggest differentiated instructional strategies for a student based on their current proficiency level and domain scores so that I have a starting point rather than building plans from scratch.
- As an EL teacher, I want to receive a recommended weekly focus for each student tied to their proficiency goals so that I can plan targeted small-group or pull-out instruction efficiently.
- As an EL director, I want to ensure that instructional plans are linked to and aligned with each student's IELP goals so that there is coherence between compliance documentation and actual instruction.

---

### Backbone Activity 6 — Communicate with Parents & Guardians

**Tasks:**
- Generate post-screener parent notification letters
- Send ACCESS score notification letters
- Track parent communication history
- Manage and record parental waiver decisions

**User Stories:**
- As an EL coordinator, I want to generate a batch of required parent notification letters immediately after screener results are recorded so that I can meet the required notification window without manual effort.
- As an EL coordinator, I want to track whether each parent notification has been sent and acknowledged so that I have a complete compliance record.
- As an EL coordinator, I want template-based letters available in multiple languages so that communications meet parent language access requirements.

---

### Backbone Activity 7 — Transfer Students Between Districts

**Tasks:**
- Export outgoing student's complete EL record
- Import incoming student's EL record from prior district
- Review transferred student's IELP and assessment history
- Determine appropriate placement for incoming student

**User Stories:**
- As an EL coordinator, I want to export a transferring student's complete EL file — IELPs, assessments, parent communications — as a structured package so that the receiving district can immediately use it.
- As an EL coordinator, I want to import an incoming student's EL record from their prior district so that I can review their history and make a placement decision on day one.
- As an EL director, I want to see a report of students who transferred in without a complete EL record so that I can flag them for immediate re-screening.

---

### Backbone Activity 8 — Analyze Program & Report to Stakeholders

**Tasks:**
- Generate district-level EL program reports
- Query data using natural language
- Build and export reports for leadership or board presentations
- Track program metrics over time

**User Stories:**
- As an EL director, I want to query student and program data using plain language (e.g., "How many students scored below a 3 in reading on ACCESS?") so that I can get answers quickly without knowing how to build reports.
- As a district admin, I want a summary dashboard showing key EL program metrics — population size, proficiency distribution, growth rates — so that I have a current picture at any time.
- As an EL director, I want to export formatted reports for board presentations so that I can communicate program outcomes without reformatting data manually.
- As a district administrator, I want to compare EL program performance across schools in my district so that I can allocate resources and support where they're most needed.

---

*Document generated from interviews with Kristi (3/2026) and Linsey (3/2026) as part of Project Bamboo discovery.*
