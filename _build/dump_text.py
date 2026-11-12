import sys
from docx import Document

doc = Document(sys.argv[1])
key = sys.argv[2]
paras = [p.text for p in doc.paragraphs]
for i, t in enumerate(paras):
    if key in t:
        for j in range(i, min(i + int(sys.argv[3]), len(paras))):
            if paras[j].strip():
                print(j, paras[j])
        print("-----")
