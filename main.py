import argparse
import json
import sys
import openpyxl
import requests
import os

from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Dict, List


def get_eccv(year       : int,
             keywords   : List[str]
            ) -> Dict:
    res = requests.get("https://www.ecva.net/papers.php")
    soup = BeautifulSoup(res.text, "html.parser")

    papers = soup.findAll("dt", {"class": "ptitle"})
    authors = soup.findAll("dd")
    assert len(papers) == len(authors) // 2

    indices = []
    parsed = {"conference": f"ECCV {year}", "papers": [], "authors": []}
    for i, paper in tqdm(enumerate(papers)):
        if f"eccv_{year}" in paper.find("a")["href"]:
            for keyword in keywords:
                if keyword.lower() in paper.text or keyword.upper() in paper.text or keyword.capitalize() in paper.text:
                    parsed["papers"].append(paper.text.strip())
                    indices.append(i)
                    break
        else:
            continue
                
    for idx in indices:
        # parsed["authors"]
        if year in [2020, 2022]:
            author = authors[idx * 2].text.split(",")
            for j in range(len(author)):
                author[j] = author[j].strip()
            parsed["authors"].append(author)
        elif year in [2018]:
            author = authors[idx * 2].text.split("and")
            for j in range(len(author)):
                author[j] = author[j].strip().split(',')
                author[j][0], author[j][1] = author[j][1].strip(), author[j][0].strip()
                author[j] = " ".join(author[j])
            parsed["authors"].append(author)
    return parsed

def get_neurips(year     : int,
                keywords : List[str]
                ) -> Dict:

    parsed = {"conference": f"NeurIPS {year}", "papers": [], "authors": []}
    if year == 2022:
        res = requests.get(f"https://api.openreview.net/notes?content.venue=NeurIPS+{year}+Accept&details=replyCount&offset=0&limit=1000&invitation=NeurIPS.cc%2F{year}%2FConference%2F-%2FBlind_Submission")
        res_json = json.loads(res.text)
        max_count = res_json["count"]
        offset = 0
        limit = 1000
        with tqdm(range(max_count)) as pbar:
            while offset <= max_count:
                res = requests.get(f"https://api.openreview.net/notes?content.venue=NeurIPS+{year}+Accept&details=replyCount&offset={offset}&limit={limit}&invitation=NeurIPS.cc%2F{year}%2FConference%2F-%2FBlind_Submission")
                res_json = json.loads(res.text)
                for note in res_json["notes"]:
                    title = note["content"]["title"]
                    keyword_found = False
                    for keyword in keywords:
                        if keyword.lower() in title or keyword.upper() in title or keyword.capitalize() in title:
                            keyword_found = True
                            break
                    
                    if keyword_found:
                        parsed["papers"].append(title)
                        parsed["authors"].append(note["content"]["authors"])
                    pbar.update(1)
                offset += limit
        
        return parsed

        
    else:
        res = requests.get(f"https://papers.nips.cc/paper/{year}")
        soup = BeautifulSoup(res.text, "html.parser")
        for i, paper in tqdm(enumerate(soup.find_all("div", {"class":"container-fluid"})[0].findAll("li"))):
            title = paper.findAll("a")
            authors = paper.findAll("i")
            keyword_found = False
            for keyword in keywords:
                if keyword.lower() in title[0].text or keyword.upper() in title[0].text or keyword.capitalize() in title[0].text:
                    keyword_found = True
                    break
            if keyword_found:
                parsed["papers"].append(title[0].text)
                parsed["authors"].append(authors[0].text.split(", "))
    return parsed

