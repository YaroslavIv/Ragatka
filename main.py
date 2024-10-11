import argparse

from rag import RagPipeline
from utils import read_files, read_json

def parse():
    parser = argparse.ArgumentParser(prog='Rag')

    parser.add_argument('cfg_db', help='path to config for init db')
    parser.add_argument('cfg_embeder', help='path to config for init embeder')
    parser.add_argument('cfg_generative', help='path to config for init generative')
    
    parser.add_argument('path_folder', help='path to files for rag')
    parser.add_argument('query')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse()

    pipeline = RagPipeline(
        read_json(args.cfg_db), 
        read_json(args.cfg_embeder), 
        read_json(args.cfg_generative)
    )

    pipeline.run(read_files(args.path_folder), args.query)