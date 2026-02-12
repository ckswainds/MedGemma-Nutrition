# Medical Guidelines Reference

Updated list of medical guideline documents organized and renamed for easy access:

## 📚 Available Guidelines

| # | File Name | Purpose |
|---|-----------|---------|
| 1 | `01_Anemia_Guidelines.pdf` | Anemia management and nutritional strategies |
| 2 | `02_PCOS_Management_Guidelines.pdf` | PCOS (Polycystic Ovary Syndrome) management guidelines |
| 3 | `03_Diabetes_Guidelines.pdf` | Type 2 Diabetes nutrition and management |
| 4 | `04_ESI_Clinical_Practice_Guidelines.pdf` | ESI clinical practice standards |
| 5 | `05_Hypertension_Guidelines.pdf` | Hypertension (High BP) management guidelines |
| 6 | `06_ICMR_NIN_Dietary_Guidelines_2024.pdf` | Indian dietary guidelines by ICMR and NIN 2024 |
| 7 | `07_Intravenous_Iron_Guidelines_Pregnancy.pdf` | IV Iron guidelines for pregnant and lactating women |

## 🔍 How These Are Used

These PDFs are used by the **RAG (Retrieval-Augmented Generation) Engine** to provide evidence-based nutrition recommendations. When a patient asks a nutrition question, the AI searches through these guidelines to find relevant clinical information.

## 📝 Adding New Guidelines

To add new medical guidelines:
1. Place PDF files in this directory
2. Name them with a numeric prefix (e.g., `08_YourGuideline_Name.pdf`)
3. The system will automatically index them on next startup
4. Restart the Streamlit app for changes to take effect

## ✅ Current Status

- **Total Guidelines:** 7 documents
- **Last Updated:** February 12, 2026
- **System:** Ready for RAG indexing
