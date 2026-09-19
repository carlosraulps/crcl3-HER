import re
import subprocess

with open("Response_letter_clean.tex") as f:
    text = f.read()

# First clean out any existing Location tags
text = re.sub(r"\\textbf\{\[Location:[^\]]+\]\}\\\\\s*", "", text)

locations = {
    "Reviewer 1 --- Comment 1": (
        "manuscript\\_marked.pdf: Pages 1--2, Lines 2--21",
        "manuscript\\_clean.tex: Line 119",
        "manuscript\\_marked.tex: Line 138"
    ),
    "Reviewer 1 --- Comment 2": (
        "manuscript\\_marked.pdf: Page 4, Lines 72--83",
        "manuscript\\_clean.tex: Line 138",
        "manuscript\\_marked.tex: Line 157"
    ),
    "Reviewer 1 --- Comment 3": (
        "manuscript\\_marked.pdf: Page 5, Lines 92--108 \\& Page 16, Lines 325--330",
        "manuscript\\_clean.tex: Lines 140, 359",
        "manuscript\\_marked.tex: Lines 159, 378"
    ),
    "Reviewer 1 --- Comment 4": (
        "manuscript\\_marked.pdf: Page 11, Lines 242--250 \\& Pages 20--21, Lines 402--412",
        "manuscript\\_clean.tex: Lines 323, 393",
        "manuscript\\_marked.tex: Lines 342, 412"
    ),
    "Reviewer 1 --- Comment 5": (
        "manuscript\\_marked.pdf: Page 5, Lines 110--115",
        "manuscript\\_clean.tex: Line 144",
        "manuscript\\_marked.tex: Line 163"
    ),
    "Reviewer 1 --- Comment 6": (
        "manuscript\\_marked.pdf: Page 5, Lines 113--115",
        "manuscript\\_clean.tex: Line 144",
        "manuscript\\_marked.tex: Line 163"
    ),
    "Reviewer 1 --- Comment 7": (
        "manuscript\\_marked.pdf: Page 28, Lines 527--536",
        "manuscript\\_clean.tex: Line 452",
        "manuscript\\_marked.tex: Line 471"
    ),
    "Reviewer 1 --- Comment 8": (
        "manuscript\\_marked.pdf: Page 18, Lines 360--375",
        "manuscript\\_clean.tex: Line 374",
        "manuscript\\_marked.tex: Line 393"
    ),

    "Reviewer 2 --- Comment 1": (
        "manuscript\\_marked.pdf: Page 6, Lines 122--126",
        "manuscript\\_clean.tex: Line 149",
        "manuscript\\_marked.tex: Line 168"
    ),
    "Reviewer 2 --- Comment 2": (
        "manuscript\\_marked.pdf: Pages 24--25, Lines 471--480",
        "manuscript\\_clean.tex: Line 429",
        "manuscript\\_marked.tex: Line 448"
    ),
    "Reviewer 2 --- Comment 3": (
        "manuscript\\_marked.pdf: Page 32, Lines 604--606",
        "manuscript\\_clean.tex: Line 475",
        "manuscript\\_marked.tex: Line 494"
    ),
    "Reviewer 2 --- Comment 4": (
        "manuscript\\_marked.pdf: Pages 20--21, Lines 402--412",
        "manuscript\\_clean.tex: Line 393",
        "manuscript\\_marked.tex: Line 412"
    ),
    "Reviewer 2 --- Comment 5": (
        "manuscript\\_marked.pdf: Page 32, Lines 606--610",
        "manuscript\\_clean.tex: Line 475",
        "manuscript\\_marked.tex: Line 494"
    ),
    "Reviewer 2 --- Comment 6": (
        "manuscript\\_marked.pdf: Pages 29--30, Lines 542--569",
        "manuscript\\_clean.tex: Line 456",
        "manuscript\\_marked.tex: Line 475"
    ),
    "Reviewer 2 --- Comment 7": (
        "manuscript\\_marked.pdf: Page 28, Lines 527--536",
        "manuscript\\_clean.tex: Line 452",
        "manuscript\\_marked.tex: Line 471"
    ),
    "Reviewer 2 --- Comment 8": (
        "manuscript\\_marked.pdf: Page 32, Lines 610--612",
        "manuscript\\_clean.tex: Line 475",
        "manuscript\\_marked.tex: Line 494"
    ),
    "Reviewer 2 --- Comment 9": (
        "manuscript\\_marked.pdf: Page 3, Lines 39--40",
        "manuscript\\_clean.tex: Line 130",
        "manuscript\\_marked.tex: Line 149"
    ),

    "Reviewer 3 --- Comment 1": (
        "manuscript\\_marked.pdf: Pages 15--16, Lines 315--324",
        "manuscript\\_clean.tex: Line 355",
        "manuscript\\_marked.tex: Line 374"
    ),
    "Reviewer 3 --- Comment 2": (
        "manuscript\\_marked.pdf: Pages 22--24, Lines 430--470",
        "manuscript\\_clean.tex: Lines 412--428",
        "manuscript\\_marked.tex: Lines 431--447"
    ),
    "Reviewer 3 --- Comment 3": (
        "manuscript\\_marked.pdf: Page 21, Lines 401--410",
        "manuscript\\_clean.tex: Line 401",
        "manuscript\\_marked.tex: Line 420"
    ),

    "Reviewer 4 --- Comment 1": (
        "manuscript\\_marked.pdf: Page 6, Lines 127--135",
        "manuscript\\_clean.tex: Line 152",
        "manuscript\\_marked.tex: Line 171"
    ),
    "Reviewer 4 --- Comment 2": (
        "manuscript\\_marked.pdf: Pages 6--7, Lines 136--144",
        "manuscript\\_clean.tex: Line 154",
        "manuscript\\_marked.tex: Line 173"
    ),
    "Reviewer 4 --- Comment 3": (
        "manuscript\\_marked.pdf: Page 17, Lines 348--357",
        "manuscript\\_clean.tex: Line 372",
        "manuscript\\_marked.tex: Line 391"
    ),
    "Reviewer 4 --- Comment 4": (
        "manuscript\\_marked.pdf: Page 8, Lines 174--177",
        "manuscript\\_clean.tex: Line 188",
        "manuscript\\_marked.tex: Line 207"
    ),
    "Reviewer 4 --- Comment 5": (
        "manuscript\\_marked.pdf: Pages 24--25, Lines 471--480",
        "manuscript\\_clean.tex: Line 429",
        "manuscript\\_marked.tex: Line 448"
    ),
    "Reviewer 4 --- Comment 6": (
        "manuscript\\_marked.pdf: Page 18, Lines 383--387",
        "manuscript\\_clean.tex: Line 385",
        "manuscript\\_marked.tex: Line 404"
    ),
    "Reviewer 4 --- Comment 7": (
        "manuscript\\_marked.pdf: Page 12, Lines 255--263",
        "manuscript\\_clean.tex: Line 325",
        "manuscript\\_marked.tex: Line 344"
    ),
    "Reviewer 4 --- Comment 8": (
        "manuscript\\_marked.pdf: Page 20, Lines 391--392 \\& SI Fig. S3",
        "manuscript\\_clean.tex: Line 391",
        "manuscript\\_marked.tex: Line 410"
    ),
    "Reviewer 4 --- Comment 9": (
        "manuscript\\_marked.pdf: Page 18, Lines 361--363",
        "manuscript\\_clean.tex: Line 374",
        "manuscript\\_marked.tex: Line 393"
    ),
    "Reviewer 4 --- Comment 10": (
        "manuscript\\_marked.pdf: Page 24, Lines 425--428",
        "manuscript\\_clean.tex: Line 427",
        "manuscript\\_marked.tex: Line 446"
    ),
    "Reviewer 4 --- Comment 11": (
        "manuscript\\_marked.pdf: Page 13, Table 1 \\& Page 27, Table 2",
        "manuscript\\_clean.tex: Lines 333, 441",
        "manuscript\\_marked.tex: Lines 352, 460"
    ),
    "Reviewer 4 --- Comment 12": (
        "manuscript\\_marked.pdf: Throughout manuscript",
        "manuscript\\_clean.tex: Multiple sections",
        "manuscript\\_marked.tex: Multiple sections"
    ),
    "Reviewer 4 --- Comment 14": (
        "manuscript\\_marked.pdf: Pages 29--30, Lines 542--569",
        "manuscript\\_clean.tex: Line 456",
        "manuscript\\_marked.tex: Line 475"
    ),
    "Reviewer 4 --- Comment 15": (
        "manuscript\\_marked.pdf: Pages 29--30, Lines 542--569",
        "manuscript\\_clean.tex: Line 456",
        "manuscript\\_marked.tex: Line 475"
    ),
    "Reviewer 4 --- Comment 16": (
        "manuscript\\_marked.pdf: Page 7, Lines 145--147",
        "manuscript\\_clean.tex: Line 156",
        "manuscript\\_marked.tex: Line 175"
    ),
    "Reviewer 4 --- Comment 17": (
        "manuscript\\_marked.pdf: Page 16, Lines 331--335",
        "manuscript\\_clean.tex: Line 361",
        "manuscript\\_marked.tex: Line 380"
    ),
    "Reviewer 4 --- Comment 18": (
        "manuscript\\_marked.pdf: Pages 20--21, Lines 402--412",
        "manuscript\\_clean.tex: Line 393",
        "manuscript\\_marked.tex: Line 412"
    ),
    "Reviewer 4 --- Comment 19": (
        "manuscript\\_marked.pdf: Page 32, Lines 610--612",
        "manuscript\\_clean.tex: Line 475",
        "manuscript\\_marked.tex: Line 494"
    ),
    "Reviewer 4 --- Comment 20": (
        "manuscript\\_marked.pdf: Page 33, Lines 634--639",
        "manuscript\\_clean.tex: Line 491",
        "manuscript\\_marked.tex: Line 510"
    ),

    "Reviewer 5 --- Comment 1": (
        "manuscript\\_marked.pdf: Page 15, Lines 308--314",
        "manuscript\\_clean.tex: Line 351",
        "manuscript\\_marked.tex: Line 370"
    ),
    "Reviewer 5 --- Comment 2": (
        "manuscript\\_marked.pdf: Pages 15--16, Lines 315--324",
        "manuscript\\_clean.tex: Line 355",
        "manuscript\\_marked.tex: Line 374"
    ),
    "Reviewer 5 --- Comment 3": (
        "manuscript\\_marked.pdf: Page 16, Lines 331--335",
        "manuscript\\_clean.tex: Line 361",
        "manuscript\\_marked.tex: Line 380"
    ),
    "Reviewer 5 --- Comment 4": (
        "manuscript\\_marked.pdf: Page 17, Lines 353--359",
        "manuscript\\_clean.tex: Line 372",
        "manuscript\\_marked.tex: Line 391"
    ),
    "Reviewer 5 --- Comment 5": (
        "manuscript\\_marked.pdf: Pages 20--21, Lines 402--412",
        "manuscript\\_clean.tex: Line 393",
        "manuscript\\_marked.tex: Line 412"
    )
}

lines = text.splitlines()
new_lines = []
cur_comment = None

for line in lines:
    if "\\begin{reviewercomment}" in line:
        m = re.search(r"\\begin\{reviewercomment\}\[(.*?)\]", line)
        if m:
            cur_comment = m.group(1).strip()
        new_lines.append(line)
    elif "\\manuscriptchange{" in line and cur_comment in locations:
        pdf_loc, cl_loc, ml_loc = locations[cur_comment]
        tag = f"\\textbf{{[Location: \\textit{{{pdf_loc}}} \\textbar\\ \\textit{{{cl_loc}}} \\textbar\\ \\textit{{{ml_loc}}}]}}\\\\ "
        new_line = line.replace("\\manuscriptchange{", f"\\manuscriptchange{{{tag}")
        new_lines.append(new_line)
    else:
        new_lines.append(line)

new_text = "\n".join(new_lines)
with open("Response_letter_clean.tex", "w") as f:
    f.write(new_text)

print("Updated Response_letter_clean.tex with all cleanly escaped location tags.")
