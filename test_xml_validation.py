import unittest
from lxml import etree
import main  # Import your main script

class TestXMLValidation(unittest.TestCase):

    # Path to the XSD and XML files
    XSD_PATH = "xsd/cards.xsd"
    XML_PATH = "ygopro_cockatrice.xml"

    def setUp(self):
        """Set up method to run the main script before the test."""
        # Fetch cards and create XML
        cards = main.fetch_all_cards()
        if cards:
            cockatrice_tree = main.create_cockatrice_xml(cards)
            main.save_xml(cockatrice_tree, self.XML_PATH)  # Save the XML to the predefined path

    def test_xml_validates_against_xsd(self):
        """Test to validate that the generated XML matches the provided XSD schema."""
        # Parse the XSD schema
        with open(self.XSD_PATH, 'r', encoding="utf-8") as f:
            schema_root = etree.XML(f.read())
        schema = etree.XMLSchema(schema_root)

        # Parse the generated XML
        with open(self.XML_PATH, 'r', encoding="utf-8") as f:
            xml_content = f.read()
        xml_doc = etree.fromstring(xml_content)

        # Validate the XML against the XSD schema
        is_valid = schema.validate(xml_doc)

        # If the XML is invalid, print all errors from the error log in a more detailed format
        if not is_valid:
            print("\nValidation failed. Detailed error log:")
            for error in schema.error_log:
                print(f"Error: {error.message}")
                print(f"Line: {error.line}, Column: {error.column}")
                print(f"Domain: {error.domain_name}, Type: {error.type_name}")
                print("-" * 40)

        # Assert that the XML is valid
        self.assertTrue(is_valid, "The XML file is not valid against the provided XSD.")

if __name__ == '__main__':
    unittest.main()
