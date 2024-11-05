import streamlit as st

# pg = st.navigation([st.Page("visualizer.py"), st.Page("config_generator.py")])
pg = st.navigation([st.Page("visualizer.py", title="Visualize Data"), st.Page("config_generator.py", title="Gernerate Config Data")])
pg.run()