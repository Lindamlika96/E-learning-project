import React, { useEffect, useState } from 'react';
import {
  Button,
  Card,
  CardContent,
  CardActions,
  Typography,
  Grid,
  Container
} from '@mui/material';
import { Theme } from '@mui/material/styles';
import { SxProps } from '@mui/system';
import axios from 'axios';

interface Course {
  course_id: string;
  title: string;
  category: string;
  level: string;
  tutor: string;
  total_pages: number;
}

const CourseList = () => {
  const [courses, setCourses] = useState<Course[]>([]);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await axios.get('/api/courses');
        setCourses(response.data);
      } catch (error) {
        console.error('Erreur lors du chargement des cours:', error);
      }
    };
    fetchCourses();
  }, []);

  const handleStartCourse = async (courseId: string) => {
    try {
      // TODO: Récupérer le student_id depuis le contexte d'authentification
      const studentId = 1; // Temporaire

      // Créer l'inscription
      await axios.post('/api/enrollments', {
        user_id: studentId,
        course_id: courseId
      });

      // Rediriger vers la page du cours
      window.location.href = `/course/${courseId}`;
    } catch (error) {
      console.error('Erreur lors de l\'inscription au cours:', error);
    }
  };

  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Catalogue des cours
      </Typography>
      <Grid container spacing={3}>
        {courses.map((course) => (
          <Grid 
            item 
            xs={12} 
            sm={6} 
            md={4} 
            key={course.course_id}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2">
                  {course.title}
                </Typography>
                <Typography color="text.secondary">
                  Niveau: {course.level}
                </Typography>
                <Typography>
                  Tuteur: {course.tutor}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  onClick={() => window.location.href = `/course/${course.course_id}/details`}
                >
                  Voir détails
                </Button>
                <Button
                  size="small"
                  color="primary"
                  onClick={() => handleStartCourse(course.course_id)}
                >
                  Commencer
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default CourseList;