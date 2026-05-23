import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import re
import cv2
import numpy as np
import easyocr


# Tesseract path for Streamlit Cloud
reader = easyocr.Reader(['en'])
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.title("📄 Invoice Data Extractor")

uploaded_file = st.file_uploader("Upload Invoice Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Invoice", use_column_width=True)

    if st.button("Extract Data"):
        img = np.array(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # text = pytesseract.image_to_string(thresh)
        results = reader.readtext(thresh, detail=0)
        text = " ".join(results)
        st.subheader("Extracted Text")
        st.text(text)

        invoice_no = re.search(r"(Invoice\s*No[:\-]?\s*)(\w+)", text, re.IGNORECASE)
        date = re.search(r"(Date[:\-]?\s*)([\d\-\/]+)", text, re.IGNORECASE)
        total = re.search(r"(Total[:\-]?\s*)(\d+)", text, re.IGNORECASE)
        gst = re.search(r"(GST[:\-]?\s*)(\d+%?)", text, re.IGNORECASE)

        data = {
            "Invoice No": invoice_no.group(2) if invoice_no else "",
            "Date": date.group(2) if date else "",
            "Total": total.group(2) if total else "",
            "GST": gst.group(2) if gst else ""
        }

        df = pd.DataFrame([data])

        st.subheader("Extracted Data")
        st.dataframe(df)

        excel_file = "output.xlsx"
        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as f:
            st.download_button("Download Excel", f, file_name="invoice_data.xlsx")
