import streamlit as st
import time
import base64
import pandas as pd
from io import BytesIO
from abbyy_document_ai import DocumentAi
from abbyy_document_ai.models import (
    BeginReceiptFieldExtractionRequestBody,
    BeginHotelInvoiceFieldExtractionRequestBody,
    BeginUtilityBillFieldExtractionRequestBody
)

st.set_page_config(page_title="Smart Expense Assistant", layout="wide")

# --- Logo ---
def load_image_base64(img_path):
    from PIL import Image
    img = Image.open(img_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    return img_b64

img_b64 = load_image_base64("abbyy-logo.png")
st.sidebar.markdown(
    f"""
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{img_b64}' width='140'/>
        <h4 style='color: #d32f2f;'>Powered by ABBYY Document AI</h4>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Session State Init ---
if "docs" not in st.session_state:
    st.session_state.docs = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "form_key" not in st.session_state:
    st.session_state.form_key = 0
if "processed" not in st.session_state:
    st.session_state.processed = False
if "results" not in st.session_state:
    st.session_state.results = []

# --- Sidebar Configuration ---
st.sidebar.header("🔐 Enter Your API Key")
st.session_state.api_key = st.sidebar.text_input(
    "API Key",
    type="password",
    help="Paste your ABBYY Document AI API key here."
)

st.sidebar.markdown("""
---
📘 **How to Use**

1. Upload your expense receipts, invoices, or bills.
2. Choose the document type and add a comment.
3. Add multiple files as needed.
4. Click **Analyze Expenses** to extract key data.
5. Download reports individually or as a summary.
6. Use **Start New Request** to reset.
""")

# --- Upload Form ---
if not st.session_state.processed:
    st.subheader("📤 Easily Submit Receipts and Bills for Expense Reimbursement")
    with st.form(key=f"doc_form_{st.session_state.form_key}", clear_on_submit=True):
        cols = st.columns([3, 2, 3])
        uploaded_file = cols[0].file_uploader(
            "Upload Document",
            type=["pdf", "jpg", "jpeg", "png"],
            help="Upload a receipt, hotel invoice, or utility bill."
        )
        doc_type = cols[1].selectbox(
            "Document Type",
            ["Receipt", "Hotel Invoice", "Utility Bill"],
            help="Select the type of expense document."
        )
        comment = cols[2].text_input(
            "Comments (Optional)",
            help="Add a comment related to this document."
        )
        submitted = st.form_submit_button("➕ Submit Expense")
        if submitted and uploaded_file:
            st.session_state.docs.append({
                "file": uploaded_file,
                "type": doc_type,
                "comment": comment,
                "status": "⏳ Waiting"
            })
            st.session_state.form_key += 1
            st.rerun()
else:
    st.warning("📁 Upload disabled. Click 'Start New Request' to begin again.")

# --- Display and Process Documents ---
if st.session_state.docs:
    st.markdown("### 🗂️ Expenses You've Added")
    for i, doc in enumerate(st.session_state.docs):
        col1, col2 = st.columns([10, 1])
        with col1:
            status_icon = "✅" if doc.get("status") == "✅ Done" else doc.get("status", "⏳")
            st.markdown(f"{status_icon} **{i+1}. {doc['file'].name}** – _{doc['type']}_")
            if doc['comment']:
                st.markdown(f"💬 _{doc['comment']}_")
        with col2:
            if st.button("❌", key=f"remove_{i}"):
                st.session_state.docs.pop(i)
                st.rerun()

    if st.button("🚀 Analyze Expenses"):
        st.session_state.results = []
        with st.spinner("Processing your expense documents..."):
            for i, doc in enumerate(st.session_state.docs):
                try:
                    file_bytes = doc["file"].read()
                    encoded = base64.b64encode(file_bytes).decode("utf-8")
                    input_source = {"base64EncodedContent": encoded, "name": doc["file"].name}

                    with DocumentAi(api_key_auth=st.session_state.api_key) as document_ai:
                        if doc["type"] == "Receipt":
                            req = BeginReceiptFieldExtractionRequestBody(inputSource=input_source)
                            res = document_ai.models.receipt.begin_field_extraction(request=req)
                            doc_id = res.documents[0].id
                            while True:
                                time.sleep(3)
                                res = document_ai.models.receipt.get_extracted_fields(document_id=doc_id)
                                if res.receipt.meta.status == "Processed":
                                    f = res.receipt.fields
                                    st.session_state.results.append({
                                        "File Name": doc["file"].name,
                                        "Document Type": doc["type"],
                                        "Vendor / Source": getattr(f, "vendor", "-"),
                                        "Total Amount": getattr(f, "total", "-"),
                                        "Currency": getattr(f, "currency", "-"),
                                        "Comment": doc["comment"]
                                    })
                                    df_line = pd.DataFrame([{
                                        "Description": i.description,
                                        "Quantity": i.quantity,
                                        "Unit Price": i.price,
                                        "Amount": i.amount
                                    } for i in f.line_items])
                                    st.download_button(f"⬇ Download {doc['type']} Line Items – {doc['file'].name}", df_line.to_csv(index=False), file_name=f"{doc['file'].name}_lines.csv")
                                    break

                        elif doc["type"] == "Hotel Invoice":
                            req = BeginHotelInvoiceFieldExtractionRequestBody(inputSource=input_source)
                            res = document_ai.models.hotel_invoice.begin_field_extraction(request=req)
                            doc_id = res.documents[0].id
                            while True:
                                time.sleep(3)
                                res = document_ai.models.hotel_invoice.get_extracted_fields(document_id=doc_id)
                                if res.hotel_invoice.meta.status == "Processed":
                                    f = res.hotel_invoice.fields
                                    st.session_state.results.append({
                                        "File Name": doc["file"].name,
                                        "Document Type": doc["type"],
                                        "Vendor / Source": getattr(f, "hotel_name", "-"),
                                        "Total Amount": getattr(f, "total", "-"),
                                        "Currency": getattr(f, "currency", "-"),
                                        "Comment": doc["comment"]
                                    })
                                    df_line = pd.DataFrame([{
                                        "Description": i.description,
                                        "Quantity": i.quantity,
                                        "Unit Price": i.price,
                                        "Amount": i.amount
                                    } for i in f.line_items])
                                    st.download_button(f"⬇ Download {doc['type']} Line Items – {doc['file'].name}", df_line.to_csv(index=False), file_name=f"{doc['file'].name}_lines.csv")
                                    break

                        elif doc["type"] == "Utility Bill":
                            req = BeginUtilityBillFieldExtractionRequestBody(inputSource=input_source)
                            res = document_ai.models.utility_bill.begin_field_extraction(request=req)
                            doc_id = res.documents[0].id
                            while True:
                                time.sleep(3)
                                res = document_ai.models.utility_bill.get_extracted_fields(document_id=doc_id)
                                if res.utility_bill.meta.status == "Processed":
                                    f = res.utility_bill.fields
                                    st.session_state.results.append({
                                        "File Name": doc["file"].name,
                                        "Document Type": doc["type"],
                                        "Vendor / Source": getattr(f, "bill_number", "-"),
                                        "Total Amount": getattr(f, "amount_due", "-"),
                                        "Currency": getattr(f, "currency", "-"),
                                        "Comment": doc["comment"]
                                    })
                                    break
                    st.session_state.docs[i]["status"] = "✅ Done"
                except Exception as e:
                    st.session_state.docs[i]["status"] = "❌ Error"
                    st.warning(f"⚠️ Could not process {doc['file'].name}: {str(e)}")

        st.session_state.processed = True

if st.session_state.processed and st.session_state.results:
    tab1, tab2 = st.tabs(["📊 Summary Report", "🧾 Line Items & Comments"])

    with tab1:
        df_summary = pd.DataFrame(st.session_state.results)
        st.dataframe(df_summary)
        st.download_button("⬇ Download Summary Report", df_summary.to_csv(index=False), file_name="summary_all_documents.csv")

    with tab2:
        for doc in st.session_state.docs:
            st.markdown(f"**{doc['file'].name}** – _{doc['type']}_")
            st.markdown(f"💬 Comment: _{doc['comment']}_")

    if st.button("🔁 Start New Request"):
        st.session_state.docs = []
        st.session_state.results = []
        st.session_state.form_key = 0
        st.session_state.processed = False
        st.rerun()

elif not st.session_state.docs:
    st.info("Begin by uploading your first expense document above.")
