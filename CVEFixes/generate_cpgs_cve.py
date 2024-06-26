import glob
import os
import shutil
from multiprocessing import Pool, freeze_support, set_start_method
from pathlib import Path

source_directory = "/home/ybc67/data/BigCVE/CVEFixes/Functions/"
output_directory = "/home/ybc67/data/BigCVE/CVEFixes/CPG/"
temp_joern_files_location = "/home/ybc67/data/BigCVE/CVEFixes/Temp/"
joern_path = "/home/ybc67/bin/joern/joern-cli/"

jdk_path = "/home/ybc67/jdk-22.0.1/"
os.environ["JAVA_HOME"] = jdk_path

done_files = {done.stem for done in Path(output_directory).iterdir()}  # Faster searching

def joern_parse(source_file):
    sample_name = Path(source_file).stem
    # Extract the function number by keeping only digits
    function_number = ''.join(filter(str.isdigit, sample_name))

    # Check if directory exists, if not create it
    function_output_dir = Path(output_directory) / f"function{function_number}"
    function_output_dir.mkdir(parents=True, exist_ok=True)  # Create directory safely

    if sample_name in done_files:
        print(f"{sample_name} already processed")
        return

    bin_file = Path(temp_joern_files_location) / f"{sample_name}.bin"
    out_file = function_output_dir / sample_name  # Put output in function directory

    os.system(f"{joern_path}joern-parse {source_file}  --language newc --output {bin_file}")
    os.system(f"{joern_path}joern-export {bin_file} --repr cpg14 --out {out_file} --format dot")
    os.remove(bin_file)


def clean_invalid_functions():
    for function_dir in Path(output_directory).iterdir():
        if function_dir.is_dir():
            function_number = ''.join(filter(str.isdigit, function_dir.stem))
            fixed_dir = function_dir / f'fixed_{function_number}'
            vulnerability_dir = function_dir / f'vulnerability_{function_number}'

            fixed_dot_files = list(fixed_dir.glob('*.dot'))
            vulnerability_dot_files = list(vulnerability_dir.glob('*.dot'))

            fixed_dot_files_count = len(fixed_dot_files)
            vulnerability_dot_files_count = len(vulnerability_dot_files)

            print(
                f"Directory {function_dir} has {fixed_dot_files_count} .dot files in 'fixed_{function_number}' and {vulnerability_dot_files_count} .dot files in 'vulnerability_{function_number}'")

            if fixed_dot_files_count == 2 or vulnerability_dot_files_count == 2:
                print(f"Removing {function_dir} due to exactly 2 .dot files in either subdirectory")
                shutil.rmtree(function_dir)

if __name__ == '__main__':
    set_start_method("spawn")
    files = glob.glob(source_directory + "*.cpp")
    print(files)

    # Create necessary directories before starting multiprocessing
    for file in files:
        sample_name = Path(file).stem
        function_number = ''.join(filter(str.isdigit, sample_name))
        function_output_dir = Path(output_directory) / f"function{function_number}"
        function_output_dir.mkdir(parents=True, exist_ok=True)

    with Pool(18) as p:
        p.map(joern_parse, files)

clean_invalid_functions()
