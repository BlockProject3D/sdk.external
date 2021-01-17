use clap::clap_app;
use std::string::String;

mod vec;
mod bpm;
mod decompiler;
mod writer;

pub const VERSION: &'static str = "1.0";

fn main() {
    let matches = clap_app!(bpmd =>
        (version: VERSION)
        (author: "BlockProject3D <https://github.com/BlockProject3D>")
        (about: "BPM Decompiler; a tool to decompile a BPM back to an OBJ")
        (@arg file: "Specifies the file to decompile")
    ).get_matches();
    let s = matches.value_of("file").unwrap();
    let mut out = String::from(s);

    out.push_str(".obj");
    match decompiler::decompile(&s)
    {
        Ok((vp, vn, vt, tris)) =>
        {
            println!("Writing OBJ to {}...", out);
            match writer::write(&out, &vp, &vn, &vt, &tris)
            {
                Err(e) =>
                {
                    eprintln!("An error has occured while writing OBJ: {}", e);
                    std::process::exit(1);
                }
                Ok(()) => std::process::exit(0)
            }
        },
        Err(e) =>
        {
            eprintln!("An error has occured while decompiling BPM: {}", e);
            std::process::exit(1);
        }
    }
}
