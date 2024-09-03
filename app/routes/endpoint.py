from flask import Blueprint, request, render_template, redirect, url_for, render_template_string
from lxml import etree

endpoint_bp = Blueprint("endpoint", __name__)
@endpoint_bp.route("/process_xml", methods=['POST'])
def process_xml():
    xml_data = request.form.get('xml_data')

    if xml_data:
        try:
            parser = etree.XMLParser()
            root = etree.fromstring(xml_data, parser=parser)

            # Extract data from XML
            title = root.find('title').text
            description = root.find('description').text

            return f"Title: {title}, Description: {description}"
        except Exception as e:
            return f"Error processing XML: {str(e)}"
        
    return "No XML data provided"


