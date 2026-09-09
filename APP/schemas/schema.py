from pydantic import BaseModel, EmailStr

# Schema for creating a student
class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    age: int


