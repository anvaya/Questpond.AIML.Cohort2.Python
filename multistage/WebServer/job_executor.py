"""
Background job executor using ThreadPoolExecutor
"""
import sys
import pathlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
import traceback

# Add parent directory to path to import multistage modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from Candidate.document_chunk_parser import prepare_normalized_chunks
from Candidate.chunk_processor import recover_identity, extract_raw_experience
from Candidate.postprocessor import build_professional_profile
from Candidate.vectorizer import sync_profile_to_master
from Employer.MatchingEngine import SOTAMatchingEngine


class JobExecutor:
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit_candidate_job(self, job_id: str, pdf_file_path: str, update_callback):
        """Submit candidate processing job to background thread"""
        future = self.executor.submit(
            self._process_candidate_resume,
            job_id, pdf_file_path, update_callback
        )
        return future

    def submit_employer_job(self, job_id: str, job_description: str, update_callback):
        """Submit employer matching job to background thread"""
        future = self.executor.submit(
            self._process_employer_matching,
            job_id, job_description, update_callback
        )
        return future

    def _process_candidate_resume(self, job_id: str, pdf_file_path: str, update_callback):
        """Process candidate resume in background"""
        try:
            import ollama

            # Step 1: Queued
            update_callback(job_id, 'queued', 10, 'Parsing resume document')

            # Initialize Ollama client
            ollama_client = ollama.Client(host='http://localhost:11434')

            # Step 2: Parse document
            update_callback(job_id, 'processing', 20, 'Extracting text chunks')
            normalized_chunks = prepare_normalized_chunks(pdf_file_path, ollama_client=ollama_client)

            save_path = pathlib.Path(__file__).parent.parent / "temp" / "normalized_chunks.json"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(normalized_chunks, f, indent=2)   

            # Step 3: Extract identity
            update_callback(job_id, 'processing', 40, 'Recovering candidate identity')
            identity = recover_identity(normalized_chunks, chat_client=ollama_client)

            # save_path = pathlib.Path(__file__).parent.parent / "temp" / "identity.json"
            # save_path.parent.mkdir(parents=True, exist_ok=True)
            # with open(save_path, 'w', encoding='utf-8') as f:
            #     import json
            #     json.dump(identity, f, indent=2)   


            # Step 4: Extract experience
            update_callback(job_id, 'processing', 60, 'Extracting work experience')
            raw_experience = extract_raw_experience(normalized_chunks, chat_client=ollama_client)

            # Step 5: Build profile
            update_callback(job_id, 'processing', 80, 'Building professional profile')
            ref_date = datetime.now().strftime("%Y-%m-%d")
            profile = build_professional_profile(raw_experience=raw_experience, ref_date=ref_date)
            profile['identity'] = identity

            # Step 6: Sync to database
            update_callback(job_id, 'processing', 90, 'Saving to database')
            from Shared.db import connect_db
            conn = connect_db()
            sync_profile_to_master(profile, raw_experience, conn)
            conn.close()

            # Step 7: Complete
            result = {
                'profile': profile
            }
            update_callback(job_id, 'completed', 100, 'Resume processed successfully', result)

        except Exception as e:
            print("--- Using traceback.print_exc(): ---")
            traceback.print_exc()
            exc_type, exc_obj, tb = sys.exc_info()            
            lineno = tb.tb_lineno # type: ignore            
            update_callback(job_id, 'failed', 0, f'Processing failed: {lineno} {str(e)}', error_message= str(e))

    def _process_employer_matching(self, job_id: str, job_description: str, update_callback):
        """Process employer matching in background"""
        try:
            # Step 1: Queued
            update_callback(job_id, 'processing', 10, 'Analyzing job description')

            # Step 2: Connect to database
            from Shared.db import connect_db
            conn = connect_db()

            # Step 3: Create matching engine
            update_callback(job_id, 'processing', 20, 'Initializing matching engine')
            engine = SOTAMatchingEngine(conn)

            # Step 4: Parse JD and rank candidates
            update_callback(job_id, 'processing', 40, 'Matching candidates to requirements')
            ranked_candidates = engine.rank_candidates(job_description) #engine.rank_candidates_with_llm(job_description)

            # Step 5: Format results
            update_callback(job_id, 'processing', 80, 'Formatting results')
            matches = [
                {
                    'name': c['name'],
                    'score': c['score'],
                    'matches': c['matches'],
                    'breakdown': c.get('breakdown', {}),
                    'confidence': c.get('confidence', 'Unknown'),
                    'skill_breakdown': c.get('skill_breakdown', []),
                    'unmatched_skills': c.get('unmatched_skills', []),
                    'total_jd_skills': c.get('total_jd_skills'),
                    'matched_skill_count': c.get('matched_skill_count'),
                    'unmatched_skill_count': c.get('unmatched_skill_count')
                }
                for c in ranked_candidates["results"]
            ]

            # Step 6: Complete
            result = {
                'matches': matches,
                'role_context': ranked_candidates["role_context"]
            }
            conn.close()
            update_callback(job_id, 'completed', 100, f'Found {len(matches)} matching candidates', result)

        except Exception as e:
            print("--- Using traceback.print_exc(): ---")
            traceback.print_exc()
            exc_type, exc_obj, tb = sys.exc_info()            
            lineno = tb.tb_lineno # type: ignore            
            update_callback(job_id, 'failed', 0, f'Matching failed: {str(e)}', error_message=str(e))

    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=False)


# Global executor instance
_executor = None


def get_executor():
    global _executor
    if _executor is None:
        _executor = JobExecutor()
    return _executor
