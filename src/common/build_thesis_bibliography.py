"""Build the single thesis-facing IEEE BibTeX registry.

The curated b1--b29 entries are stable. Research-registry entries are appended
after metadata-based deduplication. Research-only audit notes are deliberately
not rendered into the submission bibliography; their history remains in
docs/references.bib, docs/related_work.md, and docs/reference_key_map.md.
"""

from __future__ import annotations

import re
import csv
from pathlib import Path

from src.common.seed import set_seed


ROOT = Path(__file__).resolve().parents[2]
RESEARCH_BIB = ROOT / "docs" / "references.bib"
THESIS_BIB = ROOT / "docs" / "references_ieee.bib"
FULL_MAP = ROOT / "docs" / "reference_key_map_full.csv"


AUTHOR_FIXES = {
    "2605.14260": "Ziang Gao and Pengqi Liu and Archer Yi Yang and Mouloud Belbahri and Jesse C. Cresswell and Masoud Asgharian",
    "2605.05562": "Amir Rafe and Subasish Das",
    "2606.29403": "Louis Berthier and Ahmed Shokry and Maxime Moreaud and Guillaume Ramelet and Aymeric Dieuleveut",
    "2605.10405": "Elad Tolochinsky and Yaniv Tenzer and Yaniv Romano",
    "2605.31483": "Shefayat E Shams Adib and Ahmed Alfey Sani and Ekramul Alam Esham and Ajwad Abrar and Ishmam Tashdeed and Md Taukir Azam Chowdhury",
    "2605.22487": "Md. Asaduzzaman Shuvo and Mahedi Hasan and Md. Tashin Parvez and Azizul Haque Noman and Md. Shafayet Hossain Ovi",
    "2606.23196": "Elroy Stav and Dvir Berlowitz and Maayan Orner and Sarit Kraus",
    "2606.13156": "Animesh Tripathy and Aswanth Krishnan",
    "2604.18490": "Samar M. Magdy and Fakhraddin Alwajih and Abdellah El Mekki and Wesam El Sayed and Muhammad Abdul-Mageed",
    "2606.10765": "Khaled Elhady and Omar Kallas and Nizar Habash and Bashar Alhafni",
    "2608.03966": "Salah Eddine Bekhouche and Abdessalam Bouchekif and Hichem Telli and Mohammed-En-Nadhir Zighem and Abdenour Hadid",
    "2601.08070": "Shailesh Rana",
    "2605.03052": "Zhejian Zhou and Tianyi Zhou and Robin Jia and Jonathan May",
    "2605.20382": "Carolina Camassa and Derek Shiller",
    "2410.15956": "Yanzhu Guo and Simone Conia and Zelin Zhou and Min Li and Saloni Potdar and Henry Xiao",
    "2503.04369": "Yafu Li and Ronghao Zhang and Zhilin Wang and Huajian Zhang and Leyang Cui and Yongjing Yin and Tong Xiao and Yue Zhang",
    "2603.15949": "Tanvir Ahmed Sijan and S. M. Golam Rifat and Pankaj Chowdhury Partha and Md. Tanjeed Islam and Md. Musfique Anwar",
    "2512.13487": "Ayon Roy and Risat Rahaman and Sadat Shibly and Udoy Saha and Abdulla Al Kafi and Farig Yousuf Sadeque",
    "2502.15603": "Lisa Schut and Yarin Gal and Sebastian Farquhar",
    "2402.10588": "Chris Wendler and Veniamin Veselovsky and Giovanni Monea and Robert West",
    "2504.11833": "Changjiang Gao and Xu Huang and Wenhao Zhu and Shujian Huang and Lei Li and Fei Yuan",
    "2605.27649": "Qishi Zhan and Minxuan Hu and Seoyeon Jang and Lei Zhao and Ziheng Chen and Man Liang and Xinyue Xiang and Jiaxin Liu and Guansu Wang and Liang He",
    "2606.08994": "Trapoom Ukarapol and Pakhapoom Sarapat and Nut Chukamphaeng",
    "2606.19668": "Jeonghyun Park and Seunghyun Yoon and Yonghyun Jun and Hwanhee Lee",
    "2506.14012": "Amr Mohamed and Yang Zhang and Michalis Vazirgiannis and Guokan Shang",
    "2603.25015": "Tony Mason",
    "2604.16937": "Wei-Chi Wu and Sheng-Lun Wei and Hen-Hsen Huang and Hsin-Hsi Chen",
    "2601.17768": "Raja Gond and Aditya K. Kamath and Ramachandran Ramjee and Ashish Panwar",
    "2604.22411": "Alberto Messina and Stefano Scotta",
    "2605.19537": "David Pape and Jonathan Evertz and Lea Sch{\"o}nherr",
    "2602.14349": "Jiaxin Cui and Rohan Alexander",
    "2408.13586": "Yuxuan Zhou and Margret Keuper and Mario Fritz",
    "2407.01082": "Nguyen Nhat Minh and Andrew Baker and Clement Neo and Allen Roush and Andreas Kirsch and Ravid Shwartz-Ziv",
    "2602.18292": "Xiaotong Ji and Rasul Tutunov and Matthieu Zimmer and Haitham Bou-Ammar",
    "2202.12837": "Sewon Min and Xinxi Lyu and Ari Holtzman and Mikel Artetxe and Mike Lewis and Hannaneh Hajishirzi and Luke Zettlemoyer",
    "2605.08295": "Ming Liu",
    "2603.04464": "Difan Jiao and Di Wang and Lijie Hu",
    "2303.03846": "Jerry Wei and Jason Wei and Yi Tay and Dustin Tran and Albert Webson and Yifeng Lu and Xinyun Chen and Hanxiao Liu and Da Huang and Denny Zhou and Tengyu Ma",
    "2602.08033": r"Julien Fageot and Matthias Grossglauser and L{\^e}-Nguy{\^e}n Hoang and Matteo Tacchi-B{\'e}nard and Oscar Villemaud",
    "2604.17022": "Nisrine Rair and Alban Goupil and Valeriu Vrabie and Emmanuel Chochoy",
}

