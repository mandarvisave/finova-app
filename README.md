# 💰 Finova — AI Financial Coach       

Live Link- https://finova-app.streamlit.app/

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google ADK](https://img.shields.io/badge/Google_ADK-0.1.0-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_2.0_Flash-AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A production-grade, AI-powered personal finance coaching web application.**  
Analyse your budget, build smarter savings habits, and eliminate debt — all powered by a pipeline of three specialised Gemini AI agents.

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation--setup) • [Usage](#-using-the-app) • [Deployment](#-deployment) • [Contributing](#-contributing)

</div>

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Why Finova?](#-why-finova)
3. [Features](#-features)
4. [Tech Stack](#-tech-stack)
5. [Architecture — How It All Works](#-architecture--how-it-all-works)
6. [Agent Deep Dive](#-agent-deep-dive)
7. [Pydantic Data Models Explained](#-pydantic-data-models-explained)
8. [UI Design System](#-ui-design-system)
9. [Project Structure](#-project-structure)
10. [Prerequisites](#-prerequisites)
11. [Installation & Setup](#-installation--setup)
12. [Configuration](#-configuration)
13. [Running the App](#-running-the-app)
14. [Using the App — Step by Step](#-using-the-app--step-by-step)
15. [CSV Transaction Format](#-csv-transaction-format)
16. [How the AI Analysis Works Internally](#-how-the-ai-analysis-works-internally)
17. [Deployment](#-deployment)
18. [Troubleshooting](#-troubleshooting)
19. [Roadmap & Future Features](#-roadmap--future-features)
20. [Contributing](#-contributing)
21. [License](#-license)

---

## 📖 Project Overview

**Finova** is a full-stack AI web application that acts as your personal financial advisor. You enter your income, monthly expenses, and any debts — and three specialised AI agents analyse your financial situation and return structured, personalised recommendations.

Unlike generic budgeting apps that just show you charts of your past spending, Finova uses **Google's Agent Development Kit (ADK)** to run a sequential pipeline of three Gemini-powered AI agents. Each agent is an expert in its own domain — budgeting, saving, and debt elimination — and they work in sequence, each building on the previous agent's findings to produce a comprehensive 360° financial picture.

The entire application is built in a single Python file using **Streamlit** for the frontend, with a custom luxury dark fintech UI injected via CSS. It is designed to run locally, on a cloud server, or be deployed for free on platforms like Render or Streamlit Community Cloud.

---

## 💡 Why Finova?

Most personal finance tools are passive — they show you what you spent last month but don't tell you what to actually **do**. Finova bridges that gap:

| Traditional Finance App | Finova |
|---|---|
| Shows spending charts | Explains WHY your spending is problematic |
| Generic budgeting tips | Personalised recommendations based on YOUR numbers |
| Static rules | AI reasoning adapts to your specific situation |
| Separate tools for budget/debt/savings | One unified pipeline covering all three |
| Requires manual interpretation | Returns structured, actionable next steps |

---

## ✨ Features

### Core Features
- **Three-Agent AI Pipeline** — Sequential Gemini AI agents that each specialise in one financial domain and pass context to the next agent
- **Budget Analysis** — Full spending categorisation with percentage breakdowns, surplus/deficit calculation, and priority-ranked cost-cutting recommendations
- **Savings Strategy** — Emergency fund sizing, savings account type recommendations (HYSA, Roth IRA, index funds), monthly contribution amounts, and automation techniques
- **Debt Reduction Planning** — Avalanche method (minimises total interest paid) vs Snowball method (maximises psychological momentum) payoff plans with a personalised recommendation on which to use
- **CSV Transaction Upload** — Upload real bank export data for AI analysis of actual spending patterns
- **Manual Expense Entry** — Enter expenses across 8 categories without needing a CSV

### UI & Visualisation Features
- **Luxury Dark Fintech Theme** — Custom CSS injected into Streamlit with a deep navy + gold palette
- **Animated Hero Title** — Gold gradient shimmer text effect using CSS `background-clip`
- **Glass Morphism Cards** — Input sections float inside frosted glass cards with subtle gold borders that glow on hover
- **Custom Metric Cards** — Key financial figures displayed in colour-coded cards (green = positive, red = negative, gold = important)
- **Interactive Donut Chart** — Spending breakdown with a 45% hole, styled to match the dark theme
- **Side-by-Side Bar Charts** — Income vs expenses and debt balance comparisons
- **Recommendation Cards** — AI advice rendered as styled cards with colour-coded left borders instead of plain alert boxes
- **Gold-Accented Tabs** — Results split across three styled tab panels
- **Animated CTA Button** — Primary button lifts and glows on hover using CSS transitions

### Technical Features
- **Pydantic v2 Validation** — All AI outputs are validated against strict typed schemas before being rendered
- **Safe JSON Parsing** — Fallback mechanism prevents crashes if AI returns malformed output
- **Session Management** — Each analysis run gets a unique session ID, isolated from others, automatically cleaned up after completion
- **Async Agent Pipeline** — Uses Python `asyncio` for non-blocking agent execution
- **Environment Variable Security** — API keys loaded from `.env` file via `python-dotenv`, never hardcoded
- **Graceful Error Handling** — All agent errors are caught and displayed as readable error messages in the UI

---

## 🛠 Tech Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| **Web Framework** | Streamlit | ≥ 1.28.0 | Frontend UI and app server |
| **AI Agent Framework** | Google ADK | 0.1.0 | Multi-agent orchestration |
| **Large Language Model** | Gemini 2.0 Flash | Latest | AI reasoning and text generation |
| **Data Validation** | Pydantic | ≥ 2.0.0 | Typed output schemas for AI responses |
| **Data Processing** | Pandas | ≥ 2.0.0 | CSV parsing and tabular data |
| **Numerical Computing** | NumPy | ≥ 2.1.0 | Array operations |
| **Charting** | Plotly | ≥ 5.15.0 | Interactive charts |
| **Environment Config** | python-dotenv | ≥ 1.0.0 | `.env` file loading |
| **Google AI Client** | google-generativeai | ≥ 0.8.0 | Gemini API connectivity |
| **Deprecation Handling** | deprecated | ≥ 1.2.14 | Required by google-adk internals |
| **Language** | Python | 3.11+ | Runtime |

---

## 🏗 Architecture — How It All Works

Finova's core is a **Sequential Multi-Agent Architecture** powered by Google ADK. Understanding this architecture is key to understanding the entire application.

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  Monthly Income + Expenses + Debts + CSV Upload                 │
└────────────────────────────┬────────────────────────────────────┘
                             │  financial_data (Python dict)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FinanceAdvisorSystem                         │
│                                                                  │
│   1. Creates unique session_id per analysis run                 │
│   2. Stores financial data in InMemorySessionService            │
│   3. Serialises data to JSON and sends to coordinator           │
│   4. Awaits pipeline completion                                  │
│   5. Extracts results from session state                        │
│   6. Cleans up session on completion or error                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FinanceCoordinatorAgent                        │
│                   (SequentialAgent)                              │
│                                                                  │
│   Runs sub-agents one by one in strict order.                   │
│   Each agent reads from and writes to shared session state.     │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  Step 1 → BudgetAnalysisAgent                           │  │
│   │  Input:  Raw income + expenses + transactions           │  │
│   │  Output: BudgetAnalysis (validated Pydantic schema)     │  │
│   │  Stored: session.state["budget_analysis"]               │  │
│   └──────────────────────────┬──────────────────────────────┘  │
│                              │                                   │
│   ┌──────────────────────────▼──────────────────────────────┐  │
│   │  Step 2 → SavingsStrategyAgent                          │  │
│   │  Input:  Budget results + income + current savings      │  │
│   │  Output: SavingsStrategy (validated Pydantic schema)    │  │
│   │  Stored: session.state["savings_strategy"]              │  │
│   └──────────────────────────┬──────────────────────────────┘  │
│                              │                                   │
│   ┌──────────────────────────▼──────────────────────────────┐  │
│   │  Step 3 → DebtReductionAgent                            │  │
│   │  Input:  All prior results + debt information           │  │
│   │  Output: DebtReduction (validated Pydantic schema)      │  │
│   │  Stored: session.state["debt_reduction"]                │  │
│   └─────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │  results dict
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RESULTS RENDERING                           │
│   Tab 1: Budget Analysis  (charts + recommendation cards)       │
│   Tab 2: Savings Strategy (metrics + allocation cards)          │
│   Tab 3: Debt Reduction   (charts + payoff plans + actions)     │
└─────────────────────────────────────────────────────────────────┘
```

### Why a Sequential Agent Architecture?

A single AI prompt asking "analyse my budget AND savings AND debt" produces generic, shallow advice. Breaking it into three specialised sequential agents means:

1. **Specialisation** — Each agent is prompted with a precise role and focuses entirely on one domain
2. **Context accumulation** — Agent 2 knows what Agent 1 found. Agent 3 knows what both found. Advice improves at each step
3. **Structured outputs** — Each agent writes to a typed Pydantic schema, so the UI always receives predictable, renderable data
4. **Isolation** — A failure in Agent 3 doesn't wipe out valid results from Agents 1 and 2

---

## 🤖 Agent Deep Dive

### Agent 1 — BudgetAnalysisAgent

**Role:** The financial data intake and categorisation specialist.

**What it receives:**
- `monthly_income` — User's stated income
- `manual_expenses` — Dict of category → amount (e.g. `{"Housing": 1200, "Food": 400}`)
- `transactions` — List of parsed CSV rows (if uploaded)
- `dependants` — Number of dependants (affects recommended spending ratios)

**What it does:**
- Groups all expenses into named spending categories
- Calculates each category as a percentage of total spending
- Compares spending ratios to healthy benchmarks (e.g. housing should be under 30% of income)
- Identifies overspending areas
- Generates prioritised recommendations with estimated monthly savings per change

**What it returns (BudgetAnalysis schema):**
```python
{
  "total_expenses": 3200.0,
  "monthly_income": 5000.0,
  "spending_categories": [
    {"category": "Housing", "amount": 1200.0, "percentage": 37.5},
    {"category": "Food",    "amount": 600.0,  "percentage": 18.75},
    ...
  ],
  "recommendations": [
    {
      "category": "Housing",
      "suggestion": "Your housing costs are 37.5% of income, above the 30% guideline. Consider a roommate or refinancing.",
      "potential_savings": 200.0
    },
    ...
  ]
}
```

---

### Agent 2 — SavingsStrategyAgent

**Role:** The long-term wealth building strategist.

**What it receives:**
- Everything Agent 1 received, plus the `budget_analysis` results from Agent 1
- `current_savings` — User's existing savings balance

**What it does:**
- Calculates the ideal emergency fund size (typically 3–6 months of expenses, adjusted for dependants and job stability)
- Recommends specific savings vehicles appropriate for the user's situation (HYSA for emergency fund, Roth IRA for retirement, index funds for long-term growth)
- Calculates realistic monthly contribution amounts based on available surplus from Agent 1's analysis
- Suggests automation techniques like automatic transfers, round-up savings, and employer match maximisation

**What it returns (SavingsStrategy schema):**
```python
{
  "emergency_fund": {
    "recommended_amount": 9600.0,
    "current_amount": 2000.0,
    "months_covered": 2.1
  },
  "recommendations": [
    {
      "account_type": "High-Yield Savings Account (HYSA)",
      "monthly_contribution": 300.0,
      "rationale": "Build your emergency fund to 6 months of expenses. Target $9,600."
    },
    {
      "account_type": "Roth IRA",
      "monthly_contribution": 200.0,
      "rationale": "Tax-free growth for retirement. Contribute after emergency fund is established."
    }
  ],
  "automation_techniques": [
    {
      "technique": "Automatic Transfer",
      "description": "Set up an automatic $300 transfer on payday to your HYSA before you can spend it."
    }
  ]
}
```

---

### Agent 3 — DebtReductionAgent

**Role:** The debt elimination strategist.

**What it receives:**
- All prior context plus structured debt data: name, balance, interest rate, minimum payment

**What it does:**
- Totals all debts and assesses overall debt load
- Builds an **Avalanche Plan** — orders debts by interest rate (highest first). This is mathematically optimal: it minimises the total interest paid over time
- Builds a **Snowball Plan** — orders debts by balance (lowest first). This is psychologically optimal: quick wins on small debts build momentum and motivation
- Recommends which plan to follow based on the user's specific debt profile and the budget surplus available from Agent 1
- Provides additional actions like balance transfer suggestions, extra payment strategies, and prioritisation reasoning

**What it returns (DebtReduction schema):**
```python
{
  "total_debt": 18500.0,
  "debts": [
    {"name": "Credit Card", "balance": 3500.0,  "interest_rate": 22.9, "minimum_payment": 75.0},
    {"name": "Car Loan",    "balance": 15000.0, "interest_rate": 6.5,  "minimum_payment": 280.0}
  ],
  "payoff_plans": {
    "avalanche": ["1. Credit Card (22.9%)", "2. Car Loan (6.5%)"],
    "snowball":  ["1. Credit Card ($3,500)", "2. Car Loan ($15,000)"],
    "recommended_plan": "avalanche"
  },
  "recommendations": [
    {
      "suggestion": "Pay $200/month extra on your Credit Card using budget surplus identified by Budget Agent.",
      "impact": "Eliminates Credit Card debt 14 months faster, saving ~$890 in interest."
    }
  ]
}
```

---

## 📐 Pydantic Data Models Explained

Pydantic models serve as **contracts** between the AI agents and the UI. Every field the AI produces is validated against these schemas before rendering. If a field is missing or the wrong type, Pydantic either uses the default or raises a catchable error — preventing UI crashes.

### Sub-models (building blocks)

```python
# A single spending bucket (e.g. Food: $600, 18.75%)
class SpendingCategory(BaseModel):
    category: str          # Required — category name
    amount: float          # Required — dollar amount
    percentage: float      # Optional — % of total spend

# A single budget improvement suggestion
class SpendingRecommendation(BaseModel):
    category: str          # Required — which area to improve
    suggestion: str        # Required — what to do
    potential_savings: float  # Optional — estimated $/month saved

# Emergency fund details
class EmergencyFund(BaseModel):
    recommended_amount: float   # Required — target fund size
    current_amount: float       # Optional — current balance
    months_covered: float       # Optional — months of expenses covered

# A single savings account recommendation
class SavingsRecommendation(BaseModel):
    account_type: str           # Required — e.g. "Roth IRA"
    monthly_contribution: float # Required — suggested contribution
    rationale: str              # Required — why this account

# A savings automation tip
class AutomationTechnique(BaseModel):
    technique: str    # Required — technique name
    description: str  # Required — how to implement it

# A single debt
class Debt(BaseModel):
    name: str                  # Required — debt label
    balance: float             # Required — remaining balance
    interest_rate: float       # Required — annual % rate
    minimum_payment: float     # Optional — monthly minimum

# Avalanche + Snowball plans
class PayoffPlans(BaseModel):
    avalanche: List[str]       # Optional — ordered list of debts
    snowball: List[str]        # Optional — ordered list of debts
    recommended_plan: str      # Optional — "avalanche" or "snowball"

# A single debt action item
class DebtRecommendation(BaseModel):
    suggestion: str  # Required — what to do
    impact: str      # Optional — expected outcome
```

### Why `Optional` fields?

Fields marked `Optional[float] = Field(None, ...)` are allowed to be `None`. This is important because the AI may not always have enough data to calculate every metric (e.g. `months_covered` requires knowing both expenses and current savings). Making these Optional prevents validation failures when the AI correctly returns null for unknown values.

---

## 🎨 UI Design System

The entire visual theme is injected into Streamlit via a single `inject_css()` function that writes a `<style>` block using `st.markdown(..., unsafe_allow_html=True)`. This approach overrides Streamlit's default styles completely.

### Design Philosophy — Luxury Dark Fintech

The aesthetic is inspired by Bloomberg Terminal, Robinhood, and high-end wealth management dashboards. The goal is to make users feel like they're using a professional financial tool, not a student project.

### Colour Palette

| Role | Hex Code | Usage |
|---|---|---|
| Background | `#0a0e1a` | Main app background — deep navy |
| Sidebar | `#0d1220` | Slightly lighter than main bg |
| Primary Gold | `#c4a459` | Borders, labels, accents, active states |
| Dark Gold | `#a8893e` | Button gradient end colour |
| Text Primary | `#e8e4dc` | Main body text — warm off-white |
| Text Muted | `#6b7280` | Subtitles, captions, placeholders |
| Text Labels | `#9ca3af` | Input labels, legend text |
| Positive | `#4ade80` | Surplus, savings amounts |
| Negative | `#f87171` | Deficit, debt, expenses over income |
| Blue Accent | `#638fac` | Chart secondary colour |

### Typography

- **DM Serif Display** — Used for all headings (h1, h2), the hero title, metric values, and the sidebar logo. This is a refined editorial serif with beautiful italics. It communicates authority and wealth.
- **DM Sans** — Used for all body text, labels, buttons, and UI copy. It is a clean, modern geometric sans-serif that pairs elegantly with DM Serif Display.

Both fonts are loaded via Google Fonts CDN at runtime.

### Component Breakdown

**Glass Cards** (`.glass-card`)
Input sections are wrapped in glass morphism cards. These have a near-transparent dark background (`rgba(255,255,255,0.03)`), a subtle gold border (`rgba(196,164,89,0.15)`), and a `backdrop-filter: blur(10px)` effect. On hover the border brightens and a faint gold glow appears via `box-shadow`.

**Metric Cards** (`.metric-card` / `.metric-row`)
AI-generated financial figures are displayed in custom HTML metric cards (not Streamlit's default `st.metric`). Three cards sit in a flex row. Values are colour-coded: green for positive surplus, red for debt/deficit, gold for key benchmarks like emergency fund targets.

**Recommendation Cards** (`.rec-card`)
Each AI recommendation renders as a card with a colour-coded 3px left border: gold for budget tips, green for savings advice, red for debt actions. The card shows the category label in uppercase gold, the suggestion text, and an optional savings/impact figure below.

**Section Labels** (`.section-label`)
Section headings are rendered in tiny uppercase gold text with a gradient line that fades from gold to transparent extending to the right edge. This creates a premium editorial feel.

**Plotly Chart Theming** (`styled_plotly()`)
All Plotly charts are styled via the `styled_plotly()` helper function which sets:
- `paper_bgcolor` and `plot_bgcolor` to transparent (so the dark app background shows through)
- `font` to DM Sans in muted grey
- `title_font` to DM Serif Display in warm white
- `colorway` to the gold/blue/green/red palette matching the rest of the UI
- Grid lines to near-invisible `rgba(255,255,255,0.05)`

---

## 📁 Project Structure

```
finova/
│
├── ai_financial_coach_agent.py     # ← Everything lives here
│   ├── Imports & Constants         #   APP_NAME, USER_ID, GEMINI_MODEL
│   ├── Pydantic Sub-models         #   SpendingCategory, Debt, PayoffPlans, etc.
│   ├── Pydantic Output Schemas     #   BudgetAnalysis, SavingsStrategy, DebtReduction
│   ├── Helper Functions            #   parse_json_safely(), parse_csv_transactions()
│   ├── FinanceAdvisorSystem class  #   All three agents + coordinator + runner
│   ├── inject_css()                #   Complete luxury dark theme CSS
│   ├── UI Components               #   render_metric_card(), render_rec_card(), styled_plotly()
│   ├── Display Helpers             #   display_budget_analysis(), display_savings_strategy(), display_debt_reduction()
│   └── main()                      #   Streamlit page config, sidebar, input form, results tabs
│
├── requirements.txt                # Python package dependencies with version pins
│
├── .env                            # Secret API keys — NEVER commit this file
│   └── GOOGLE_API_KEY=...
│
├── .gitignore                      # Excludes .env, __pycache__, venv, etc.
│
└── .streamlit/
    └── config.toml                 # Server settings and base theme colours
```

> **Note:** The entire application — all agents, UI, CSS, models, and logic — is intentionally kept in a single file for simplicity of deployment and review. In a production team setting this would be split into `agents/`, `models/`, `ui/`, and `utils/` modules.

---

## 📋 Prerequisites

Before you begin, ensure you have the following:

### 1. Python 3.11 or higher
```bash
python --version   # Should show Python 3.11.x or higher
```
Download from [python.org](https://www.python.org/downloads/) if needed.

> **Python 3.14 Users:** `numpy==1.26.4` does not have a pre-built wheel for Python 3.14 and will fail to build from source. This project uses `numpy>=2.1.0` which ships a pre-built wheel for Python 3.14. Ensure your `requirements.txt` is not changed.

### 2. Google Gemini API Key (Free)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key — you will add it to your `.env` file

> The free tier of Gemini API is sufficient to run this application. No billing setup required for basic usage.

### 3. Git (for cloning)
```bash
git --version
```

---

## ⚙ Installation & Setup

Follow these steps exactly to get Finova running on your machine.

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/finova-app.git
cd finova-app
```

### Step 2 — Create a Virtual Environment

A virtual environment keeps Finova's dependencies isolated from your system Python. This is strongly recommended.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt, confirming the virtual environment is active.

### Step 3 — Install All Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs all packages listed in `requirements.txt`. Expect this to take 2–5 minutes depending on your internet connection.

**What gets installed:**

| Package | Why It's Needed |
|---|---|
| `google-adk==0.1.0` | The multi-agent framework — LlmAgent, SequentialAgent, Runner, InMemorySessionService |
| `streamlit>=1.28.0` | The web framework that renders the UI |
| `pandas>=2.0.0` | CSV parsing, DataFrame operations, tabular data display |
| `matplotlib>=3.7.0` | Required by some google-adk dependencies |
| `numpy>=2.1.0` | Numerical operations, required by pandas |
| `plotly>=5.15.0` | Interactive donut and bar charts |
| `python-dotenv>=1.0.0` | Loads `GOOGLE_API_KEY` from `.env` file |
| `pydantic>=2.0.0` | Type-safe data models for all AI outputs |
| `google-generativeai>=0.8.0` | Google's Python client for the Gemini API |
| `deprecated>=1.2.14` | Required internally by `google-adk` |

### Step 4 — Create Your .env File

```bash
# Windows PowerShell
New-Item .env -ItemType File

# macOS / Linux
touch .env
```

Open the `.env` file in any text editor and add your Gemini API key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

**How does the app load this?**
At the top of `ai_financial_coach_agent.py`, `load_dotenv()` is called. This reads the `.env` file and injects all key-value pairs as environment variables. The Google ADK then automatically reads `GOOGLE_API_KEY` from the environment when initialising the Gemini clients. You never need to pass the key explicitly in code.

### Step 5 — Verify Your Setup

```bash
# Confirm all packages installed correctly
pip list | grep -E "streamlit|google-adk|pydantic|plotly"

# Confirm your API key is set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key found!' if os.getenv('GOOGLE_API_KEY') else 'Key NOT found!')"
```

---

## 🔧 Configuration

### Streamlit Config — `.streamlit/config.toml`

```toml
[server]
headless = true              # Prevents browser auto-open — required for cloud deployment
port = 8501                  # Default Streamlit port
enableCORS = false           # Disables CORS restriction — needed for embedded deployments
enableXsrfProtection = false # Simplifies token handling in containerised environments
address = "0.0.0.0"          # Binds to all network interfaces — required for AWS/Render/Fly

[theme]
base = "dark"                       # Dark base theme from Streamlit
backgroundColor = "#0a0e1a"         # Main background (overridden by CSS but set as fallback)
secondaryBackgroundColor = "#0d1220" # Sidebar background
textColor = "#e8e4dc"               # Default text colour
primaryColor = "#c4a459"            # Accent colour for widgets
```

### Changing the AI Model

Open `ai_financial_coach_agent.py` and find this line near the top:

```python
GEMINI_MODEL: str = "gemini-2.0-flash"
```

You can change this to any available Gemini model:

| Model | Speed | Quality | Best For |
|---|---|---|---|
| `gemini-2.0-flash` | Fast | Good | Default — balanced speed and quality |
| `gemini-1.5-flash` | Fast | Good | Alternative if 2.0 has availability issues |
| `gemini-1.5-pro` | Slower | Best | More detailed analysis, longer reasoning |

> **Note:** `gemini-2.0-flash-exp` has been deprecated and removed. Do not use it.

### Changing the App Name / User ID

These constants control the ADK session namespacing:

```python
APP_NAME: str = "ai_financial_coach"   # Identifies your app in ADK session service
USER_ID: str = "user_001"              # User identifier for session isolation
```

For a multi-user deployment, `USER_ID` should be set dynamically per user session using Streamlit's `st.session_state`.

---

## ▶ Running the App

```bash
# Make sure your virtual environment is activated first
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

python -m streamlit run ai_financial_coach_agent.py
```

Streamlit will print something like:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open **http://localhost:8501** in your browser.

> **Why `python -m streamlit` instead of just `streamlit`?**
> On Windows with user-level Python installs (common with Python 3.14), the `streamlit` executable may not be on PATH. Using `python -m streamlit` bypasses this by calling the module directly through the Python interpreter, which always works.

---

## 📱 Using the App — Step by Step

### Step 1 — Financial Overview Section
Fill in your **Monthly Income** (your take-home pay after tax) and **Number of Dependants** (children, elderly parents, etc. you financially support — this affects recommended savings ratios). Optionally upload a CSV of your bank transactions.

### Step 2 — Monthly Expenses Section
Enter your average monthly spend across 8 categories. Leave a field at `0` if it doesn't apply — zero values are automatically excluded from the analysis. The categories are:

- **Housing** — Rent or mortgage payment
- **Food** — Groceries + dining out combined
- **Transportation** — Car payment, fuel, insurance, public transit
- **Utilities** — Electricity, water, internet, phone
- **Healthcare** — Insurance premiums, medications, appointments
- **Entertainment** — Streaming, hobbies, social activities
- **Education** — Tuition, courses, books
- **Other** — Anything that doesn't fit the above categories

### Step 3 — Debt Information (Optional)
Enter one debt at a time with its name, current balance, annual interest rate, and minimum monthly payment. Even one debt entry gives the AI enough to build a meaningful payoff plan.

### Step 4 — Click "Analyse My Finances"
The three agents will run sequentially. This typically takes **15–45 seconds** depending on Gemini API response time. A spinner with the message "Running AI agents — analysing your finances..." will display during processing.

### Step 5 — Review Your Results

Results appear in three tabs:

**Tab 1 — Budget Analysis**
- Three metric cards: Monthly Income, Total Expenses, Surplus/Deficit (green if positive, red if negative)
- A donut chart showing your spending breakdown by category
- A bar chart comparing income vs total expenses
- Recommendation cards — one per AI suggestion, with estimated monthly savings per change

**Tab 2 — Savings Strategy**
- Three metric cards: Recommended Emergency Fund size, Your Current Savings, Months of Expenses Covered
- Green savings allocation cards — one per recommended account type, showing monthly contribution and rationale
- Automation technique cards — practical steps to automate saving

**Tab 3 — Debt Reduction Plan**
- Two metric cards: Total Debt, Number of Debts
- Bar chart of debt balances
- Full debt breakdown table
- Avalanche method card (highest interest first — saves most money)
- Snowball method card (lowest balance first — builds momentum)
- Red action recommendation cards with expected impact statements

---

## 📊 CSV Transaction Format

To upload your bank transactions, your CSV must contain exactly these three column headers. Column names are case-sensitive.

```csv
Date,Category,Amount
2024-01-01,Housing,1200.00
2024-01-02,Food,85.50
2024-01-03,Transportation,45.00
2024-01-05,Entertainment,32.99
2024-01-07,Healthcare,150.00
2024-01-10,Food,62.40
2024-01-15,Utilities,95.00
2024-01-20,Education,200.00
```

**Column specifications:**

| Column | Type | Format | Notes |
|---|---|---|---|
| `Date` | String | YYYY-MM-DD | Other date formats are also parsed automatically via `pd.to_datetime()` |
| `Category` | String | Any text | Should match the expense categories used in the manual entry section for consistency |
| `Amount` | Number | Decimal | Dollar signs (`$`) and commas (`,`) are automatically stripped |

**How CSV data is processed:**

1. File bytes are decoded as UTF-8 and read into a Pandas DataFrame
2. Required columns are validated — missing columns raise a clear error message
3. `Date` column is parsed with `pd.to_datetime()` and reformatted to `YYYY-MM-DD`
4. `Amount` column has `$` and `,` stripped via regex, then cast to `float`
5. Rows are grouped by `Category` and totals are computed
6. The full transaction list and category totals are passed to the agent pipeline

**A CSV template with the correct format is available to download directly from the app sidebar.**

---

## 🔍 How the AI Analysis Works Internally

Here is a detailed walk-through of what happens inside `analyze_finances()` from the moment you click the button:

```python
async def analyze_finances(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
```

**1. Session Creation**
A unique `session_id` is generated using the current timestamp (e.g. `finance_session_20240315_143022`). This ensures multiple simultaneous users (or rapid repeated runs) don't interfere with each other. The financial data is stored as the initial session state in `InMemorySessionService`.

**2. Data Preprocessing**
If transactions were uploaded, `_preprocess_transactions()` is called to prepare the data. If manual expenses were entered, `_preprocess_manual_expenses()` prepares them. Both are currently stub methods you can extend.

**3. Default Results Creation**
Before the agents run, `_create_default_results()` builds a safe fallback dict. If any agent fails to produce output, the default (empty lists, zero values) is used instead of crashing the UI.

**4. Agent Pipeline Execution**
The financial data is serialised to JSON and wrapped in a `types.Content` message (the format Gemini expects). The `Runner.run_async()` method streams events from the coordinator agent. The loop runs until `event.is_final_response()` is `True` and the event author is the coordinator agent.

**5. Result Extraction**
After the pipeline completes, the updated session is fetched. For each of the three output keys (`budget_analysis`, `savings_strategy`, `debt_reduction`), the value is extracted from session state and passed through `parse_json_safely()` which handles any malformed JSON from the AI, falling back to the default if parsing fails.

**6. Session Cleanup**
The `finally` block always runs (even if an exception occurred) and deletes the session from `InMemorySessionService`, freeing memory.

---

## 🚀 Deployment

### Option 1 — Streamlit Community Cloud (100% Free, Forever, Easiest)

Streamlit's own cloud platform is the simplest free deployment option. No credit card, no time limit.

1. Push your code to a **public** GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select your repository, branch (`main`), and main file (`ai_financial_coach_agent.py`)
5. Expand **"Advanced settings"** → **"Secrets"** and add:
   ```toml
   GOOGLE_API_KEY = "your_actual_key_here"
   ```
6. Click **"Deploy"**

Your app will be live at `https://your-app-name.streamlit.app` within 2 minutes.

---

### Option 2 — Render.com (Free Tier Available)

1. Push code to GitHub (without `.env`)
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repository
4. Configure the service:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m streamlit run ai_financial_coach_agent.py --server.port $PORT --server.address 0.0.0.0`
5. Under **Environment Variables**, add `GOOGLE_API_KEY` = your key
6. Click **Create Web Service**

> Free tier instances spin down after 15 minutes of inactivity and take ~30 seconds to wake on the next request.

---

### Option 3 — AWS EC2 Free Tier (12 Months Free)

AWS offers a `t2.micro` instance free for 12 months — enough to run Finova 24/7.

```bash
# After SSH-ing into your EC2 instance:
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y

git clone https://github.com/YOUR_USERNAME/finova-app.git
cd finova-app

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env with your API key
echo "GOOGLE_API_KEY=your_key_here" > .env

# Run persistently with screen
sudo apt install screen -y
screen -S finova
source venv/bin/activate
python -m streamlit run ai_financial_coach_agent.py
# Press Ctrl+A then D to detach — app keeps running
```

Access at `http://YOUR_EC2_PUBLIC_IP:8501`

> Open port **8501** in your EC2 Security Group inbound rules (Custom TCP, 0.0.0.0/0).

---

### Deployment Comparison

| Platform | Cost | Always On | Custom Domain | Setup Time | Best For |
|---|---|---|---|---|---|
| Streamlit Cloud | Free forever | Yes | `.streamlit.app` subdomain | 2 min | Quickest public share |
| Render | Free (sleeps) | No (free tier) | Yes | 5 min | Permanent URL without AWS |
| AWS EC2 | Free 12 months | Yes | Needs setup | 30 min | Full control |
| Fly.io | Free (3 VMs) | Yes | Yes | 15 min | Best free always-on option |

---

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'deprecated'`
```bash
pip install deprecated --user
```

### `streamlit: command not found` or not recognised
```bash
python -m streamlit run ai_financial_coach_agent.py
```

### `404 NOT_FOUND: models/gemini-2.0-flash-exp is not found`
The experimental model was deprecated. The `GEMINI_MODEL` constant in the code is already set to `gemini-2.0-flash` (stable). If you see this error, check that you haven't accidentally changed it back.

### `numpy` build error on Python 3.14
Your `requirements.txt` must have `numpy>=2.1.0` (not `numpy==1.26.4`). Check with:
```bash
cat requirements.txt | grep numpy
```

### Blank / Black Screen
The app is running but has no content in the main body. This happens if `main()` only contains sidebar code. Ensure your version of the file includes the full input form and results rendering code in the main body.

### VS Code Pylance import warnings
These are not errors — they mean VS Code can't find your packages in its selected Python interpreter. Fix with:
`Ctrl+Shift+P` → **Python: Select Interpreter** → choose your virtual environment or Python 3.14 path.

### Analysis takes too long or times out
The Gemini API free tier has rate limits. If analysis consistently times out:
- Try switching to `gemini-1.5-flash` which may have different rate limit buckets
- Add retry logic around the `runner.run_async()` call
- Check your API key quota at [Google AI Studio](https://aistudio.google.com)

---

## 🗺 Roadmap & Future Features

Planned improvements for future versions:

- [ ] **Multiple Debt Support** — Add/remove multiple debts dynamically using `st.session_state`
- [ ] **Financial Goals Tracker** — Set goals (house down payment, vacation fund) and track progress
- [ ] **Monthly Trend Analysis** — Visualise spending trends across multiple months of CSV data
- [ ] **PDF Report Export** — Generate a downloadable PDF of the full analysis
- [ ] **Multi-Currency Support** — Add a currency selector for non-USD users
- [ ] **User Accounts** — Persistent profiles with analysis history using a database backend
- [ ] **Investment Portfolio Analysis** — Fourth agent specialising in investment allocation
- [ ] **Net Worth Tracker** — Assets vs liabilities over time
- [ ] **Bill Reminder Reminders** — Calendar integration for due date alerts

---

## 🤝 Contributing

Contributions are welcome and appreciated! Here is how to get involved:

### Setting Up for Development

```bash
git clone https://github.com/mandarvisave/finova-app.git
cd finova-app
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env       # then add your API key
```

### Contribution Workflow

1. **Fork** the repository on GitHub
2. **Create a branch** for your feature: `git checkout -b feature/pdf-export`
3. **Make your changes** and test them locally
4. **Commit** with a clear message: `git commit -m "Add PDF export for analysis results"`
5. **Push** to your fork: `git push origin feature/pdf-export`
6. **Open a Pull Request** against the `main` branch

### Contribution Guidelines

- Keep all logic within the single-file structure unless the addition is substantial enough to warrant a module split
- All new AI outputs must have a corresponding Pydantic model — no raw dict returns from agents
- New UI components should use the existing CSS class system (`.glass-card`, `.rec-card`, `.metric-card`)
- Test with at least one manual expense entry and one CSV upload before submitting
- Update this README if you add a new feature, configuration option, or dependency

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 Finova Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<div align="center">

**Built with Google ADK · Gemini AI · Streamlit · Pydantic · Plotly**

**Finova — AI Financial Intelligence**

*If this project helped you, please give it a ⭐ on GitHub*

</div>
