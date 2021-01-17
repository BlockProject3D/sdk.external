use clap::clap_app;
use std::string::String;
use std::io::Result;

mod vec;
mod bpm;
mod decompiler;

fn write_obj(out: &str, vp: &Vec<vec::Vec3f>, vn: &Vec<vec::Vec3f>, vt: &Vec<vec::Vec2f>, tris: &Vec<decompiler::Triangle>) -> Result<()>
{
    return Ok(());
}

fn main() {
    let matches = clap_app!(bpmd =>
        (version: "1.0")
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
            match write_obj(&out, &vp, &vn, &vt, &tris)
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
            eprintln!("An error has occured while decompiling: {}", e);
            std::process::exit(1);
        }
    }
}
