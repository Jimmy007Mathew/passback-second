from fastapi import FastAPI, File, UploadFile
import subprocess
import os
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pass-second.vercel.app","https://pass-second-jimmy-mathews-projects.vercel.app"],  # Adjust this to the frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/process-files/")
async def process_files(input_file: UploadFile = File(...), optab_file: UploadFile = File(...)):

    input_file_path = TEMP_DIR / "input.txt"
    optab_file_path = TEMP_DIR / "optab.txt"
    output_file_path = TEMP_DIR / "out.txt"
    record_file_path = TEMP_DIR / "record.txt"
    intermediate_file_path = TEMP_DIR / "intermediate.txt"
    symtab_file_path = TEMP_DIR / "symtab.txt"

    try:
       
        with input_file_path.open("wb") as f:
            f.write(await input_file.read())

      
        with optab_file_path.open("wb") as f:
            f.write(await optab_file.read())

        result1 = subprocess.run(
            ["python", "pass1.py", str(input_file_path), str(optab_file_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print("Pass1 Output:", result1.stdout)

     
        if not intermediate_file_path.exists() or not symtab_file_path.exists():
            return {"error": "Intermediate or Symtab file not found"}

      
        result2 = subprocess.run(
            ["python", "pass2.py"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Pass2 Output:", result2.stdout)

      
        if not output_file_path.exists():
            return {"output_file": "Output file not found", "record_file": ""}

        
        with output_file_path.open("r") as result_file:
            output_content = result_file.read()
        
        with intermediate_file_path.open("r") as intermediate_file:
            intermediate_content = intermediate_file.read()

        with symtab_file_path.open("r") as symtab_file:
            symtab_content = symtab_file.read()

        record_content = ""
        if record_file_path.exists():
            with record_file_path.open("r") as record_file:
                record_content = record_file.read()

        return {
            "output_file": output_content,
            "record_file": record_content,
            "intermediate_file": intermediate_content,
            "symtab_file": symtab_content
        }

    except subprocess.CalledProcessError as e:
        
        print(f"Error running script: {e.stderr}")
        return {"error": f"Error running scripts: {e.stderr}"}
    except Exception as e:
        
        print(f"Unexpected error: {e}")
        return {"error": "Error processing files"}
