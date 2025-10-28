import React, { useEffect, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Container,
  Typography,
  TableSortLabel,
  Chip
} from '@mui/material';
import axios from 'axios';

interface Student {
  student_id: number;
  student_name: string;
  course_id: number;
  course_name: string;
  abandon_score: number;
  predicted_at: string;
  status: string;
}

const AdminDashboard = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [orderBy, setOrderBy] = useState<keyof Student>('abandon_score');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');

  const fetchData = async () => {
    try {
      const response = await axios.get('/api/students/at-risk');
      setStudents(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSort = (property: keyof Student) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedStudents = [...students].sort((a, b) => {
    const aValue = a[orderBy];
    const bValue = b[orderBy];
    if (order === 'asc') {
      return aValue < bValue ? -1 : 1;
    } else {
      return bValue < aValue ? -1 : 1;
    }
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Critique':
        return 'error';
      case 'À surveiller':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Tableau de bord - Étudiants à risque
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'student_name'}
                  direction={orderBy === 'student_name' ? order : 'asc'}
                  onClick={() => handleSort('student_name')}
                >
                  Étudiant
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'course_name'}
                  direction={orderBy === 'course_name' ? order : 'asc'}
                  onClick={() => handleSort('course_name')}
                >
                  Cours
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'abandon_score'}
                  direction={orderBy === 'abandon_score' ? order : 'asc'}
                  onClick={() => handleSort('abandon_score')}
                >
                  Score
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'status'}
                  direction={orderBy === 'status' ? order : 'asc'}
                  onClick={() => handleSort('status')}
                >
                  Statut
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'predicted_at'}
                  direction={orderBy === 'predicted_at' ? order : 'asc'}
                  onClick={() => handleSort('predicted_at')}
                >
                  Date
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedStudents.map((student) => (
              <TableRow key={`${student.student_id}-${student.course_id}`}>
                <TableCell>{student.student_name}</TableCell>
                <TableCell>{student.course_name}</TableCell>
                <TableCell>{(student.abandon_score * 100).toFixed(1)}%</TableCell>
                <TableCell>
                  <Chip
                    label={student.status}
                    color={getStatusColor(student.status) as any}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  {new Date(student.predicted_at).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default AdminDashboard;