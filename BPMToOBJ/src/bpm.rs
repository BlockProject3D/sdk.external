use std::io::Read;
use std::io::BufReader;
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

const SIZE_BYTES_VERTEX: usize = 32;

impl PartialEq for Vertex
{
    fn eq(&self, other: &Self) -> bool
    {
        return self.normal == other.normal && self.position == other.position && self.uv == other.uv;
    }
}

pub struct BPM
{
    vertices: Vec<Vertex>,
    header: Header
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

fn load_vertices(reader: &mut dyn Read, count: u16) -> Result<Vec<Vertex>>
{
    let mut v = Vec::with_capacity(count as usize);

    for _ in 0..count
    {
        let mut buf: [u8; SIZE_BYTES_VERTEX] = [0; SIZE_BYTES_VERTEX];

        reader.read(&mut buf)?;
        v.push(Vertex
        {
            position: load_vec3f(&buf[0..12]),
            normal: load_vec3f(&buf[12..24]),
            uv: load_vec2f(&buf[24..32])
        });
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

impl BPM
{
    pub fn new(path: &Path) -> Result<BPM>
    {
        let file = File::open(&path)?;
        let mut reader = BufReader::new(file);
        let head = Header::read(&mut reader)?;

        check_header(&head)?;
        return Ok(BPM
        {
            vertices: load_vertices(&mut reader, head.vertices)?,
            header: head
        });
    }
}
