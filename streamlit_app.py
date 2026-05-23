import streamlit as st
from PIL import Image
import pandas as pd
import re
import cv2
import numpy as np
import easyocr

# Initialize OCR ONCE (important)
reader = easyocr.Reader(['en'], gpu=False)

st.title("📄 Sathya Invoice Automation Tool")

uploaded_files = st.file_uploader(
    "Upload Invoice Images",
    type=["png", "jpg", "jpeg","pdf"],
    accept_multiple_files=True
)

for uploaded_file in uploaded_files:
    images = []

    # Check if PDF
    if uploaded_file.type == "application/pdf":
        pdf_bytes = uploaded_file.read()
        images = convert_from_bytes(pdf_bytes)
    else:
        images = [Image.open(uploaded_file)]

    for i, image in enumerate(images):
        st.image(image, caption=f"{uploaded_file.name} - Page {i+1}", width=300)

        img = np.array(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        results = reader.readtext(thresh, detail=0)
        text = " ".join(results)

        st.subheader(f"Extracted Text - {uploaded_file.name} Page {i+1}")
        st.text(text)

        invoice_no = re.search(r"(Invoice\s*No[:\-]?\s*)(\w+)", text, re.IGNORECASE)
        date = re.search(r"(Date[:\-]?\s*)([\d\-\/]+)", text, re.IGNORECASE)
        total = re.search(r"(Total[:\-]?\s*)(\d+)", text, re.IGNORECASE)
        gst = re.search(r"(GST[:\-]?\s*)(\d+%?)", text, re.IGNORECASE)

        data = {
            "File Name": uploaded_file.name,
            "Page": i+1,
            "Invoice No": invoice_no.group(2) if invoice_no else "Not Found",
            "Date": date.group(2) if date else "Not Found",
            "Total": total.group(2) if total else "Not Found",
            "GST": gst.group(2) if gst else "Not Found"
        }

        all_data.append(data)
        # Create DataFrame
        df = pd.DataFrame(all_data)

        st.subheader("📊 Final Extracted Data")
        st.dataframe(df)

        # Add total summary (NEW FEATURE 🔥)
        try:
            df["Total"] = pd.to_numeric(df["Total"], errors='coerce')
            total_sum = df["Total"].sum()
            st.success(f"💰 Total Amount of All Invoices: ₹{total_sum}")
        except:
            pass

        # Download Excel
        excel_file = "all_invoices.xlsx"
        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as f:
            st.download_button(
                "⬇ Download All Invoices Excel",
                f,
                file_name="all_invoices.xlsx"
            )
