use std::io::Result;
use std::path::Path;
use std::vec::Vec;
use super::vec::Vec3f;
use super::vec::Vec2f;
use super::bpm::Vertex;
use super::bpm::BPM;

pub struct Triangle
{
    vp: usize,
    vn: usize,
    vt: usize
}

fn unpack_dedupe(verts: &Vec<Vertex>) -> (Vec<Vec3f>, Vec<Vec3f>, Vec<Vec2f>)
{
    let mut vp: Vec<Vec3f> = Vec::with_capacity(verts.len());
    let mut vn: Vec<Vec3f> = Vec::with_capacity(verts.len());
    let mut vt: Vec<Vec2f> = Vec::with_capacity(verts.len());

    for v in verts
    {
        vp.push(v.position);
        vn.push(v.normal);
        vt.push(v.uv);
    }
    vp.dedup_by(|v, v1| v == v1);
    vn.dedup_by(|v, v1| v == v1);
    vt.dedup_by(|v, v1| v == v1);
    return (vp, vn, vt);
}

fn reconstruct_index_buffer(verts: &Vec<Vertex>, vp: &Vec<Vec3f>, vn: &Vec<Vec3f>, vt: &Vec<Vec2f>) -> Vec<Triangle>
{
    let mut res = Vec::with_capacity(verts.len());

    for v in verts
    {
        let tri = Triangle
        {
            vp: vp.iter().position(|&p| p == v.position).unwrap(),
            vn: vn.iter().position(|&p| p == v.normal).unwrap(),
            vt: vt.iter().position(|&p| p == v.uv).unwrap()
        };
        res.push(tri);
    }
    return res;
}

pub fn decompile(s: &str) -> Result<(Vec<Vec3f>, Vec<Vec3f>, Vec<Vec2f>, Vec<Triangle>)>
{
    println!("Loading {} into memory...", s);
    let bpm = BPM::new(Path::new(s))?;
    println!("Unpacking and de-duping vertices...");
    let (vp, vn, vt) = unpack_dedupe(&bpm.vertices);
    println!("Reconstructing index buffer...");
    let tris = reconstruct_index_buffer(&bpm.vertices, &vp, &vn, &vt);
    return Ok((vp, vn, vt, tris));
}
