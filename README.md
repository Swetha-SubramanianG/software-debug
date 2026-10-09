# Software Debugging Agent

A Streamlit application that accepts a program, error message, and expected
behavior. It asks an OpenAI model to explain the likely cause, propose a
complete correction, and suggest tests. For Python, it can check syntax and,
after explicit approval, run one input/output test. Failed runtime or output
validation can be sent back to the model for another correction.

## Requirements

- Python 3.10 or newer
- An OpenAI API key with access to `gpt-4o-mini`

## Run locally

1. Activate your Python environment.
2. Install the project dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your key:

   ```text
   OPENAI_API_KEY=your_key_here
   ```

   Keep `.env` private; it is excluded from version control.

4. Start the application:

   ```powershell
   streamlit run app.py
   ```

The app starts with an editable example demonstrating an empty-line
`ZeroDivisionError`. Analyze it, review the proposed fix, use the prefilled
blank-line test input with expected output `0`, approve execution, and select
**Validate corrected code**. To demonstrate iterative correction, change the
expected output to a value the corrected program will not produce, validate,
then use **Try another correction using validation feedback**.

## Validation and safety

Automatic execution is implemented only for Python. The program runs in a
temporary working directory, isolated Python mode, with a five-second timeout;
these measures are **not a security sandbox**. Python code may still access
local resources. Review code and approve execution only when you trust it.

Output comparison trims leading and trailing whitespace. If expected output is
left blank, the app reports runtime success but does not claim that expected
behavior was verified. Model-generated reasoning and test suggestions are not
execution results.

## Run tests

```powershell
python -m unittest -v
```