def get_iclr(year           : int,
             keywords       : List[str],
             ) -> Dict:
    if year == 2023:
        under_review = True
    else:
        under_review = False

    if under_review:
        parsed = {"conference": f"ICLR {year} underreview", "papers": [], "authors": []}
        res = requests.get("https://api.openreview.net/notes?details=replyCount%2Cinvitation%2Coriginal&offset=0&limit=50&invitation=ICLR.cc%2F2023%2FConference%2F-%2FBlind_Submission")
        res_json = json.loads(res.text)
        max_count = res_json["count"]
        offset = 0
        limit = 1000
        with tqdm(range(max_count)) as pbar:
            while offset <= max_count:
                res = requests.get(f"https://api.openreview.net/notes?details=replyCount%2Cinvitation%2Coriginal&offset={offset}&limit={limit}&invitation=ICLR.cc%2F2023%2FConference%2F-%2FBlind_Submission")
                res_json = json.loads(res.text)
                for row in res_json["notes"]:
                    title = row["content"]["title"]
                    keyword_found = False
                    for keyword in keywords:
                        if keyword.lower() in title or keyword.upper() in title or keyword.capitalize() in title:
                            keyword_found = True
                            break
                    if keyword_found:
                        parsed["papers"].append(row["content"]["title"])
                        parsed["authors"].append(["Anonymous"])
                    pbar.update(1)
                offset += limit
        return parsed
    else:
        parsed_poster = {"conference": f"ICLR {year}", "papers": [], "authors": []}
        parsed_spotlight = {"conference": f"ICLR {year} spotlight", "papers": [], "authors": []}
        parsed_oral = {"conference": f"ICLR {year} oral", "papers": [], "authors": []}
        # poster session
        res = requests.get(f"https://api.openreview.net/notes?content.venue=ICLR+{year}+Poster&details=replyCount&offset=0&limit=1000&invitation=ICLR.cc%2F{year}%2FConference%2F-%2FBlind_Submission")
        res_json = json.loads(res.text)
        max_count = res_json["count"]
        offset = 0
        limit = 1000
        with tqdm(range(max_count)) as pbar:
            while offset <= max_count:
                res = requests.get(f"https://api.openreview.net/notes?content.venue=ICLR+{year}+Poster&details=replyCount&offset=0&limit=1000&invitation=ICLR.cc%2F{year}%2FConference%2F-%2FBlind_Submission")
                res_json = json.loads(res.text)
                for row in res_json["notes"]:
                    title = row["content"]["title"]
                    keyword_found = False
                    for keyword in keywords:
                        if keyword.lower() in title or keyword.upper() in title or keyword.capitalize() in title:
                            keyword_found = True
                            break
                    if keyword_found:
                        parsed_poster["papers"].append(row["content"]["title"])
                        parsed_poster["authors"].append(["Anonymous"])
                    pbar.update(1)
                offset += limit
        # spotlight session
        res = requests.get(f"https://api.openreview.net/notes?content.venue=ICLR+{year}+Spotlight&details=replyCount&offset=0&limit=1000&invitation=ICLR.cc%2F{year}%2FConference%2F-%2FBlind_Submission")
        res_json = json.loads(res.text)
        max_count = res_json["count"]
        offset = 0
        limit = 1000
        with tqdm(range(max_count)) as pbar:
            while offset <= max_count:
                res = requests.get(f"https://api.openreview.net/notes?content.venue=ICLR+{year}+Spotlight&details=replyCount&offset=0&limit=1000&invitation=ICLR.cc%2F{year}%2FConference%2F-%2FBlind_Submission")
                res_json = json.loads(res.text)
                for row in res_json["notes"]:
                    title = row["content"]["title"]
                    keyword_found = False
                    for keyword in keywords:
                        if keyword.lower() in title or keyword.upper() in title or keyword.capitalize() in title:
                            keyword_found = True
                            break
                    if keyword_found:
                        parsed_spotlight["papers"].append(row["content"]["title"])
                        parsed_spotlight["authors"].append(["Anonymous"])
                    pbar.update(1)
                offset += limit
        # oral session
        res = requests.get(f"https://api.openreview.net/notes?content.venue=ICLR+{year}+Oral&details=replyCount&offset=0&limit=1000&invitation=ICLR.cc%2F{year}%2FConference%2F-%2FBlind_Submission")
        res_json = json.loads(res.text)
        max_count = res_json["count"]
        offset = 0
        limit = 1000
        with tqdm(range(max_count)) as pbar:
            while offset <= max_count:
                res = requests.get(f"https://api.openreview.net/notes?content.venue=ICLR+{year}+Oral&details=replyCount&offset=0&limit=1000&invitation=ICLR.cc%2F{year}%2FConference%2F-%2FBlind_Submission")
                res_json = json.loads(res.text)
                for row in res_json["notes"]:
                    title = row["content"]["title"]
                    keyword_found = False
                    for keyword in keywords:
                        if keyword.lower() in title or keyword.upper() in title or keyword.capitalize() in title:
                            keyword_found = True
                            break
                    if keyword_found:
                        parsed_oral["papers"].append(row["content"]["title"])
                        parsed_oral["authors"].append(["Anonymous"])
                    pbar.update(1)
                offset += limit
        return parsed_poster, parsed_spotlight, parsed_oral


