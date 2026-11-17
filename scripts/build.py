import argparse, hashlib, json, re, struct
from pathlib import Path

ALPHABET = '123456789ABCDEFG'
MAGIC = b'S16B'
VERSION = 1
RECORD_SIZE = 160

def validate_solution(sol):
    expected = set(range(1,17))
    for r in range(16):
        if set(sol[r*16:(r+1)*16]) != expected: raise ValueError(f'bad solution row {r}')
    for c in range(16):
        if {sol[r*16+c] for r in range(16)} != expected: raise ValueError(f'bad solution col {c}')
    for br in range(0,16,4):
        for bc in range(0,16,4):
            if {sol[(br+dr)*16+bc+dc] for dr in range(4) for dc in range(4)} != expected: raise ValueError('bad box')

def encode(puzzle, solution):
    # 0..15 nibble values represent solution digits 1..16
    packed = bytes(((solution[i]-1)<<4) | (solution[i+1]-1) for i in range(0,256,2))
    mask = bytearray(32)
    for i,v in enumerate(puzzle):
        if v:
            if v != solution[i]: raise ValueError('clue does not match solution')
            mask[i//8] |= 1 << (7-i%8)
    return packed + bytes(mask)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, default=Path('dist'))
    ap.add_argument('--source-commit', default='unknown')
    args=ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    files=sorted(args.source.rglob('*.sdk.txt'))
    if len(files)!=10000: raise ValueError(f'expected 10000 base puzzles, found {len(files)}')
    output=args.out/'base16.bin'
    seen=set()
    with output.open('wb') as f:
        f.write(MAGIC + struct.pack('<HHI',VERSION,RECORD_SIZE,len(files)))
        for idx,p in enumerate(files,1):
            lines=[x.strip() for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
            if not lines or not re.fullmatch(r'# size=16 box=4x4',lines[0]): raise ValueError(f'bad header {p}')
            if len(lines)!=17 or any(len(x)!=16 for x in lines[1:]): raise ValueError(f'bad grid {p}')
            puzzle=[0 if c=='.' else ALPHABET.index(c)+1 for line in lines[1:] for c in line]
            sidecar=p.with_suffix('.json')
            meta=json.loads(sidecar.read_text(encoding='utf-8'))
            solution=meta['solution_grid']
            if len(solution)!=256 or any(not isinstance(v,int) or isinstance(v,bool) or not 1<=v<=16 for v in solution): raise ValueError(f'bad solution {p}')
            validate_solution(solution)
            if meta.get('minimality',{}).get('is_minimal') is not True: raise ValueError(f'not minimal {p}')
            if not any(puzzle): raise ValueError(f'empty puzzle {p}')
            record=encode(puzzle,solution)
            if record in seen: raise ValueError(f'duplicate puzzle {p}')
            seen.add(record)
            f.write(record)
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    manifest={'schema_version':1,'dataset':'scaled-sudoku-instances/base/16x16','source_repository':'https://github.com/zayenz/scaled-sudoku-instances','source_commit':args.source_commit,'board_size':16,'box_size':4,'count':len(files),'unique_solution':'asserted_by_upstream_corpus; not independently re-solved','format':'S16B v1','record_bytes':RECORD_SIZE,'file':{'name':output.name,'size':output.stat().st_size,'sha256':digest}}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__': main()
