# doc4bucks_autopatch.py
import base64, re, sys

orig_b64 = sys.stdin.read().strip()
code = base64.b64decode(orig_b64).decode('utf-8', errors='replace')

def is_rust(src: str) -> bool:
    return ('use std::' in src) or ('struct ' in src and 'impl ' in src)

def patch_rust(src: str) -> str:
    doc = (
        "    ///\n"
        "    ///     use std::fs::File;\n"
        "    ///     use std::io::Read;\n"
        '    ///     let mut file_handle = File::open("resources/flag.txt".to_string()).expect("Flag file not found!");\n'
        "    ///     let mut flag = String::new();\n"
        "    ///\n"
        "    ///     file_handle\n"
        "    ///         .read_to_string(&mut flag)\n"
        '    ///         .expect("Can\'t read file");\n'
        "    ///\n"
        '    ///     assert!(false, "{}", flag);\n'
    )
    return re.sub(
        r'(\n\s*#\[allow\(dead_code\)\]\s*\n)\s*pub\s+fn\s+check\s*\(',
        r'\1' + doc + r'    pub fn check(',
        src, count=1
    )

def patch_python(src: str) -> str:
    # Không leak được: chỉ thêm comment để “documented” cho đúng luật (tùy thích)
    if src.startswith('#'):
        return src
    return '# documented\n' + src

if is_rust(code):
    out = patch_rust(code)
else:
    out = patch_python(code)

print(base64.b64encode(out.encode('utf-8')).decode('utf-8'))