def get_cvpr(year       : int,
             keywords   : List[str]
            ) -> Dict:
    parsed = {"conference": f"CVPR {year}", "papers": [], "authors": []}
    if year in [2021, 2022]:
        res = requests.get(f"https://openaccess.thecvf.com/CVPR{year}?day=all")
        soup = BeautifulSoup(res.text, "html.parser")
        papers = soup.find_all("dt", {"class": "ptitle"})
        authors = soup.find_all("dd")[1:]
        for i, paper in enumerate(tqdm(papers)):
            for keyword in keywords:
                if keyword.lower() in paper.text.lower():
                    parsed["papers"].append(paper.text)
                    parsed["authors"].append(authors[i * 2].text.split(","))
                    break

    elif year in [2018, 2019, 2020]:
        dates = {2018: ["2018-06-19", "2018-06-20", "2018-06-21"],
                 2019: ["2019-06-18", "2019-06-19", "2019-06-20"],
                 2020: ["2020-06-16", "2020-06-17", "2020-06-18"]}
        for date in dates[year]:
            res = requests.get(f"https://openaccess.thecvf.com/CVPR{year}?day={date}")
            soup = BeautifulSoup(res.text, "html.parser")
            papers = soup.find_all("dt", {"class": "ptitle"})
            authors = soup.find_all("dd")[1:]
            for i, paper in enumerate(papers):
                for keyword in keywords:
                    if keyword.lower() in paper.text.lower():
                        parsed["papers"].append(paper.text)
                        parsed["authors"].append(authors[i * 2].text.split(","))
                        break

    else:
        res = requests.get(f"https://openaccess.thecvf.com/CVPR{year}")
        soup = BeautifulSoup(res.text, "html.parser")
        papers = soup.find_all("dt", {"class": "ptitle"})
        authors = soup.find_all("dd")[1:]
        for i, paper in enumerate(papers):
            for keyword in keywords:
                if keyword.lower() in paper.text.lower():
                    parsed["papers"].append(paper.text)
                    parsed["authors"].append(authors[i * 2].text.split(","))
                    break
    return parsed

def get_iccv(year       : int,
             keywords   : List[str]
            ) -> Dict:
    parsed = {"conference": f"ICCV {year}", "papers": [], "authors": []}
    if year in [2021]:
        res = requests.get(f"https://openaccess.thecvf.com/ICCV{year}?day=all")
        soup = BeautifulSoup(res.text, "html.parser")
        papers = soup.find_all("dt", {"class": "ptitle"})
        authors = soup.find_all("dd")[1:]
        for i, paper in enumerate(tqdm(papers)):
            for keyword in keywords:
                if keyword.lower() in paper.text.lower():
                    parsed["papers"].append(paper.text)
                    parsed["authors"].append(authors[i * 2].text.split(","))
                    break

    elif year in [2019]:
        dates = {2019: ["2019-10-29", "2019-10-30", "2019-10-31", "2019-11-01"]}
        for date in dates[year]:
            res = requests.get(f"https://openaccess.thecvf.com/ICCV{year}?day={date}")
            soup = BeautifulSoup(res.text, "html.parser")
            papers = soup.find_all("dt", {"class": "ptitle"})
            authors = soup.find_all("dd")[1:]
            for i, paper in enumerate(papers):
                for keyword in keywords:
                    if keyword.lower() in paper.text.lower():
                        parsed["papers"].append(paper.text)
                        parsed["authors"].append(authors[i * 2].text.split(","))
                        break

    else:
        res = requests.get(f"https://openaccess.thecvf.com/ICCV{year}")
        soup = BeautifulSoup(res.text, "html.parser")
        papers = soup.find_all("dt", {"class": "ptitle"})
        authors = soup.find_all("dd")
        for i, paper in enumerate(papers):
            for keyword in keywords:
                if keyword.lower() in paper.text.lower():
                    parsed["papers"].append(paper.text)
                    parsed["authors"].append(authors[i * 2].text.split(","))
                    break
    return parsed

