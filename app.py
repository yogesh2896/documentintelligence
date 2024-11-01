

import streamlit as st
import pandas as pd
import pdfplumber
import requests
import os

# Azure OpenAI API configuration
api_key = "3db3696541524407bdbbba4879d9d24e"
endpoint = "https://azureocrllmtesting.openai.azure.com/openai/deployments/TESTOCRLLMDeployGPT35/chat/completions?api-version=2024-08-01-preview"

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    extracted_text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                text = page.extract_text(x_tolerance=3, y_tolerance=3, layout=True, keep_blank_chars=True)
                tables = page.extract_tables()

                extracted_text += f"--- Page {page_number + 1} ---\n"
                if text:
                    extracted_text += text + "\n"
                else:
                    extracted_text += "[No text found]\n"

                if tables:
                    extracted_text += "\n--- Extracted Tables ---\n"
                    for table in tables:
                        for row in table:
                            extracted_text += " | ".join([cell if cell else '' for cell in row]) + "\n"

                extracted_text += "\n\n"

        return extracted_text

    except Exception as e:
        print(f"Error processing the PDF: {e}")
        return None

# Function to ask the 100 questions using Azure OpenAI
def ask_questions_from_text(extracted_text):
    prompt = f"""
    Based on the provided PDF text, please answer the following questions:

        1. Can you assess the impact of changes in the borrower's credit rating on their access to capital and borrowing costs?
        2. Can you assess the impact of covenant compliance on the borrower's cost of borrowing?
        3. Can you assess the impact of covenant compliance on the borrower's financial planning and risk management strategies?
        4. Can you assess the impact of late payments on the borrower's credit score and credit rating?
        5. Can you assess the impact of lender confidence on the borrower's overall creditworthiness and market reputation?
        6. Can you assess the impact of recent credit inquiries on the borrower's credit score?
        7. Can you assess the impact of revenue fluctuations on the borrower's operating cash flow?
        8. Can you assess the impact of the borrower's capital expenditure decisions on their future cash flow?
        9. Can you assess the liquidity of the borrower's investment portfolio?
        10. Can you assess the proportion of the borrower's total debt that is long-term versus short-term?
        11. Can you assess the relationship between the borrower's capital expenditures and their free cash flow?
        12. Can you assess the relationship between the borrower's cash flow generation and their debt maturity schedule?
        13. Can you assess the relationship between the borrower's cash-based dividend payout ratio and their free cash flow?
        14. Can you assess the return on investment (ROI) for the borrower's R&D expenditures?
        15. Can you assess the risks associated with the borrower's dependence on a limited number of suppliers for key inputs?
        16. Can you assess the sensitivity of the borrower's cash flow to changes in interest rates?
        17. Can you assess the sustainability of the borrower's financing cash flows in light of their current financial position?
        18. Can you assess the sustainability of the borrower's net cash flow from operations?
        19. Can you break down the borrower's accounts receivable by aging categories (e.g., 30, 60, 90 days)?
        20. Can you break down the borrower's return on assets (ROA) and compare it to similar companies in the industry?
        21. Can you break down the borrower's revenue by geographic region and identify which regions contribute the most to total revenue?
        22. Can you break down the borrower's SG&A expenses into fixed and variable components?
        23. Can you calculate the borrower's cash flow margin (Operating Cash Flow/Revenue) over the past five years?
        24. Can you calculate the borrower's cash return on assets (CROA) (Operating Cash Flow/Total Assets) over the past five years?
        25. Can you calculate the borrower's cash-based dividend payout ratio (Dividends Paid/Operating Cash Flow) over the past five years?
        26. Can you calculate the borrower's free cash flow (operating cash flow minus capital expenditures) over the past five years?
        27. Can you calculate the borrower's gross profit margin (Gross Profit/Revenue) over the past five years?
        28. Can you calculate the borrower's operating cash flow ratio (Operating Cash Flow/Current Liabilities) over the past five years?
        29. Can you calculate the borrower's operating profit margin (Operating Income/Revenue) over the past five years?
        30. Can you compare the borrower's gross profit margin to industry averages and key competitors?
        31. Can you compare the borrower's gross profit margin to that of key competitors in the same industry?
        32. Can you conduct a scenario analysis to project the borrower's cash flow under different economic conditions?
        33. Can you evaluate the borrower's ability to maintain strong coverage ratios under different economic scenarios?
        34. Can you evaluate the borrower's debt-to-EBITDA ratio in the context of their ability to generate earnings for debt repayment?

    Here is the extracted text:
    {extracted_text}
    """

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800  # Adjust max_tokens based on expected answer length
    }

    response = requests.post(endpoint, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Streamlit app
st.title("Document Analyzer")
# st.set_page_config(page_title="PDF Data Extractor", page_icon=":page_facing_up:", layout="wide")

# Custom CSS for styling


# logo = fetch_logo(company_logo_url)
# st.image(logo, width=80, caption="", use_column_width=False)

# Title under the logo

# Function to fetch the logo

# company_logo_url = "https://enoahisolution.com/wp-content/themes/enoah-new/images/newimages/enoah-logo-fixed.png"  # Replace with actual logo URL

# def fetch_logo(logo_url):
#     with urllib.request.urlopen(logo_url) as response:
#         logo_image = Image.open(response)
#     return logo_image
# st.markdown('<div class="header-box">DOcument Intelligence</div>', unsafe_allow_html=True)




uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with open("uploaded_pdf.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    extracted_text = extract_text_from_pdf("uploaded_pdf.pdf")

    if extracted_text:
        answers = ask_questions_from_text(extracted_text)
        if answers:
            statements = [statement.strip() for statement in answers.split("\n") if statement.strip()]
            df = pd.DataFrame({
                "Statement_Number": range(1, len(statements) + 1),
                "Statement": statements
            })
            df = df['Statement']

            questions = [
                "Can you assess the impact of changes in the borrower's credit rating on their access to capital and borrowing costs?",
                "Can you assess the impact of covenant compliance on the borrower's cost of borrowing?",
                "Can you assess the impact of covenant compliance on the borrower's financial planning and risk management strategies?",
                "Can you assess the impact of late payments on the borrower's credit score and credit rating?",
                "Can you assess the impact of lender confidence on the borrower's overall creditworthiness and market reputation?",
                "Can you assess the impact of recent credit inquiries on the borrower's credit score?",
                "Can you assess the impact of revenue fluctuations on the borrower's operating cash flow?",
                "Can you assess the impact of the borrower's capital expenditure decisions on their future cash flow?",
                "Can you assess the liquidity of the borrower's investment portfolio?",
                "Can you assess the proportion of the borrower's total debt that is long-term versus short-term?",
                "Can you assess the relationship between the borrower's capital expenditures and their free cash flow?",
                "Can you assess the relationship between the borrower's cash flow generation and their debt maturity schedule?",
                "Can you assess the relationship between the borrower's cash-based dividend payout ratio and their free cash flow?",
                "Can you assess the return on investment (ROI) for the borrower's R&D expenditures?",
                "Can you assess the risks associated with the borrower's dependence on a limited number of suppliers for key inputs?",
                "Can you assess the sensitivity of the borrower's cash flow to changes in interest rates?",
                "Can you assess the sustainability of the borrower's financing cash flows in light of their current financial position?",
                "Can you assess the sustainability of the borrower's net cash flow from operations?",
                "Can you break down the borrower's accounts receivable by aging categories (e.g., 30, 60, 90 days)?",
                "Can you break down the borrower's return on assets (ROA) and compare it to similar companies in the industry?",
                "Can you break down the borrower's revenue by geographic region and identify which regions contribute the most to total revenue?",
                "Can you break down the borrower's SG&A expenses into fixed and variable components?",
                "Can you calculate the borrower's cash flow margin (Operating Cash Flow/Revenue) over the past five years?",
                "Can you calculate the borrower's cash return on assets (CROA) (Operating Cash Flow/Total Assets) over the past five years?",
                "Can you calculate the borrower's cash-based dividend payout ratio (Dividends Paid/Operating Cash Flow) over the past five years?",
                "Can you calculate the borrower's free cash flow (operating cash flow minus capital expenditures) over the past five years?",
                "Can you calculate the borrower's gross profit margin (Gross Profit/Revenue) over the past five years?",
                "Can you calculate the borrower's operating cash flow ratio (Operating Cash Flow/Current Liabilities) over the past five years?",
                "Can you calculate the borrower's operating profit margin (Operating Income/Revenue) over the past five years?",
                "Can you compare the borrower's gross profit margin to industry averages and key competitors?",
                "Can you compare the borrower's gross profit margin to that of key competitors in the same industry?",
                "Can you conduct a scenario analysis to project the borrower's cash flow under different economic conditions?",
                "Can you evaluate the borrower's ability to maintain strong coverage ratios under different economic scenarios?",
                "Can you evaluate the borrower's debt-to-EBITDA ratio in the context of their ability to generate earnings for debt repayment?"
            ]

            q_df = pd.DataFrame(questions)
            f_df = pd.merge(q_df, df, left_index=True, right_index=True)
            f_df.columns = ['questions', 'output']
            st.dataframe(f_df)
            csv = f_df.to_csv(index=False).encode('utf-8')

# Create a download button
            st.download_button(
            label="Download CSV",
            data=csv,
            file_name='data.csv',
            mime='text/csv')
        else:
            st.write("No answers found.")
    else:
        st.write("No data extracted from the PDF.")
