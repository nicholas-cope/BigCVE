#Thanks Miles
import glob
import os
from multiprocessing import Pool, set_start_method
from pathlib import Path
import subprocess

source_directory = "/home/ybc67/data/BigCVE/BigVul/Functions/"
output_directory = "/home/ybc67/data/BigCVE/BigVul/CPG/"
temp_joern_files_location = "/home/ybc67/data/BigCVE/BigVul/Temp/"

#Paths
jdk_path = "/home/ybc67/jdk-22.0.1/"
joern_path = "/home/ybc67/bin/joern/joern-cli/"
os.environ["JAVA_HOME"] = jdk_path

done_files = {done.stem for done in Path(output_directory).iterdir()}  #Faster seraching

def joern_parse(source_file):
    sample_name = Path(source_file).stem
    # Extract the function number by keeping only digits
    function_number = ''.join(filter(str.isdigit, sample_name))
    print(f"Starting to process: {sample_name}")

    # Check if directory exists, if not create it
    function_output_dir = Path(output_directory) / f"function{function_number}"
    if not function_output_dir.exists():
        function_output_dir.mkdir(parents=True)

    if sample_name in done_files:
        print(f"{sample_name} already processed")
        return

    bin_file = Path(temp_joern_files_location) / f"{sample_name}.bin"
    out_file = function_output_dir / sample_name  # Put output in function directory

    os.system(f"{joern_path}joern-parse {source_file}  --language newc --output {bin_file}")
    os.system(f"{joern_path}joern-export {bin_file} --repr cpg14 --out {out_file} --format dot")
    os.remove(bin_file)


#Well this fixed the error
if __name__ == '__main__':
    set_start_method("spawn")
    files = glob.glob(source_directory + "*.cpp")
    print(files)

    with Pool(18) as p:
        p.map(joern_parse, files)


    # java_location = "~/.jdks/openjdk-19.0.2"
    #os.environ["JAVA_HOME"] = java_location