def get_icml(year       : int,
             keywords   : List[str]
            ) -> Dict:
    parsed = {"conference": f"ICML {year}", "papers": [], "authors": []}
    res = requests.get("https://proceedings.mlr.press")
    soup = BeautifulSoup(res.text, "html.parser")
    proceedings_list = soup.find_all("ul", {"class": "proceedings-list"})[1].find_all("li")
    for proceeding in proceedings_list:
        if year >= 2017:
            if f"Proceedings of ICML {year}" in proceeding.text and "Workshop" not in proceeding.text:
                href = proceeding.find("a")["href"]
                break
        else:
            if f"ICML {year} Proceedings" in proceeding.text and "Workshop" not in proceeding.text:
                href = proceeding.find("a")["href"]
                break

    res = requests.get(f"https://proceedings.mlr.press/{href}")
    soup = BeautifulSoup(res.text, "html.parser")
    papers = soup.find_all("div", {"class": "paper"})
    for paper in tqdm(papers):
        title = paper.find("p", {"class": "title"}).text
        for keyword in keywords:
            if keyword.lower() in title.lower():
                authors = paper.find("p", {"class": "details"}).find("span", {"class": "authors"}).text.split(",")
                authors = [a.strip() for a in authors]
                parsed["papers"].append(title)
                parsed["authors"].append(authors)
                

    return parsed

def get_acl(year    : int,
            keywords: List[str]) -> Dict:
    parsed = {"conference": f"ACL {year}", "papers": [], "authors": []}

    if year >= 2021:
        res = requests.get(f"https://aclanthology.org/events/acl-{year}/")
        soup = BeautifulSoup(res.text, "html.parser")
        long_div = soup.find_all("div", {"id": f"{year}acl-long"})[0]
        papers = long_div.find_all("span", {"class": "d-block"})
        for paper in tqdm(papers):
            a_list = paper.find_all("a")
            title = a_list[0].text
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    authors = a_list[1:]
                    authors = [a.text for a in authors]
                    parsed["papers"].append(title)
                    parsed["authors"].append(authors)
                    break
            

        short_div = soup.find_all("div", {"id": f"{year}acl-short"})[0]
        papers = short_div.find_all("span", {"class": "d-block"})
        for paper in tqdm(papers):
            a_list = paper.find_all("a")
            title = a_list[0].text
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    authors = a_list[1:]
                    authors = [a.text for a in authors]
                    parsed["papers"].append(title)
                    parsed["authors"].append(authors)
                    break

    elif year == 2020:
        res = requests.get(f"https://aclanthology.org/events/acl-{year}/")
        soup = BeautifulSoup(res.text, "html.parser")
        div = soup.find_all("div", {"id": f"{year}acl-main"})[0]
        papers = div.find_all("span", {"class": "d-block"})
        for paper in tqdm(papers):
            a_list = paper.find_all("a")
            title = a_list[0].text
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    authors = a_list[1:]
                    authors = [a.text for a in authors]
                    parsed["papers"].append(title)
                    parsed["authors"].append(authors)
                    break

    elif year == 2019:
        res = requests.get(f"https://aclanthology.org/events/acl-{year}/")
        soup = BeautifulSoup(res.text, "html.parser")
        div = soup.find_all("div", {"id": f"p{str(year)[2:]}-1"})[0]
        papers = div.find_all("span", {"class": "d-block"})
        for paper in tqdm(papers):
            a_list = paper.find_all("a")
            title = a_list[0].text
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    authors = a_list[1:]
                    authors = [a.text for a in authors]
                    parsed["papers"].append(title)
                    parsed["authors"].append(authors)
                    break

    elif year == 2018:
        res = requests.get(f"https://aclanthology.org/events/acl-{year}/")
        soup = BeautifulSoup(res.text, "html.parser")
        long_div = soup.find_all("div", {"id": f"p{str(year)[2:]}-1"})[0]
        papers = long_div.find_all("span", {"class": "d-block"})
        for paper in tqdm(papers):
            a_list = paper.find_all("a")
            title = a_list[0].text
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    authors = a_list[1:]
                    authors = [a.text for a in authors]
                    parsed["papers"].append(title)
                    parsed["authors"].append(authors)
                    break
            
        short_div = soup.find_all("div", {"id": f"p{str(year)[2:]}-2"})[0]
        papers = short_div.find_all("span", {"class": "d-block"})
        for paper in tqdm(papers):
            a_list = paper.find_all("a")
            title = a_list[0].text
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    authors = a_list[1:]
                    authors = [a.text for a in authors]
                    parsed["papers"].append(title)
                    parsed["authors"].append(authors)
                    break
    
    return parsed

