use clap::clap_app;

mod vec;
mod bpm;

fn main() {
    let matches = clap_app!(bpmd =>
        (version: "1.0")
        (author: "BlockProject3D <https://github.com/BlockProject3D>")
        (about: "BPM Decompiler; a tool to decompile a BPM back to an OBJ")
        (@arg file: "Specifies the file to decompile")
    ).get_matches();

    let s = matches.value_of("file").unwrap();

    println!("Hello, world!");
}