# Non-arXiv records whose research-registry author field was intentionally
# abbreviated during discovery.  These lists were checked against publisher,
# proceedings, or paper metadata before entering the thesis bibliography.
LEGACY_AUTHOR_FIXES = {
    "gundersen2023conclusions": "Odd Erik Gundersen and Saeid Shamsaliei and Henrik S. Kj{\\ae}rnli and Helge Langseth",
    "casola2022transformers": "Silvia Casola and Ivano Lauriola and Alberto Lavelli",
    "laurer2023bertnli": "Moritz Laurer and Wouter van Atteveldt and Andreu Casas and Kasper Welbers",
    "tunstall2022setfit": "Lewis Tunstall and Nils Reimers and Unso Eun Seo Jo and Luke Bates and Daniel Korat and Moshe Wasserblat and Oren Pereg",
    "beliveau2024smalldata": "Vincent Beliveau and Helene Kaas and Martin Prener and Claes N. Ladefoged and Desmond Elliott and Gitte M. Knudsen and Lars H. Pinborg and Melanie Ganz",
    "balanya2022adaptivetemp": "Sergio A. Balanya and Juan Maro{~n}as and Daniel Ramos",
    "guo2025smart": "Haolan Guo and Linwei Tao and Haoyang Luo and Minjing Dong and Chang Xu",
    "bucher2024finetuned": "Martin Juan Jos{\\'e} Bucher and Marco Martini",
    "hasan2025banglaemotion": "M. R. Hasan and Z. Chong and T. K. Abdulwasea and H. O. Rashid and F. Sultana",
    "mitra2025muril": "Sudipto Kumar Mitra and T. Riyad and M. Faysal Hossan and P. Sen and S. J. Islam and S. T. Shara",
    "hassin2026banglablend": "Farhan Hassin and Abrar Rakin and Md. Samiul Alom and Md. Istiak Ahamed and Snaholata Mondal and Azmeri Islam",
    "mazumder2025banglaforms": "Samiul Karim Mazumder and Sabiha Jannat and Snaholata Mondal",
    "hasan2023banglawar": "Mahmud Hasan and Labiba Islam and Ismat Jahan and Sabrina Mannan Meem and Rashedur M. Rahman",
    "mukherjee2023blp": "Sourabrata Mukherjee and Atul Kr. Ojha and Ond{\\v{r}}ej Du{\\v{s}}ek",
    "coakley2022implementation": "Kevin Coakley and Christine R. Kirkpatrick and Odd Erik Gundersen",
    "teodorescu2025kfold": "Vlad Teodorescu and Laura Obreja Bra{\\c{s}}oveanu",
    "wang2026rewardhacking": "Xiaohua Wang and Muzhao Tian and Yuqi Zeng and Zisu Huang and Jiakang Yuan and Bowen Chen and Jingwen Xu and Mingbo Zhou and Wenhao Liu and Muling Wu and Zhengkang Guo and Qi Qian and Yifei Wang and Feiran Zhang and Ruicheng Yin and Shihan Dou and Changze Lv and Tao Chen and Kaitao Song and Xu Tan and Tao Gui and Xiaoqing Zheng and Xuanjing Huang",
    "baker2025monitoring": "Bowen Baker and Joost Huizinga and Leo Gao and Zehao Dou and Melody Y. Guan and Aleksander Madry and Wojciech Zaremba and Jakub Pachocki and David Farhi",
    "shaib2025diversity": "Chantal Shaib and Venkata S. Govindarajan and Joe Barrow and Jiuding Sun and Alexa F. Siu and Byron C. Wallace and Ani Nenkova",
    "rahman2025hallucination": "Subhey Sadi Rahman and Md. Adnanul Islam and Md. Mahbub Alam and Musarrat Zeba and Md. Abdur Rahman and Sadia Sultana Chowa and Mohaimenul Azam Khan Raiaan and Sami Azam",
    "zhu2024rageval": "Kunlun Zhu and Yifan Luo and Dingling Xu and Yukun Yan and Zhenghao Liu and Shi Yu and Ruobing Wang and Shuo Wang and Yishan Li and Nan Zhang and Xu Han and Zhiyuan Liu and Maosong Sun",
}