def get_emnlp(year    : int,
              keywords: List[str]) -> Dict:
    parsed = {"conference": f"EMNLP {year}", "papers": [], "authors": []}

    if year >= 2020:
        res = requests.get(f"https://aclanthology.org/events/emnlp-{year}/")
        soup = BeautifulSoup(res.text, "html.parser")
        div = soup.find_all("div", {"id": f"{year}emnlp-main"})[0]
        papers = div.find_all("span", {"class": "d-block"})
        for paper in tqdm(papers):
            a_list = paper.find_all("a")
            title = a_list[0].text
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    authors = a_list[1:]
                    authors = [a.text for a in authors]
                    parsed["papers"].append(title)
                    parsed["authors"].append(authors)
                    break
    
    elif year >= 2018:
        res = requests.get(f"https://aclanthology.org/events/emnlp-{year}/")
        soup = BeautifulSoup(res.text, "html.parser")
        div = soup.find_all("div", {"id": f"d{str(year)[2:]}-1"})[0]
        papers = div.find_all("span", {"class": "d-block"})
        for paper in tqdm(papers):
            a_list = paper.find_all("a")
            title = a_list[0].text
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    authors = a_list[1:]
                    authors = [a.text for a in authors]
                    parsed["papers"].append(title)
                    parsed["authors"].append(authors)
                    break
    
    return parsed

conference = {
    "eccv"    : get_eccv,
    "neurips" : get_neurips,
    "iclr" : get_iclr,
    "cvpr" : get_cvpr,
    "iccv" : get_iccv,
    "icml" : get_icml,
    "acl" : get_acl,
    "emnlp" : get_emnlp,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conference", type=str)
    parser.add_argument("-y", "--year", type=int)
    parser.add_argument("-k", "--keywords", type=str, nargs="+")
    args = parser.parse_args()
    parsed = conference[args.conference.lower()](args.year, args.keywords)
    if isinstance(parsed, tuple):
        if len(parsed) == 2:
            pass
        elif len(parsed) == 3: # poster, spotlight, oral
            wb = openpyxl.Workbook()
            sheet = wb.worksheets[0]
            offset = 1
            for session in range(len(parsed)):
                for row, (paper, author) in enumerate(zip(parsed[session]["papers"], parsed[session]["authors"]), offset):
                    sheet.cell(row=row, column=1).value = parsed[session]["conference"]
                    sheet.cell(row=row, column=2).value = paper
                    sheet.cell(row=row, column=3).value = author[0]
                offset += len(parsed[session]["papers"])
    else:
        wb = openpyxl.Workbook()
        sheet = wb.worksheets[0]
        for row, (paper, author) in enumerate(zip(parsed["papers"], parsed["authors"]), 1):
            sheet.cell(row=row, column=1).value = parsed["conference"]
            sheet.cell(row=row, column=2).value = paper
            sheet.cell(row=row, column=3).value = author[0]
    if args.conference.lower() == 'neurips':
        upper_conference = 'NeurIPS'
    else:
        upper_conference = args.conference.upper()
    keywords = [k.lower() for k in args.keywords]
    keywords = "_".join(sorted(keywords))
    save_path = f"{upper_conference}_{args.year}_{keywords}.xlsx"
    wb.save(save_path)
