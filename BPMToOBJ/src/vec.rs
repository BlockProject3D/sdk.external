#[derive(Copy, Clone)]
pub struct Vec3f
{
    pub x: f32,
    pub y: f32,
    pub z: f32
}

impl Vec3f
{
    pub fn new(x: f32, y: f32, z: f32) -> Vec3f
    {
        return Vec3f
        {
            x: x,
            y: y,
            z: z
        };
    }
}

impl PartialEq for Vec3f
{
    fn eq(&self, other: &Self) -> bool
    {
        return self.x == other.x && self.y == other.y && self.z == other.z;
    }
}

#[derive(Copy, Clone)]
pub struct Vec2f
{
    pub x: f32,
    pub y: f32
}

impl Vec2f
{
    pub fn new(x: f32, y: f32) -> Vec2f
    {
        return Vec2f
        {
            x: x,
            y: y
        };
    }
}

impl PartialEq for Vec2f
{
    fn eq(&self, other: &Self) -> bool
    {
        return self.x == other.x && self.y == other.y;
    }
}