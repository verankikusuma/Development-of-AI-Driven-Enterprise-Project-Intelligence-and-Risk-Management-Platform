import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('final_project')
from utils.local_ai import local_answer

text = "Altura Freight Technologies total budget USD $2,700,000. In January 2028 Current Phase Platform Integration, Data Migration & Pilot Preparation is planned. Reporting Frequency Weekly delivery review. Risk: Dependency scanning and penetration testing delays. Vendor dependencies: AWS cloud infrastructure and Salesforce API integration."
chunks = [{'text': text, 'filename': 'sample.pdf'}]

ans = local_answer('Summarize budget and cost overrun status.', chunks)
print("=== BUDGET ANSWER ===")
print(ans['answer'])

ans2 = local_answer('Which milestones or deliverables are delayed?', chunks)
print("\n=== MILESTONES ANSWER ===")
print(ans2['answer'])
