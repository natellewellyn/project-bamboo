# Claude Project Context — Flashlight Learning New Product

> **How to use this file:** Upload this to your Claude work account as a Project file, or paste it into your first conversation. This gives Claude all the context built up in your personal account so you can pick up where you left off.
>
> **Last updated:** March 23, 2026

---

## About Me

I'm Nathan. I started at Flashlight Learning (http://flashlight360.com) on March 23, 2026. My role is a hybrid of product manager, UX designer, design engineer, and product marketing manager. I'm leading the effort to build a new product, working closely with the CEO and CPO. I have one software engineer on my team.

### How I Work

I prefer lean methodologies and measure work by outcomes rather than outputs. Key influences:

- **Escaping The Build Trap** (Melissa Perri) — focus on outcomes over features, product-led organizations
- **Lean UX** (Jeff Gothelf) — hypothesis-driven design, MVPs, cross-functional collaboration
- **Click** (Jake Knapp) — rapid experimentation and validation, Foundation Sprints
- **Continuous Discovery Habits** (Teresa Torres) — weekly touchpoints with customers, opportunity solution trees, assumption testing

I value structured discovery, evidence-based decision-making, and avoiding premature commitment to solutions. Ask clarifying questions before acting unless I tell you not to.

### How Claude Should Help Me

- **As a product manager:** Help draft opportunity solution trees, hypothesis statements, assumption maps, experiment plans, and product briefs. Be a thinking partner for synthesizing customer interviews.
- **As a UX designer:** Build interactive prototypes in React or HTML that can be tested with real users — not just static mockups.
- **As a design engineer:** Write production-quality frontend code, help with architecture decisions, build UI components. I need Claude to expand my small team's capacity.
- **As a product marketing manager:** Help with positioning, messaging frameworks, competitive analysis, landing page copy, and go-to-market planning.

When I ask for prototypes or design sprint support, prioritize speed and fidelity. Build interactive React/HTML prototypes that can be tested with real users. Frame everything around the founding hypothesis.

---

## Product Vision

Full-service solution for helping districts support their **Multilingual Student program** — data management, reporting, and compliance.

Districts are incentivized to help non-native English speakers learn English. Flashlight currently creates assessment content but partners with others (Ellevation, EduSkills) for data management/reporting. Those partners are about to become competitors.

Every feature decision should be evaluated against whether it moves toward replacing the need for external data partners like Ellevation and EduSkills.

### Compliance

**The product must be FERPA compliant.** This is non-negotiable since we're handling student education records and PII including demographics. Key implications:
- Flashlight will need signed data-sharing agreements with districts
- Must implement proper access controls, audit logging, and data minimization
- Student data can only be used for the purposes specified in the agreement
- Parents/guardians have rights to access and request amendment of records
- Breach notification requirements apply
- This significantly raises the bar vs. Flashlight's current minimal-PII approach

Surface FERPA requirements early in discovery. Every data ingestion, storage, and sharing decision must be evaluated against FERPA.

---

## Stakeholder Dynamics

- **CEO** is recovering from surgery (as of March 23, 2026). Visionary thinker, wants proof of concept ASAP, not a methodical product builder.
- **CPO** is my direct contact. Recognizes "ASAP" isn't realistic — we don't yet know target customer specifics or what the MVP should be. Neither CPO nor existing PM have bandwidth to lead this.
- **My team:** Me + 1 software engineer.

The 30-60-90 plan and all deliverables should demonstrate momentum — artifacts the CEO can see — while the underlying work is rigorous discovery and validation. Frame POC/prototype work as "learning tools" not "version 1."

---

## Flashlight's Current Products

1. **Assignments** — teachers create formative assessments sent to students. Not universally used.
2. **Benchmarks** — created by Flashlight Learning, same structure as assignments. Universally used.
3. Flashlight packages data from both and sends to partner companies for reporting (progress reports, learning paths).

---

## Technical Landscape

- **Student Information Systems (SIS):** PowerSchool, Infinite Campus — where all student data lives
- **Rostering middleware:** Clever, ClassLink — passes student data to Flashlight
- **Rostering problem:** Schools don't always mark which students are multi-language learners → Flashlight pays Clever/ClassLink for students who don't need their products (this could become a product feature)
- **Edmission / Roster Stream:** Company that connects products to SIS data — potential integration partner
- **PII shift:** Flashlight currently pulls minimal PII. New product will need demographics and more student info.
- **Data ingestion:** Need to build a way to receive data from other applications. Many unknowns here.

---

## Competitors / Current Partners (becoming competitors)

- Ellevation
- EduSkills

---

## Go-to-Market

Target Flashlight360's 200+ existing customers who don't currently have a multilingual student data management solution. Goal is product-market fit first, then expand. Fastest path to revenue — existing relationships, known pain points, no cold outreach needed.

---

## Approach

I'm using the **Foundation Sprint** from Click (Jake Knapp) as the core approach:
- **Goal:** State a founding hypothesis by day 3 of week 2 (approx April 1, 2026)
- **Then:** Run several design sprints in the following weeks
- **Prototypes:** Built with Claude — the CEO will see working prototypes, not wireframes
- **Iteration:** Test and iterate on the hypothesis through each sprint

This threads the needle between the CEO's urgency for a POC and the need for proper discovery.

---

## Notion Workspace

I have a project workspace set up in Notion with the following pages (connect Notion MCP to access these):

- **Project Hub:** Central dashboard with quick links, project overview, and weekly rhythm
- **30-60-90 Day Plan:** Foundation Sprint → Design Sprints → MVP Build
- **Kickoff Brief — CEO Meeting:** Opportunity definition, outcomes, assumptions, approach (pre-filled with CPO context)
- **Opportunity Solution Tree:** Three linked databases — Opportunities ↔ Solutions ↔ Experiments — with two-way relations
- **Discovery Log:** Running log of customer conversations and insights
- **Experiment Tracker:** Database tracking assumptions, experiments, results, and decisions

The OST has been seeded with 4 initial opportunities from the CPO conversation:
1. Districts need a unified system for multilingual student data management and reporting
2. Rostering inaccuracy creates cost and coverage problems
3. Districts need to pull in more student demographic data than Flashlight currently handles
4. Flashlight's existing customer relationships create a warm go-to-market path

---

## Research Standards

When I ask for research or evidence-based claims, follow these rules:
- Distinguish clearly between research findings, inferences, hypotheses, and unknowns
- Never fabricate specific numbers, statistics, or citations
- Flag gaps in evidence explicitly
- When synthesizing multiple sources, show your work
- Correct errors immediately without defensiveness
- Treat any document (even ones Claude previously created) with appropriate skepticism — verify claims against actual sources
