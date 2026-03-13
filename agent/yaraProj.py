import yara
import os
import sys
import argparse

def compile_rules(rule_path):
    try:
        return yara.compile(filepath=rule_path)
    except yara.SyntaxError as e:
        print(f"[!] Failed to compile YARA rules: {e}")
        sys.exit(1)

def triage_file(target_file, rules):
    if not os.path.exists(target_file):
        print(f"[!] Error: File '{target_file}' not found.")
        return

    matches = rules.match(target_file)
    match_names = [match.rule for match in matches]
    hits = len(match_names)

    # bucket 1: nothing hits at all, totally safe to ignore it
    if hits == 0:
        print("nothing")
        return

    # bucket 2: definitive malware got, just a normal scan 
    if "Definitive_Malware_Signature" in match_names:
        print("normal scan")
        return

    # bucket 3: deep scan. 1 to 3 rules hit out of 15. 
    # it's suspicous but missing a lot of red flags. trying to blend in.
    # we push to deep scan cause we arent sure what it is actually doing
    if hits > 0 and hits <= 3:
        print("deep scan")
        return

    # bucket 4 (well, back to normal scan): it hits 4 or more rules.
    # out of 15 rules, hitting 4+ means its super noisy and hitting tons of red flags. 
    # not well hiddden malware at all, so normal scan is fine.
    if hits >= 4:
        print("normal scan")
        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Route files to Assemblyline scan buckets.")
    parser.add_argument("file_to_scan", help="Path to the file to scan")
    parser.add_argument("-r", "--rules", default="triage_rules.yar", help="Path to YARA rules file")
    args = parser.parse_args()
    
    compiled_rules = compile_rules(args.rules)
    triage_file(args.file_to_scan, compiled_rules)