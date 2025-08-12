import streamlit as st
import subprocess
import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

def quick_debug_file(file_path):
    """Run and debug a Python script from a file."""
    try:
        with open(file_path, "r") as f:
            code_string = f.read()

        result = subprocess.run([sys.executable, file_path], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return {
                "status": "success",
                "output": result.stdout,
                "error": None
            }
        else:
            prompt = f"""Fix this Python code:
    

CODE:
{code_string}

ERROR:
{result.stderr}

Provide:
1) What's wrong
2) Fixed code
"""
            ai_response = client.chat.completions.create(
                model="gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2,
                timeout=60
            )
            return {
                "status": "error",
                "output": None,
                "error": result.stderr,
                "ai_fix": ai_response.choices[0].message.content
            }

    except Exception as e:
        import traceback
        return {"status": "fail", "error": traceback.format_exc()}

st.set_page_config(page_title="Python Script Debugger")
st.title("Python Script Debugger with AI Fix")

uploaded_file = st.file_uploader("Upload your Python script (.py)", type=["py"])

if uploaded_file:
    temp_path = "temp_script.py"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    st.write("Running your script...")
    result = quick_debug_file(temp_path)

    if result["status"] == "success":
        st.success("Script executed successfully!")
        if result["output"]:
            st.code(result["output"], language="plaintext")

    elif result["status"] == "error":
        st.error("Script has errors!")
        st.subheader("Error Output:")
        st.code(result["error"], language="plaintext")
        st.subheader("AI Suggested Fix:")
        st.markdown(result["ai_fix"])

    else:
        st.error("Execution failed")
        st.text(result["error"])