ENTRY_FIXES = {
    "bethard2022seeds": (
        "misc",
        """
  title         = {We Need to Talk About Random Seeds},
  author        = {Steven Bethard},
  year          = {2022},
  eprint        = {2210.13393},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  doi           = {10.48550/arXiv.2210.13393},
  url           = {https://arxiv.org/abs/2210.13393},
""",
    ),
    "fu2023stability": (
        "misc",
        """
  title         = {A Stability Analysis of Fine-Tuning a Pre-Trained Model},
  author        = {Zihao Fu and Anthony Man-Cho So and Nigel Collier},
  year          = {2023},
  eprint        = {2301.09820},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/2301.09820},
""",
    ),
    "xue2023reproducibility": (
        "inproceedings",
        """
  title     = {We Need to Talk About Reproducibility in {NLP} Model Comparison},
  author    = {Yan Xue and Xuefei Cao and Xingli Yang and Yu Wang and Ruibo Wang and Jihong Li},
  booktitle = {Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing},
  pages     = {9424--9434},
  year      = {2023},
  doi       = {10.18653/v1/2023.emnlp-main.586},
  url       = {https://aclanthology.org/2023.emnlp-main.586/},
""",
    ),
}


ENTRY_RE = re.compile(r"(?ms)^@(\w+)\{([^,]+),(.*?)^\}")


def entries(text: str) -> list[tuple[str, str, str]]:
    return [(m.group(1), m.group(2).strip(), m.group(3)) for m in ENTRY_RE.finditer(text)]


