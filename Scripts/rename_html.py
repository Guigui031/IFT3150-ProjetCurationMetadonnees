import os, pandas
import shutil
import time

import pandas as pd

from SRProject import *
from os_path import EXTRACTED_PATH
from bs4 import BeautifulSoup
import htmlParser


path = f"{EXTRACTED_PATH}/Bibtex"
def rename_files():
    for file in os.listdir(path):
        # print(file)
        rightly_formatted_file = file
        # for char in special_char_conversion.keys():
        #     rightly_formatted_file = rightly_formatted_file.replace(special_char_conversion[char], "%" + special_char_conversion[char])
        # rightly_formatted_file = rightly_formatted_file.replace("3f", "?")
        # # rightly_formatted_file = rightly_formatted_file.replace("24", "$")
        # rightly_formatted_file = rightly_formatted_file.replace("26", "&")
        # rightly_formatted_file = rightly_formatted_file.replace("2b", "+")
        # rightly_formatted_file = rightly_formatted_file.replace("2c", ",")
        # rightly_formatted_file = rightly_formatted_file.replace("3b", ";")
        # rightly_formatted_file = rightly_formatted_file.replace("40", "@")
        # print(file[8:10])
        # if not (file[8:10] == "22" or file[8:10] == "25"):
        #     continue
        # rightly_formatted_file = "2024-08-20_" + rightly_formatted_file
        rightly_formatted_file = rightly_formatted_file[:-7] + "_07" + rightly_formatted_file[-4:]
        print(rightly_formatted_file)
        # os.rename(path + "/" + file, path + "/" + rightly_formatted_file)


# rename_files()

def test_keys():
    name= "2024-06-25_Adaptive Behavior Control Model Of Non Player Character_05.html"
    print(name[-7:-5])
    print(list(code_source.keys()))
    print(code_source[name[-7:-5]])
    try:
        venue = code_source[name[-7:-5]]
    except:
        venue = None
    print(venue)
    # print(code_source[name[-7:-5]] if str(name[-7:5]) in ['00', '01', '02', '03', '04', '05'] else None)
    print(name[11:-8])


# test_keys()

def generate_bibtex():
    df = pandas.read_excel(f"{MAIN_PATH}\\Datasets\\GameSE\\GameSE_final_2.xlsx")
    for idx, row in df.iterrows():
        bibtex = f"""@article{{{''},
title = {{{row['title']}}},
journal = {{{row['venue']}}},
pages = {{{row['pages']}}},
year = {{{row['year']}}},
issn = {{{''}}},
doi = {{{row['doi']}}},
url = {{{''}}},
author = {{{row['authors']}}},
keywords = {{{row['keywords']}}},
abstract = {{{row['abstract']}}}
}}
"""
        row['bibtex'] = bibtex
        df.iloc[idx] = row
    df.to_excel(f"{MAIN_PATH}/Datasets/GameSE/GameSE_final_2-bibtex.xlsx")

# generate_bibtex()

def get_url_from_html():
    extract = pd.read_excel(f"{MAIN_PATH}/Datasets/GameSE/GameSE.xlsx")
    for idx, row in extract.iterrows():
        if not pd.isna(row['link']) or not pd.isna(row['doi']):
            continue
        file_to_search = None
        for file in os.listdir(f"{EXTRACTED_PATH}/HTML extracted"):
            if file[11:-8] == format_link(str(row['meta_title'])):
                file_to_search = file
                break
        if not file_to_search:
            continue
        with open(f"{EXTRACTED_PATH}/HTML extracted/{file_to_search}") as f:
            soup = BeautifulSoup(f)
        if file_to_search[-7:-5] == '05':
            suffix = soup.find('span', {'id': 'HiddenSecTa-accessionNo'})
            url = "https://www.webofscience.com/wos/woscc/full-record/" + suffix
            save_link(row['meta_title'], url)
# get_url_from_html()

def extract_from_manual():
    metadata = metadata_base.copy()
    metadata['Title'] = "Role-Playing Computer Game To Improve Speech Ability Of Down Syndrome Children"
    articles_extract_manually = pd.read_csv(f'{MAIN_PATH}/Scripts/articles_extract_manually.tsv', sep='\t',
                                            encoding='windows-1252', encoding_errors='ignore')
    if metadata['Title'] in articles_extract_manually['meta_title'].values:
        print("link already extracted manually, adding it")
        row = articles_extract_manually.loc[articles_extract_manually['meta_title'] == metadata['Title']].iloc[0]
        print(row)
        metadata['Title'] = row['title']
        metadata['Abstract'] = row['abstract']
        metadata['Keywords'] = row['keywords']
        metadata['Authors'] = row['authors']
        metadata['Venue'] = row['venue']
        metadata['DOI'] = row['doi']
        metadata['References'] = row['references']
        metadata['Pages'] = row['pages']
        metadata['Bibtex'] = row['bibtex']
        metadata['Source'] = row['source']
        metadata['Year'] = row['year']
        metadata['Link'] = row['link']
        metadata['Publisher'] = row['publisher']
    print(metadata)
