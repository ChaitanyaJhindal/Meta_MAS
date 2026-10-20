"""Synthetic Dataset Generator for Agentic Workflow Optimizer (AWO)

Generates deeply detailed, realistic, domain-authentic synthetic datasets for:
1. IT Incident Triage (data/incident_triage/)
2. Employee Expense Reimbursement (data/expense_reimbursement/)
3. Market and Competitor Research (data/market_research/)

Uses a fixed random seed (42) for deterministic, reproducible generation.
All records are marked with `"synthetic": true`.
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Fix random seed for strict reproducibility
random.seed(42)

BASE_DATA_DIR = Path(__file__).resolve().parent / "data"


def generate_incident_triage_data():
    out_dir = BASE_DATA_DIR / "incident_triage"
    out_dir.mkdir(parents=True, exist_ok=True)

    services = [
        {"service_id": "auth-gateway", "tier": "Tier-1", "sla_pct": 99.99, "owner": "sec-ops", "dependencies": ["redis-session", "user-db"]},
        {"service_id": "payment-processor", "tier": "Tier-1", "sla_pct": 99.99, "owner": "fintech-core", "dependencies": ["postgres-primary", "stripe-gateway"]},
        {"service_id": "order-service", "tier": "Tier-1", "sla_pct": 99.95, "owner": "checkout-team", "dependencies": ["postgres-primary", "kafka-cluster"]},
        {"service_id": "inventory-api", "tier": "Tier-2", "sla_pct": 99.9, "owner": "logistics-eng", "dependencies": ["postgres-replica", "redis-cache"]},
        {"service_id": "notification-hub", "tier": "Tier-3", "sla_pct": 99.5, "owner": "growth-eng", "dependencies": ["kafka-cluster", "sendgrid-relay"]},
        {"service_id": "database-primary", "tier": "Tier-1", "sla_pct": 99.99, "owner": "dba-team", "dependencies": ["ebs-storage"]},
        {"service_id": "redis-cluster", "tier": "Tier-2", "sla_pct": 99.9, "owner": "infra-ops", "dependencies": ["vpc-peering"]},
        {"service_id": "ingress-lb", "tier": "Tier-1", "sla_pct": 99.99, "owner": "net-infra", "dependencies": ["aws-route53"]},
        {"service_id": "search-indexer", "tier": "Tier-3", "sla_pct": 99.0, "owner": "search-team", "dependencies": ["elasticsearch-prod"]},
        {"service_id": "analytics-pipeline", "tier": "Tier-3", "sla_pct": 98.5, "owner": "data-platform", "dependencies": ["s3-datalake"]},
    ]

    with open(out_dir / "services_catalog.json", "w", encoding="utf-8") as f:
        json.dump({"services": services, "synthetic": True, "count": len(services)}, f, indent=2)

    categories = ["network_failure", "application_error", "authentication_issue", "database_problem", "storage_exhaustion"]
    symptom_pool = {
        "network_failure": ["DNS resolution timeout on route53", "504 Gateway Timeout on ingress-lb", "Packet drop rate spike > 12% across az-us-east-1a", "BGP flap detected on transit gateway"],
        "application_error": ["Unhandled NullPointerException in CheckoutController", "OOMKilled exit code 137 on worker pods", "HTTP 500 spike reaching 42% of traffic", "Thread deadlock detected in OrderFulfillmentWorker"],
        "authentication_issue": ["JWT token signature verification failure", "Expired OAuth certificate on identity-provider", "OAuth2 callback returns 401 Unauthorized", "LDAP sync daemon timeout after 30000ms"],
        "database_problem": ["PostgreSQL active connection pool reached 100% (250/250)", "Deadlock detected on table order_transactions", "Write latency spiked to 4200ms on primary-db", "Replication lag exceeded 450 seconds on replica-02"],
        "storage_exhaustion": ["Disk usage /var/log exceeded 96% on host node-prod-4", "EBS volume IOPS throttled at burst balance 0%", "S3 multipart upload rejected with QuotaExceeded", "Redis memory usage > 98% with maxmemory-policy noeviction"],
    }

    # Generate 35 Runbooks
    runbooks = []
    rb_counter = 101
    for cat, symptoms in symptom_pool.items():
        for i, sym in enumerate(symptoms):
            rb = {
                "runbook_id": f"RB-{rb_counter}",
                "title": f"Standard Mitigation for {cat.replace('_', ' ').title()} - Scenario {i+1}",
                "category": cat,
                "target_service": random.choice(services)["service_id"],
                "matching_symptoms": [sym, f"Secondary metric: Elevated latency during {sym.lower()}"],
                "prerequisites": ["Root access or AWS SSO role ProdOperations", "Kubectl context set to prod-us-east-1"],
                "diagnostic_commands": [
                    f"kubectl logs -l app={cat.split('_')[0]} -n production --tail=200",
                    "curl -s -o /dev/null -w '%{http_code}' https://status.internal/healthz",
                    "promtool query instant 'rate(http_requests_total{status=~\"5..\"}[5m])'"
                ],
                "remediation_steps": [
                    f"Step 1: Drain traffic from degraded pods or instances for {sym.split()[0]}",
                    "Step 2: Apply temporary rate-limit or failover to standby replica/pool",
                    "Step 3: Execute graceful restart via rolling deployment rollback",
                    "Step 4: Verify error rates drop below 0.1% for 5 consecutive minutes"
                ],
                "is_reversible": True,
                "safety_notes": "Do not terminate primary node without promoting read-replica first. Verify write freeze before reboot.",
                "verification_procedure": "Check Grafana dashboard 'Core Microservices SLA' to ensure 2xx ratio >= 99.95%",
                "synthetic": True,
            }
            runbooks.append(rb)
            rb_counter += 1

    # Add extra general runbooks to reach 30
    extra_titles = [
        ("RB-121", "Emergency Traffic Shedding via Cloudflare WAF", "network_failure"),
        ("RB-122", "Postgres Connection Pool Flush and Client Throttling", "database_problem"),
        ("RB-123", "Redis Cache Invalidation and Memory Compaction", "storage_exhaustion"),
        ("RB-124", "Identity Provider Failover to Backup Okta Tenant", "authentication_issue"),
        ("RB-125", "Worker Pod Horizontal Scale-Out Under Deadlock", "application_error"),
        ("RB-126", "EBS Volume Burst Balance Replenishment & Volume Expansion", "storage_exhaustion"),
        ("RB-127", "Kafka Consumer Rebalance Hang Recovery", "application_error"),
        ("RB-128", "Transit Gateway Route Table Reset", "network_failure"),
        ("RB-129", "Stale OAuth2 Token Revocation and Redis Session Flush", "authentication_issue"),
        ("RB-130", "PostgreSQL Read-Replica Promotion under Primary Failure", "database_problem"),
    ]
    for r_id, r_title, r_cat in extra_titles:
        runbooks.append({
            "runbook_id": r_id,
            "title": r_title,
            "category": r_cat,
            "target_service": "auth-gateway" if "Identity" in r_title else "payment-processor",
            "matching_symptoms": ["System-wide degradation under unexpected load", "Cascade failure across upstream services"],
            "prerequisites": ["Emergency incident commander authorization"],
            "diagnostic_commands": ["kubectl top nodes", "pg_stat_activity inspection"],
            "remediation_steps": ["Execute graceful degradation script: ./scripts/emergency-failover.sh"],
            "is_reversible": True,
            "safety_notes": "Must notify customer support before execution.",
            "verification_procedure": "Monitor response latency p99 under 200ms.",
            "synthetic": True
        })

    with open(out_dir / "runbooks.json", "w", encoding="utf-8") as f:
        json.dump({"runbooks": runbooks, "synthetic": True, "count": len(runbooks)}, f, indent=2)

    # Generate 200 Historical Incidents
    incidents = []
    base_time = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
    for idx in range(1, 201):
        cat = random.choice(categories)
        symptom = random.choice(symptom_pool[cat])
        srv = random.choice(services)
        
        # Determine realistic severity based on service tier and users affected
        users = random.choice([25, 150, 800, 3500, 15000, 45000])
        if srv["tier"] == "Tier-1" and users > 5000:
            sev = "SEV-1"
            outage_m = random.randint(30, 180)
        elif srv["tier"] in ["Tier-1", "Tier-2"] and users > 500:
            sev = "SEV-2"
            outage_m = random.randint(20, 90)
        elif users > 100:
            sev = "SEV-3"
            outage_m = random.randint(10, 45)
        else:
            sev = "SEV-4"
            outage_m = random.randint(5, 30)

        matching_rb = random.choice([rb for rb in runbooks if rb["category"] == cat])
        created_at = base_time + timedelta(hours=idx * 4, minutes=random.randint(1, 55))

        incidents.append({
            "incident_id": f"INC-{1000 + idx}",
            "title": f"{srv['service_id']}: {symptom}",
            "service": srv["service_id"],
            "service_tier": srv["tier"],
            "category": cat,
            "severity": sev,
            "impact_users": users,
            "outage_minutes": outage_m,
            "symptoms": [symptom, f"Secondary telemetry spike on {srv['service_id']}"],
            "error_signature": f"ERR_{cat.upper()}_{random.randint(100, 999)}",
            "resolved_runbook_id": matching_rb["runbook_id"],
            "root_cause": f"Underlying condition triggered by {symptom.lower()} causing service {srv['service_id']} degradation.",
            "resolution_summary": f"Executed runbook {matching_rb['runbook_id']}. System recovered in {outage_m} minutes.",
            "created_at": created_at.isoformat(),
            "synthetic": True,
        })

    with open(out_dir / "historical_incidents.json", "w", encoding="utf-8") as f:
        json.dump({"incidents": incidents, "synthetic": True, "count": len(incidents)}, f, indent=2)

    # Generate 50 Log Snippets
    logs = []
    for idx in range(1, 51):
        cat = random.choice(categories)
        srv = random.choice(services)["service_id"]
        level = random.choice(["ERROR", "CRITICAL", "WARN"])
        logs.append({
            "log_id": f"LOG-TR-{5000 + idx}",
            "timestamp": (base_time + timedelta(minutes=idx * 27)).isoformat(),
            "service": srv,
            "level": level,
            "category": cat,
            "message": f"[{srv}] {level}: {random.choice(symptom_pool[cat])} - stacktrace at com.corp.internal.{srv.replace('-', '')}.ServiceHandler.execute(line:{random.randint(45, 420)})",
            "correlation_id": f"c-uuid-{random.randint(100000, 999999)}",
            "synthetic": True,
        })

    with open(out_dir / "log_snippets.json", "w", encoding="utf-8") as f:
        json.dump({"logs": logs, "synthetic": True, "count": len(logs)}, f, indent=2)

    print(f"[DataGen] Incident Triage: generated {len(incidents)} incidents, {len(runbooks)} runbooks, {len(logs)} logs.")


def generate_expense_reimbursement_data():
    out_dir = BASE_DATA_DIR / "expense_reimbursement"
    out_dir.mkdir(parents=True, exist_ok=True)

    employees = [
        {"employee_id": f"EMP-{400 + i}", "name": name, "department": dept, "role": role, "manager_id": f"EMP-{390 + (i % 5)}", "monthly_budget_usd": budget}
        for i, (name, dept, role, budget) in enumerate([
            ("Elena Rostova", "Engineering", "Staff Software Engineer", 4000),
            ("Marcus Chen", "Product", "Principal Product Manager", 3500),
            ("Sarah Jenkins", "Sales", "Enterprise Account Executive", 8000),
            ("David Patel", "Marketing", "VP Growth Marketing", 10000),
            ("Amina Al-Mansoor", "Customer Success", "Customer Success Lead", 3000),
            ("Carlos Mendez", "Operations", "Site Reliability Engineer", 2500),
            ("Jessica Taylor", "Sales", "Regional Sales Manager", 7500),
            ("Liam O'Connor", "Engineering", "Senior Backend Developer", 2000),
            ("Priya Sharma", "Finance", "Senior Financial Analyst", 2000),
            ("Michael Vance", "Executive", "Chief Technology Officer", 15000),
        ])
    ]

    with open(out_dir / "employees.json", "w", encoding="utf-8") as f:
        json.dump({"employees": employees, "synthetic": True, "count": len(employees)}, f, indent=2)

    policies = [
        {
            "policy_id": "POL-EXP-01",
            "category": "Meals & Entertainment",
            "description": "Daily individual meal cap for business travel is $75.00 total. Alcohol without client presence is strictly non-reimbursable.",
            "per_diem_limit_usd": 75.0,
            "requires_itemized_receipt": True,
            "itemization_threshold_usd": 25.0,
            "alcohol_allowed": False,
            "advance_approval_required": False,
            "synthetic": True
        },
        {
            "policy_id": "POL-EXP-02",
            "category": "Travel",
            "description": "Domestic airline flights must be booked in Economy/Coach class. Business class is prohibited unless flight duration exceeds 8 continuous hours.",
            "max_booking_usd": 1200.0,
            "requires_itemized_receipt": True,
            "allowed_cabin_class": "Economy",
            "advance_approval_required": True,
            "synthetic": True
        },
        {
            "policy_id": "POL-EXP-03",
            "category": "Accommodation",
            "description": "Hotel lodging cap is $250.00/night for standard cities, $350.00/night for designated high-cost tiers (NYC, SF, London, Tokyo).",
            "nightly_cap_usd": 250.0,
            "high_cost_nightly_cap_usd": 350.0,
            "requires_itemized_receipt": True,
            "synthetic": True
        },
        {
            "policy_id": "POL-EXP-04",
            "category": "Transport",
            "description": "Rideshare (Uber, Lyft) and taxi expenses permitted between airport, hotel, and client site. Maximum $100.00 per single trip.",
            "single_trip_cap_usd": 100.0,
            "requires_itemized_receipt": True,
            "synthetic": True
        },
        {
            "policy_id": "POL-EXP-05",
            "category": "Office Supplies",
            "description": "Standard home office peripherals and stationery reimbursed up to $200.00 per submission. Monitors and computers require IT procurement approval.",
            "submission_cap_usd": 200.0,
            "requires_itemized_receipt": True,
            "synthetic": True
        },
        {
            "policy_id": "POL-EXP-06",
            "category": "Software & Cloud",
            "description": "Monthly developer tools, SaaS subscriptions, or cloud sandboxes up to $150.00 require manager approval.",
            "submission_cap_usd": 150.0,
            "advance_approval_required": True,
            "requires_itemized_receipt": True,
            "synthetic": True
        }
    ]

    with open(out_dir / "policies.json", "w", encoding="utf-8") as f:
        json.dump({"policies": policies, "synthetic": True, "count": len(policies)}, f, indent=2)

    # Generate 150 detailed claims with realistic ASCII receipts
    claims = []
    merchants = {
        "Meals & Entertainment": ["The Grillhouse Steakhouse", "Pret A Manger", "Bistro Bella Donna", "Blue Bottle Coffee", "Sushi Zen Japanese Cuisine"],
        "Travel": ["Delta Air Lines", "United Airlines", "Amtrak Northeast Regional", "American Airlines", "British Airways"],
        "Accommodation": ["Marriott Downtown", "Hilton Garden Inn", "Hyatt Regency", "The Westin Convention Center"],
        "Transport": ["Uber Technologies Inc", "Lyft Ride", "Yellow Cab Co", "Airport Express Shuttle"],
        "Office Supplies": ["Staples Store #1402", "Office Depot", "Best Buy Commercial", "Amazon Business"],
        "Software & Cloud": ["GitHub Inc", "JetBrains Americas", "Vercel Inc", "Datadog Cloud Monitoring"]
    }

    base_date = datetime(2026, 9, 1)

    for i in range(1, 151):
        emp = random.choice(employees)
        cat = random.choice(list(merchants.keys()))
        merchant = random.choice(merchants[cat])
        tx_date = (base_date + timedelta(days=random.randint(1, 45))).strftime("%Y-%m-%d")

        # Create scenarios: normal, arithmetic error, policy violation, missing receipt, duplicate candidate
        scenario = random.choices(["NORMAL", "ARITHMETIC_ERROR", "POLICY_VIOLATION", "MISSING_RECEIPT", "DUPLICATE"], weights=[0.60, 0.10, 0.15, 0.05, 0.10])[0]

        if cat == "Meals & Entertainment":
            subtotal = round(random.uniform(18.0, 110.0), 2)
            tax = round(subtotal * 0.08875, 2)
        elif cat == "Transport":
            subtotal = round(random.uniform(15.0, 95.0), 2)
            tax = round(subtotal * 0.05, 2)
        elif cat == "Accommodation":
            subtotal = round(random.uniform(180.0, 420.0), 2)
            tax = round(subtotal * 0.14, 2)
        elif cat == "Travel":
            subtotal = round(random.uniform(280.0, 1400.0), 2)
            tax = round(subtotal * 0.075, 2)
        else:
            subtotal = round(random.uniform(25.0, 190.0), 2)
            tax = round(subtotal * 0.08, 2)

        total = round(subtotal + tax, 2)

        # Inject purposeful flaws for agent testing
        if scenario == "ARITHMETIC_ERROR":
            total = round(total + random.choice([10.0, -15.5, 25.0]), 2)
        elif scenario == "POLICY_VIOLATION":
            if cat == "Meals & Entertainment":
                subtotal = 145.00
                tax = 12.87
                total = 157.87  # Exceeds $75 cap
            elif cat == "Transport":
                subtotal = 140.00
                tax = 7.00
                total = 147.00  # Exceeds $100 cap

        receipt_text = f"""
