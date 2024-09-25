import requests
import xml.etree.ElementTree as ET
import html  # Import the html module for escaping
import xml.dom.minidom as minidom  # For pretty-printing XML

# YGOPRODeck API URL
API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"


# Function to fetch all cards from YGOPRODeck API
def fetch_all_cards():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Failed to fetch cards: {response.status_code}")
        return []


# Function to escape and decode card description
def escape_description(description):
    # Decode HTML entities
    decoded_desc = html.unescape(description)
    # Replace double-encoded apostrophes if necessary
    return decoded_desc.replace("&#x27;", "'").replace("\n", " ")


# Function to add card properties to the XML
def add_card_properties(card_element, card):
    # Add 'name' element
    ET.SubElement(card_element, "name").text = card.get('name', '')

    # Add 'text' element next, as per XSD
    description = card.get('desc', '')
    ET.SubElement(card_element, "text").text = escape_description(description)

    # Now add 'prop' element
    prop = ET.SubElement(card_element, "prop")

    ET.SubElement(prop, "Archetype").text = card.get('archetype', '')
    ET.SubElement(prop, "cmc").text = str(card.get('level', '0'))  # Convert to string
    ET.SubElement(prop, "colors").text = card.get('attribute', 'NORMAL')
    ET.SubElement(prop, "Konami_ID").text = str(card.get('id', ''))  # Ensure ID is a string
    ET.SubElement(prop, "maintype").text = card.get('type', '')

    # Add "pt" only if the card is a monster
    if 'monster' in card.get('type', '').lower():  # Check if card type includes "monster"
        ET.SubElement(prop, "pt").text = f"{str(card.get('atk', '?'))}/{str(card.get('def', '?'))}"  # Ensure atk/def are strings

    ET.SubElement(prop, "type").text = card.get('race', '')


# Function to create XML structure for Cockatrice
def create_cockatrice_xml(cards):
    root = ET.Element("cockatrice_carddatabase", version="4", attrib={
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemaLocation': "https://raw.githubusercontent.com/Cockatrice/Cockatrice/master/doc/carddatabase_v4/cards.xsd"
    })

    sets_element = ET.SubElement(root, "sets")
    cards_element = ET.SubElement(root, "cards")

    for card in cards:
        card_element = ET.SubElement(cards_element, "card")
        add_card_properties(card_element, card)  # Add properties to the card element

        card_sets = card.get('card_sets', [])
        if not card_sets:
            # Add a default set if no sets are provided
            set_element = ET.SubElement(card_element, "set", rarity="Unknown")
            set_element.text = "Unknown"
            ET.SubElement(card_element, "set", picURL=card['card_images'][0]['image_url']).text = f"°{card['id']}.1"

        # Set information for card sets
        for card_set in card_sets:
            set_element = ET.SubElement(card_element, "set", rarity=card_set.get('set_rarity', ''))
            set_element.text = card_set.get('set_code', '')
            ET.SubElement(card_element, "set", picURL=card['card_images'][0]['image_url']).text = f"°{card['id']}.1"

    return ET.ElementTree(root)


# Function to pretty-print XML
def pretty_print_xml(tree):
    rough_string = ET.tostring(tree.getroot(), 'utf-8')
    parsed = minidom.parseString(rough_string)
    return parsed.toprettyxml(indent="  ")


# Save the XML to a file with pretty print
def save_xml(tree, filename):
    pretty_xml = pretty_print_xml(tree)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print(f"Pretty-printed XML saved to {filename}")


if __name__ == "__main__":
    # Fetch all cards from YGOPRODeck
    cards = fetch_all_cards()

    if cards:
        # Create XML structure
        cockatrice_tree = create_cockatrice_xml(cards)

        # Save pretty-printed XML to a file
        save_xml(cockatrice_tree, "ygopro_cockatrice.xml")
