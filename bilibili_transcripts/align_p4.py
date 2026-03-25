import re
import os

def clean_text(text):
    return set(re.findall(r'[\u4e00-\u9fff]', text))

# Read OCR
with open("all_slides_ocr.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()[1289:]

slides = []
curr_slide = None
curr_text = []

for line in lines:
    m = re.match(r'^---\s*Slide\s+(\d+)\s*---', line)
    if m:
        if curr_slide is not None:
            slides.append((curr_slide, "".join(curr_text)))
        curr_slide = int(m.group(1))
        curr_text = []
    else:
        curr_text.append(line)
if curr_slide is not None:
    slides.append((curr_slide, "".join(curr_text)))

print(f"Total slides found for P4: {len(slides)}")

# Read Transcript
with open("bilibili_audio/p4_large.txt", "r", encoding="utf-8") as f:
    transcript_lines = [l.strip() for l in f if l.strip()]

CHUNKS = []
CHUNK_SIZE = 5
for i in range(0, len(transcript_lines), CHUNK_SIZE):
    chunk_text = " ".join(transcript_lines[i:i+CHUNK_SIZE])
    CHUNKS.append(chunk_text)

print(f"Total transcript chunks: {len(CHUNKS)}")

def extract_links(text):
    return re.findall(r'https?://[^\s\)]+', text)

# Compute similarity matrix
# sim[i][j] = score for slide i and chunk j
sim = []
for i, (sid, stext) in enumerate(slides):
    s_chars = clean_text(stext)
    row = []
    for j, ctext in enumerate(CHUNKS):
        c_chars = clean_text(ctext)
        score = len(s_chars.intersection(c_chars))
        row.append(score)
    sim.append(row)

# dp[i][j] = max score for aligning first i slides up to chunk j
# parent[i][j] = best k (k <= j)
dp = [[0]*len(CHUNKS) for _ in range(len(slides))]
parent = [[0]*len(CHUNKS) for _ in range(len(slides))]

for j in range(len(CHUNKS)):
    dp[0][j] = sim[0][j]
    if j > 0 and dp[0][j-1] > dp[0][j]:
        dp[0][j] = dp[0][j-1]

for i in range(1, len(slides)):
    max_k = 0
    max_val = -1
    for j in range(len(CHUNKS)):
        # Can we align slide i to chunk j?
        # If we do, we could have aligned slide i-1 to any k <= j.
        # Wait, if we force slide i to j: score is sim[i][j] + max(dp[i-1][k]) for k <= j
        # Oh wait, dp[i-1][j] is exactly max(score of previous up to j).
        
        # We need the maximum of (dp[i-1][k]) for k <= j
        best_prev = -1
        best_prev_idx = -1
        for k in range(j+1):
            if dp[i-1][k] > best_prev:
                best_prev = dp[i-1][k]
                best_prev_idx = k
        
        current_score = best_prev + sim[i][j]
        dp[i][j] = current_score
        parent[i][j] = best_prev_idx

# Backtrack
assignments = [0] * len(slides)
best_j = 0
max_final = -1
for j in range(len(CHUNKS)):
    if dp[-1][j] > max_final:
        max_final = dp[-1][j]
        best_j = j

for i in range(len(slides)-1, -1, -1):
    assignments[i] = best_j
    if i > 0:
        best_j = parent[i][best_j]

print("Alignment done.")

with open("p4_pdf/p4_full_transcript_with_slides.md", "w", encoding="utf-8") as f:
    f.write("# 第四集 Context Engineering (全内容对比版)\n\n")
    f.write("> 自动生成的带全部图片的逐字稿对应文档。如果图片有外部链接，也会一并提取。\n\n")
    
    chunk_to_slides = {}
    for i, j in enumerate(assignments):
        chunk_to_slides.setdefault(j, []).append(i)
    
    for j, ctext in enumerate(CHUNKS):
        if j in chunk_to_slides:
            for s_idx in chunk_to_slides[j]:
                sid = slides[s_idx][0]
                stext = slides[s_idx][1]
                links = extract_links(stext)
                
                slide_filename = f"slide_{sid:04d}.jpg"
                f.write(f"\n![Slide {sid}](../../bilibili_video/slides_p4/{slide_filename})\n")
                if links:
                    f.write("\n**幻灯片引用链接:**\n")
                    for link in links:
                        link = re.sub(r'[\)\]\},]+$', '', link)
                        f.write(f"- [{link}]({link})\n")
                f.write("\n")
                
        f.write(ctext + "\n\n")

print("Output written to p4_pdf/p4_full_transcript_with_slides.md")
