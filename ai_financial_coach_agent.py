import os
import json
import asyncio
import logging
from io import StringIO
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
load_dotenv()

APP_NAME: str = "ai_financial_coach"
USER_ID: str = "user_001"
GEMINI_MODEL: str = "gemini-2.0-flash"

# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class SpendingCategory(BaseModel):
    category: str = Field(..., description="Name of the spending category")
    amount: float = Field(..., description="Amount spent in this category")
    percentage: Optional[float] = Field(None, description="Percentage of total spending")

class SpendingRecommendation(BaseModel):
    category: str = Field(..., description="Category to improve")
    suggestion: str = Field(..., description="Actionable recommendation")
    potential_savings: Optional[float] = Field(None, description="Estimated monthly savings")

class EmergencyFund(BaseModel):
    recommended_amount: float = Field(..., description="Recommended emergency fund size")
    current_amount: Optional[float] = Field(None, description="Current emergency fund balance")
    months_covered: Optional[float] = Field(None, description="Months of expenses covered")

class SavingsRecommendation(BaseModel):
    account_type: str = Field(..., description="Type of savings account or vehicle")
    monthly_contribution: float = Field(..., description="Recommended monthly contribution")
    rationale: str = Field(..., description="Reason for this recommendation")

class AutomationTechnique(BaseModel):
    technique: str = Field(..., description="Name of the automation technique")
    description: str = Field(..., description="How to implement this technique")

class Debt(BaseModel):
    name: str = Field(..., description="Name or label of the debt")
    balance: float = Field(..., description="Remaining balance")
    interest_rate: float = Field(..., description="Annual interest rate as a percentage")
    minimum_payment: Optional[float] = Field(None, description="Minimum monthly payment")

class PayoffPlans(BaseModel):
    avalanche: Optional[List[str]] = Field(None, description="Avalanche method payoff order")
    snowball: Optional[List[str]] = Field(None, description="Snowball method payoff order")
    recommended_plan: Optional[str] = Field(None, description="Which plan is recommended")

class DebtRecommendation(BaseModel):
    suggestion: str = Field(..., description="Actionable debt reduction recommendation")
    impact: Optional[str] = Field(None, description="Expected impact of following this advice")

# ---------------------------------------------------------------------------
# Primary Pydantic output schemas
# ---------------------------------------------------------------------------

class BudgetAnalysis(BaseModel):
    total_expenses: float = Field(..., description="Total monthly expenses")
    monthly_income: Optional[float] = Field(None, description="Monthly income")
    spending_categories: List[SpendingCategory] = Field(..., description="Breakdown of spending by category")
    recommendations: List[SpendingRecommendation] = Field(..., description="Spending recommendations")

class SavingsStrategy(BaseModel):
    emergency_fund: EmergencyFund = Field(..., description="Emergency fund recommendation")
    recommendations: List[SavingsRecommendation] = Field(..., description="Savings allocation recommendations")
    automation_techniques: Optional[List[AutomationTechnique]] = Field(None, description="Automation techniques to help save")

class DebtReduction(BaseModel):
    total_debt: float = Field(..., description="Total debt amount")
    debts: List[Debt] = Field(..., description="List of all debts")
    payoff_plans: PayoffPlans = Field(..., description="Debt payoff strategies")
    recommendations: Optional[List[DebtRecommendation]] = Field(None, description="Recommendations for debt reduction")

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def parse_json_safely(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, dict):
        return value
    try:
        cleaned = str(value).replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        return default

