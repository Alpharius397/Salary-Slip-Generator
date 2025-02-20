import argparse
import sys
import os
parse = argparse.ArgumentParser()

parse.add_argument("data",type=str,help="Fetches data")
parse.add_argument("url",type=str,help="send response")

args = parse.parse_args(sys.argv[1:])

file_path = f"{os.path.dirname(sys.executable)}"
with open(os.path.join(file_path,"sample.txt"), 'w') as f:
    f.write(f"Data String: {args.data}\nSend to: {args.url}")
