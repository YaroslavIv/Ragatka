import argparse

from rag import RagPipeline
from utils import read_txt_file, read_txt_files, read_json
from authorization import Authorization

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

    chat = subparsers.add_parser('chat', help='ask a question')
    chat.add_argument('cfg_db', help='path to config for init db')
    chat.add_argument('cfg_embeder', help='path to config for init embeder')
    chat.add_argument('cfg_generative', help='path to config for init generative')
    chat.add_argument('cfg_chat', help='path to config for init chat')
    chat.add_argument('cfg_auth', help='path to config for init auth')

    return parser

if __name__ == '__main__':
    parser = parse()
    args = parser.parse_args()
    pipeline = RagPipeline()

    if args.command == 'question':
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        pipeline.init_generative(read_json(args.cfg_generative)) 
        pipeline.init_db(read_json(args.cfg_db))

        pipeline.query(args.question)
    
    elif args.command == 'add':
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        pipeline.init_db(read_json(args.cfg_db)) 
        
        pipeline.add_docs(read_txt_files(args.path_folder))
    
    elif args.command == 'delete':
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        pipeline.init_db(read_json(args.cfg_db)) 
        
        pipeline.delete_file(read_txt_file(args.path_file))
    elif args.command == 'search':
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        pipeline.init_db(read_json(args.cfg_db)) 
        
        pipeline.search(read_txt_file(args.path_file))
    if args.command == 'chat':
        pipeline.init_embeder(read_json(args.cfg_embeder)) 
        pipeline.init_generative(read_json(args.cfg_generative)) 
        pipeline.init_db(read_json(args.cfg_db))
        pipeline.init_auth(read_json(args.cfg_auth))
        pipeline.init_chat(read_json(args.cfg_chat))
        pipeline.chat()
    else:
        parser.print_help()