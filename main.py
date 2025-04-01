import uuid

import requests
import xml.etree.ElementTree as ET
import html
import xml.dom.minidom as minidom

# YGOPRODeck API URL
API_URL  = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
SETS_URL = "https://db.ygoprodeck.com/api/v7/cardsets.php"

NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")


# Function to fetch all cards from YGOPRODeck API
def fetch_all_cards():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Failed to fetch cards: {response.status_code}")
        return []

def fetch_all_sets():
    response = requests.get(SETS_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch cards: {response.status_code}")
        return []

# Function to escape and decode card description
def escape_description(description):
    decoded_desc = html.unescape(description)
    return decoded_desc.replace("&#x27;", "'").replace("\n", " ")


# Function to add card properties to the XML
def add_card_properties(card_element, card):
    ET.SubElement(card_element, "name").text = card.get('name', '')

    description = card.get('desc', '')
    ET.SubElement(card_element, "text").text = escape_description(description)

    prop = ET.SubElement(card_element, "prop")

    card_archetype = card.get('archetype', '')
    if card_archetype != '':
        ET.SubElement(prop, "Archetype").text = card_archetype

    ET.SubElement(prop, "manacost").text = str(card.get('level', 'None'))
    ET.SubElement(prop, "colors").text = card.get('attribute', 'NORMAL')
    ET.SubElement(prop, "Konami_ID").text = str(card.get('id', ''))

    card_type = card.get('type', '')
    if "Monster" in card_type:
        ET.SubElement(prop, "maintype").text = 'Monster'
        ET.SubElement(prop, "Complete_Card_type").text = card_type
    else:
        ET.SubElement(prop, "maintype").text = card_type

    # Add "pt" only if the card is a monster
    if 'monster' in card.get('type', '').lower():
        ET.SubElement(prop, "pt").text = f"{str(card.get('atk', '?'))}/{str(card.get('def', '?'))}"  # Ensure atk/def are strings

    ET.SubElement(prop, "type").text = card.get('race', '')

def generate_deterministic_uuid(set_code):
    return str(uuid.uuid5(NAMESPACE, str(set_code)))

# Function to create XML structure for Cockatrice
def create_cockatrice_xml(cards, sets):
    root = ET.Element("cockatrice_carddatabase", version="4", attrib={
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemaLocation': "https://raw.githubusercontent.com/Cockatrice/Cockatrice/master/doc/carddatabase_v4/cards.xsd"
    })

    sets_element = ET.SubElement(root, "sets")

    set_element = ET.SubElement(sets_element, "set")
    ET.SubElement(set_element, "name").text = "YGO"
    ET.SubElement(set_element, "longname").text = "Yu-Gi-Oh"
    ET.SubElement(set_element, "settype").text = "Yu-Gi-Oh"

    cards_element = ET.SubElement(root, "cards")

    for card in cards:
        card_element = ET.SubElement(cards_element, "card")
        add_card_properties(card_element, card)

        card_sets = card.get('card_images', [])

        # Set information for card sets
        for card_set in card_sets:
            set_element = ET.SubElement(card_element, "set", picURL=card_set["image_url"], uuid=generate_deterministic_uuid(card_set["id"]))
            set_element.text = "YGO"

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
    cards = fetch_all_cards()
    sets  = fetch_all_sets()

    if cards:
        cockatrice_tree = create_cockatrice_xml(cards, sets)

        save_xml(cockatrice_tree, "ygopro_cockatrice.xml")
