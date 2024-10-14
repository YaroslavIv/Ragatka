import argparse

from rag import RagPipeline
from utils import read_file, read_files, read_json

def parse():
    parser = argparse.ArgumentParser(prog='RAGATKA')
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    add = subparsers.add_parser('add', help='add docs')
    add.add_argument('cfg_db', help='path to config for init db')
    add.add_argument('cfg_embeder', help='path to config for init embeder')
    add.add_argument('path_folder', help='path to files for rag')
    
    delete = subparsers.add_parser('delete', help='delete file')
    delete.add_argument('cfg_db', help='path to config for init db')
    delete.add_argument('cfg_embeder', help='path to config for init embeder')
    delete.add_argument('path_file', help='path to file from rag')

    search = subparsers.add_parser('search', help='search file')
    search.add_argument('cfg_db', help='path to config for init db')
    search.add_argument('cfg_embeder', help='path to config for init embeder')
    search.add_argument('path_file', help='path to file')

    question = subparsers.add_parser('question', help='ask a question')
    question.add_argument('cfg_db', help='path to config for init db')
    question.add_argument('cfg_embeder', help='path to config for init embeder')
    question.add_argument('cfg_generative', help='path to config for init generative')
    question.add_argument('question')

    return parser

if __name__ == '__main__':
    parser = parse()
    args = parser.parse_args()
    pipeline = RagPipeline()

    if args.command == 'question':
        pipeline.init_db(read_json(args.cfg_db)) 
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        pipeline.init_generative(read_json(args.cfg_generative)) 

        pipeline.query(args.question)
    
    elif args.command == 'add':
        pipeline.init_db(read_json(args.cfg_db)) 
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        
        pipeline.add_docs(read_files(args.path_folder))
    
    elif args.command == 'delete':
        pipeline.init_db(read_json(args.cfg_db)) 
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        
        pipeline.delete_file(read_file(args.path_file))
    elif args.command == 'search':
        pipeline.init_db(read_json(args.cfg_db)) 
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        
        pipeline.search(read_file(args.path_file))
    else:
        parser.print_help()