def parse_csv_transactions(file_content: bytes) -> Dict[str, Any]:
    try:
        df = pd.read_csv(StringIO(file_content.decode("utf-8")))
        required_columns = ["Date", "Category", "Amount"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        df["Amount"] = df["Amount"].replace(r"[\$,]", "", regex=True).astype(float)
        category_totals = df.groupby("Category")["Amount"].sum().reset_index()
        return {
            "transactions": df.to_dict("records"),
            "category_totals": category_totals.to_dict("records"),
        }
    except Exception as exc:
        raise ValueError(f"Error parsing CSV file: {exc}") from exc

# ---------------------------------------------------------------------------
# Finance advisor system
# ---------------------------------------------------------------------------

class FinanceAdvisorSystem:
    def __init__(self) -> None:
        self.session_service = InMemorySessionService()
        self.budget_analysis_agent = LlmAgent(
            name="BudgetAnalysisAgent", model=GEMINI_MODEL,
            description="Analyses spending patterns and recommends budget improvements.",
            instruction=("You are a Budget Analysis Agent specialised in reviewing financial "
                "transactions and expenses. You are the first of three financial advisor agents."),
            output_schema=BudgetAnalysis, output_key="budget_analysis",
        )
        self.savings_strategy_agent = LlmAgent(
            name="SavingsStrategyAgent", model=GEMINI_MODEL,
            description="Recommends savings strategies based on income and expenses.",
            instruction=("You are a Savings Strategy Agent specialised in creating personalised "
                "savings plans. You are the second agent in the sequence."),
            output_schema=SavingsStrategy, output_key="savings_strategy",
        )
        self.debt_reduction_agent = LlmAgent(
            name="DebtReductionAgent", model=GEMINI_MODEL,
            description="Creates optimised debt payoff plans.",
            instruction=("You are a Debt Reduction Agent specialised in creating debt payoff "
                "strategies. You are the final agent in the sequence."),
            output_schema=DebtReduction, output_key="debt_reduction",
        )
        self.coordinator_agent = SequentialAgent(
            name="FinanceCoordinatorAgent",
            description="Coordinates the three finance agents.",
            sub_agents=[self.budget_analysis_agent, self.savings_strategy_agent, self.debt_reduction_agent],
        )
        self.runner = Runner(agent=self.coordinator_agent, app_name=APP_NAME, session_service=self.session_service)

    async def analyze_finances(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        session_id = f"finance_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            initial_state: Dict[str, Any] = {
                "monthly_income": financial_data.get("monthly_income", 0),
                "dependants": financial_data.get("dependants", 0),
                "transactions": financial_data.get("transactions", []),
                "manual_expenses": financial_data.get("manual_expenses", {}),
                "debts": financial_data.get("debts", []),
            }
            session = self.session_service.create_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=session_id, state=initial_state)
            if session.state.get("transactions"):
                self._preprocess_transactions(session)
            if session.state.get("manual_expenses"):
                self._preprocess_manual_expenses(session)
            default_results = self._create_default_results(financial_data)
            user_content = types.Content(role="user", parts=[types.Part(text=json.dumps(financial_data))])
            async for event in self.runner.run_async(user_id=USER_ID, session_id=session_id, new_message=user_content):
                if event.is_final_response() and event.author == self.coordinator_agent.name:
                    break
            updated_session = self.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
            results: Dict[str, Any] = {}
            for key in ["budget_analysis", "savings_strategy", "debt_reduction"]:
                value = updated_session.state.get(key)
                results[key] = parse_json_safely(value, default_results[key]) if value else default_results[key]
            return results
        finally:
            self.session_service.delete_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)

    def _preprocess_transactions(self, session: Any) -> None:
        pass

    def _preprocess_manual_expenses(self, session: Any) -> None:
        pass

    def _create_default_results(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "budget_analysis": {"total_expenses": 0, "monthly_income": financial_data.get("monthly_income", 0), "spending_categories": [], "recommendations": []},
            "savings_strategy": {"emergency_fund": {"recommended_amount": 0}, "recommendations": [], "automation_techniques": []},
            "debt_reduction": {"total_debt": 0, "debts": [], "payoff_plans": {}, "recommendations": []},
        }

# ---------------------------------------------------------------------------
# Custom CSS — Luxury Dark Fintech Theme
# ---------------------------------------------------------------------------

