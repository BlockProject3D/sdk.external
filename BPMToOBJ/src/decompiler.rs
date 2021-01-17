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

use std::io::Result;
use std::path::Path;
use std::vec::Vec;
use super::vec::Vec3f;
use super::vec::Vec2f;
use super::bpm::Vertex;
use super::bpm::BPM;

#[derive(Copy, Clone)]
pub struct VertexIndex
{
    pub vp: usize,
    pub vn: usize,
    pub vt: usize
}

pub struct Triangle
{
    pub p1: VertexIndex,
    pub p2: VertexIndex,
    pub p3: VertexIndex
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

fn reconstruct_index_buffer(verts: &Vec<Vertex>, vp: &Vec<Vec3f>, vn: &Vec<Vec3f>, vt: &Vec<Vec2f>) -> Vec<VertexIndex>
{
    let mut res = Vec::with_capacity(verts.len());

    for v in verts
    {
        let vi = VertexIndex
        {
            vp: vp.iter().position(|&p| p == v.position).unwrap(),
            vn: vn.iter().position(|&p| p == v.normal).unwrap(),
            vt: vt.iter().position(|&p| p == v.uv).unwrap()
        };
        res.push(vi);
    }
    return res;
}

fn reconstruct_triangles(verts: Vec<VertexIndex>) -> Vec<Triangle>
{
    let mut res = Vec::with_capacity(verts.len() / 3);

    for i in (0..verts.len()).step_by(3)
    {
        let tri = Triangle
        {
            p1: verts[i],
            p2: verts[i + 1],
            p3: verts[i + 2]
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
    let vis = reconstruct_index_buffer(&bpm.vertices, &vp, &vn, &vt);
    println!("Reconstructing triangles...");
    let tris = reconstruct_triangles(vis);
    return Ok((vp, vn, vt, tris));
}
