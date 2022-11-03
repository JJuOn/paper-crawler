from ast import parse
import openpyxl
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from tqdm import tqdm



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


if __name__ == "__main__":
    parsed_eccv = get_eccv(2022, keywords=["lifelong", 'contin', 'incre'])
    wb = openpyxl.Workbook()
    sheet = wb.worksheets[0]
    for row, (paper, author) in enumerate(zip(parsed_eccv['papers'], parsed_eccv['authors']), 1):
        sheet.cell(row=row, column=1).value = parsed_eccv['conference']
        sheet.cell(row=row, column=2).value = paper
        sheet.cell(row=row, column=3).value = author[0]
    wb.save('eccv_2022.xlsx')
