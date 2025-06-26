"""
Professional Report Generator
Creates institutional-quality PDF reports with compliance tracking and audit trails
"""
import io
import base64
from datetime import date, datetime
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, field

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus import Image as RLImage
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from models.financial_models import ResearchReport, EPVCalculation, CompanyProfile
from analysis.advanced_valuations import DCFCalculation, AssetBasedValuation, MarketMultiplesValuation

@dataclass
class ReportTemplate:
    """Professional report template configuration"""
    template_name: str
    title_style: Dict[str, Any]
    header_style: Dict[str, Any]
    body_style: Dict[str, Any]
    color_scheme: Dict[str, str]
    logo_path: Optional[str] = None
    
    # Compliance settings
    include_disclaimers: bool = True
    include_methodology: bool = True
    include_audit_trail: bool = True

@dataclass
class ComplianceInfo:
    """Compliance and regulatory information"""
    analyst_name: str
    analyst_credentials: str
    firm_name: str
    report_date: date
    
    # Regulatory
    investment_advisor_license: Optional[str] = None
    cfa_charter: bool = False
    
    # Disclaimers
    standard_disclaimers: List[str] = field(default_factory=list)
    risk_warnings: List[str] = field(default_factory=list)
    
    # Audit trail
    report_version: str = "1.0"
    approval_date: Optional[date] = None
    approved_by: Optional[str] = None

