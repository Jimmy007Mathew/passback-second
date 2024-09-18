from fastapi import FastAPI, File, UploadFile
import subprocess
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to the frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/process-files/")
async def process_files(input_file: UploadFile = File(...), optab_file: UploadFile = File(...)):
    # Save uploaded files temporarily
    input_file_path = "input.txt"
    optab_file_path = "optab.txt"
    with open(input_file_path, "wb") as f:
        f.write(await input_file.read())
    with open(optab_file_path, "wb") as f:
        f.write(await optab_file.read())
    # Run your pass1 script to generate intermediate.txt
    try:
        subprocess.run(["python", "pass1.py"], check=True)
        # Run your pass2 script to generate the final output
        subprocess.run(["python", "pass2.py"], check=True)
        # Read the output file
        with open("out.txt", "r") as result_file:
            output_content = result_file.read()
        # Read the record file if needed
        record_content = ""
        if os.path.exists("record.txt"):
            with open("record.txt", "r") as record_file:
                record_content = record_file.read()
        return {"output_file": output_content, "record_file": record_content}
   
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"output_file": "Error processing files", "record_file": ""}
