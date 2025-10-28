import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Box
} from '@mui/material';
import axios from 'axios';

interface CourseContent {
  course_id: string;
  title: string;
  content: string;
}

const CourseViewer = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const [content, setContent] = useState<CourseContent | null>(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const response = await axios.get(`/api/courses/${courseId}`);
        setContent(response.data);

        // Enregistrer l'événement de début de session
        const enrollmentResponse = await axios.get('/api/enrollments', {
          params: { user_id: 1 } // TODO: Récupérer depuis le contexte d'auth
        });

        const enrollment = enrollmentResponse.data.find(
          (e: any) => e.course_id === courseId
        );

        if (enrollment) {
          await axios.post(`/api/enrollments/${enrollment.id}/events`, {
            event_type: 'session_start',
            metadata: {
              timestamp: new Date().toISOString()
            }
          });
        }
      } catch (error) {
        console.error('Erreur lors du chargement du cours:', error);
      }
    };
    fetchContent();

    // Enregistrer les événements de page vue
    const trackPageView = async () => {
      try {
        const enrollmentResponse = await axios.get('/api/enrollments', {
          params: { user_id: 1 } // TODO: Récupérer depuis le contexte d'auth
        });

        const enrollment = enrollmentResponse.data.find(
          (e: any) => e.course_id === courseId
        );

        if (enrollment) {
          await axios.post(`/api/enrollments/${enrollment.id}/events`, {
            event_type: 'page_view',
            metadata: {
              timestamp: new Date().toISOString(),
              page: window.location.pathname
            }
          });
        }
      } catch (error) {
        console.error('Erreur lors du tracking:', error);
      }
    };

    trackPageView();
    const interval = setInterval(trackPageView, 60000); // Tracker toutes les minutes

    return () => {
      clearInterval(interval);
    };
  }, [courseId]);

  if (!content) {
    return <Typography>Chargement...</Typography>;
  }

  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        {content.title}
      </Typography>
      <Paper>
        <Box p={3}>
          <div dangerouslySetInnerHTML={{ __html: content.content }} />
        </Box>
      </Paper>
    </Container>
  );
};

export default CourseViewer;