#Thanks Miles
import glob
import os
from multiprocessing import Pool, set_start_method
from pathlib import Path

source_directory = "Functions/"
output_directory = "CPG/"
joern_path = "/Users/yurischool/joern/joern-cli/"
temp_joern_files_location = "Temp/"

done_files = {done.stem for done in Path(output_directory).iterdir()}  #Faster seraching

def joern_parse(source_file):
    sample_name = Path(source_file).stem

    if sample_name in done_files:
        print(f"{sample_name} already processed")
        return

    bin_file = Path(temp_joern_files_location) / f"{sample_name}.bin"
    out_file = Path(output_directory) / sample_name

    # Changing up string concatenation
    os.system(f"{joern_path}joern-parse {source_file} --language c --output {bin_file}")
    os.system(f"{joern_path}joern-export {bin_file} --repr cpg --out {out_file} --format dot")
    os.remove(bin_file)


#Well this fixed the error
if __name__ == '__main__':
    set_start_method("spawn")
    files = glob.glob(source_directory + "*.cpp")

    with Pool(18) as p:
        p.map(joern_parse, files)


    # java_location = "~/.jdks/openjdk-19.0.2"
    #os.environ["JAVA_HOME"] = java_location