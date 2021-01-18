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

use std::io::Read;
use bufferedreader::BufferedReader;
use std::io::Result;
use byteorder::LittleEndian;
use byteorder::ByteOrder;
use std::path::Path;
use std::fs::File;
use super::vec::Vec3f;
use super::vec::Vec2f;
use std::vec::Vec;
use std::io::Error;
use std::io::ErrorKind;
use std::fs::metadata;

pub struct Header
{
    signature: [u8; 3],
    version: u8,
    vertices: u16
}

const SIZE_BYTES_HEADER: usize = 6;

impl Header
{
    pub fn read(reader: &mut dyn Read) -> Result<Header>
    {
        let mut buf: [u8; SIZE_BYTES_HEADER] = [0; SIZE_BYTES_HEADER];

        reader.read(&mut buf)?;
        return Ok(Header
        {
            signature: [buf[0], buf[1], buf[2]],
            version: buf[3],
            vertices: LittleEndian::read_u16(&buf[4..6])
        });
    }
}

pub struct Vertex
{
    pub position: Vec3f, //+0 to +12
    pub normal: Vec3f, //+12 to +24
    pub uv: Vec2f //+24 to +32
}

const SIZE_BYTES_VERTEX_REV2: usize = 32;
const SIZE_BYTES_VERTEX_REV1: usize = 20;

impl PartialEq for Vertex
{
    fn eq(&self, other: &Self) -> bool
    {
        return self.normal == other.normal && self.position == other.position && self.uv == other.uv;
    }
}

pub struct BPM
{
    pub vertices: Vec<Vertex>
}

fn load_vec3f(block: &[u8]) -> Vec3f
{
    return Vec3f::new(
        LittleEndian::read_f32(&block[0..4]),
        LittleEndian::read_f32(&block[4..8]),
        LittleEndian::read_f32(&block[8..12])
    );
}

fn load_vec2f(block: &[u8]) -> Vec2f
{
    return Vec2f::new(
        LittleEndian::read_f32(&block[0..4]),
        LittleEndian::read_f32(&block[4..8])
    );
}

fn load_vertices(reader: &mut dyn Read, count: u16, version: u8) -> Result<Vec<Vertex>>
{
    let mut v = Vec::with_capacity(count as usize);

    for _ in 0..count
    {
        if version == 1
        {
            let mut buf: [u8; SIZE_BYTES_VERTEX_REV2] = [0; SIZE_BYTES_VERTEX_REV2];
            let res = reader.read(&mut buf)?;

            if res != SIZE_BYTES_VERTEX_REV2
            {
                return Err(Error::new(ErrorKind::InvalidData, "[BPM] File is truncated"));
            }
            v.push(Vertex
            {
                position: load_vec3f(&buf[0..12]),
                normal: load_vec3f(&buf[12..24]),
                uv: load_vec2f(&buf[24..32])
            });
        }
        else
        {
            let mut buf: [u8; SIZE_BYTES_VERTEX_REV1] = [0; SIZE_BYTES_VERTEX_REV1];
            let res = reader.read(&mut buf)?;

            if res != SIZE_BYTES_VERTEX_REV1
            {
                return Err(Error::new(ErrorKind::InvalidData, "[BPM] File is truncated"));
            }
            v.push(Vertex
            {
                position: load_vec3f(&buf[0..12]),
                normal: Vec3f::new(0 as f32, 0 as f32, 0 as f32),
                uv: load_vec2f(&buf[12..20])
            });
        }
    }
    return Ok(v);
}

fn check_header(header: &Header) -> Result<()>
{
    if header.signature[0] != 0x42 || header.signature[1] != 0x50 || header.signature[2] != 0x4D
    {
        return Err(Error::new(ErrorKind::InvalidData, "[BPM] Bad signature"));
    }
    if header.version != 0 //There are no further version only version 0 ever existed
    {
        return Err(Error::new(ErrorKind::InvalidData, "[BPM] Bad version"));
    }
    return Ok(());
}

fn get_file_size(path: &Path) -> Result<u64>
{
    let md = metadata(path)?;

    return Ok(md.len());
}

impl BPM
{
    pub fn new(path: &Path) -> Result<BPM>
    {
        let size = get_file_size(&path)?;
        let file = File::open(&path)?;
        let mut reader = BufferedReader::new(file);
        let mut head = Header::read(&mut reader)?;

        check_header(&head)?;
        if SIZE_BYTES_VERTEX_REV2 as u64 * head.vertices as u64 == size - SIZE_BYTES_HEADER as u64
        {
            head.version = 1; //Correct version number
        }
        println!("Found BPM version {} with {} vertices", head.version, head.vertices);
        return Ok(BPM
        {
            vertices: load_vertices(&mut reader, head.vertices, head.version)?
        });
    }
}
