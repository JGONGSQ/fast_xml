import lxml
import argparse
import sys
import os
import json
import csv

from templates.demo import TEST_TEMPLATES, LIST_OF_TEMPLATES
from lxml import etree

# def fast_iter(context, func):
#     for event, elem in context:
#         func(elem)
#         elem.clear()
#         while elem.getprevious() is not None:
#             del elem.getparent()[0]

#     del context


def get_list_of_processing_files(input_dir):
    list_of_datafiles = list()
    for root, dirname, filenames in os.walk(input_dir):
        for filename in filenames:
            list_of_datafiles.append("{root}/{filename}".format(root=root, filename=filename))
    return list_of_datafiles


def get_data_dict(inputfile, target_tag):
    data_dict = dict()
    list_of_content = list()

    context = etree.iterparse(inputfile, events=('end',), tag=target_tag['name'])
    for event, elem in context:
        print("This is the event and elem", event, elem.tag)
        content_dict = dict()
        
        # read each key for the tag
        for key in target_tag["fields"]:
            sub_element = elem.find(key)
            # print("This is the getted value from the tag", sub_element, sub_element.text)
            content_dict.update({key: sub_element.text})

        # insert the contetn to the dict
        list_of_content.append(content_dict)

        # After processing each subelement in the element, clear and delete the elem found
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    data_dict.update({target_tag['name']:list_of_content})
    return data_dict


def load_data_to_outputdir(data, outputdir, inputfile, filetype="csv"):
    path, filename = os.path.split(inputfile)
    outputfile = "{outputdir}/{filename}".format(
        outputdir=outputdir, 
        filename=filename.replace(".xml", ".{filetype}".format(filetype=filetype))
        )

    if filetype == "csv":
        load_data_to_csv(data, outputfile)
    
    if filetype == "json":
        load_data_to_json(data, outputfile)

    return


def load_data_to_csv(data, outputfile):
    title_list = list()
    title_list.append("Scheme")
    row_data = list()

    for key, values in data.items():
        for i, value in enumerate(values):
            data_list = list()
            data_list.append(key)

            for k, v in value.items():
                if i == 0:
                    title_list.append(k)
                data_list.append(v)

            row_data.append(data_list)

    with open(outputfile, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        # write the header first
        csv_writer.writerow(title_list)

        # write each line
        for row in row_data:
            print("Writing row", row)
            csv_writer.writerow(row)

    return


def load_data_to_json(data, outputfile):
    with open(outputfile, 'w') as fp:
        json.dump(data, fp)
    return

def get_the_tag(inputfile):
    
    inputfile_tag = None
    selected_template = None
    context = etree.iterparse(inputfile, events=('end',), tag="OUTPUT")
    for event, elem in context:
        try:
            print("This is the target tag", elem.getchildren()[0].tag)
            inputfile_tag = elem.getchildren()[0].tag
        except Exception:
            pass

    # use of global variables here
    if inputfile_tag is not None:
        for template in LIST_OF_TEMPLATES:
            if inputfile_tag == template['name']:
                selected_template = template
    return selected_template


def main():
    input_option_str = 'i'
    output_dir_option_str = 'o'
    format_option_str = 't'

    format_json = 'json'
    format_csv = 'csv'

    parser = argparse.ArgumentParser(
        description='The xml data loader'
    )
    parser.add_argument(
        "-"+input_option_str,
        help="The input directory of XMLs"
    )
    parser.add_argument(
        "-"+output_dir_option_str,
        help="The output directory of extracted data"
    )
    parser.add_argument(
        "-"+format_option_str,
        help="The output format of extracted data, could be json or csv"
    )
    args = parser.parse_args()
    
    input_dir = getattr(args, input_option_str)
    output_dir = getattr(args, output_dir_option_str)

    # generate the list of files need to be processed
    list_of_datafiles = get_list_of_processing_files(input_dir)
    # print("##########", list_of_datafiles)
    
    # find the data according to the templates.

    # create the warapper here

    for inputfile in list_of_datafiles:
        # get the target tag of the file
        target_tag = get_the_tag(inputfile)

        if target_tag is None:
            raise Exception("The target tag for inputfile is None", inputfile)
        
        data_dict = get_data_dict(inputfile, target_tag)
        # print("This is the data dict", data_dict)

        # output the data with selected format
        load_data_to_outputdir(data_dict, output_dir, inputfile, filetype=args.t)

    return

if __name__ == '__main__':
    main()
