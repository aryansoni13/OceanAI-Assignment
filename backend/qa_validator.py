"""
QA Validator - Provides intelligent suggestions for missing elements and validation rules
"""
from bs4 import BeautifulSoup
from typing import List, Dict
import re


class QAValidator:
    """Validates HTML and documentation for common QA issues and provides suggestions"""
    
    def __init__(self, html_content: str, docs_content: str = ""):
        self.html_content = html_content
        self.docs_content = docs_content
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.suggestions = []
    
    def validate_all(self) -> List[Dict[str, str]]:
        """Run all validation checks and return suggestions"""
        self.suggestions = []
        
        self._check_form_validation()
        self._check_error_messages()
        self._check_discount_code_elements()
        self._check_payment_elements()
        self._check_shipping_elements()
        self._check_documentation_coverage()
        
        return self.suggestions
    
    def _add_suggestion(self, category: str, issue: str, suggestion: str, severity: str = "warning"):
        """Add a suggestion to the list"""
        self.suggestions.append({
            "category": category,
            "issue": issue,
            "suggestion": suggestion,
            "severity": severity  # info, warning, error
        })
    
    def _check_form_validation(self):
        """Check if form fields have proper validation"""
        # Check for email field
        email_field = self.soup.find('input', {'type': 'email'}) or self.soup.find('input', {'id': re.compile('email', re.I)})
        if email_field:
            # Check if validation rules are documented
            if 'email' not in self.docs_content.lower() and 'validation' not in self.docs_content.lower():
                self._add_suggestion(
                    "Form Validation",
                    "Email field requires validation, but no validation rule found in documents.",
                    "Add email validation rules to UI/UX documentation (e.g., format requirements, error messages).",
                    "warning"
                )
        
        # Check for required fields
        required_fields = self.soup.find_all('input', {'required': True})
        if not required_fields:
            # Check if there are inputs that should be required
            name_field = self.soup.find('input', {'id': re.compile('name|fullname', re.I)})
            if name_field and not name_field.get('required'):
                self._add_suggestion(
                    "Form Validation",
                    "Name field is not marked as required in HTML.",
                    "Add 'required' attribute to name input field for better validation.",
                    "info"
                )
    
    def _check_error_messages(self):
        """Check if error message elements exist"""
        error_elements = self.soup.find_all(class_=re.compile('error', re.I))
        
        # Check for discount code error
        discount_input = self.soup.find('input', {'id': re.compile('discount|coupon', re.I)})
        if discount_input:
            # Look for associated error message element
            discount_error = self.soup.find(id=re.compile('discount.*error|discount.*msg', re.I))
            if not discount_error:
                self._add_suggestion(
                    "Error Handling",
                    "The HTML does not contain an element for discount error message.",
                    "Add an error message element (e.g., <span id='discount-error' class='error'></span>) near the discount input field.",
                    "warning"
                )
        
        # Check for form field errors
        form_inputs = self.soup.find_all('input', {'type': ['text', 'email']})
        for input_field in form_inputs:
            field_id = input_field.get('id', '')
            if field_id:
                error_id = f"error-{field_id}"
                if not self.soup.find(id=error_id):
                    self._add_suggestion(
                        "Error Handling",
                        f"Missing error message element for '{field_id}' field.",
                        f"Add <span id='{error_id}' class='error'></span> below the {field_id} input for validation feedback.",
                        "info"
                    )
    
    def _check_discount_code_elements(self):
        """Check discount code functionality elements"""
        discount_input = self.soup.find('input', {'id': re.compile('discount|coupon', re.I)})
        
        if discount_input:
            # Check for apply button
            apply_btn = self.soup.find('button', string=re.compile('apply', re.I))
            if not apply_btn:
                self._add_suggestion(
                    "Discount Code",
                    "Discount input found but no 'Apply' button detected.",
                    "Add a button with text 'Apply' to trigger discount code validation.",
                    "error"
                )
            
            # Check if discount codes are documented
            if 'discount' not in self.docs_content.lower() and 'coupon' not in self.docs_content.lower():
                self._add_suggestion(
                    "Documentation",
                    "Discount code feature exists in HTML but not documented.",
                    "Add discount code specifications to product_specs.md (e.g., valid codes, discount percentages).",
                    "warning"
                )
    
    def _check_payment_elements(self):
        """Check payment method elements"""
        payment_radios = self.soup.find_all('input', {'type': 'radio', 'name': re.compile('payment', re.I)})
        
        if payment_radios:
            payment_methods = [radio.get('value', '') for radio in payment_radios]
            
            # Check if payment methods are documented
            if 'payment' not in self.docs_content.lower():
                self._add_suggestion(
                    "Documentation",
                    "Payment methods found in HTML but not documented.",
                    f"Add payment method specifications to documentation. Found methods: {', '.join(payment_methods)}",
                    "warning"
                )
    
    def _check_shipping_elements(self):
        """Check shipping method elements"""
        shipping_radios = self.soup.find_all('input', {'type': 'radio', 'name': re.compile('shipping', re.I)})
        
        if shipping_radios:
            # Check if shipping rules are documented
            if 'shipping' not in self.docs_content.lower():
                self._add_suggestion(
                    "Documentation",
                    "Shipping options found in HTML but not documented.",
                    "Add shipping rules and costs to product_specs.md.",
                    "warning"
                )
    
    def _check_documentation_coverage(self):
        """Check if key features are documented"""
        # Check for buttons and their purposes
        buttons = self.soup.find_all('button')
        for btn in buttons:
            btn_text = btn.get_text(strip=True).lower()
            if btn_text and btn_text not in self.docs_content.lower():
                if btn_text not in ['apply', 'submit', 'pay']:  # Common buttons
                    self._add_suggestion(
                        "Documentation",
                        f"Button '{btn.get_text(strip=True)}' found but not documented.",
                        f"Document the purpose and behavior of the '{btn.get_text(strip=True)}' button.",
                        "info"
                    )
    
    def format_suggestions_markdown(self) -> str:
        """Format suggestions as markdown for display"""
        if not self.suggestions:
            return "✅ **No issues found!** Your HTML and documentation are well-structured."
        
        md = "## 🔍 Quick Fix Suggestions\n\n"
        
        # Group by severity
        errors = [s for s in self.suggestions if s['severity'] == 'error']
        warnings = [s for s in self.suggestions if s['severity'] == 'warning']
        info = [s for s in self.suggestions if s['severity'] == 'info']
        
        if errors:
            md += "### 🚨 Critical Issues\n"
            for s in errors:
                md += f"**{s['category']}**: {s['issue']}\n"
                md += f"💡 *Fix*: {s['suggestion']}\n\n"
        
        if warnings:
            md += "### ⚠️ Warnings\n"
            for s in warnings:
                md += f"**{s['category']}**: {s['issue']}\n"
                md += f"💡 *Fix*: {s['suggestion']}\n\n"
        
        if info:
            md += "### ℹ️ Recommendations\n"
            for s in info:
                md += f"**{s['category']}**: {s['issue']}\n"
                md += f"💡 *Fix*: {s['suggestion']}\n\n"
        
        return md


def validate_project(html_content: str, docs_content: str = "") -> str:
    """Main function to validate project and return suggestions"""
    validator = QAValidator(html_content, docs_content)
    validator.validate_all()
    return validator.format_suggestions_markdown()