# extract_from_manual()

def compare_titles_and_metatitles():
    errors = []
    df = pd.read_csv(f"{MAIN_PATH}/Datasets/GameSE/GameSE.tsv", sep='\t')
    for idx, row in df.iterrows():
        title = clean_title(str(row['title']))
        meta_title = clean_title(str(row['meta_title']))
        if title not in meta_title and meta_title not in title:
            print("erreur")
            errors.append((idx, title, meta_title))
            print((idx, title, meta_title))
            # errors.append((idx, row['title'], row['meta_title']))
            if abs(len(title.split()) - len(meta_title.split())) > 4 or abs(len(title) - len(meta_title)) > 10: decision = 'y'
            else: decision = input("delete?")
            if decision == "y":
                n = 0
                for file in os.listdir(f"{EXTRACTED_PATH}/HTML extracted"):
                    if file[11:-8] == format_link(str(row['meta_title'])):
                        os.rename(f"{EXTRACTED_PATH}/HTML extracted/{file}", f"{EXTRACTED_PATH}/Error/{file}")
                        print(file)
                        n += 1
                for file in os.listdir(f"{EXTRACTED_PATH}/Bibtex"):
                    if file[11:-7] == format_link(str(row['meta_title'])):
                        os.rename(f"{EXTRACTED_PATH}/Bibtex/{file}", f"{EXTRACTED_PATH}/Error/{file}")
                        print(file)
                        n += 1
                print('nb deplace:', n)
                time.sleep(1)
        else:
            print("correct")
    print("====================================")
    for er in errors: print(er)
    print(len(errors))
# compare_titles_and_metatitles()

def clean_bad_html():
    n = 0
    for file in os.listdir(f"{EXTRACTED_PATH}/HTML extracted"):
        if 'http' in file:
            continue
        if file[-7:-5] == '00':
            with open(f"{EXTRACTED_PATH}/HTML extracted/{file}", 'rb') as f:
                doc = f.read().decode('utf-8')
                metadata = htmlParser.get_metadata_from_html_ieee(doc)
                if not metadata or not metadata['Title']:
                    print(file)
                    print(metadata)
                    if "Getting results..." in doc:
                        os.rename(f"{EXTRACTED_PATH}/HTML extracted/{file}",f"{EXTRACTED_PATH}/Error/{file}")
                        print('deplace...')
                        n += 1
        if file[-7:-5] == '01':
            with open(f"{EXTRACTED_PATH}/HTML extracted/{file}", 'rb') as f:
                doc = f.read().decode('utf-8')
                metadata = htmlParser.get_metadata_from_html_ACM(doc)
                if not metadata or not metadata['Title']:
                    print(file)
                    print(metadata)
                    if "Search Results" in doc:
                        os.rename(f"{EXTRACTED_PATH}/HTML extracted/{file}",f"{EXTRACTED_PATH}/Error/{file}")
                        print('deplace...')
                        n += 1
    print('nb deplace:', n)
# clean_bad_html()

def clean_and_duplicate_good_scopus_html():
    n = 0
    for file in os.listdir(f"{EXTRACTED_PATH}/HTML extracted"):
        if not 'scopus' in file:
            continue
        # if file[-8:-5] == '_04':
        #     os.remove(f"{EXTRACTED_PATH}/HTML extracted/{file}")
        shutil.copy(f"{EXTRACTED_PATH}/HTML extracted/{file}", f"{EXTRACTED_PATH}/HTML extracted/{file[:-5] + '_04' + file[-5:]}")
# clean_and_duplicate_good_scopus_html()

def clean_publisher(publisher: str):
    if not publisher:
        return publisher
    publisher = publisher.replace('All rights reserved.', '')
    publisher = re.sub('^\d+[-,\d\s]*?(?=[A-Za-z])', '', publisher.strip())  # chiffre avant texte
    publisher = re.sub('\d+\s*.*$', '', publisher.strip())  # chiffre apres texte
    if publisher[-1] == '.': publisher = publisher[:-1]
    return publisher
print(clean_publisher('ACTA PRESS2509 DIEPPE AVE SW, BLDG B6, STE 101, CALGARY, AB T3E 7J9, CANADA'))