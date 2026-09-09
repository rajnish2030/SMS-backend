from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from APP.database import engine, Base, get_db
from APP.model.model import Student
from APP.schemas.schema import StudentCreate

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management API")

# Enable CORS for cross-origin frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"Message": "Student management API is running ✅"}


@app.get("/health")
def database_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "Success", "message": "Database working ✅"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/students", status_code=status.HTTP_201_CREATED)
@app.post("/students/", status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentCreate, 
    db: Session = Depends(get_db)
):
    existing_student = (
        db.query(Student)
        .filter(Student.email == student.email)
        .first()
    )

    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    new_student = Student(
        name=student.name,
        email=student.email,
        age=student.age
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "Message": "Student created successfully ✅",
        "student": {
            "id": new_student.id,
            "name": new_student.name,
            "email": new_student.email,
            "age": new_student.age,
        }
    }


@app.get("/students")
@app.get("/students/")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()

    return {
        "message": "Students fetched successfully",
        "students": [
            {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "age": student.age
            }
            for student in students
        ]
    }


@app.delete("/students/{student_id}")
@app.delete("/students/{student_id}/")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"  # Fixed typo: changed 'details' to 'detail'
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully",
        "student_id": student_id
    }