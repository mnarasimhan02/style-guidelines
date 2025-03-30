import React from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Box,
} from '@mui/material';
import FileDownloadIcon from '@mui/icons-material/FileDownload';

const ResultsTable = ({ results }) => {
  const handleExport = () => {
    const csvContent = [
      ['Section', 'Original Text', 'Corrected Text', 'Rules Applied'],
      ...results.map((row) => [
        row.section,
        row.original_text,
        row.corrected_text,
        row.rules_applied.join('; '),
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'style_corrections.csv';
    link.click();
  };

  return (
    <Paper elevation={3}>
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          startIcon={<FileDownloadIcon />}
          onClick={handleExport}
        >
          Export to CSV
        </Button>
      </Box>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Section</TableCell>
              <TableCell>Original Text</TableCell>
              <TableCell>Corrected Text</TableCell>
              <TableCell>Rules Applied</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {results.map((row, index) => (
              <TableRow key={index}>
                <TableCell>{row.section}</TableCell>
                <TableCell>{row.original_text}</TableCell>
                <TableCell>{row.corrected_text}</TableCell>
                <TableCell>{row.rules_applied.join(', ')}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default ResultsTable;
