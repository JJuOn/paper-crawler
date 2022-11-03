import json
from ast import parse

from typing import List, Dict
import openpyxl
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
import sys
import argparse


def get_eccv(year, keywords):
    res = requests.get("https://www.ecva.net/papers.php")
    soup = BeautifulSoup(res.text, "html.parser")

    papers = soup.findAll("dt", {"class": "ptitle"})
    authors = soup.findAll("dd")
    assert len(papers) == len(authors) // 2

    indices = []
    parsed = {'conference': f'ECCV {year}', 'papers': [], 'authors': []}
    for i, paper in tqdm(enumerate(papers)):
        if f"eccv_{year}" in paper.find("a")["href"]:
            for keyword in keywords:
                if keyword.lower() in paper.text or keyword.upper() in paper.text or keyword.capitalize() in paper.text:
                    parsed['papers'].append(paper.text.strip())
                    indices.append(i)
                    break
        else:
            continue
                
    for idx in indices:
        # parsed['authors']
        author = authors[idx * 2].text.split(',')
        for j in range(len(author)):
            author[j] = author[j].strip()
        parsed['authors'].append(author)
    return parsed

def get_neurips(year     : int,
                keywords : List[str]
                ) -> Dict:

    parsed = {'conference': f'NeurIPS {year}', 'papers': [], 'authors': []}
    if year == 2022:
        for i, keyword in tqdm(enumerate(keywords)):
            res = requests.get(f"https://api.openreview.net/notes/search?term={keyword}&type=terms&content=all&source=forum&group=NeurIPS.cc%2F2022%2FConference&limit=5000&offset=0&venue=NeurIPS+2022+Accept")
            res_json = json.loads(res.text)
            for note in res_json['notes']:
                parsed['papers' ].append(note['content']['title'])
                parsed['authors'].append(note['content']['authors'])
    else:
        res = requests.get(f"https://papers.nips.cc/paper/{year}")
        soup = BeautifulSoup(res.text, "html.parser")
        for i, paper in tqdm(enumerate(soup.find_all("div",{"class":"container-fluid"})[0].findAll("li"))):
            title = paper.findAll("a")
            authors = paper.findAll("i")
            parsed['papers'].append(title[0].text)
            parsed['authors'].append(authors[0].text.split(', '))
            pass
    return parsed


parser = argparse.ArgumentParser()
parser.add_argument("-conference", type=str)
parser.add_argument("-year", type=int)
parser.add_argument("-keywords", type=str, nargs='+')

conference = {
    'eccv'    : get_eccv,
    'neurips' : get_neurips,
}

if __name__ == "__main__":
    
    argv = parser.parse_args(sys.argv[1:])
    parsed = conference[argv.conference](argv.year, argv.keywords)
    wb = openpyxl.Workbook()
    sheet = wb.worksheets[0]
    for row, (paper, author) in enumerate(zip(parsed['papers'], parsed['authors']), 1):
        sheet.cell(row=row, column=1).value = parsed['conference']
        sheet.cell(row=row, column=2).value = paper
        sheet.cell(row=row, column=3).value = author[0]
    wb.save(f'{argv.conference}_{argv.year}.xlsx')
