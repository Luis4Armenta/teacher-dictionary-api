from pydantic import BaseModel, Field
from models.course import Course
from typing import List

class Schedule(BaseModel):
  courses: List[Course] = Field(title="Cursos", description="Cursos que conforman el horario")
  # start_time: str
  # end_time:str
  popularity: float = Field(title="Puntaje positivo", description="Promedio del puntaje positivo de todos los profesores que imparten las asignaturas que conforman el horario.")