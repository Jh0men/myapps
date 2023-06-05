import os
import datetime
import json
import csv
import xml.etree.ElementTree as Xet
import pandas as pd

# This is a XML parser script, whitch fetches student information from XML files gathered from primus application
# and refactors the data to easily readable and modifiable CSV table format

# Create timestamp
time = datetime.datetime.now()
timestamp = f"{time.day}_{time.month}_{time.year}"
# Declaring columns for the dataset frame
cols = ["hetu", "etunimi", "sukunimi",
        "kutsumanimi", "ryhma", "koulu", "opiskelijalaji"]

# Declaring paths and file names

new_data_path = ""
citizens_data_path = ""

# Parse XML files and return organized data set


def parse_xml_data(path, filename_list):
    primus_data = []
    # Initializing XML element tree parameters
    placement = Xet.parse(f'{path}/{filename_list[0]}')
    placement_root = placement.getroot()
    department = Xet.parse(f'{path}/{filename_list[1]}')
    department_root = department.getroot()
    unit = Xet.parse(f'{path}/{filename_list[2]}')
    unit_root = unit.getroot()
# Parsing all the needed data and creating easily accessible list of dictionaries (primus_data)
    # PrimusPlacement.xml data collection
    for placement_data in placement_root.findall('CARD'):
        temp_dict = {
            "hetu": placement_data.find('hetu').text,
            "etunimi": None,
            "sukunimi": None,
            "kutsumanimi": None,
            "ryhma": 0,
            "ryhma_id": int(placement_data.find('luokkaryhmaid').text),
            "koulu": 0,
            "koulu_id": int(placement_data.find('paivakodinid').text),
            "opiskelijalaji": placement_data.find('opiskelijalaji').text
        }
        primus_data.append(temp_dict)
    # PrimusDepartment.xml data collection
    for set in primus_data:
        for department_data in department_root.findall('CARD'):
            if set["ryhma_id"] == int(department_data.find('luokkaryhmaid').text):
                set["ryhma"] = department_data.find('ryhmanimi').text
                del set["ryhma_id"]
                break

    # PrimusUnit.xml data collection
    for set in primus_data:
        for unit_data in unit_root.findall('CARD'):
            if set["koulu_id"] == int(unit_data.find('paivakodinid').text):
                set["koulu"] = unit_data.find('paivakodinnimi').text
                del set["koulu_id"]
                break
    return primus_data

# Parsing citizens data


def parse_vaesto_data():
    vaesto_list = list()
    parsed_vaesto_list = list()
    with open(citizens_data_path, 'r') as vaesto_data:
        reader = csv.DictReader(vaesto_data)
        for dict in reader:
            vaesto_list.append(dict)
    for set in vaesto_list:
        temp_dict = {
            "hetu": set["C_HENKTUNN"],
            "etunimi": str(set["NIMI"]).split()[1],
            "sukunimi": str(set["NIMI"]).split(maxsplit=1)[0],
        }
        parsed_vaesto_list.append(temp_dict)
    return parsed_vaesto_list

# Attaching names from citizens to primus data by comparing social security numbers


def add_names_to_primus_data(primus_data, vaesto_data):
    final_data = list()
    no_names = list()
    for dict1 in primus_data:
        for dict2 in vaesto_data:
            if dict1["hetu"] == dict2["hetu"]:
                dict1.update(
                    {"etunimi": dict2["etunimi"], "sukunimi": dict2["sukunimi"], "kutsumanimi": dict2["etunimi"]})
                final_data.append(dict1)
                break
    for set1 in primus_data:
        if not any([set1["hetu"] == set2["hetu"] for set2 in final_data]):
            no_names.append(set1)
    return (final_data, no_names)

# This function forms the CSV data and additionally JSON data if neaded


def create_output_file(data, file_name, extension):
    path = os.path.join(os.getcwd(), "Output_files")
    if not os.path.exists(path):
        os.mkdir(path, 0o666)
    match str(extension).lower():
        case "csv":
            df = pd.DataFrame(data, columns=cols)
            df.to_csv(
                f'{path}/{file_name}.csv', encoding="ISO-8859-1", index=False, header=False)
        case "json":
            with open(f"{path}/{file_name}.json", "w") as jsonfile:
                jsonfile.write(json.dumps(data, indent=2))
        case _:
            print("Extension does not exist, output file not created.")


# Defining the main function


def main():
    new_files = ["PrimusPlacement.xml",
                 "PrimusDepartment.xml", "PrimusUnit.xml"]

    new_xml_data = parse_xml_data(new_data_path, new_files)
    vaesto_data = parse_vaesto_data()
    final_data_tuple = add_names_to_primus_data(new_xml_data, vaesto_data)

    create_output_file(final_data_tuple[0],
                       f'oppilastiedot_{timestamp}', 'csv')
    create_output_file(final_data_tuple[1],
                       f'puuttuvat_oppilastiedot_{timestamp}', 'csv')


# Running the main function


if __name__ == "__main__":
    main()
