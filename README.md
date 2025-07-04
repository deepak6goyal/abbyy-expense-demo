# abbyy-expense-demo
Streamlit demo for extracting procurement and expense data using ABBYY Document AI API. Supports Receipts, Hotel Invoices, and Utility Bills with CSV exports and customizable UI.
# 🧾 Procurement & Expense Document Extractor  
**Powered by ABBYY Document AI API**

This is a ready-to-demo Streamlit web app that extracts structured data from Receipts, Hotel Invoices, and Utility Bills — all using ABBYY's Document AI API. The tool is ideal for procurement teams, finance automation prototypes, and internal innovation showcases.

---

## 🔍 What It Does

- Upload one or multiple documents of different types (Receipt, Hotel Invoice, Utility Bill)
- Extract key fields like vendor, total, currency, tax, line items, etc.
- Add comments per document
- View processed results in a user-friendly table
- Export:
  - Line Items as CSV (per document)
  - Summary CSV (all documents with type and comments)

---

## 📁 Supported Document Types

- **Receipts** (multi-line items, payment info, vendor info)
- **Hotel Invoices** (itemized charges, taxes, total)
- **Utility Bills** (billing period, amount due, charges, penalties)

---
## Set Up Python Environment
pip install -r requirements.txt

**##Run the App Locally**

streamlit run app.py
🔐 You will be asked to enter your ABBYY Document AI API key in the app interface. It is stored securely only for the session.

**Customization Ideas**

Add more document types supported by ABBYY Document AI API

Integrate into procurement or AP workflows

Connect with external systems like Google Sheets, SAP, or ERPs

Add email export or storage integration (e.g. SharePoint, S3)
