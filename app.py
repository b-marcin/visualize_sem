import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
import re
import pandas as pd
import matplotlib.pyplot as plt
import rpy2.robjects as ro  # Interface for running R scripts

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with fitz.open(pdf_file) as doc:
        text = "\n".join([page.get_text("text") for page in doc])
    return text

# Function to extract fit indices
def extract_fit_indices(text):
    indices = {
        "CFI": None, "TLI": None, "NNFI": None, "NFI": None, "PNFI": None,
        "RFI": None, "IFI": None, "RNI": None, "RMSEA": None, "SRMR": None,
        "GFI": None, "MFI": None, "ECVI": None
    }
    for key in indices.keys():
        pattern = rf"{key}.*?([\d\.Ee\-]+)"
        match = re.search(pattern, text)
        if match:
            try:
                indices[key] = float(match.group(1))
            except ValueError:
                indices[key] = None
    return indices

# Function to generate SEM path diagram using R (lavaan + semPlot)
def generate_sem_path_diagram():
    r_script = """
    library(lavaan)
    library(semPlot)

    # Load SEM model (this should be adapted based on your data)
    model <- '
      CM  =~ DIDS_1 + DIDS_2 + DIDS_3 + DIDS_4 + DIDS_5
      EiB =~ DIDS_6 + DIDS_7 + DIDS_8 + DIDS_9 + DIDS_10
      RE  =~ DIDS_11 + DIDS_12 + DIDS_13 + DIDS_14 + DIDS_15
      IwC =~ DIDS_16 + DIDS_17 + DIDS_18 + DIDS_19 + DIDS_20
      EiD =~ DIDS_21 + DIDS_22 + DIDS_23 + DIDS_24 + DIDS_25
    '

    fit <- cfa(model, sample.cov = matrix(runif(25), 5, 5), sample.nobs = 200)
    
    # Save path diagram
    png("sem_diagram.png", width = 800, height = 600)
    semPaths(fit, what = "std", edge.label.cex = 1.2, layout = "tree")
    dev.off()
    """
    
    # Run R script
    ro.r(r_script)

st.title("Structural Equation Modeling (SEM) Results Visualization")

st.markdown("""
### Upload Your SEM Results (PDF)
This app extracts fit indices from your SEM analysis results and generates **visualizations**, including a **bar chart of fit indices** and an **SEM path diagram** (using R's lavaan + semPlot).
""")

uploaded_file = st.file_uploader("Upload a PDF containing SEM results", type=["pdf"])

if uploaded_file:
    # Extract text from PDF
    file_text = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Text Preview")
    st.text(file_text[:2000])  # Show a preview of the extracted text

    # Extract fit indices
    fit_indices = extract_fit_indices(file_text)
    
    # Convert to DataFrame
    fit_df = pd.DataFrame(list(fit_indices.items()), columns=["Index", "Value"])
    st.subheader("Extracted Fit Indices")
    st.write(fit_df)

    # Remove None values for visualization
    fit_indices_filtered = {k: v for k, v in fit_indices.items() if v is not None}
    
    if fit_indices_filtered:
        st.subheader("Fit Indices Bar Chart")
        fig, ax = plt.subplots()
        ax.bar(fit_indices_filtered.keys(), fit_indices_filtered.values(), color="skyblue")
        ax.set_ylabel("Value")
        ax.set_title("SEM Fit Indices")
        st.pyplot(fig)
    else:
        st.warning("No fit indices were found in the PDF. Please check the formatting.")

    # Generate SEM Path Diagram
    st.subheader("Generate SEM Path Diagram")
    if st.button("Create Diagram"):
        generate_sem_path_diagram()
        st.image("sem_diagram.png", caption="SEM Path Diagram")

st.markdown("**Tip:** Ensure that the uploaded PDF contains numerical fit indices in text format (not as images).")