def field(body: str, name: str) -> str:
    match = re.search(rf"(?ms)^\s*{re.escape(name)}\s*=\s*\{{(.*?)\}}\s*,?\s*$", body)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def normalized_title(body: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", field(body, "title").lower())


def remove_field(body: str, name: str) -> str:
    return re.sub(
        rf"(?ms)^\s*{re.escape(name)}\s*=\s*\{{.*?\}}\s*,?\s*$",
        "",
        body,
    )


def replace_author(body: str, author: str) -> str:
    replacement = f"\n  author = {{{author}}},"
    updated, count = re.subn(
        r"(?ms)^\s*author\s*=\s*\{.*?\}\s*,?\s*$",
        lambda _match: replacement,
        body,
        count=1,
    )
    if count:
        return updated
    return replacement + body


def clean_body(body: str, source_key: str = "") -> str:
    body = remove_field(body, "note")
    eprint = field(body, "eprint")
    if not eprint:
        match = re.search(r"(\d{4})_(\d{4,5})", source_key)
        if match:
            eprint = f"{match.group(1)}.{match.group(2)}"
            body += (
                f"\n  eprint = {{{eprint}}},"
                "\n  archivePrefix = {arXiv},"
                f"\n  url = {{https://arxiv.org/abs/{eprint}}},"
            )
    if eprint in AUTHOR_FIXES:
        body = replace_author(body, AUTHOR_FIXES[eprint])
    if source_key in LEGACY_AUTHOR_FIXES:
        body = replace_author(body, LEGACY_AUTHOR_FIXES[source_key])
    body = re.sub(r"\n{3,}", "\n\n", body).rstrip()
    return body


def render(kind: str, key: str, body: str, source_key: str = "") -> str:
    return f"@{kind}{{{key},{clean_body(body, source_key)}\n}}"


def main() -> None:
    set_seed()
    curated = [
        entry
        for entry in entries(THESIS_BIB.read_text(encoding="utf-8"))
        if re.fullmatch(r"b(?:[1-9]|1\d|2\d)", entry[1])
    ]
    research = entries(RESEARCH_BIB.read_text(encoding="utf-8"))
    output: list[str] = []
    mapping: list[dict[str, str]] = []
    seen_doi: set[str] = set()
    seen_eprint: set[str] = set()
    seen_title: set[str] = set()

    def remember(body: str) -> None:
        doi = field(body, "doi").lower()
        eprint = field(body, "eprint").lower()
        title = normalized_title(body)
        if doi:
            seen_doi.add(doi)
        if eprint:
            seen_eprint.add(eprint)
        if title:
            seen_title.add(title)

    def already_seen(body: str) -> bool:
        doi = field(body, "doi").lower()
        eprint = field(body, "eprint").lower()
        title = normalized_title(body)
        return bool(
            (doi and doi in seen_doi)
            or (eprint and eprint in seen_eprint)
            or (title and title in seen_title)
        )

    for kind, key, body in curated:
        output.append(render(kind, key, body))
        remember(body)
        mapping.append(
            {
                "b_key": key,
                "legacy_key": "",
                "title": field(body, "title"),
                "identifier": field(body, "doi") or field(body, "eprint"),
                "metadata_status": "curated_verified",
                "reading_status": "chapter_cited",
            }
        )

    next_number = max(int(key[1:]) for _, key, _ in curated if re.fullmatch(r"b\d+", key)) + 1
    for kind, old_key, body in research:
        if already_seen(body):
            continue
        original_body = body
        if old_key in ENTRY_FIXES:
            kind, body = ENTRY_FIXES[old_key]
        new_key = f"b{next_number}"
        output.append(render(kind, new_key, body, old_key))
        remember(body)
        reading_status = "full_or_primary_record"
        if re.search(r"NOT read in full|Abstract only", original_body, re.I):
            reading_status = "metadata_verified_not_full_read"
        metadata_status = "registry_metadata_preserved"
        eprint = field(body, "eprint")
        key_match = re.search(r"(\d{4})_(\d{4,5})", old_key)
        inferred_eprint = f"{key_match.group(1)}.{key_match.group(2)}" if key_match else ""
        if eprint in AUTHOR_FIXES or inferred_eprint in AUTHOR_FIXES:
            metadata_status = "alphaxiv_author_resolved"
        if old_key in LEGACY_AUTHOR_FIXES:
            metadata_status = "primary_author_resolved"
        if old_key in ENTRY_FIXES:
            metadata_status = "primary_metadata_corrected"
        mapping.append(
            {
                "b_key": new_key,
                "legacy_key": old_key,
                "title": field(body, "title"),
                "identifier": field(body, "doi") or eprint or inferred_eprint,
                "metadata_status": metadata_status,
                "reading_status": reading_status,
            }
        )
        next_number += 1

    header = (
        "% Canonical thesis bibliography. Render with IEEEtran or IEEE CSL.\n"
        "% Stable source keys b1, b2, ...; do not renumber existing entries.\n"
        "% Generated by src/common/build_thesis_bibliography.py.\n\n"
    )
    THESIS_BIB.write_text(header + "\n\n".join(output) + "\n", encoding="utf-8", newline="\n")
    with FULL_MAP.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "b_key",
                "legacy_key",
                "title",
                "identifier",
                "metadata_status",
                "reading_status",
            ],
        )
        writer.writeheader()
        writer.writerows(mapping)
    print(f"curated={len(curated)} research={len(research)} final={len(output)}")


if __name__ == "__main__":
    main()
