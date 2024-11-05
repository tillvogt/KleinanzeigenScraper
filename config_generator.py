import streamlit as st
import json
import pandas as pd


st.title("Webscrape Configurator")

with open("traced_objects.json", "r") as file:
    config = pd.DataFrame(json.load(file))
    
st.write("Actual Config Entries:")
st.table(config)

st.write("Delete Entry:")
delete_entry = st.selectbox("Select Entry to delete", config["name"])
confirm = st.checkbox("I confirm that I want to delete this entry")
delete_button = st.button("Delete Entry", disabled=not confirm)

if delete_button and confirm:
    config = config[config["name"] != delete_entry]
    
    with open("traced_objects.json", "w") as file:
        json.dump(config.to_dict('records'), file, indent=2)
    
    st.success(f"Entry '{delete_entry}' deleted successfully!")
    st.rerun()

st.write("Add new entry:")
name = st.text_input("Name")
url = st.text_input("URL")
checks_per_day = int(st.number_input("Checks per day", min_value=1, max_value=24))
kfz = bool(st.checkbox("Kfz"))
blacklist = list(str(st.text_area("Blacklist (use comma as seperator)")).split(","))

add_button = st.button("Add Entry")

if add_button:
    new_entry = pd.DataFrame([{"name": name, "url": url, "checks_per_day": checks_per_day, "kfz": kfz, "blacklist": blacklist}])
    st.write(new_entry)
    config = pd.concat([config, new_entry], axis=0, ignore_index=True)
    st.table(config)
    with open("traced_objects.json", "w") as file:
        json.dump(config.reset_index().to_dict(orient="records"), file)
    st.rerun()