def inject_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #e8e4dc;
    }

    .stApp {
        background: #0a0e1a;
        background-image:
            radial-gradient(ellipse at 10% 20%, rgba(196,164,89,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 80%, rgba(99,143,172,0.05) 0%, transparent 50%);
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1200px; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #0d1220;
        border-right: 1px solid rgba(196,164,89,0.15);
    }
    [data-testid="stSidebar"] .block-container { padding: 2rem 1.5rem; }

    /* ── Typography ── */
    h1 { font-family: 'DM Serif Display', serif !important; font-size: 3rem !important; line-height: 1.1 !important; }
    h2 { font-family: 'DM Serif Display', serif !important; font-size: 1.8rem !important; }
    h3 { font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; font-size: 1.1rem !important; letter-spacing: 0.05em; text-transform: uppercase; color: #c4a459 !important; }

    /* ── Gold accent text ── */
    .gold { color: #c4a459; }
    .muted { color: #6b7280; font-size: 0.9rem; }

    /* ── Hero section ── */
    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 3.2rem;
        line-height: 1.15;
        background: linear-gradient(135deg, #e8e4dc 0%, #c4a459 50%, #e8e4dc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    .hero-sub {
        color: #6b7280;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 0.02em;
        margin-bottom: 2.5rem;
    }

    /* ── Glass cards ── */
    .glass-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(196,164,89,0.15);
        border-radius: 16px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(196,164,89,0.35);
        box-shadow: 0 0 30px rgba(196,164,89,0.07);
    }
    .card-title {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #c4a459;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── Metric cards ── */
    .metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .metric-card {
        flex: 1;
        min-width: 160px;
        background: rgba(196,164,89,0.05);
        border: 1px solid rgba(196,164,89,0.2);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
    }
    .metric-label { font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; color: #6b7280; margin-bottom: 0.4rem; }
    .metric-value { font-family: 'DM Serif Display', serif; font-size: 1.9rem; color: #e8e4dc; }
    .metric-value.positive { color: #4ade80; }
    .metric-value.negative { color: #f87171; }
    .metric-value.gold { color: #c4a459; -webkit-text-fill-color: #c4a459; }

    /* ── Divider ── */
    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(196,164,89,0.4), transparent);
        margin: 2rem 0;
        border: none;
    }

    /* ── Input fields ── */
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(196,164,89,0.2) !important;
        border-radius: 8px !important;
        color: #e8e4dc !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stTextInput"] input:focus {
        border-color: rgba(196,164,89,0.6) !important;
        box-shadow: 0 0 0 2px rgba(196,164,89,0.1) !important;
    }
    label { color: #9ca3af !important; font-size: 0.85rem !important; font-weight: 500 !important; letter-spacing: 0.03em !important; }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.02) !important;
        border: 1px dashed rgba(196,164,89,0.3) !important;
        border-radius: 12px !important;
    }

    /* ── Primary button ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #c4a459 0%, #a8893e 100%) !important;
        color: #0a0e1a !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.05em !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        transition: opacity 0.2s ease, transform 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(196,164,89,0.3) !important;
    }

    /* ── Secondary button (download) ── */
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid rgba(196,164,89,0.4) !important;
        color: #c4a459 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(196,164,89,0.08) !important;
        border-color: rgba(196,164,89,0.7) !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] [role="tablist"] {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 0.3rem;
        gap: 0.25rem;
        border: 1px solid rgba(196,164,89,0.1);
    }
    [data-testid="stTabs"] button[role="tab"] {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        color: #6b7280 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: rgba(196,164,89,0.12) !important;
        color: #c4a459 !important;
    }

    /* ── Alerts & info boxes ── */
    .stAlert {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 10px !important;
        border-left-width: 3px !important;
    }

    /* ── Recommendation cards ── */
    .rec-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-left: 3px solid #c4a459;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .rec-card.green { border-left-color: #4ade80; }
    .rec-card.red { border-left-color: #f87171; }
    .rec-category { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #c4a459; margin-bottom: 0.25rem; font-weight: 600; }
    .rec-text { color: #d1d5db; font-size: 0.95rem; line-height: 1.5; }
    .rec-savings { font-size: 0.8rem; color: #4ade80; margin-top: 0.3rem; }

    /* ── Spinner ── */
    [data-testid="stSpinner"] { color: #c4a459 !important; }

    /* ── Sidebar elements ── */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        font-family: 'DM Serif Display', serif !important;
        color: #e8e4dc !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] li { color: #9ca3af; font-size: 0.875rem; }
    .sidebar-logo {
        font-family: 'DM Serif Display', serif;
        font-size: 1.5rem;
        color: #c4a459;
        letter-spacing: 0.02em;
        margin-bottom: 0.25rem;
    }
    .sidebar-tagline { font-size: 0.75rem; color: #4b5563; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 2rem; }

    /* ── Section label ── */
    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #c4a459;
        margin-bottom: 1rem;
        margin-top: 2rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(196,164,89,0.3), transparent);
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(196,164,89,0.15) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* ── Success/error messages ── */
    .stSuccess { background: rgba(74,222,128,0.08) !important; border-color: rgba(74,222,128,0.3) !important; }
    .stError { background: rgba(248,113,113,0.08) !important; border-color: rgba(248,113,113,0.3) !important; }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# UI Components
# ---------------------------------------------------------------------------

def render_metric_card(label: str, value: str, style: str = "") -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {style}">{value}</div>
    </div>"""

def render_rec_card(category: str, text: str, savings: str = "", style: str = "") -> None:
    savings_html = f'<div class="rec-savings">Potential saving: {savings}</div>' if savings else ""
    st.markdown(f"""
    <div class="rec-card {style}">
        <div class="rec-category">{category}</div>
        <div class="rec-text">{text}</div>
        {savings_html}
    </div>""", unsafe_allow_html=True)

def styled_plotly(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#9ca3af"),
        title_font=dict(family="DM Serif Display", color="#e8e4dc", size=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9ca3af")),
        margin=dict(t=50, b=20, l=20, r=20),
        colorway=["#c4a459", "#638fac", "#4ade80", "#f87171", "#a78bfa", "#fb923c"],
    )
    return fig

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def display_budget_analysis(analysis: Dict[str, Any]) -> None:
    income = analysis.get("monthly_income") or 0
    expenses = analysis.get("total_expenses") or 0
    surplus = income - expenses

    # Metric row
    surplus_style = "positive" if surplus >= 0 else "negative"
    st.markdown(f"""
    <div class="metric-row">
        {render_metric_card("Monthly Income", f"${income:,.0f}")}
        {render_metric_card("Total Expenses", f"${expenses:,.0f}", "negative" if expenses > income else "")}
        {render_metric_card("Surplus / Deficit", f"${abs(surplus):,.0f}", surplus_style)}
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        if analysis.get("spending_categories"):
            fig = px.pie(
                values=[c["amount"] for c in analysis["spending_categories"]],
                names=[c["category"] for c in analysis["spending_categories"]],
                title="Spending Breakdown",
                hole=0.45,
            )
            fig = styled_plotly(fig)
            fig.update_traces(textfont_color="#e8e4dc", marker=dict(line=dict(color="#0a0e1a", width=2)))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if income or expenses:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=["Income", "Expenses"],
                y=[income, expenses],
                marker_color=["#4ade80", "#f87171"],
                marker_line_color="rgba(0,0,0,0)",
                width=0.45,
            ))
            fig2 = styled_plotly(fig2)
            fig2.update_layout(title="Income vs Expenses", showlegend=False)
            fig2.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)")
            st.plotly_chart(fig2, use_container_width=True)

    if analysis.get("recommendations"):
        st.markdown('<div class="section-label">Recommendations</div>', unsafe_allow_html=True)
        for rec in analysis["recommendations"]:
            savings_str = f"${rec['potential_savings']:,.0f}/mo" if rec.get("potential_savings") else ""
            render_rec_card(rec.get("category", ""), rec.get("suggestion", ""), savings_str)


def display_savings_strategy(strategy: Dict[str, Any]) -> None:
    ef = strategy.get("emergency_fund", {})

    if ef:
        rec_amount = ef.get("recommended_amount", 0)
        current = ef.get("current_amount") or 0
        months = ef.get("months_covered") or 0
        st.markdown(f"""
        <div class="metric-row">
            {render_metric_card("Recommended Fund", f"${rec_amount:,.0f}", "gold")}
            {render_metric_card("Current Savings", f"${current:,.0f}")}
            {render_metric_card("Months Covered", f"{months:.1f}" if months else "N/A")}
        </div>""", unsafe_allow_html=True)

    if strategy.get("recommendations"):
        st.markdown('<div class="section-label">Savings Allocations</div>', unsafe_allow_html=True)
        for rec in strategy["recommendations"]:
            render_rec_card(
                rec.get("account_type", ""),
                rec.get("rationale", ""),
                f"${rec.get('monthly_contribution', 0):,.0f}/mo",
                "green",
            )

    if strategy.get("automation_techniques"):
        st.markdown('<div class="section-label">Automation Techniques</div>', unsafe_allow_html=True)
        for tech in strategy["automation_techniques"]:
            render_rec_card(tech.get("technique", ""), tech.get("description", ""))


def display_debt_reduction(debt_plan: Dict[str, Any]) -> None:
    total = debt_plan.get("total_debt") or 0
    debts = debt_plan.get("debts", [])

    st.markdown(f"""
    <div class="metric-row">
        {render_metric_card("Total Debt", f"${total:,.0f}", "negative" if total > 0 else "")}
        {render_metric_card("Number of Debts", str(len(debts)))}
    </div>""", unsafe_allow_html=True)

    if debts:
        st.markdown('<div class="section-label">Debt Breakdown</div>', unsafe_allow_html=True)
        df = pd.DataFrame(debts)
        fig = go.Figure(go.Bar(
            x=[d["name"] for d in debts],
            y=[d["balance"] for d in debts],
            marker_color="#f87171",
            marker_line_color="rgba(0,0,0,0)",
        ))
        fig = styled_plotly(fig)
        fig.update_layout(title="Debt Balances", showlegend=False)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

    plans = debt_plan.get("payoff_plans", {})
    if plans:
        st.markdown('<div class="section-label">Payoff Strategies</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="glass-card"><div class="card-title">Avalanche Method — Highest Interest First</div>', unsafe_allow_html=True)
            for item in (plans.get("avalanche") or []):
                st.markdown(f"<div class='rec-text'>&#8227; {item}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="glass-card"><div class="card-title">Snowball Method — Lowest Balance First</div>', unsafe_allow_html=True)
            for item in (plans.get("snowball") or []):
                st.markdown(f"<div class='rec-text'>&#8227; {item}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    if debt_plan.get("recommendations"):
        st.markdown('<div class="section-label">Recommendations</div>', unsafe_allow_html=True)
        for rec in debt_plan["recommendations"]:
            render_rec_card("Action", rec.get("suggestion", ""), rec.get("impact", ""), "red")


# ---------------------------------------------------------------------------
# Streamlit entry point
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Finova — AI Financial Coach",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">Finova</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">AI Financial Intelligence</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="card-title">API Setup</div>', unsafe_allow_html=True)
        st.markdown("""
        <p>Add your Gemini API key to the <code>.env</code> file:</p>
        <code>GOOGLE_API_KEY=your_key_here</code>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:2rem">CSV Template</div>', unsafe_allow_html=True)
        st.markdown("""
        <p>Required columns:</p>
        <p><strong style="color:#c4a459">Date</strong> &nbsp;·&nbsp; <strong style="color:#c4a459">Category</strong> &nbsp;·&nbsp; <strong style="color:#c4a459">Amount</strong></p>
        """, unsafe_allow_html=True)
        sample_csv = "Date,Category,Amount\n2024-01-01,Housing,1200.00\n2024-01-02,Food,150.50\n2024-01-03,Transportation,45.00\n"
        st.download_button(label="Download CSV Template", data=sample_csv, file_name="expense_template.csv", mime="text/csv")

        st.markdown("---")
        st.markdown('<p class="muted">Powered by Google ADK &amp; Gemini AI</p>', unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown('<div class="hero-title">Your AI Financial Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Personalised budget analysis, savings strategies &amp; debt reduction — powered by Gemini AI</div>', unsafe_allow_html=True)

    # ── Income & Overview ─────────────────────────────────────────────────
    st.markdown('<div class="section-label">Financial Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, value=5000.0, step=100.0)
    with col2:
        dependants = st.number_input("Dependants", min_value=0, value=0, step=1)
    with col3:
        uploaded_file = st.file_uploader("Upload Transactions CSV", type=["csv"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Monthly Expenses ──────────────────────────────────────────────────
    st.markdown('<div class="section-label">Monthly Expenses</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1:
        housing = st.number_input("Housing ($)", min_value=0.0, value=0.0, step=50.0)
        food = st.number_input("Food ($)", min_value=0.0, value=0.0, step=50.0)
    with ec2:
        transport = st.number_input("Transportation ($)", min_value=0.0, value=0.0, step=25.0)
        utilities = st.number_input("Utilities ($)", min_value=0.0, value=0.0, step=25.0)
    with ec3:
        healthcare = st.number_input("Healthcare ($)", min_value=0.0, value=0.0, step=25.0)
        entertainment = st.number_input("Entertainment ($)", min_value=0.0, value=0.0, step=25.0)
    with ec4:
        education = st.number_input("Education ($)", min_value=0.0, value=0.0, step=25.0)
        savings_input = st.number_input("Current Savings ($)", min_value=0.0, value=0.0, step=100.0)
    other = st.number_input("Other Expenses ($)", min_value=0.0, value=0.0, step=25.0)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Debts ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Debt Information (Optional)</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    dc1, dc2, dc3, dc4 = st.columns(4)
    with dc1:
        debt_name = st.text_input("Debt Name", placeholder="e.g. Car Loan")
    with dc2:
        debt_balance = st.number_input("Balance ($)", min_value=0.0, value=0.0, step=100.0)
    with dc3:
        debt_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=0.0, step=0.1)
    with dc4:
        debt_min = st.number_input("Min. Payment ($)", min_value=0.0, value=0.0, step=25.0)
    st.markdown('</div>', unsafe_allow_html=True)

    debts = []
    if debt_name and debt_balance > 0:
        debts.append({"name": debt_name, "balance": debt_balance, "interest_rate": debt_rate, "minimum_payment": debt_min})

    # ── CTA Button ────────────────────────────────────────────────────────
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    if st.button("Analyse My Finances", type="primary", use_container_width=True):
        manual_expenses = {k: v for k, v in {
            "Housing": housing, "Food": food, "Transportation": transport,
            "Utilities": utilities, "Healthcare": healthcare, "Entertainment": entertainment,
            "Education": education, "Other": other,
        }.items() if v > 0}

        transactions = []
        if uploaded_file:
            try:
                parsed = parse_csv_transactions(uploaded_file.read())
                transactions = parsed.get("transactions", [])
                st.success(f"{len(transactions)} transactions loaded successfully.")
            except ValueError as e:
                st.error(str(e))

        financial_data = {
            "monthly_income": monthly_income, "dependants": dependants,
            "manual_expenses": manual_expenses, "transactions": transactions,
            "debts": debts, "current_savings": savings_input,
        }

        with st.spinner("Running AI agents — analysing your finances..."):
            try:
                advisor = FinanceAdvisorSystem()
                results = asyncio.run(advisor.analyze_finances(financial_data))

                st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="hero-title" style="font-size:2rem">Analysis Results</div>', unsafe_allow_html=True)

                tab1, tab2, tab3 = st.tabs(["  Budget Analysis  ", "  Savings Strategy  ", "  Debt Reduction  "])
                with tab1:
                    display_budget_analysis(results.get("budget_analysis", {}))
                with tab2:
                    display_savings_strategy(results.get("savings_strategy", {}))
                with tab3:
                    display_debt_reduction(results.get("debt_reduction", {}))

            except Exception as e:
                st.error(f"Analysis failed: {e}")
                logging.exception("Analysis failed")


if __name__ == "__main__":
    main()
