import streamlit as st
import fitz
import re

def extract_text_ordered(uploaded_file):
    # 파일 포인터를 처음으로 되돌림
    uploaded_file.seek(0)
    # 바이트 데이터를 직접 전달
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_result = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        text_blocks = []
        
        for b in blocks:
            if "lines" in b:
                x0, y0 = b["bbox"][:2]
                text = ""
                for line in b["lines"]:
                    for span in line["spans"]:
                        text += span["text"]
                # 텍스트가 비어있지 않은 경우만 추가
                if text.strip():
                    text_blocks.append({'x': x0, 'y': y0, 'text': text})
        
        # [정렬 개선] x좌표(큰 값부터)를 10 단위로 묶어 정렬 (오차 보정)
        text_blocks.sort(key=lambda b: (-round(b['x'] / 10), b['y']))
        
        # 문단 구성: 텍스트를 하나로 합침
        page_text = "".join([b['text'] for b in text_blocks])
        
        # 정제 작업 (숫자 제거 및 줄바꿈)
        page_text = re.sub(r'\d+', '', page_text)
        page_text = re.sub(r'([.!?♡。…？♪])\s*', r'\1\n', page_text)
        
        full_result.append(page_text)
        
    return "\n\n".join(full_result)

st.title("📄 일본어 세로 쓰기 PDF 변환기")
uploaded_file = st.file_uploader("PDF 업로드", type="pdf")

if uploaded_file is not None:
    if st.button("문단 유지하여 변환"):
        try:
            with st.spinner("처리 중..."):
                result = extract_text_ordered(uploaded_file)
                st.download_button("텍스트 파일 다운로드", result, "result.txt")
                st.text_area("미리보기", result, height=300)
        except Exception as e:
            st.error(f"오류 발생: {e}")
