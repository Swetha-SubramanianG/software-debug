import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from debugging_agent import analyze_code, extract_code, validate_python


load_dotenv()

st.set_page_config(
    page_title="Software Debugging Agent",
    page_icon="🐞",
    layout="wide",
)

st.title("🐞 Software Debugging Agent")
st.write(
    "Analyze a bug, understand its likely cause, propose a correction, "
    "and validate the result against expected behavior."
)

defaults = {
    "source_code": (
        "numbers = list(map(int, input().split()))\n"
        "print(sum(numbers) / len(numbers))"
    ),
    "error_message": (
        "ZeroDivisionError: division by zero when the input line is empty"
    ),
    "expected_behavior": (
        "Print the arithmetic mean of the input numbers. "
        "If no numbers are provided, print 0."
    ),
    "test_input": "\n",
    "expected_output": "0",
    "analysis": "",
    "corrected_code": "",
    "analysis_language": "Python",
    "validation": None,
    "execution_approved": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

language = st.selectbox(
    "Programming language",
    ["Python", "Java", "C", "C++", "JavaScript", "C#"],
)

source_code = st.text_area(
    "Source code",
    key="source_code",
    height=220,
    help="Paste the program that is producing the problem.",
)
error_message = st.text_area(
    "Error message (optional)",
    key="error_message",
    height=90,
)
expected_behavior = st.text_area(
    "Expected behavior",
    key="expected_behavior",
    height=90,
    help="Describe what the program should do, including important edge cases.",
)

st.subheader("Python validation test")
st.caption(
    "Enter one test case. Validation compares standard output when expected "
    "output is provided."
)
test_input = st.text_area(
    "Program input (optional)",
    key="test_input",
    height=70,
)
expected_output = st.text_area(
    "Expected standard output (optional)",
    key="expected_output",
    height=70,
)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your_actual_api_key_here":
    st.info(
        "Add OPENAI_API_KEY to your local .env file to enable AI analysis. "
        "The key is read locally and is never displayed by this app."
    )
else:
    st.caption("AI analysis is ready.")

if st.button("Analyze and Fix Code", type="primary"):
    if not source_code.strip():
        st.warning("Enter source code before starting the analysis.")
    elif not expected_behavior.strip():
        st.warning("Describe the expected behavior before starting the analysis.")
    elif not api_key or api_key == "your_actual_api_key_here":
        st.error("AI analysis is unavailable because OPENAI_API_KEY is not set.")
    else:
        try:
            with st.spinner("Analyzing the source code..."):
                response = analyze_code(
                    OpenAI(api_key=api_key),
                    source_code,
                    error_message,
                    expected_behavior,
                    language,
                )

            if not response.strip():
                st.error("The AI service returned an empty analysis.")
            else:
                st.session_state.analysis = response
                st.session_state.corrected_code = extract_code(
                    response, language
                )
                st.session_state.analysis_language = language
                st.session_state.validation = None
                st.session_state.execution_approved = False
        except Exception as error:
            st.error(
                "The AI request failed. Check the API key, model access, "
                f"account limits, and network connection. Details: {error}"
            )

if st.session_state.analysis:
    result_language = st.session_state.analysis_language
    st.divider()
    st.subheader("Agent analysis and reasoning")
    st.markdown(st.session_state.analysis)

    corrected_code = st.session_state.corrected_code
    if corrected_code:
        st.subheader("Proposed corrected program")
        code_languages = {
            "Python": "python",
            "Java": "java",
            "C": "c",
            "C++": "cpp",
            "JavaScript": "javascript",
            "C#": "csharp",
        }
        extensions = {
            "Python": "py",
            "Java": "java",
            "C": "c",
            "C++": "cpp",
            "JavaScript": "js",
            "C#": "cs",
        }
        st.code(corrected_code, language=code_languages[result_language])
        st.download_button(
            "Download corrected code",
            data=corrected_code,
            file_name=f"corrected_program.{extensions[result_language]}",
            mime="text/plain",
        )

        st.divider()
        st.subheader("Validation")
        if result_language == "Python":
            st.warning(
                "Executing code can access files, networks, and other local "
                "resources. The timeout is not a security sandbox. Review the "
                "correction and run only code you trust."
            )
            st.checkbox(
                "I reviewed this code and approve local execution",
                key="execution_approved",
            )

            if st.button("Validate corrected code"):
                with st.spinner("Checking syntax and running the test..."):
                    status, details = validate_python(
                        corrected_code,
                        user_input=test_input,
                        expected_output=(
                            expected_output
                            if expected_output.strip()
                            else None
                        ),
                        approved=st.session_state.execution_approved,
                    )
                st.session_state.validation = {
                    "status": status,
                    "details": details,
                }

            validation = st.session_state.validation
            if validation:
                st.write(f"**Status:** {validation['status']}")
                st.code(validation["details"], language="text")
        else:
            st.info(
                "Code analysis and correction are available for this language. "
                "Automatic compilation and execution are currently supported "
                "only for Python."
            )
    else:
        st.warning(
            "No corrected code block was found. Review the analysis, or run "
            "the analysis again and ask for a complete fenced program."
        )

    validation = st.session_state.validation
    retryable_statuses = {
        "FAILED",
        "EXECUTION FAILED",
        "TESTS FAILED",
        "TIMEOUT",
        "VALIDATION ERROR",
    }
    if (
        result_language == "Python"
        and validation
        and validation["status"] in retryable_statuses
        and corrected_code
    ):
        if st.button("Try another correction using validation feedback"):
            if not api_key or api_key == "your_actual_api_key_here":
                st.error("A configured OPENAI_API_KEY is required to retry.")
            else:
                try:
                    with st.spinner("Revising the correction..."):
                        response = analyze_code(
                            OpenAI(api_key=api_key),
                            corrected_code,
                            error_message,
                            expected_behavior,
                            result_language,
                            previous=validation["details"],
                        )

                    if not response.strip():
                        st.error("The AI service returned an empty correction.")
                    else:
                        st.session_state.analysis = response
                        st.session_state.corrected_code = extract_code(
                            response, result_language
                        )
                        st.session_state.validation = None
                        st.session_state.execution_approved = False
                        st.rerun()
                except Exception as error:
                    st.error(f"The retry request failed. Details: {error}")

st.divider()
st.caption(
    "Software Debugging Agent | Code analysis • Reasoned correction • "
    "Python validation • Iterative debugging"
)
