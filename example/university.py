import os
import sys
from random import randint

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from persistify.persistify import save, load

class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.courses = []

    def enroll(self, course):
        """Sign the student up for the course."""
        self.courses.append(course)
        course.add_student(self)

    def list_courses(self):
        """Returns a list of course titles in which the student is signed up."""
        return [course.title for course in self.courses]

    def __str__(self):
        courses_list = ', '.join(self.list_courses())
        return f"Student: {self.name} (ID: {self.student_id}), Enrolled in: [{courses_list}]"


class Professor:
    def __init__(self, name, field):
        self.name = name
        self.field = field
        self.courses = []  # Courses taught by Prof.

    def add_course(self, course):
        """Attach the course to the professor's list of courses and set the professor at the course."""
        self.courses.append(course)
        course.professor = self

    def list_courses(self):
        """Returns a list of the names of courses taught by the professor."""
        return [course.title for course in self.courses]

    def __str__(self):
        courses_list = ', '.join(self.list_courses())
        return f"Professor: {self.name} (Field: {self.field}), Courses: [{courses_list}]"


class Course:
    def __init__(self, title):
        self.title = title
        self.lessons = []
        #self.professor = None
        #self.students = []  

    # def add_student(self, student):
    #     if student not in self.students:
    #         self.students.append(student)
    #         if self not in student.courses:
    #             student.courses.append(self)
    
    def add_lesson(self, lesson_name: str):
        self.lessons.append(lesson_name)

    # def __str__(self):
    #     prof_name = self.professor.name if self.professor else "No professor"
    #     student_names = ', '.join([s.name for s in self.students])
    #     return f"Course: {self.title}, Professor: {prof_name}, Students: [{student_names}]"
    def __str__(self) -> str:
        res = f"\tCourse: {self.title}:"
        for lesson in self.lessons:
            res += f"\n\t\t{lesson}"
        return res

class Department:
    def __init__(self, name):
        self.name = name
        self.professors = []
        self.courses = []
        self.students = [] # Students attached to the department

    def add_professor(self, professor):
        self.professors.append(professor)

    def add_course(self, course):
        self.courses.append(course)

    def add_student(self, student):
        self.students.append(student)

    def __str__(self):
        profs = ', '.join([prof.name for prof in self.professors])
        students = ', '.join([student.name for student in self.students])

        courses = ""
        for course in self.courses:
            courses += f"\n{course}"

        return f"Department: {self.name}\n  Professors: [{profs}]\n  Courses: {courses}\n  Students: [{students}]"

class University:
    def __init__(self, name):
        self.name = name
        self.departments = [] # List of university departments

    def add_department(self, department):
        self.departments.append(department)

    def __str__(self):
        dept_str = "\n".join([str(dept) for dept in self.departments])
        return f"University: {self.name}\nDepartments:\n{dept_str}"


def main():
    university = University("State University")

    cs_department = Department("Computer Science")
    math_department = Department("Mathematics")

    university.add_department(cs_department)
    university.add_department(math_department)

    prof_alice = Professor("Alice", "Computer Science")
    prof_bob = Professor("Bob", "Mathematics")

    cs_department.add_professor(prof_alice)
    math_department.add_professor(prof_bob)

    course_python = Course("Introduction to Python")
    course_algorithms = Course("Algorithms")
    course_java  = Course("Java Fundamentals")

    courses = [course_python, course_algorithms, course_java]
    for course in courses:
        unit = 0
        lessons_count = randint(30, 50)

        for i in range(lessons_count):
            if randint(1, 100) <= 30:
                unit += 1
            course.add_lesson(f"Unit #{unit} Lesson #{i+1} of {course.title}.")

    cs_department.add_course(course_python)
    cs_department.add_course(course_algorithms)
    math_department.add_course(course_java)    

    #prof_alice.add_course(course_python)
    #prof_alice.add_course(course_algorithms)
    #prof_bob.add_course(course_calculus)


    student_charlie = Student(1001, "Charlie")
    student_david = Student(1002, "David")
    student_eve = Student(1003, "Eve")

    cs_department.add_student(student_charlie)
    cs_department.add_student(student_david)
    math_department.add_student(student_eve)

    #course_python.add_student(student_charlie)
    #course_algorithms.add_student(student_david)
    #course_calculus.add_student(student_eve)
    
    print("Original instance of University:")
    print(university)
    
    # Save the university object to a file that is indented for easy reading
    file = os.path.join(os.path.dirname(__file__), "university_data.pydat")
    with open(file, "w") as f:
        save(f, university, indent=4)

    print(f"\nAn instance of the university class has been saved to a file: {file}")

    # Recover our object from the file, passing the list of classes to recover
    with open(file, "r") as f:
        restored_data = load(f, (University, Department, Course, Professor, Student))

    print("\nRestored object University:")
    print(restored_data)

    string_universite = save(None, restored_data)
    university_restored = load(string_universite, (University, Department, Course, Professor, Student))
    #print(f"Loaded again: {university_restored}") 

if __name__ == "__main__":
    main()
