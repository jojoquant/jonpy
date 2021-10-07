import subprocess
from pathlib import Path

# python -m grpc_tools.protoc -I../../protos --python_out=. --grpc_python_out=. ../../protos/helloworld.proto
# python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. hello.proto
# -I. 表示输入文件在当前目录下，后面接空格+文件名
# --python_out=. --grpc_python_out=. 表示生成文件都放在当前目录下

p = Path('.')
files_str = " ".join([file.name for file in p.iterdir() if file.suffix == ".proto"])
gen_grpc_cmd = [f"python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. {files_str}"]

cmd = subprocess.Popen(
    gen_grpc_cmd, shell=True
)

cmd.wait()
