import frappe
import zeep
import requests
import xml.etree.ElementTree as ET
from frappe.utils import getdate
import json
import pymssql
from frappe.model.workflow import get_workflow_safe_globals
from erp_space import erpspace

def define_header_xml():
    client = zeep.Client('http://dc7-web.marsavco.com:8124/soap-wsdl/syracuse/collaboration/syracuse/CAdxWebServiceXmlCC?wsdl')
    client.transport.session.auth = requests.auth.HTTPBasicAuth('kossivi', 'A2ggrb012345-')
    # Set up context
    CContext = {
        'codeLang': 'ENG',
        'poolAlias': 'LIVE',
        'requestConfig': 'adxwss.trace.on=on&adxwss.trace.size=16384&adonix.trace.on=on&adonix.trace.level=3&adonix.trace.size=8',
    }

    return CContext, client

def create_salary_xml_doc(pay_doc):
    root_xml = ET.Element("PARAM")
    
    posting_date = getdate()

    emp_name = (pay_doc.employee + " - " + pay_doc.employee_name) if len(pay_doc.employee + " - " + pay_doc.employee_name) <= 30 else (pay_doc.employee + " - " + pay_doc.employee_name)[:30]

    ET.SubElement(root_xml, 'FLD', {'NAME': 'FCY'}).text  = "M0001" if pay_doc.branch == "Kinshasa" else "M0002"
    ET.SubElement(root_xml, 'FLD', {'NAME': 'ACC'}).text  = "42110100"
    ET.SubElement(root_xml, 'FLD', {'NAME': 'BPAINV'}).text  = "1"
    ET.SubElement(root_xml, 'FLD', {'NAME': 'ACCDAT'}).text  = posting_date.strftime("%Y%m%d")
    ET.SubElement(root_xml, 'FLD', {'NAME': 'REF'}).text  = emp_name
    ET.SubElement(root_xml, 'FLD', {'NAME': 'DES'}).text  = pay_doc.pay_period + " | " + pay_doc.type
    ET.SubElement(root_xml, 'FLD', {'NAME': 'BAN'}).text  = pay_doc.cashier
    ET.SubElement(root_xml, 'FLD', {'NAME': 'CUR'}).text  = pay_doc.currency
    ET.SubElement(root_xml, 'FLD', {'NAME': 'AMTCUR'}).text  = str(pay_doc.amount)
    ET.SubElement(root_xml, 'FLD', {'NAME': 'CHQNUM'}).text  = pay_doc.name

    lines_xml = ET.SubElement(root_xml, 'TAB', {'DIM': '200', 'ID': 'PAY1_4', 'SIZE': "1"})
    line = ET.SubElement(lines_xml, 'LIN', {'NUM': "1"})
    code = ET.SubElement(line, 'FLD', {'NAME': 'DENCOD', 'TYPE': 'Char'})
    code.text = "ZAPAY"
    amount = ET.SubElement(line, 'FLD', {'NAME': 'AMTLIN', 'TYPE': 'Decimal'})
    amount.text = str(pay_doc.amount)
    cost_center = ET.SubElement(line, 'FLD', {'NAME': 'CCE1', 'TYPE': 'Char'})
    cost_center.text = pay_doc.cost_center.split("-")[0].strip()
    employee = ET.SubElement(line, 'FLD', {'NAME': 'CCE5', 'TYPE': 'Char'})
    employee.text = pay_doc.employee
        

    return root_xml


def create_salary_withdrawal(name,public_name='ZPAY'):
    pay_doc = frappe.get_doc("BPM Salary Withdrawals", name)
    xmlInput = create_salary_xml_doc(pay_doc)
    CContext, client = define_header_xml()

    #frappe.msgprint(str(len(xmlInput)))

    with client.settings(strict=False):
        data = client.service.save(callContext=CContext, publicName=public_name, objectXml=ET.tostring(xmlInput))

    result = data.resultXml
    xmlInput2 = ET.fromstring(result)
    code = xmlInput2.findall(".//GRP[@ID='PAY0_1']/FLD[@NAME='NUM']")[0].text
    return code


def share_doc(doc):
    if not doc.workflow_state in ["Draft","Rejected"]:
        users = frappe.db.sql(
            """
            SELECT DISTINCT h.parent
            FROM `tabWorkflow Transition` t INNER JOIN tabRole r ON r.name = t.allowed INNER JOIN `tabHas Role` h ON h.role = r.name
            WHERE t.parent = %s AND t.state = %s AND h.parenttype = 'User'
            """, (doc.doctype, doc.workflow_state), as_dict =1
        )

        #if not frappe.has_permission(doc=doc, ptype="submit", user=users[0].parent):
        for user in users:
            frappe.share.add_docshare(
                doc.doctype, doc.name, user.parent, submit=1, flags={"ignore_share_permission": True}
            )
            frappe.db.commit()

def send_email(email, doctype, docname):
    frappe.sendmail(
        recipients=email,
        subject = f"{doctype} [{docname}]",
        message = f"""
        <p>The document <b>{docname}</b> requires your appoval.</p>
        <p><a href="{frappe.utils.get_url_to_form(doctype, docname)}">View Document</a></p>
        """
    )

@frappe.whitelist()
def share_doc_2(doc):
    if doc.workflow_state not in ["Draft", "Rejected"]:
        # Fetch custom role formula
        formulas = frappe.db.sql(
            """
            SELECT t.custom_role_formula, t.custom_role
            FROM `tabWorkflow Transition` t 
            WHERE t.parent = %s AND t.state = %s AND t.action = 'Approve'
            """,
            (doc.doctype, doc.workflow_state),
            as_dict=True
        )

        # Evaluate the formula with restricted globals
        role = ""
        if formulas[0].get("custom_role"):
            role = formulas[0].get("custom_role")
        else:
            role = frappe.safe_eval(
                formulas[0].get("custom_role_formula"),
                get_workflow_safe_globals(), dict(doc=doc.as_dict())
            )

        # Fetch emails of users with the specified role
        emails = frappe.db.sql(
            """
            SELECT u.name AS email
            FROM `tabUser` u 
            INNER JOIN `tabHas Role` r ON r.parent = u.name
            WHERE r.role = %s
            """,
            (role,),
            as_dict=True
        )

        # Share the document with users
        for email_entry in emails:
            email = email_entry.get("email")
            frappe.share.add_docshare(
                doc.doctype, doc.name, email, submit=1, flags={"ignore_share_permission": True}
            )

            send_email(email, doc.doctype, doc.name)
            
# Register the function in erpspace
erpspace.register_function("share_doc", share_doc_2)


