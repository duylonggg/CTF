use std::fs::{File, OpenOptions};
use std::io::{self, Read, Write, BufRead, Cursor, Seek, SeekFrom};
use std::path::Path;
use std::env;
use std::process;
use std::time::{SystemTime, UNIX_EPOCH};
use rand::{Rng, thread_rng};
use rand::distributions::Alphanumeric;
use openssl::symm::{Cipher, Crypter, Mode};
use hex_literal::hex;
use byteorder::{LittleEndian, ReadBytesExt, WriteBytesExt};
use leb128;
const H_START: [u8; 4] = hex!("FF1337FF");
const H_END:   [u8; 4] = hex!("FFCAFEFF");
const D_START:   [u8; 4] = hex!("FF7270FF");
const D_END:     [u8; 4] = hex!("FFEDEDFF");
const F_START: [u8; 4] = hex!("FFDEADFF");
const F_END:   [u8; 4] = hex!("FFBEEFFF");
const SIG:    [u8; 4] = hex!("4C554E41"); 
enum DbMode<'a> {
    Append { existing: &'a [[u8; 8]] },
    Create,
}
fn find_pattern(data: &[u8], pattern: &[u8]) -> Option<usize> {
    data.windows(pattern.len()).position(|w| w == pattern)
}
fn get_input(prompt_text: &str) -> io::Result<String> {
    print!("{}", prompt_text);
    io::stdout().flush()?;
    let stdin = io::stdin();
    let mut line = String::new();
    stdin.lock().read_line(&mut line)?;
    Ok(line.trim().to_string())
}
fn write_string(w: &mut impl Write, s: &str) -> std::io::Result<()> {
    if s.is_empty() {
        w.write_all(&[0x00])?;
    } else {
        w.write_all(&[0x0b])?;
        leb128::write::unsigned(w, s.len() as u64)?;
        w.write_all(s.as_bytes())?;
    }
    Ok(())
}
fn write_byte_string(w: &mut impl Write, data: &[u8]) -> std::io::Result<()> {
    if data.is_empty() {
        w.write_all(&[0x00])?;
    } else {
        w.write_all(&[0x0c])?;
        leb128::write::unsigned(w, data.len() as u64)?;
        w.write_all(data)?;
    }
    Ok(())
}
fn skip_string(cursor: &mut Cursor<&[u8]>) -> io::Result<bool> {
    let flag = cursor.read_u8()?;
    match flag {
        0x00 => Ok(false),
        0x0b | 0x0c => {
            let len = leb128::read::unsigned(cursor)
                .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, format!("Something wrong... {}", e)))?;
            let current_pos = cursor.position();
            let remaining = cursor.get_ref().len() as u64;
            
            if current_pos.checked_add(len).map_or(true, |end_pos| end_pos > remaining) {
                 return Err(io::Error::new(io::ErrorKind::UnexpectedEof, format!("Something wrong... {} {}", len, current_pos)));
            }
            cursor.seek(SeekFrom::Current(len as i64))?;
            Ok(true)
        }
        _ => Err(io::Error::new(io::ErrorKind::InvalidData, format!("Something wrong...: {:#04x}", flag))),
    }
}
fn get_next_id(file_content: &[u8]) -> io::Result<u16> {
    let d_start_pos = find_pattern(file_content, &D_START)
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidData, "Something wrong..."))?;
    let d_end_pos = find_pattern(file_content, &D_END)
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidData, "Something wrong..."))?;
    if d_end_pos <= d_start_pos + D_START.len() {
        return Ok(1); 
    }
    let d_section = &file_content[d_start_pos + D_START.len()..d_end_pos];
    let mut cursor = Cursor::new(d_section);
    let mut max_id: u16 = 0;
    let mut notes_found = false;
    while cursor.position() < d_section.len() as u64 {
        let start_pos = cursor.position(); 
        if cursor.position() + 2 > d_section.len() as u64 {
             if cursor.position() != d_section.len() as u64 { 
                 eprintln!("Warning: Truncated data found while seeking note ID at position {}. Assuming end of notes.", start_pos);
             }
             break;
        }
        let current_id = cursor.read_u16::<LittleEndian>()?;
        max_id = max_id.max(current_id);
        notes_found = true;
        
        let mut skip = |field_name: &str, skip_fn: fn(&mut Cursor<&[u8]>) -> io::Result<()>| -> io::Result<()> {
             let remaining_bytes = d_section.len() as u64 - cursor.position();
             if remaining_bytes == 0 && field_name != "End Check" { 
             }
            skip_fn(&mut cursor).map_err(|e| {
                io::Error::new(e.kind(), format!("Something wrong... {} {} {} {}", field_name, current_id, start_pos, e))
            })
        };
        skip("Access token",        |c| skip_string(c).map(|_|()))?;
        skip("Author First Name",   |c| skip_string(c).map(|_|()))?;
        skip("Author Last Name",    |c| skip_string(c).map(|_|()))?;
        skip("Author Email",        |c| skip_string(c).map(|_|()))?;
        skip("Title",               |c| skip_string(c).map(|_|()))?;
        skip("Key Index",           |c| c.seek(SeekFrom::Current(8)).map(|_| ()))?;
        skip("Encrypted Content",   |c| skip_string(c).map(|_|()))?;
        skip("Creation Date",       |c| c.seek(SeekFrom::Current(8)).map(|_| ()))?;
        skip("Modification Date",   |c| c.seek(SeekFrom::Current(8)).map(|_| ()))?;
        skip("Suspended State",     |c| c.seek(SeekFrom::Current(1)).map(|_| ()))?;
        if cursor.position() <= start_pos { 
             return Err(io::Error::new(io::ErrorKind::InvalidData, format!("Something wrong... {} {}", current_id, start_pos)));
        }
    }
    if max_id == u16::MAX {
        Err(io::Error::new(io::ErrorKind::Other, "Something wrong..."))
    } else {
        Ok(if notes_found { max_id + 1 } else { 1 })
    }
}
fn encrypt(key: &[u8;8], plaintext: &[u8]) -> Result<Vec<u8>, String> {
    let cipher = Cipher::des_ecb();
    let mut crypter = Crypter::new(cipher, Mode::Encrypt, key, None)
        .map_err(|e| format!("Something wrong... {}", e))?;
    crypter.pad(true);
    let mut out = vec![0; plaintext.len() + cipher.block_size()];
    let mut len = crypter.update(plaintext, &mut out)
        .map_err(|e| format!("Something wrong... {}", e))?;
    len += crypter.finalize(&mut out[len..])
        .map_err(|e| format!("Something wrong... {}", e))?;
    out.truncate(len);
    Ok(out)
}
fn get_rand_string(len: usize) -> String {
    thread_rng().sample_iter(&Alphanumeric).take(len).map(char::from).collect()
}
fn get_rand_key() -> [u8;8] {
    let mut k = [0u8;8];
    thread_rng().fill(&mut k);
    k
}
struct Note {
    first_name: String,
    last_name: String,
    email: String,
    title: String,
    content: String,
}
struct Header {
    db_name: String,
    reg_name: String,
    license_key: Vec<u8>,
}
fn write_header(w: &mut impl Write, details: &Header, version: u32, reg_date: u64) -> io::Result<()> {
    write_string(w, &details.db_name)?;
    w.write_u32::<LittleEndian>(version)?;
    write_string(w, &details.reg_name)?;
    w.write_u64::<LittleEndian>(reg_date)?;
    write_byte_string(w, &details.license_key)?;
    Ok(())
}
fn write_note(
    w: &mut impl Write,
    details: &Note,
    note_id: u16,
    access_token: &str,
    key_index_field: u64,
    encrypted_content: &[u8],
    creation_date: u64,
    modification_date: u64,
    is_suspended: bool
) -> io::Result<()> {
    w.write_u16::<LittleEndian>(note_id)?;
    write_string(w, access_token)?;
    write_string(w, &details.first_name)?;
    write_string(w, &details.last_name)?;
    write_string(w, &details.email)?;
    write_string(w, &details.title)?;
    let final_key_index_field = if details.title.is_empty() || encrypted_content.is_empty() {
        0xFFFFFFFFFFFFFFFF
    } else {
        key_index_field
    };
    w.write_u64::<LittleEndian>(final_key_index_field)?;
    write_byte_string(w, encrypted_content)?;
    w.write_u64::<LittleEndian>(creation_date)?;
    w.write_u64::<LittleEndian>(modification_date)?;
    w.write_u8(if is_suspended { 0x01 } else { 0x00 })?;
    Ok(())
}
fn prompt() -> io::Result<Note> {
    Ok(Note {
        first_name: get_input("Author's First Name: ")?,
        last_name:  get_input("Author's Last Name: ")?,
        email:      get_input("Author's Email: ")?,
        title:      get_input("Note Title: ")?,
        content:    get_input("Note Content: ")?,
    })
}
fn build(
    mode: DbMode<'_>,
    count: usize,
    mut next_id: u16,
) -> io::Result<(Vec<Vec<u8>>, Vec<u8>, u16)> {
    let mut rng = thread_rng();
    let mut notes = Vec::with_capacity(count);
    let mut new_keys = Vec::new();
    for i in 0..count {
        println!("\n--- Creating Note {} of {} (ID: {}) ---", i+1, count, next_id);
        let note = prompt()?;
        
        let (key, idx, collect_keys) = match mode {
            DbMode::Append { existing } => {
                let j = rng.gen_range(0..existing.len());
                (existing[j], j as u64, false)
            }
            DbMode::Create => {
                let nk = rng.gen_range(16..64);
                let mut temp = Vec::with_capacity(nk);
                for _ in 0..nk {
                    let k = get_rand_key();
                    new_keys.extend_from_slice(&k);
                    temp.push(k);
                }
                let j = rng.gen_range(0..nk);
                (temp[j], ((new_keys.len()/8 - nk) + j) as u64, true)
            }
        };
        let encrypted = encrypt(&key, note.content.as_bytes())
            .map_err(|e| io::Error::new(io::ErrorKind::Other, e))?;
        let field = if idx < 64 { 1u64 << idx } else { 0xFFFFFFFFFFFFFFFF };
        let now   = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
        let token = get_rand_string(32);
        let mut buf = Vec::new();
        write_note(&mut buf, &note, next_id, &token, field, &encrypted, now, now, false)?;
        notes.push(buf);
        next_id = next_id.checked_add(1)
            .ok_or_else(|| io::Error::new(io::ErrorKind::Other, "Something wrong..."))?;
    }
    Ok((notes, new_keys, next_id))
}
fn write_db(
    path: &Path,
    header: Option<Header>,
    existing_blob: Option<&[u8]>,
    notes: &[Vec<u8>],
    keys: &[u8],
) -> io::Result<()> {
    let mut out = OpenOptions::new()
        .write(true)
        .truncate(existing_blob.is_some())
        .create(existing_blob.is_none())
        .open(path)?;
    let mut blob = Vec::new();
    if let Some(old) = existing_blob {
        let d_end = find_pattern(old, &D_END).unwrap();
        blob.extend_from_slice(&old[..d_end]);
    } else {
        let mut hb = Vec::new();
        let hdr = header.expect("Something wrong...");
        write_header(&mut hb, &hdr, 1, SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs())?;
        blob.extend_from_slice(&SIG);
        blob.extend_from_slice(&H_START);
        blob.extend_from_slice(&hb);
        blob.extend_from_slice(&H_END);
        blob.extend_from_slice(&D_START);
    }
    
    for n in notes { blob.extend_from_slice(n); }
    blob.extend_from_slice(&D_END);
    blob.extend_from_slice(&F_START);
    if let Some(old) = existing_blob {
        
        let fstart = find_pattern(old, &F_START).unwrap() + F_START.len();
        let fend   = find_pattern(old, &F_END).unwrap();
        blob.extend_from_slice(&old[fstart..fend]);
    } else {
        
        blob.extend_from_slice(keys);
    }
    
    blob.extend_from_slice(&F_END);
    out.write_all(&blob)?;
    Ok(())
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: {} <lunadb_file>", args[0]);
        process::exit(1);
    }
    let db_path = Path::new(&args[1]);
    let num_notes_to_create: usize = loop {
        match get_input("How many notes do you want to create? ")?.parse() {
            Ok(n) if n > 0 => break n,
            _ => println!("Please enter a valid positive number."),
        }
    };
    if db_path.exists() {
        
        let mut f = Vec::new();
        File::open(&db_path)?.read_to_end(&mut f)?;
        let keys = {
            let start = find_pattern(&f, &F_START).unwrap() + F_START.len();
            let end   = find_pattern(&f, &F_END).unwrap();
            (&f[start..end]).chunks_exact(8)
                         .map(|c| c.try_into().unwrap())
                          .collect::<Vec<[u8;8]>>()
        };
        let next_id = get_next_id(&f)?;
        let (notes, _, _) = build(DbMode::Append { existing: &keys }, num_notes_to_create, next_id)?;
        write_db(&db_path, None, Some(&f), &notes, &[])?;
        println!("Appended {} notes", num_notes_to_create);
    } else {
        let header = Header {
            db_name:  get_input("Database Name: ")?,
            reg_name: get_input("Registered Name: ")?,
            license_key: get_input("License Key: ")?.into_bytes(),
        };
        let (notes, keys, _) = build(DbMode::Create, num_notes_to_create, 1)?;
        write_db(&db_path, Some(header), None, &notes, &keys)?;
        println!("Created new DB with {} notes", num_notes_to_create);
    }
    Ok(())
}