class ProfessionalReportGenerator:
    """
    Professional-grade report generator for institutional use
    """
    
    def __init__(self, compliance_info: ComplianceInfo):
        self.compliance_info = compliance_info
        self.logger = logging.getLogger(__name__)
        
        # Default templates
        self.templates = self._create_default_templates()
        
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available. PDF generation will be limited.")
    
    def generate_comprehensive_pdf_report(self, 
                                        research_report: ResearchReport,
                                        dcf_calculation: Optional[DCFCalculation] = None,
                                        asset_valuation: Optional[AssetBasedValuation] = None,
                                        multiples_valuation: Optional[MarketMultiplesValuation] = None,
                                        template_name: str = "institutional") -> bytes:
        """
        Generate comprehensive PDF research report
        
        Args:
            research_report: Main research report data
            dcf_calculation: DCF valuation results
            asset_valuation: Asset-based valuation results
            multiples_valuation: Market multiples valuation
            template_name: Template to use
            
        Returns:
            PDF content as bytes
        """
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation")
        
        self.logger.info(f"Generating comprehensive PDF report for {research_report.symbol}")
        
        try:
            buffer = io.BytesIO()
            template = self.templates[template_name]
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build report content
            story = []
            
            # Title page
            story.extend(self._create_title_page(research_report, template))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._create_executive_summary(research_report, template))
            story.append(PageBreak())
            
            # Company overview
            story.extend(self._create_company_overview(research_report, template))
            
            # Financial analysis
            story.extend(self._create_financial_analysis(research_report, template))
            
            # Valuation section
            story.extend(self._create_valuation_section(
                research_report, dcf_calculation, asset_valuation, multiples_valuation, template
            ))
            
            # Risk analysis
            story.extend(self._create_risk_analysis(research_report, template))
            
            # ESG and alternative data (if available)
            if hasattr(research_report, 'alternative_data') and research_report.alternative_data:
                story.extend(self._create_alternative_data_section(research_report, template))
            
            # Methodology
            if template.include_methodology:
                story.append(PageBreak())
                story.extend(self._create_methodology_section(template))
            
            # Disclaimers and compliance
            if template.include_disclaimers:
                story.append(PageBreak())
                story.extend(self._create_disclaimers_section(template))
            
            # Build PDF
            doc.build(story)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            self.logger.info(f"PDF report generated successfully for {research_report.symbol}")
            return pdf_content
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {e}")
            raise
    
    def generate_executive_summary_pdf(self, research_report: ResearchReport) -> bytes:
        """Generate condensed executive summary PDF"""
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation")
        
        try:
            buffer = io.BytesIO()
            template = self.templates["executive"]
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            # Header
            story.extend(self._create_executive_header(research_report, template))
            
            # Key metrics table
            story.extend(self._create_key_metrics_table(research_report, template))
            
            # Investment thesis
            story.extend(self._create_investment_thesis_section(research_report, template))
            
            # Recommendation and target price
            story.extend(self._create_recommendation_section(research_report, template))
            
            # Build PDF
            doc.build(story)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {e}")
            raise
    
    def _create_default_templates(self) -> Dict[str, ReportTemplate]:
        """Create default report templates"""
        
        templates = {}
        
        # Institutional template
        templates["institutional"] = ReportTemplate(
            template_name="institutional",
            title_style={
                'fontSize': 24,
                'textColor': HexColor('#1f4e79'),
                'spaceAfter': 30
            },
            header_style={
                'fontSize': 16,
                'textColor': HexColor('#2c5aa0'),
                'spaceAfter': 12
            },
            body_style={
                'fontSize': 11,
                'textColor': HexColor('#333333'),
                'spaceAfter': 12
            },
            color_scheme={
                'primary': '#1f4e79',
                'secondary': '#2c5aa0',
                'accent': '#5b9bd5',
                'text': '#333333',
                'light': '#f2f2f2'
            }
        )
        
        # Executive template
        templates["executive"] = ReportTemplate(
            template_name="executive",
            title_style={
                'fontSize': 20,
                'textColor': HexColor('#c5504b'),
                'spaceAfter': 20
            },
            header_style={
                'fontSize': 14,
                'textColor': HexColor('#d86613'),
                'spaceAfter': 10
            },
            body_style={
                'fontSize': 10,
                'textColor': HexColor('#333333'),
                'spaceAfter': 10
            },
            color_scheme={
                'primary': '#c5504b',
                'secondary': '#d86613',
                'accent': '#ffc000',
                'text': '#333333',
                'light': '#f2f2f2'
            }
        )
        
        return templates
    
    def _create_title_page(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create title page elements"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=template.title_style['fontSize'],
            textColor=template.title_style['textColor'],
            spaceAfter=template.title_style['spaceAfter'],
            alignment=1  # Center
        )
        
        story.append(Paragraph(f"INVESTMENT RESEARCH REPORT", title_style))
        story.append(Spacer(1, 20))
        
        # Company name and symbol
        company_style = ParagraphStyle(
            'CompanyTitle',
            parent=styles['Title'],
            fontSize=20,
            textColor=template.color_scheme['secondary'],
            spaceAfter=20,
            alignment=1
        )
        
        story.append(Paragraph(
            f"{research_report.company_name} ({research_report.symbol})", 
            company_style
        ))
        
        # Report details table
        report_data = [
            ['Report Date:', research_report.report_date.strftime('%B %d, %Y')],
            ['Analyst:', self.compliance_info.analyst_name],
            ['Credentials:', self.compliance_info.analyst_credentials],
            ['Firm:', self.compliance_info.firm_name],
            ['Recommendation:', research_report.recommendation],
            ['Target Price:', f"${research_report.target_price:.2f}" if research_report.target_price else "N/A"],
            ['Confidence Level:', f"{research_report.confidence_level:.0%}" if research_report.confidence_level else "N/A"]
        ]
        
        report_table = Table(report_data, colWidths=[2*inch, 3*inch])
        report_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), ['white', template.color_scheme['light']]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Spacer(1, 50))
        story.append(report_table)
        
        return story
    
    def _create_executive_summary(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create executive summary section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Section header
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=template.header_style['fontSize'],
            textColor=template.header_style['textColor'],
            spaceAfter=template.header_style['spaceAfter']
        )
        
        story.append(Paragraph("EXECUTIVE SUMMARY", header_style))
        
        # Investment thesis
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=template.body_style['fontSize'],
            textColor=template.body_style['textColor'],
            spaceAfter=template.body_style['spaceAfter'],
            alignment=0  # Left
        )
        
        story.append(Paragraph(f"<b>Investment Thesis:</b> {research_report.investment_thesis}", body_style))
        
        # Key metrics summary
        if research_report.epv_calculation:
            epv = research_report.epv_calculation
            
            summary_text = f"""
            <b>Key Valuation Metrics:</b><br/>
            • Earnings Power Value (EPV): ${epv.epv_per_share:.2f} per share<br/>
            • Current Price: ${epv.current_price:.2f} per share<br/>
            • Margin of Safety: {epv.margin_of_safety:.1f}%<br/>
            • Quality Score: {research_report.quality_score:.2f}/1.0<br/>
            • Risk Score: {research_report.risk_score:.2f}/1.0<br/>
            """
            
            story.append(Paragraph(summary_text, body_style))
        
        return story
    
    def _create_company_overview(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create company overview section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Section header
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=template.header_style['fontSize'],
            textColor=template.header_style['textColor'],
            spaceAfter=template.header_style['spaceAfter']
        )
        
        story.append(Paragraph("COMPANY OVERVIEW", header_style))
        
        # Company details
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=template.body_style['fontSize'],
            textColor=template.body_style['textColor'],
            spaceAfter=template.body_style['spaceAfter']
        )
        
        if research_report.profile:
            profile = research_report.profile
            
            overview_text = (
                "<b>Business Description:</b><br/>"
                f"{profile.description or 'Business description not available.'}<br/><br/>"
                "<b>Industry & Sector:</b><br/>"
                f"• Sector: {profile.sector or 'N/A'}<br/>"
                f"• Industry: {profile.industry or 'N/A'}<br/>"
                f"• Country: {profile.country or 'N/A'}<br/>"
                f"• Exchange: {profile.exchange or 'N/A'}<br/><br/>"
                "<b>Key Metrics:</b><br/>"
                f"• Market Cap: {f'${profile.market_cap:,.0f}' if profile.market_cap else 'N/A'}<br/>"
                f"• Enterprise Value: {f'${profile.enterprise_value:,.0f}' if profile.enterprise_value else 'N/A'}<br/>"
                f"• Employees: {f'{profile.employees:,}' if profile.employees else 'N/A'}<br/>"
            )
            
            story.append(Paragraph(overview_text, body_style))
        
        return story
    
    def _create_financial_analysis(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create financial analysis section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Section header
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=template.header_style['fontSize'],
            textColor=template.header_style['textColor'],
            spaceAfter=template.header_style['spaceAfter']
        )
        
        story.append(Paragraph("FINANCIAL ANALYSIS", header_style))
        
        # Historical performance table
        if research_report.income_statements and len(research_report.income_statements) > 0:
            # Create financial summary table
            financial_data = []
            headers = ['Metric'] + [str(stmt.fiscal_year) for stmt in research_report.income_statements[-5:]]
            financial_data.append(headers)
            
            # Revenue row
            revenue_row = ['Revenue ($M)']
            for stmt in research_report.income_statements[-5:]:
                revenue_row.append(f"${stmt.revenue/1e6:.1f}" if stmt.revenue else "N/A")
            financial_data.append(revenue_row)
            
            # Net income row
            income_row = ['Net Income ($M)']
            for stmt in research_report.income_statements[-5:]:
                income_row.append(f"${stmt.net_income/1e6:.1f}" if stmt.net_income else "N/A")
            financial_data.append(income_row)
            
            financial_table = Table(financial_data, colWidths=[1.5*inch] + [1*inch]*len(headers[1:]))
            financial_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), ['white', template.color_scheme['light']]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(financial_table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_valuation_section(self, 
                                research_report: ResearchReport,
                                dcf_calculation: Optional[DCFCalculation],
                                asset_valuation: Optional[AssetBasedValuation],
                                multiples_valuation: Optional[MarketMultiplesValuation],
                                template: ReportTemplate) -> List:
        """Create comprehensive valuation section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Section header
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=template.header_style['fontSize'],
            textColor=template.header_style['textColor'],
            spaceAfter=template.header_style['spaceAfter']
        )
        
        story.append(Paragraph("VALUATION ANALYSIS", header_style))
        
        # Valuation summary table
        valuation_data = [['Method', 'Value per Share', 'Weight', 'Weighted Value']]
        
        total_weighted_value = 0
        total_weight = 0
        
        # EPV
        if research_report.epv_calculation:
            epv_weight = 0.4
            epv_value = research_report.epv_calculation.epv_per_share
            weighted_epv = epv_value * epv_weight
            valuation_data.append(['Earnings Power Value', f'${epv_value:.2f}', f'{epv_weight:.0%}', f'${weighted_epv:.2f}'])
            total_weighted_value += weighted_epv
            total_weight += epv_weight
        
        # DCF
        if dcf_calculation:
            dcf_weight = 0.3
            dcf_value = dcf_calculation.dcf_per_share
            weighted_dcf = dcf_value * dcf_weight
            valuation_data.append(['Discounted Cash Flow', f'${dcf_value:.2f}', f'{dcf_weight:.0%}', f'${weighted_dcf:.2f}'])
            total_weighted_value += weighted_dcf
            total_weight += dcf_weight
        
        # Asset-based
        if asset_valuation:
            asset_weight = 0.15
            asset_value = asset_valuation.adjusted_book_value_per_share
            weighted_asset = asset_value * asset_weight
            valuation_data.append(['Asset-Based', f'${asset_value:.2f}', f'{asset_weight:.0%}', f'${weighted_asset:.2f}'])
            total_weighted_value += weighted_asset
            total_weight += asset_weight
        
        # Market multiples
        if multiples_valuation:
            multiples_weight = 0.15
            multiples_value = multiples_valuation.multiples_average_value
            weighted_multiples = multiples_value * multiples_weight
            valuation_data.append(['Market Multiples', f'${multiples_value:.2f}', f'{multiples_weight:.0%}', f'${weighted_multiples:.2f}'])
            total_weighted_value += weighted_multiples
            total_weight += multiples_weight
        
        # Total
        if total_weight > 0:
            valuation_data.append(['', '', '', ''])  # Separator
            valuation_data.append(['TOTAL WEIGHTED VALUE', '', f'{total_weight:.0%}', f'${total_weighted_value:.2f}'])
        
        valuation_table = Table(valuation_data, colWidths=[2*inch, 1.2*inch, 0.8*inch, 1.2*inch])
        valuation_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), ['white', template.color_scheme['light']]),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('LINEBELOW', (0, -2), (-1, -2), 2, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor(template.color_scheme['accent']))
        ]))
        
        story.append(valuation_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_risk_analysis(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create risk analysis section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Section header
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=template.header_style['fontSize'],
            textColor=template.header_style['textColor'],
            spaceAfter=template.header_style['spaceAfter']
        )
        
        story.append(Paragraph("RISK ANALYSIS", header_style))
        
        # Risk factors
        if research_report.risk_factors:
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=template.body_style['fontSize'],
                textColor=template.body_style['textColor'],
                spaceAfter=template.body_style['spaceAfter']
            )
            
            risk_text = "<b>Key Risk Factors:</b><br/>"
            for i, risk in enumerate(research_report.risk_factors, 1):
                risk_text += f"{i}. {risk}<br/>"
            
            story.append(Paragraph(risk_text, body_style))
        
        return story
    
    def _create_methodology_section(self, template: ReportTemplate) -> List:
        """Create methodology section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Section header
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=template.header_style['fontSize'],
            textColor=template.header_style['textColor'],
            spaceAfter=template.header_style['spaceAfter']
        )
        
        story.append(Paragraph("METHODOLOGY", header_style))
        
        # Methodology content
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=template.body_style['fontSize'],
            textColor=template.body_style['textColor'],
            spaceAfter=template.body_style['spaceAfter']
        )
        
        methodology_text = """
        <b>Earnings Power Value (EPV) Methodology:</b><br/>
        The EPV methodology, developed by Bruce Greenwald, estimates the value of a company's 
        current earnings power in perpetuity without assuming any growth. This conservative 
        approach focuses on sustainable, normalized earnings divided by an appropriate cost of capital.<br/><br/>
        
        <b>Key Steps:</b><br/>
        1. Calculate normalized earnings over a full economic cycle (typically 7-10 years)<br/>
        2. Adjust for one-time items and extraordinary events<br/>
        3. Estimate appropriate cost of capital based on company risk profile<br/>
        4. Calculate EPV = Normalized Earnings / Cost of Capital<br/>
        5. Assess quality factors that may justify premium or discount to EPV<br/><br/>
        
        <b>Quality Assessment:</b><br/>
        Our quality score incorporates earnings stability, return on capital, balance sheet strength, 
        liquidity position, and revenue growth consistency. Higher quality companies may trade at 
        premiums to their calculated EPV.<br/><br/>
        
        <b>Risk Assessment:</b><br/>
        Risk factors are evaluated across earnings volatility, leverage, liquidity, competitive position, 
        and market valuation. These factors inform our overall investment recommendation.
        """
        
        story.append(Paragraph(methodology_text, body_style))
        
        return story
    
    def _create_disclaimers_section(self, template: ReportTemplate) -> List:
        """Create disclaimers and compliance section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Section header
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=template.header_style['fontSize'],
            textColor=template.header_style['textColor'],
            spaceAfter=template.header_style['spaceAfter']
        )
        
        story.append(Paragraph("IMPORTANT DISCLAIMERS", header_style))
        
        # Disclaimers content
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#666666'),
            spaceAfter=8
        )
        
        standard_disclaimers = [
            "This report is for informational purposes only and does not constitute investment advice.",
            "Past performance is not indicative of future results.",
            "All investments carry risk of loss, including potential loss of principal.",
            "The analyst may hold positions in the securities discussed in this report.",
            "This analysis is based on publicly available information and may contain errors or omissions.",
            "Investors should conduct their own due diligence before making investment decisions.",
            "Market conditions and company fundamentals may change rapidly.",
            "The EPV methodology is one of many valuation approaches and should not be used in isolation."
        ]
        
        for disclaimer in standard_disclaimers:
            story.append(Paragraph(f"• {disclaimer}", disclaimer_style))
        
        # Compliance information
        story.append(Spacer(1, 20))
        
        compliance_text = f"""
        <b>Analyst Information:</b><br/>
        Analyst: {self.compliance_info.analyst_name}<br/>
        Credentials: {self.compliance_info.analyst_credentials}<br/>
        Firm: {self.compliance_info.firm_name}<br/>
        Report Version: {self.compliance_info.report_version}<br/>
        Report Date: {self.compliance_info.report_date.strftime('%B %d, %Y')}
        """
        
        story.append(Paragraph(compliance_text, disclaimer_style))
        
        return story
    
    def _create_executive_header(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create executive summary header"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'ExecTitle',
            parent=styles['Title'],
            fontSize=template.title_style['fontSize'],
            textColor=template.title_style['textColor'],
            spaceAfter=10,
            alignment=1
        )
        
        story.append(Paragraph(f"{research_report.company_name} ({research_report.symbol})", title_style))
        story.append(Paragraph("EXECUTIVE SUMMARY", title_style))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_key_metrics_table(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create key metrics summary table"""
        
        story = []
        
        if research_report.epv_calculation:
            epv = research_report.epv_calculation
            
            metrics_data = [
                ['Current Price', f'${epv.current_price:.2f}' if epv.current_price else 'N/A'],
                ['EPV per Share', f'${epv.epv_per_share:.2f}'],
                ['Target Price', f'${research_report.target_price:.2f}' if research_report.target_price else 'N/A'],
                ['Margin of Safety', f'{epv.margin_of_safety:.1f}%' if epv.margin_of_safety is not None else 'N/A'],
                ['Quality Score', f'{research_report.quality_score:.2f}/1.0'],
                ['Recommendation', research_report.recommendation or 'N/A']
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), ['white', template.color_scheme['light']]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_investment_thesis_section(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create investment thesis section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        header_style = ParagraphStyle(
            'SubHeader',
            parent=styles['Heading2'],
            fontSize=template.header_style['fontSize']-2,
            textColor=template.header_style['textColor'],
            spaceAfter=10
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=template.body_style['fontSize'],
            textColor=template.body_style['textColor'],
            spaceAfter=template.body_style['spaceAfter']
        )
        
        story.append(Paragraph("Investment Thesis", header_style))
        story.append(Paragraph(research_report.investment_thesis or "Investment thesis not available.", body_style))
        
        return story
    
    def _create_recommendation_section(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create recommendation section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        header_style = ParagraphStyle(
            'SubHeader',
            parent=styles['Heading2'],
            fontSize=template.header_style['fontSize']-2,
            textColor=template.header_style['textColor'],
            spaceAfter=10
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=template.body_style['fontSize'],
            textColor=template.body_style['textColor'],
            spaceAfter=template.body_style['spaceAfter']
        )
        
        story.append(Paragraph("Recommendation", header_style))
        
        target_price_str = (
            f"${research_report.target_price:.2f}" if research_report.target_price else "N/A"
        )
        confidence_str = (
            f"{research_report.confidence_level:.0%}" if research_report.confidence_level else "N/A"
        )

        recommendation_text = (
            f"<b>Recommendation:</b> {research_report.recommendation or 'N/A'}<br/>"
            f"<b>Target Price:</b> {target_price_str}<br/>"
            f"<b>Confidence Level:</b> {confidence_str}"
        )

        story.append(Paragraph(recommendation_text, body_style))
        
        return story
    
    def _create_alternative_data_section(self, research_report: ResearchReport, template: ReportTemplate) -> List:
        """Create alternative data analysis section"""
        
        styles = getSampleStyleSheet()
        story = []
        
        # This would integrate with the alternative data module
        # For now, placeholder
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading1'],
            fontSize=template.header_style['fontSize'],
            textColor=template.header_style['textColor'],
            spaceAfter=template.header_style['spaceAfter']
        )
        
        story.append(Paragraph("ALTERNATIVE DATA ANALYSIS", header_style))
        
        # ESG, sentiment, insider trading analysis would go here
        
        return story
