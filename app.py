import streamlit as st
import json
import tempfile
from pdf_parser import pdf_to_json

st.set_page_config(page_title="PDF Viewer", layout="wide")
st.title("Simple PDF Content Viewer")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    # Save  file to a temp file 
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        pdf_path = tmp_file.name

    with st.spinner("Parsing PDF... This may take a while. Please be patient."):
        parsed_data = pdf_to_json(pdf_path, out_dir="Images")

    if parsed_data:
        st.success("PDF Parsed Successfully!")

        json_data = json.dumps(parsed_data, indent=4)
        st.download_button(
            label="Download Parsed JSON",
            data=json_data,
            file_name="parsed_pdf.json",
            mime="application/json"
        )

        pages = [p["page_number"] for p in parsed_data]
        page_num = st.selectbox("Select Page", pages)

        page_data = next((p for p in parsed_data if p["page_number"] == page_num), None)

        if page_data:
            st.subheader(f"Page {page_num}")

            # img_width = st.slider("Image Width", min_value=200, max_value=800, value=400, step=50)

            for item in page_data["content"]:
                if item["type"] == "heading":
                    st.markdown(f"**Heading:** {item['text']}")
                elif item["type"] == "paragraph":
                    # st.markdown(f"**Paragraph:** {item['text']}")
                    st.markdown(f"**Paragraph:** ")
                    for line in item['text'].splitlines():
                        st.write(line)
                elif item["type"] == "table":
                    st.write("**Table:**")
                    st.table(item["table_data"])
                elif item["type"] == "image":
                    st.write("**Image:**")
                    st.image(item["path"], caption=f"Image (Page {page_num})", width=img_width)

        else:
            st.warning("No content detected for this page.")
    else:
        st.error("Failed to parse PDF or no content found.")
