import lxml
import argparse
import sys

from templates.demo import TEST_TEMPLATES
from lxml import etree



def main():
    # input_option_str = 'input'

    # parser = argparse.ArgumentParser(
    #     description='The path of input xml files'
    # )
     
    # for item in TEST_TEMPLATES['fields']:
    #     print("This is the item", item)

    inputfile = sys.argv[1]

    context = etree.iterparse(inputfile, events=('end',), tag=TEST_TEMPLATES['name'])
    for event, elem in context:
        print("This is the event and elem", event, elem.tag)
        for key in TEST_TEMPLATES["fields"]:
            # sub_element = etree.SubElement(elem, key)
            sub_element = elem.find(key)
            print("This is the getted value from the tag", sub_element, sub_element.text)
        
        # # After processing each subelement in the element, clear and delete the elem found
        # elem.clear()
        # while elem.getprevious() is not None:
        #     del elem.getparent()[0]

    return

if __name__ == '__main__':
    main()
