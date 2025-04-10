import streamlit as st
import requests
import pandas as pd
from config import *

# Load SHL catalog CSV (detailed data for fallback display)
catalog_df = pd.read_csv(PATH_TESTS_INFO)

st.title("🔍 Assessment Recommender")
query = st.text_area("Enter job description / profile / LinkedIn Job link :")

if st.button("Get Recommendations"):
    with st.spinner("Getting predictions..."):
        if query.strip() != "":
            response = requests.post(BACKEND_RECOMMEND, json={"query": query})

            if response.status_code == 200:
                try:
                    results = response.json()["recommended_assessments"]

                    st.success("✅ Recommendations generated:")
                    mapped_rows = []

                    for assessment in results:
                        mapped_rows.append({
                            "Assessment Name": f"[{assessment['name']}]({assessment['url']})",
                            "Description": assessment['description'],
                            "Test Type": ", ".join(assessment["test_type"]),
                            "Remote Testing Support": assessment["remote_support"],
                            "Adaptive/IRT Support": assessment["adaptive_support"],
                            "Assessment Length": assessment["duration"]
                        })

                    df = pd.DataFrame(mapped_rows)
                    df.index = range(1, len(df) + 1)
                    df.index.name = "S.No."

                    st.write(df.to_markdown(index=True), unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Error parsing or displaying response: {e}")
            else:
                st.error("❌ Failed to fetch recommendations from the backend.")
        else:
            st.error("❌ No Description Found!!!")
