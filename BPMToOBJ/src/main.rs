// Copyright (c) 2021, BlockProject 3D
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//     * Redistributions of source code must retain the above copyright notice,
//       this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above copyright notice,
//       this list of conditions and the following disclaimer in the documentation
//       and/or other materials provided with the distribution.
//     * Neither the name of BlockProject 3D nor the names of its contributors
//       may be used to endorse or promote products derived from this software
//       without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
        (@arg file: +required "Specifies the file to decompile")
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
