import streamlit as st
import requests
import pandas as pd
from config import *

# Load SHL catalog CSV (your detailed data)
catalog_df = pd.read_csv(PATH_TESTS_INFO)

st.title("🔍 Assessment Recommender")
query = st.text_area("Enter job description / profile / LinkedIn Job link :")

if st.button("Get Recommendations"):
    with st.spinner("Getting predictions..."):
        if(query != ""):
            response = requests.post(BACKEND_RECOMMEND, json={"description": query})

            if response.status_code == 200:
                try:
                    raw_json = response.json()["recommended_assessments"]
                    raw_json = raw_json.replace("```json", "").replace("```", "").strip()
                    parsed = eval(raw_json)

                    # Group similar sets
                    grouped = {}
                    for item in parsed:
                        exam_names = tuple(item["Exam Name"])
                        durations = item["Duration"]
                        grouped.setdefault(exam_names, []).append(durations)

                    st.success("✅ Recommendations generated:")

                    for idx, (exam_set, duration_lists) in enumerate(grouped.items(), start=1):
                        st.markdown(f"### 📘 Exam Set {idx}:")
                        flat_durations = [d for sublist in duration_lists for d in sublist]

                        mapped_rows = []
                        for i, exam in enumerate(exam_set):
                            match = catalog_df[catalog_df["Assessment Name"].str.lower() == exam.lower()]
                            if not match.empty:
                                row = match.iloc[0][RECOMMENDATION_FIELDS].to_dict()
                                # Make name clickable
                                row['Assessment Length'] = flat_durations[i] if i < len(flat_durations) else "Unknown"
                                row["Assessment Name"] = f"[{row['Assessment Name']}]({row['URL']})"
                                mapped_rows.append(row)
                            else:
                                url = BASE_COURSE_URL
                                name_link = f"[{exam}]({url})"
                                mapped_rows.append({
                                    "Assessment Name": name_link,
                                    "Test Type": "Unknown",
                                    "Remote Testing Support": "Unknown",
                                    "Adaptive/IRT Support": "Unknown",
                                    "Assessment Length": flat_durations[i] if i < len(flat_durations) else "Unknown",
                                    "URL": url
                                })

                        df = pd.DataFrame(mapped_rows)
                        df.drop(columns=["URL"], inplace=True)  # Remove raw URL column
                        df.index = range(1, len(df) + 1)
                        df.index.name = "S.No."

                        st.write(df.to_markdown(index=True), unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Error parsing or displaying response: {e}")
            else:
                st.error("❌ Failed to fetch recommendations from the backend.")

        else:
            st.error("❌ No Description Found!!!")