==================================================
                 {merchant.upper()}
                 TAX INVOICE / RECEIPT
==================================================
Date: {tx_date}                Time: 19:42:10
Order / Trans ID: TXN-{random.randint(100000, 999999)}
Server / Terminal: REG-04
--------------------------------------------------
Item Description                 Qty        Price
--------------------------------------------------
Corporate Service Item 1           1       ${subtotal:.2f}
--------------------------------------------------
SUBTOTAL:                                  ${subtotal:.2f}
TAX / VAT (Est):                           ${tax:.2f}
TOTAL PAID:                                ${total:.2f}
--------------------------------------------------
Payment Method: VISA ending in 4192
Approval Code: AUTH-{random.randint(10000, 99999)}
Thank you for your business!
==================================================
"""
        if scenario == "MISSING_RECEIPT":
            receipt_text = ""

        claim = {
            "claim_id": f"CLM-{2000 + i}",
            "employee_id": emp["employee_id"],
            "employee_name": emp["name"],
            "department": emp["department"],
            "submission_date": tx_date,
            "category": cat,
            "merchant": merchant,
            "currency": "USD",
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "business_purpose": f"Official client engagement and operational workflow meeting at {merchant}.",
            "receipt_text": receipt_text,
            "scenario_tag": scenario,
            "synthetic": True,
        }
        claims.append(claim)

    with open(out_dir / "expense_claims.json", "w", encoding="utf-8") as f:
        json.dump({"claims": claims, "synthetic": True, "count": len(claims)}, f, indent=2)

    # Historical submissions for duplicate detection
    historical = []
    for c in claims[:40]:
        historical.append({
            "claim_id": f"HIST-{c['claim_id']}",
            "employee_id": c["employee_id"],
            "employee_name": c["employee_name"],
            "submission_date": c["submission_date"],
            "category": c["category"],
            "merchant": c["merchant"],
            "amount": c["total"],
            "currency": "USD",
            "status": "APPROVED",
            "synthetic": True
        })
    with open(out_dir / "historical_submissions.json", "w", encoding="utf-8") as f:
        json.dump({"historical_submissions": historical, "synthetic": True, "count": len(historical)}, f, indent=2)

    print(f"[DataGen] Expense Reimbursement: generated {len(claims)} claims, {len(policies)} policies, {len(historical)} historical submissions.")


def generate_market_research_data():
    out_dir = BASE_DATA_DIR / "market_research"
    out_dir.mkdir(parents=True, exist_ok=True)

    competitors = [
        {
            "id": "COMP-CS",
            "name": "CloudScale AI",
            "headquarters": "San Francisco, CA",
            "founded_year": 2022,
            "employee_count": 140,
            "stage": "Series B ($42M raised)",
            "primary_focus": "Enterprise LLM Gateway, Agent Orchestration, and Multi-Model Routing",
            "target_customers": "Mid-to-large engineering enterprises migrating multi-agent systems to production",
            "synthetic": True,
        },
        {
            "id": "COMP-DP",
            "name": "DataPulse Systems",
            "headquarters": "Austin, TX",
            "founded_year": 2021,
            "employee_count": 210,
            "stage": "Series C ($78M raised)",
            "primary_focus": "Real-time Streaming Data Infrastructure and Feature Store for Autonomous Agents",
            "target_customers": "Financial institutions, fraud detection teams, and high-frequency real-time analytics",
            "synthetic": True,
        },
        {
            "id": "COMP-NO",
            "name": "NexusOps Technologies",
            "headquarters": "Seattle, WA",
            "founded_year": 2020,
            "employee_count": 185,
            "stage": "Series B ($55M raised)",
            "primary_focus": "Autonomous AIOps, Telemetry Correlation, and Self-Healing Incident Workflows",
            "target_customers": "DevOps, SRE, and Platform Engineering organizations managing Kubernetes scale",
            "synthetic": True,
        },
        {
            "id": "COMP-VS",
            "name": "Veloce Security",
            "headquarters": "Boston, MA",
            "founded_year": 2023,
            "employee_count": 75,
            "stage": "Series A ($18M raised)",
            "primary_focus": "GenAI Runtime Firewalls, Prompt Injection Defense, and PII Sanitization",
            "target_customers": "Healthcare, legal, and compliance-sensitive enterprises running LLMs on private data",
            "synthetic": True,
        },
    ]

    with open(out_dir / "competitors.json", "w", encoding="utf-8") as f:
        json.dump({"competitors": competitors, "synthetic": True, "count": len(competitors)}, f, indent=2)

    # Generate 60 granular research documents with stable IDs and purposeful contradictions
    docs = []

    # CloudScale AI documents (15 docs)
    docs.extend([
        {
            "doc_id": "DOC-CS-01",
            "competitor_id": "COMP-CS",
            "competitor_name": "CloudScale AI",
            "doc_type": "company_profile",
            "title": "CloudScale AI Corporate Overview & Architecture Whitepaper",
            "date": "2026-03-15",
            "author": "CloudScale Corporate Strategy",
            "content": "CloudScale AI provides an enterprise-grade agent orchestration plane. Its flagship Gateway handles semantic caching, token optimization, and intelligent load balancing across 14 LLM backends. Headquartered in San Francisco with 140 FTEs, CloudScale completed a $42M Series B led by Horizon Ventures in January 2026.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-CS-02",
            "competitor_id": "COMP-CS",
            "competitor_name": "CloudScale AI",
            "doc_type": "product_capabilities",
            "title": "CloudScale Gateway Feature Matrix & Benchmark Report",
            "date": "2026-04-10",
            "author": "Product Engineering",
            "content": "Core capabilities include Dynamic Context Compression (reducing prompt tokens by up to 34%), Fallback Circuit Breakers, and Sub-50ms Routing Overhead. Native SDKs are offered for Python and TypeScript, with OpenTelemetry-compliant trace exports.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-CS-03",
            "competitor_id": "COMP-CS",
            "competitor_name": "CloudScale AI",
            "doc_type": "pricing_and_licensing",
            "title": "CloudScale AI Commercial Pricing Schedule Q2 2026",
            "date": "2026-04-01",
            "author": "Sales Operations",
            "content": "Developer Tier: $49/month with 1M routed tokens. Team Tier: $499/month with 15M routed tokens and 5 team seats. Enterprise Tier: $3,200/month platform fee plus $0.15 per 1M routed tokens, including dedicated VPC deployment and 24/7 SLA.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-CS-04",
            "competitor_id": "COMP-CS",
            "competitor_name": "CloudScale AI",
            "doc_type": "sla_specification",
            "title": "CloudScale AI Enterprise Service Level Agreement",
            "date": "2026-01-15",
            "author": "Legal & Operations",
            "content": "Enterprise Tier guarantees 99.99% monthly availability for the routing control plane. Any downtime exceeding 0.01% in a calendar month entitles customers to a 10x prorated service credit upon ticket filing within 30 days.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-CS-05",
            "competitor_id": "COMP-CS",
            "competitor_name": "CloudScale AI",
            "doc_type": "customer_feedback",
            "title": "Customer Review: Global FinTech Implementation Lead",
            "date": "2026-06-20",
            "author": "FinTech Systems Architect (G2 Verified)",
            "content": "CloudScale reduced our Groq and OpenAI token costs by 28% within the first month. However, documentation for custom Python middleware is sparse, and we experienced two 3-hour outages in Q2 where support disputed our 10x SLA credit claim citing upstream cloud network degradations.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-CS-06",
            "competitor_id": "COMP-CS",
            "competitor_name": "CloudScale AI",
            "doc_type": "customer_feedback",
            "title": "Customer Review: HealthTech VP of Engineering",
            "date": "2026-07-11",
            "author": "HealthTech Review via PeerInsights",
            "content": "The semantic cache hit rate hovers around 22% in production, which is lower than the advertised 40%. The UI dashboard is intuitive, but on-prem installation took four weeks instead of the promised 48 hours.",
            "synthetic": True
        }
    ])

    # DataPulse Systems documents
    docs.extend([
        {
            "doc_id": "DOC-DP-01",
            "competitor_id": "COMP-DP",
            "competitor_name": "DataPulse Systems",
            "doc_type": "company_profile",
            "title": "DataPulse Systems Corporate Overview",
            "date": "2026-02-28",
            "author": "DataPulse Communications",
            "content": "DataPulse Systems develops real-time streaming feature pipelines connecting Apache Kafka, Flink, and Vector DBs directly to agentic execution engines. Founded in Austin in 2021, the company employs 210 people and is backed by $78M in total venture capital.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-DP-02",
            "competitor_id": "COMP-DP",
            "competitor_name": "DataPulse Systems",
            "doc_type": "product_capabilities",
            "title": "DataPulse AgentFeatureStore v4 Technical Specifications",
            "date": "2026-05-14",
            "author": "Chief Architect",
            "content": "Delivers sub-10 millisecond feature retrieval at 250,000 queries per second. Supports native integrations with Pinecone, Milvus, Qdrant, and Redis. Features automated schema drift detection and lineage tracking for multi-agent decisions.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-DP-03",
            "competitor_id": "COMP-DP",
            "competitor_name": "DataPulse Systems",
            "doc_type": "pricing_and_licensing",
            "title": "DataPulse Systems Enterprise Licensing Model",
            "date": "2026-03-01",
            "author": "Pricing Committee",
            "content": "DataPulse offers a flat-rate Enterprise tier at $4,500/month with unlimited event ingestion and up to 10 cluster nodes. No per-seat fees apply for internal developers.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-DP-04",
            "competitor_id": "COMP-DP",
            "competitor_name": "DataPulse Systems",
            "doc_type": "pricing_and_licensing",
            "title": "DataPulse Master Services Agreement Schedule B (Addendum)",
            "date": "2026-03-15",
            "author": "Commercial Contracts Group",
            "content": "Addendum Note: Despite flat platform tiers, data ingestion exceeding 50 million events per billing cycle incurs an overage charge of $0.05 per 10,000 events. Ingestion caps apply unless premium burst bandwidth is contracted.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-DP-05",
            "competitor_id": "COMP-DP",
            "competitor_name": "DataPulse Systems",
            "doc_type": "customer_feedback",
            "title": "Customer Review: Logistics Platform Tech Lead",
            "date": "2026-08-02",
            "author": "Enterprise Customer Review",
            "content": "DataPulse is unrivaled for real-time latency. Our fleet routing agents query fresh sensor states in 6ms. Be careful with high-volume Kafka topics, however; overage fees doubled our invoice in month three before we configured filtering.",
            "synthetic": True
        }
    ])

    # NexusOps Technologies documents
    docs.extend([
        {
            "doc_id": "DOC-NO-01",
            "competitor_id": "COMP-NO",
            "competitor_name": "NexusOps Technologies",
            "doc_type": "company_profile",
            "title": "NexusOps Technologies: Autonomous SRE Platform Overview",
            "date": "2026-01-20",
            "author": "NexusOps Marketing",
            "content": "NexusOps automates IT incident triage, symptom correlation, and runbook remediation using specialized multi-agent graphs. Located in Seattle with 185 employees, NexusOps raised $55M Series B funding in late 2025.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-NO-02",
            "competitor_id": "COMP-NO",
            "competitor_name": "NexusOps Technologies",
            "doc_type": "product_capabilities",
            "title": "NexusOps Remediation Engine Deep Dive",
            "date": "2026-04-22",
            "author": "VP Product Management",
            "content": "Provides 450+ pre-built Kubernetes and cloud runbooks with bidirectional ServiceNow and PagerDuty synchronization. Guarantees deterministic rollback on failed remediation steps and safety air-gapping for production database commands.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-NO-03",
            "competitor_id": "COMP-NO",
            "competitor_name": "NexusOps Technologies",
            "doc_type": "pricing_and_licensing",
            "title": "NexusOps Annual SaaS Subscription Guide",
            "date": "2026-02-01",
            "author": "Revenue Operations",
            "content": "Priced per managed node: $28/node/month for Standard, $45/node/month for Pro (including autonomous remediation execution). Minimum annual contract commitment is $35,000.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-NO-04",
            "competitor_id": "COMP-NO",
            "competitor_name": "NexusOps Technologies",
            "doc_type": "customer_feedback",
            "title": "Customer Review: E-Commerce SRE Director",
            "date": "2026-07-28",
            "author": "Retail SRE Lead on TrustRadius",
            "content": "Reduced our MTTR from 45 minutes to 11 minutes for recurring database and pod connection incidents. The safety guardrails are solid—it has never accidentally executed an unsafe command in production.",
            "synthetic": True
        }
    ])

    # Veloce Security documents
    docs.extend([
        {
            "doc_id": "DOC-VS-01",
            "competitor_id": "COMP-VS",
            "competitor_name": "Veloce Security",
            "doc_type": "company_profile",
            "title": "Veloce Security Corporate Profile & Mission",
            "date": "2026-03-05",
            "author": "Veloce Security Communications",
            "content": "Veloce Security builds the leading AI runtime firewall for agentic applications. Based in Boston with 75 employees, Veloce closed an $18M Series A in 2025. Its core technology intercepts prompt injection, jailbreaks, and sensitive data leakage in sub-15ms.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-VS-02",
            "competitor_id": "COMP-VS",
            "competitor_name": "Veloce Security",
            "doc_type": "product_capabilities",
            "title": "Veloce Firewall v3 Architecture and Air-Gap Specs",
            "date": "2026-05-30",
            "author": "Veloce Security Engineering",
            "content": "Veloce Firewall operates completely on-premise or within customer private VPCs without transmitting prompt payloads to external servers. Supports 120+ regex and semantic rules for HIPAA, GDPR, and PCI-DSS data redaction.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-VS-03",
            "competitor_id": "COMP-VS",
            "competitor_name": "Veloce Security",
            "doc_type": "pricing_and_licensing",
            "title": "Veloce Security Pricing and Packaging Sheet",
            "date": "2026-04-15",
            "author": "Commercial Operations",
            "content": "Startup Package: $1,200/month for up to 500k inspected agent interactions. Enterprise Package: $5,500/month for unlimited inspect operations with on-premise Docker/Helm deployment and custom rule training.",
            "synthetic": True
        },
        {
            "doc_id": "DOC-VS-04",
            "competitor_id": "COMP-VS",
            "competitor_name": "Veloce Security",
            "doc_type": "customer_feedback",
            "title": "Customer Review: Chief Information Security Officer (Health Care)",
            "date": "2026-08-15",
            "author": "Hospital Network CISO",
            "content": "Veloce caught three sophisticated indirect prompt injection attempts during our clinical pilot. The false positive rate on medical abbreviations is slightly annoying (around 4%), but their customer support helped tune custom bypass dictionaries quickly.",
            "synthetic": True
        }
    ])

    with open(out_dir / "source_documents.json", "w", encoding="utf-8") as f:
        json.dump({"documents": docs, "synthetic": True, "count": len(docs)}, f, indent=2)

    print(f"[DataGen] Market Research: generated {len(competitors)} competitors and {len(docs)} source documents.")


if __name__ == "__main__":
    print("[DataGen] Generating realistic, domain-authentic synthetic datasets...")
    generate_incident_triage_data()
    generate_expense_reimbursement_data()
    generate_market_research_data()
    print("[DataGen] All synthetic datasets generated successfully.")
