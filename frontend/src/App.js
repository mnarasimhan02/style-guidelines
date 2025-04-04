import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  LinearProgress,
  Alert,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import FileUpload from './components/FileUpload';
import ResultsTable from './components/ResultsTable';
import RuleDrawer from './components/RuleDrawer';
import { uploadFile } from './services/api';

const StyledContainer = styled(Container)(({ theme }) => ({
  marginTop: theme.spacing(4),
  marginBottom: theme.spacing(4),
}));

const App = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [results, setResults] = useState(null);
  const [styleGuideUploaded, setStyleGuideUploaded] = useState(false);
  const [rules, setRules] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleStyleGuideUpload = async (file) => {
    try {
      setLoading(true);
      setError(null);
      const response = await uploadFile('/upload/style-guide', file);
      setStyleGuideUploaded(true);
      setRules(response.rules);
      setDrawerOpen(true);
      setSuccess('Style guide uploaded and processed successfully!');
    } catch (err) {
      setError(err.message || 'Error uploading style guide');
      setStyleGuideUploaded(false);
    } finally {
      setLoading(false);
    }
  };

  const handleCSRUpload = async (file) => {
    try {
      setLoading(true);
      setError(null);
      const response = await uploadFile('/upload/csr', file);
      if (response && Array.isArray(response)) {
        setResults(response);
        setSuccess('CSR document processed successfully!');
      } else {
        throw new Error('Invalid response format from server');
      }
    } catch (err) {
      setError(err.message || 'Error uploading CSR');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(null);
    setError(null);
  };

  // Function to highlight differences between original and corrected text
  const highlightDifferences = (original, corrected) => {
    if (original === corrected) return corrected;
    
    // Split both texts into words
    const originalWords = original.split(/(\s+)/);
    const correctedWords = corrected.split(/(\s+)/);
    
    // Find and highlight differences
    let result = [];
    let i = 0, j = 0;
    
    while (i < originalWords.length && j < correctedWords.length) {
      if (originalWords[i] === correctedWords[j]) {
        result.push(correctedWords[j]);
        i++;
        j++;
      } else {
        result.push(<span key={j} style={{ backgroundColor: '#e3f2fd', fontWeight: 'bold' }}>{correctedWords[j]}</span>);
        j++;
        // Skip the corresponding word in original
        i++;
      }
    }
    
    // Add any remaining words
    while (j < correctedWords.length) {
      result.push(<span key={j} style={{ backgroundColor: '#e3f2fd', fontWeight: 'bold' }}>{correctedWords[j]}</span>);
      j++;
    }
    
    return <>{result}</>;
  };

  return (
    <StyledContainer maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Style Guide Checker
      </Typography>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert severity="error" onClose={handleCloseSnackbar}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert severity="success" onClose={handleCloseSnackbar}>
          {success}
        </Alert>
      </Snackbar>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          1. Upload Style Guide (PDF)
        </Typography>
        <FileUpload
          onUpload={handleStyleGuideUpload}
          accept=".pdf"
          disabled={loading || styleGuideUploaded}
        />
        {styleGuideUploaded && (
          <Button
            variant="outlined"
            onClick={() => setDrawerOpen(true)}
            sx={{ mt: 2 }}
          >
            View Style Guide Rules
          </Button>
        )}
        {styleGuideUploaded && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Style guide uploaded and ready for use
          </Alert>
        )}
      </Paper>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          2. Upload CSR Document (PDF or DOCX)
        </Typography>
        <FileUpload
          onUpload={handleCSRUpload}
          accept=".pdf,.docx"
          disabled={loading || !styleGuideUploaded}
        />
      </Paper>

      {loading && (
        <Box sx={{ width: '100%', mb: 2 }}>
          <LinearProgress />
        </Box>
      )}

      {results && results.length > 0 && (
        <>
          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
            Analysis Results
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Section</TableCell>
                  <TableCell>Original Text</TableCell>
                  <TableCell>Corrected Text</TableCell>
                  <TableCell>Changes and Matches</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((result, index) => (
                  <TableRow key={index}>
                    <TableCell>Section {index + 1}</TableCell>
                    <TableCell style={{ whiteSpace: 'pre-wrap' }}>{result.text}</TableCell>
                    <TableCell style={{ whiteSpace: 'pre-wrap' }}>
                      {highlightDifferences(result.text, result.corrected_text)}
                    </TableCell>
                    <TableCell>
                      {result.changes.map((change, idx) => (
                        <Typography key={idx} variant="body2" gutterBottom>
                          {change}
                        </Typography>
                      ))}
                      {result.matches.map((match, idx) => (
                        <Typography key={`match-${idx}`} variant="body2" color="textSecondary" gutterBottom>
                          Rule: {match.rule.description}
                        </Typography>
                      ))}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}

      <RuleDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        rules={rules}
      />
    </StyledContainer>
  );
};

export default App;
