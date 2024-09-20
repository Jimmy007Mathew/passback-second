from fastapi import FastAPI, File, UploadFile
import subprocess
import os
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a temporary folder to store files if it doesn't exist
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/process-files/")
async def process_files(input_file: UploadFile = File(...), optab_file: UploadFile = File(...)):
    # Save uploaded files temporarily in the temp directory
    input_file_path = TEMP_DIR / "input.txt"
    optab_file_path = TEMP_DIR / "optab.txt"
    output_file_path = TEMP_DIR / "out.txt"
    record_file_path = TEMP_DIR / "record.txt"

    try:
        # Write the input file
        with input_file_path.open("wb") as f:
            f.write(await input_file.read())

        # Write the optab file
        with optab_file_path.open("wb") as f:
            f.write(await optab_file.read())

        # Run pass1 script with the input and optab files
        result1 = subprocess.run(
            ["python", "pass1.py", str(input_file_path), str(optab_file_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print("Pass1 Output:", result1.stdout)

        # Run pass2 script to generate the final output
        result2 = subprocess.run(
            ["python", "pass2.py"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Pass2 Output:", result2.stdout)

        # Check if the output file exists
        if not output_file_path.exists():
            return {"output_file": "Output file not found", "record_file": ""}

        # Read the output file
        with output_file_path.open("r") as result_file:
            output_content = result_file.read()

        # Read the record file if it exists
        record_content = ""
        if record_file_path.exists():
            with record_file_path.open("r") as record_file:
                record_content = record_file.read()

        return {"output_file": output_content, "record_file": record_content}

    except subprocess.CalledProcessError as e:
        # Catch errors in subprocess calls and provide feedback
        print(f"Error running script: {e.stderr}")
        return {"output_file": f"Error running scripts: {e.stderr}", "record_file": ""}
    except Exception as e:
        # Catch any other errors
        print(f"Unexpected error: {e}")
        return {"output_file": "Error processing files", "record_file": ""}