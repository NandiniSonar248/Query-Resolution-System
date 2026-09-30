import asyncio
from app.agents.response_generation import response_generation_node
from app.rag.retriever import retrieve
import logging

logging.basicConfig(level=logging.INFO)

def test():
    print('1. Retrieving chunks...')
    retrieval_res = retrieve('give me all the projects from the resume in detail')
    print(f'   Got {len(retrieval_res["chunks"])} chunks.')
    
    state = {
        'normalized_query': 'give me all the projects from the resume in detail',
        'chunks': retrieval_res["chunks"],
        'retrieval_confidence': retrieval_res["retrieval_confidence"],
        'chat_history': []
    }
    
    print('2. Generating response...')
    try:
        new_state = response_generation_node(state)
        print('SUCCESS!')
        print(new_state.get('answer_text'))
        print(f"Confidence: {new_state.get('generation_confidence')}")
    except Exception as e:
        import traceback
        traceback.print_exc()

test()
