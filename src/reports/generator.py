"""
PDF report generator
"""
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


def build_report(data: dict, template_name: str, output_path: str) -> str:
    """Build a PDF report from a template and data."""
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    html_out = template.render(data)

    pdf_path = os.path.join(output_path, f"{data['symbol']}_report.pdf")
    HTML(string=html_out).write_pdf(pdf_path)

    return pdf_path
